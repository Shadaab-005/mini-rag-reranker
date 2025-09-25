import sqlite3, pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from rank_bm25 import BM25Okapi
import re

DB_PATH = "sqlite_chunks.db"
FAISS_FILE = "vector.index"
BM25_FILE = "bm25_index.pkl"
EMB_FILE = "embeddings.npy"

def tokenize(text):
    return [w.lower() for w in re.findall(r"\w+", text)]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, url, chunk_text FROM chunks")
    rows = cur.fetchall()
    conn.close()

    texts = [r[3] for r in rows]
    metas = [{"id": r[0], "title": r[1], "url": r[2]} for r in rows]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Embedding chunks...")
    embs = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    np.save(EMB_FILE, embs)

    # FAISS index
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    faiss.normalize_L2(embs)
    index.add(embs)
    faiss.write_index(index, FAISS_FILE)

    # BM25 index
    print("Building BM25...")
    bm25 = BM25Okapi([tokenize(t) for t in texts])
    with open(BM25_FILE, "wb") as f:
        pickle.dump({"bm25": bm25, "texts": texts, "meta": metas}, f)

    print("Done. FAISS + BM25 indices built.")

if __name__ == "__main__":
    main()
