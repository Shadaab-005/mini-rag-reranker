import pickle, re

with open("bm25_index.pkl", "rb") as f:
    data = pickle.load(f)

_bm25  = data["bm25"]
_texts = data["texts"]
_meta  = data["meta"]

def _tok(t):
    return [w.lower() for w in re.findall(r"\w+", t)]

def bm25_search(query, k=30):
    scores = _bm25.get_scores(_tok(query))
    ranked = sorted(zip(_texts, _meta, scores), key=lambda x: x[2], reverse=True)[:k]
    return [
        {"text": t, "meta": m, "bm25_score": float(s)}
        for t, m, s in ranked
    ]
