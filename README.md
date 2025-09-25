# Mini RAG + Reranker Q\&A Service

A small **question-answering system** over industrial & machine safety PDFs using **vector search** and a **hybrid reranker** (vector + BM25), with lightweight extractive summarization.

---

## Project Structure

```
mini-rag-reranker/
├─ data/
│  ├─ pdfs/                 # Place provided PDFs here
│  ├─ sources.json           # Metadata for PDFs
│  └─ questions.json         # 8 evaluation questions
├─ sqlite_chunks.db          # Chunked PDF text (created by ingest.py)
├─ ingest.py                 # Extracts & chunks PDFs
├─ build_index.py            # Builds FAISS vector index + BM25
├─ search.py                 # Vector retriever
├─ lexical_bm25.py           # BM25 keyword search
├─ reranker.py               # Hybrid reranker
├─ api.py                    # FastAPI /ask endpoint with T5 summarization
├─ evaluate_questions.py     # Evaluate 8 questions & print table
├─ requirements.txt
└─ README.md
```

---

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## How to Run

1. **Ingest PDFs and create chunks**

```bash
python ingest.py
```

2. **Build FAISS embeddings and BM25 index**

```bash
python build_index.py
```

3. **Start API server**

```bash
uvicorn api:app --reload
```

4. **Example API Requests**

 - Easy Question

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{
  "q": "What is the purpose of machine guards?",
  "k": 3,
  "mode": "hybrid"
}'
```

**Expected Behavior:**

* Returns a concise extractive answer summarizing chunks about machine guards.
* Includes top-k contexts with titles, URLs, vector & hybrid scores.

---
- Tricky Question

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
-H "Content-Type: application/json" \
-d '{
  "q": "Which ISO standard specifies emergency stop requirements?",
  "k": 3,
  "mode": "hybrid"
}'
```

**Expected Behavior:**

* Hybrid reranker helps surface chunks with rare keywords like `ISO 13850`.
* Returns a short, cited answer and top-k contexts, even if baseline vector search would rank them lower.

---

5. **Evaluate 8 questions**

```bash
python evaluate_questions.py
```

---

### Evaluation Results

