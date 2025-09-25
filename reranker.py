import numpy as np
from lexical_bm25 import bm25_search

class HybridReranker:
    def __init__(self, alpha=0.5):
        self.alpha = alpha

    def rerank(self, query, vector_hits):
        bm_hits = bm25_search(query, k=30)
        bm_dict = {h["meta"]["id"]: h["bm25_score"] for h in bm_hits}
        bm_max  = max(bm_dict.values() or [1e-9])

        merged = []
        for v in vector_hits:
            bid = v["meta"]["id"]
            b_score = bm_dict.get(bid, 0.0)
            b_norm  = b_score / bm_max
            final   = self.alpha * v["vector_score"] + (1 - self.alpha) * b_norm
            v["bm25_score"] = b_score
            v["final_score"] = final
            merged.append(v)

        return sorted(merged, key=lambda x: x["final_score"], reverse=True)
