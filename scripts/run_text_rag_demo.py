from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.week2.vector_index import (  # noqa: E402
    HashingTextEmbedder,
    SentenceTransformerEmbedder,
    build_sample_documents_index,
)
from src.week3.text_rag import TextRAGConfig, TextRAGPipeline, format_citations  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the EPIC D text RAG demo.")
    parser.add_argument("query", help="User support question")
    parser.add_argument("--sample-docs", default="data/sample_documents")
    parser.add_argument("--catalog", default="data/sample_documents/catalog.json")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-score", type=float, default=0.05)
    parser.add_argument("--log-path", default="output/week_3/text_rag_interactions.jsonl")
    parser.add_argument(
        "--embedder",
        choices=["hashing", "sentence-transformer"],
        default="hashing",
        help="Use hashing for repeatable offline demos, or sentence-transformer for runtime quality.",
    )
    parser.add_argument(
        "--model-name",
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        help="SentenceTransformer model name when --embedder sentence-transformer is used.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    embedder = (
        HashingTextEmbedder()
        if args.embedder == "hashing"
        else SentenceTransformerEmbedder(model_name=args.model_name)
    )
    vector_index = build_sample_documents_index(
        args.sample_docs,
        args.catalog,
        embedder=embedder,
    )
    pipeline = TextRAGPipeline(
        vector_index,
        config=TextRAGConfig(top_k=args.top_k, min_score=args.min_score),
        log_path=Path(args.log_path),
    )
    response = pipeline.answer(args.query)
    print(response.answer)
    if response.citations:
        print("\nSources:")
        print(format_citations(response.citations))
    print(f"\nconfidence={response.confidence} fallback={response.is_fallback}")
    print(f"latency_ms={response.latency_ms}")


if __name__ == "__main__":
    main()
