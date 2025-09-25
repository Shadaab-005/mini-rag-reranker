import sqlite3
import numpy as np
import faiss

class Retriever:
    def __init__(self, emb_file="embeddings.npy", faiss_file="vector.index", db_path="sqlite_chunks.db"):
        
        self.embs = np.load(emb_file)
        self.index = faiss.read_index(faiss_file)

        
        self.docs = []
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, title, url, chunk_text FROM chunks")
        for row in cur.fetchall():
            self.docs.append({
                "id": row[0],
                "meta": {"id": row[0], "title": row[1], "url": row[2]},
                "text": row[3]
            })
        conn.close()

    def vector_search(self, query, model, k=30):
        q_emb = model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, k)

        results = []
        for rank, i in enumerate(I[0]):
            results.append({
                "text": self.docs[i]["text"],
                "meta": self.docs[i]["meta"],
                "vector_score": float(D[0][rank])
            })
        return results
