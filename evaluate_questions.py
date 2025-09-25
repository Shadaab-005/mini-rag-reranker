import json
import requests
import pandas as pd

Q_FILE = "questions.json"
API_URL = "http://127.0.0.1:8000/ask"

def call_api(q_text, mode="baseline", k=3):
    resp = requests.post(API_URL, json={"q": q_text, "k": k, "mode": mode})
    resp.raise_for_status()
    return resp.json()

def main():
    with open(Q_FILE, "r", encoding="utf-8") as f:
        questions = json.load(f)

    rows = []
    for q in questions:
        q_text = q["q"]
        baseline = call_api(q_text, mode="baseline")
        hybrid   = call_api(q_text, mode="hybrid")

        rows.append({
            "question": q_text,
            "baseline_answer_present": baseline["answer"] is not None,
            "hybrid_answer_present": hybrid["answer"] is not None,
            "baseline_top_title": baseline["contexts"][0]["meta"]["title"] if baseline["contexts"] else None,
            "hybrid_top_title": hybrid["contexts"][0]["meta"]["title"] if hybrid["contexts"] else None,
            "baseline_top_score": baseline["contexts"][0].get("vector_score") if baseline["contexts"] else None,
            "hybrid_top_final": hybrid["contexts"][0].get("final_score") if hybrid["contexts"] else None,
            "baseline_answer": baseline["answer"],
            "hybrid_answer": hybrid["answer"]
        })

    df = pd.DataFrame(rows)
    print(df.to_markdown(index=False))
    df.to_csv("evaluation_results.csv", index=False)
    print("\n Evaluation saved to evaluation_results.csv")

if __name__ == "__main__":
    main()
