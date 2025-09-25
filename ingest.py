import os
import json
import sqlite3
import pdfplumber
import re
import nltk
from tqdm import tqdm


nltk.download('punkt')

DATA_DIR = "data/pdfs"
SOURCES_JSON = "data/sources.json"
DB_PATH = "sqlite_chunks.db"
CHUNK_MIN_WORDS = 150
CHUNK_MAX_WORDS = 350


def text_from_pdf(path: str) -> str:
    texts = []
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                texts.append(t)
    return "\n\n".join(texts)


def split_to_chunks(text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks = []
    for para in paras:
        words = para.split()
        if len(words) < CHUNK_MIN_WORDS:
            chunks.append(para)
        else:
            sents = nltk.tokenize.sent_tokenize(para)
            cur, cur_words = [], 0
            for s in sents:
                sw = len(s.split())
                if cur_words + sw > CHUNK_MAX_WORDS and cur:
                    chunks.append(" ".join(cur))
                    cur, cur_words = [s], sw
                else:
                    cur.append(s)
                    cur_words += sw
            if cur:
                chunks.append(" ".join(cur))
    return [c for c in chunks if len(c.split()) >= 30]


def main():
    with open(SOURCES_JSON, "r", encoding="utf-8") as f:
        sources = json.load(f)
        if not isinstance(sources, list):
            raise ValueError("sources.json must contain a list of source objects")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            source_id TEXT,
            title TEXT,
            url TEXT,
            chunk_text TEXT,
            chunk_len INTEGER
        );
        """
    )
    conn.commit()

    for s in tqdm(sources, desc="Ingesting sources"):
        # Try multiple key names to locate the local file
        filename = (
            s.get("local_filename")
            or s.get("filename")
            or (s.get("url").split("/")[-1] if s.get("url") else None)
        )
        if not filename:
            print(f"No filename for source: {s}")
            continue

        local_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(local_path):
            print(f"Missing file {local_path}; skipping")
            continue

        text = text_from_pdf(local_path)
        chunks = split_to_chunks(text)

        for c in chunks:
            cur.execute(
                """
                INSERT INTO chunks (source_id, title, url, chunk_text, chunk_len)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    s.get("id") or s.get("url") or filename,
                    s.get("title") or filename,
                    s.get("url"),
                    c,
                    len(c.split()),
                ),
            )

    conn.commit()
    conn.close()
    print(f"Ingest complete. SQLite DB created at {DB_PATH}")


if __name__ == "__main__":
    main()