| Question                                                                  | Baseline Answer Present   | Hybrid Answer Present   | Baseline Top Title                                                                            | Hybrid Top Title                                                                              |   Baseline Top Score |   Hybrid Top Final | Baseline Answer                                                                                                                                                                                                                                                                                                                                                      | Hybrid Answer                                                                                                                                                                                                                                                                                                                       |
|:--------------------------------------------------------------------------|:--------------------------|:------------------------|:----------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------|---------------------:|-------------------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| What is the primary purpose of the EU Machinery Directive 2006/42/EC?     | True                      | True                    | SICK — Guide for Safe Machinery: Six Steps to a Safe Machine                                  | SICK — Guide for Safe Machinery: Six Steps to a Safe Machine                                  |             0.730977 |           0.804689 | the directives are freely available, e.g., at eur-lex.europa.eu . they apply to manufacturers and organizations that place machinery on the market in the Euro pean Union . the Directives apply to machines and safety compo nents . it establishes the necessary tasks for new machines to meet health and safety requirements .                                   | the Directive 2006/42/EC addresses manufacturers and distributors of machines and safety compo nents . it establishes the necessary tasks for new machines to meet health and safety requirements in order to dismantle trade barriers within Europe . by 1995, this directive had to be applied in all EC Member States .          |
| What are the two methods to show compliance with the Machinery Directive? | True                      | True                    | Rockwell — Machinery SafeBook 5                                                               | Rockwell — Machinery SafeBook 5                                                               |             0.685218 |           0.770199 | new machinery and second hand machinery from outside the EU must provide minimum requirements given in an annex of the U.W.E. Directive . if the machine is listed in Annex IV of the Machinery Directive, special conformity assessment procedures must be met . the manufacturer must document all relevant hazards/risks and counter measures with test results . | the machinery Directive covers the supply of new machinery and other equipment including safety components . it is an offense to supply machinery within the EU unless the provisions and requirements of the Directive are met . a detailed risk assessment must be conducted to ensure that all potential hazards are addressed . |
| What does “residual risk” mean in machine safety?                         | True                      | True                    | Rockwell — Machinery SafeBook 5                                                               | Rockwell — Machinery SafeBook 5                                                               |             0.614597 |           0.731264 | the risk Graph or Table must not be used in isolation or in an overly simplistic manner . the risk estimation must be repeated taking into account any foreseeable changes in the way that people may intervene with the machine . if the protective measure fails they will be at a greater risk than envisaged before .                                            | each method is intended to take account of the detailed content of the standard . the risk Graph or Table must not be used in isolation or in an overly simplistic manner . it is important to repeat the risk estimation after the protective measure has been chosen .                                                            |
| What does Diagnostic Coverage (DC) indicate?                              | True                      | True                    | IFA — Functional safety of machine controls (Application of EN ISO 13849), IFA Report 2/2017e | IFA — Functional safety of machine controls (Application of EN ISO 13849), IFA Report 2/2017e |             0.65752  |           0.764307 | DC is a measure of the effec- seen here to be a value relating to the tested unit (e.g. the tiveness of a control system's self-test and monitoring block) and not to the test equipment . a simplified approach of EN ISO 13849-1 allows only a mini- mum total of 65 points and even then, only for SRP/CS .                                                       | DC is a measure of the effec- seen here to be a value relating to the tested unit (e.g. the tiveness of a control system's self-test and monitoring block) and not to the test equipment .                                                                                                                                          |
| What does CE marking allow manufacturers to do?                           | True                      | True                    | Eaton — Safety Manual (EN ISO 13849-1 and IEC 62061)                                          | Eaton — Safety Manual (EN ISO 13849-1 and IEC 62061)                                          |             0.746318 |           0.847791 | the CE marking must be carried out before putting the product onto the Affix CE mark market, i.e. before selling and commissioning . imports into the EU are also safety requirements of the relevant directives and EN standards . the manufacturer takes full responsibility for the affixing of the CE for use, devices, tools and machines .                     | CE marking must be carried out before putting the product onto the market . importation into the EU is also safety requirements of the relevant directives and EN standards . the manufacturer takes full responsibility for the affixing of the CE marking .                                                                       |
| What tool is provided by IFA to calculate PL?                             | True                      | True                    | IFA — Functional safety of machine controls (Application of EN ISO 13849), IFA Report 2/2017e | IFA — SISTEMA Cookbook 1                                                                      |             0.53694  |           0.664999 | EN ISO 13849-1 has a con- that has already been developed in the field . it contains valu- involvement of experienced experts at the IFA . the previous EN 954 standard with its purely deterministic requirements has finally been re-placed .                                                                                                                      | the safety-related parts of machine controls can be implemented in accordance with EN ISO 13849-1 . for this purpose, the machine design engineer must calculate the probability of a dan- gerous failure per hour (PFH) in order to determine the Performance Level (PL)                                                           |
| Explain how a two-hand control device helps protect workers.              | True                      | True                    | Rockwell — Machinery SafeBook 5                                                               | SICK — Guide for Safe Machinery: Six Steps to a Safe Machine                                  |             0.640402 |           0.771306 | two-hand controls must be operated concurrently (within 0.5 s of each other) to start the machine . this ensures that both hands of the operator are occupied in a safe position (i.e., at the controls) and therefore cannot be in the hazard area . a new function may only be initiated if both controls have been actuated .                                     | two-hand control devices are designed to be movable (ergonomics) a spacer ring ensures that the safety distance from the hazardous point is main tained . a new function may only be initiated if both controls have been released and then actuated .                                                                              |
| What is the main purpose of functional safety in machinery?               | True                      | True                    | Rockwell — Machinery SafeBook 5                                                               | Rockwell — Machinery SafeBook 5                                                               |             0.703418 |           0.799659 | functional safety was a term introduced in IEC 61508:1998 . it covers a broad range of devices that are used to create safety systems . devices like interlocks, light curtains, safety relays, safety PLCs and safety contactors are interconnected to form a safety system, which perform a specifi c safety-related function .                                    | functional safety is the part of the overall safety requirement . a safety function is implemented by the safety-related parts of the machine control system to achieve or maintain the equipment under control in a safe state with respect to a specifi c hazard or set of hazards .                                              |

---

## Learnings

During this sprint, I learned how to build a **lightweight retriever-augmented generation (RAG)** pipeline without paid APIs, combining semantic vector search with a BM25 hybrid reranker. Using extractive summarization (T5-small) ensures answers are **grounded in retrieved chunks** while still concise. Hybrid reranking improved results for queries containing **rare keywords**, demonstrating how semantic and lexical methods complement each other.

---

