# EPIC D - Text RAG E2E

## Scope

EPIC D adds the first end-to-end text RAG path on top of the week 2 vector index:

- retrieve top-k chunks for a support question;
- assemble a grounded prompt from retrieved chunks;
- return an extractive baseline answer with citations;
- fall back safely when retrieval confidence is too low;
- write structured JSONL logs with query, sources, confidence, and latency.

The implementation intentionally avoids new dependencies. Runtime deployments can use
`SentenceTransformerEmbedder`, while tests and demos use `HashingTextEmbedder` for repeatable
offline evidence.

## Usage

```bash
python scripts/run_text_rag_demo.py "INVALID_CREDENTIALS Caps Lock ten dang nhap"
```

Use a sentence-transformer model when the environment has model cache/network capacity:

```bash
python scripts/run_text_rag_demo.py "VPN_CONNECTION_FAILED VPN" \
  --embedder sentence-transformer \
  --model-name sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Logs are appended to:

```text
output/week_3/text_rag_interactions.jsonl
```

## API

```python
from src.week2.vector_index import HashingTextEmbedder, build_sample_documents_index
from src.week3.text_rag import TextRAGPipeline

index = build_sample_documents_index(
    "data/sample_documents",
    "data/sample_documents/catalog.json",
    embedder=HashingTextEmbedder(),
)
response = TextRAGPipeline(index).answer("INVALID_CREDENTIALS Caps Lock ten dang nhap")
print(response.answer)
print(response.citations)
```

## Fallback Behavior

The pipeline returns a fallback response when:

- the query is empty;
- retrieval returns no hits;
- the top retrieval score is below `TextRAGConfig.min_score`.

This keeps EPIC D aligned with the project requirement that unsupported answers escalate instead
of inventing risky guidance.

## Benchmark Decision

No committed notebook output in this branch currently proves that a heavier embedding/retrieval
candidate beats the current baseline on Recall@k, MRR, nDCG, and latency. Therefore EPIC D does
not promote BGE-M3, Qwen embedding, hybrid RRF, or rerankers into source defaults.

Promotion remains gated by repeatable benchmark artifacts from the planned notebooks:

- `01_rag_retrieval_benchmark.ipynb`
- `02_chunking_embedding_benchmark.ipynb`
- `05_error_matching_rerank.ipynb`

Recommended decision rule:

1. Prefer higher Recall@5 first when missing a relevant support document is costly.
2. Use MRR/nDCG@5 to detect whether the relevant chunk appears near the top, not merely somewhere.
3. Reject a candidate if latency breaks the text NFR: P50 <= 5s and P95 <= 10s.
4. Promote only when the metric gain is repeatable and explainable on the same query/ground-truth set.

## Notebook / Colab Gate

The git repo did not contain executed notebook outputs for EPIC D at implementation time. No Colab
result is claimed in this implementation.

Before changing source defaults based on embeddings or retrieval strategy:

1. Commit and push the notebook/input branch.
2. Run the same notebook matrix in Colab for BM25, TF-IDF, dense, hybrid, and optional rerank.
3. Export `retrieval_scores.csv`, `retrieval_error_analysis.md`, and latency percentiles.
4. Promote the winner only when the CSV evidence beats the baseline and respects the text latency NFR.

## Verification

```bash
pytest tests/week2 tests/week3 -q
python scripts/run_text_rag_demo.py "INVALID_CREDENTIALS Caps Lock ten dang nhap"
```
