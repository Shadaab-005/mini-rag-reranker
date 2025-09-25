from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from search import Retriever
from reranker import HybridReranker
from transformers import pipeline
import re

ABSTAIN_THRESHOLD = 0.25

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")


retriever = Retriever()
reranker = HybridReranker(alpha=0.6)


summarizer = pipeline(
    "summarization",
    model="t5-small",           
    tokenizer="t5-small"
)

class Query(BaseModel):
    q: str
    k: int = 3
    mode: str = "baseline"   

def compose_summary(chunks, max_len=120, min_len=40):
    """
    Join the top chunks and create a short 2–3 sentence summary.
    """
    if not chunks:
        return None
    text = " ".join(c["text"] for c in chunks)
    
    summary = summarizer(
        text,
        max_length=max_len,
        min_length=min_len,
        do_sample=False
    )[0]["summary_text"]
    return re.sub(r"\s+", " ", summary).strip()

@app.post("/ask")
def ask(query: Query):
    hits = retriever.vector_search(query.q, model, k=30)
    if query.mode == "hybrid":
        hits = reranker.rerank(query.q, hits)

    top = hits[:query.k]

    # Compose a concise summary if confidence is high enough
    answer = None
    if top and top[0].get("vector_score", 0) >= ABSTAIN_THRESHOLD:
        answer = compose_summary(top)

    return {
        "answer": answer,
        "contexts": top,
        "reranker_used": query.mode
    }
