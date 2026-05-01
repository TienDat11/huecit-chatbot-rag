from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import faiss
import numpy as np

from src.week1.document_parser import parse_file


DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class Embedder(Protocol):
    def encode(self, texts: list[str]) -> np.ndarray:
        ...


@dataclass
class ChunkRecord:
    chunk_id: str
    doc_id: str
    title: str
    domain_id: str | None
    function_area: str | None
    source_path: str
    source_type: str
    chunk_type: str
    heading_path: str | None
    text: str


@dataclass
class SearchHit:
    rank: int
    score: float
    chunk_id: str
    doc_id: str
    title: str
    chunk_type: str
    heading_path: str | None
    text: str


@dataclass
class RetrievalEvaluation:
    query_id: str
    top_k: int
    retrieved_doc_ids: list[str]
    relevant_doc_ids: list[str]
    hit: bool


class SentenceTransformerEmbedder:
    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        normalize_embeddings: bool = True,
    ) -> None:
        self.model_name = model_name
        self.normalize_embeddings = normalize_embeddings
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)

        embeddings = self._get_model().encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_embeddings,
        )
        return np.asarray(embeddings, dtype=np.float32)


class FaissVectorIndex:
    def __init__(
        self,
        index: faiss.Index,
        chunks: list[ChunkRecord],
        embedder: Embedder,
        embedding_model: str,
        built_at: str | None = None,
    ) -> None:
        self.index = index
        self.chunks = chunks
        self.embedder = embedder
        self.embedding_model = embedding_model
        self.built_at = built_at or datetime.now(timezone.utc).isoformat()

    def search(self, query: str, top_k: int = 5) -> list[SearchHit]:
        if not query.strip() or not self.chunks:
            return []

        query_embedding = _normalize_embeddings(self.embedder.encode([query]))
        limit = min(top_k, len(self.chunks))
        scores, indices = self.index.search(query_embedding, limit)

        hits: list[SearchHit] = []
        for rank, (score, index_value) in enumerate(zip(scores[0], indices[0]), start=1):
            if index_value < 0:
                continue
            chunk = self.chunks[index_value]
            hits.append(
                SearchHit(
                    rank=rank,
                    score=float(score),
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    title=chunk.title,
                    chunk_type=chunk.chunk_type,
                    heading_path=chunk.heading_path,
                    text=chunk.text,
                )
            )
        return hits

    def save(self, output_dir: str | Path) -> Path:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(output_path / "index.faiss"))
        metadata = {
            "embedding_model": self.embedding_model,
            "built_at": self.built_at,
            "chunk_count": len(self.chunks),
            "chunks": [asdict(chunk) for chunk in self.chunks],
        }
        (output_path / "metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output_path

    @classmethod
    def load(
        cls,
        input_dir: str | Path,
        embedder: Embedder,
        embedding_model: str | None = None,
    ) -> "FaissVectorIndex":
        input_path = Path(input_dir)
        index = faiss.read_index(str(input_path / "index.faiss"))
        metadata = json.loads((input_path / "metadata.json").read_text(encoding="utf-8"))
        chunks = [ChunkRecord(**chunk) for chunk in metadata["chunks"]]
        return cls(
            index=index,
            chunks=chunks,
            embedder=embedder,
            embedding_model=embedding_model or metadata["embedding_model"],
            built_at=metadata.get("built_at"),
        )


def _normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    array = np.asarray(embeddings, dtype=np.float32)
    if array.ndim != 2:
        raise ValueError("Embeddings must be a 2D array")
    if array.shape[0] == 0:
        return array

    norms = np.linalg.norm(array, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return array / norms


def load_sample_document_catalog(catalog_path: str | Path) -> list[dict[str, Any]]:
    return json.loads(Path(catalog_path).read_text(encoding="utf-8"))


def load_benchmark_queries(query_path: str | Path) -> list[dict[str, Any]]:
    return json.loads(Path(query_path).read_text(encoding="utf-8"))


def load_ground_truth_retrieval(ground_truth_path: str | Path) -> dict[str, dict[str, Any]]:
    entries = json.loads(Path(ground_truth_path).read_text(encoding="utf-8"))
    return {entry["query_id"]: entry for entry in entries}


def build_sample_document_corpus(
    sample_docs_dir: str | Path,
    catalog_path: str | Path,
) -> list[dict[str, Any]]:
    sample_dir = Path(sample_docs_dir)
    catalog = load_sample_document_catalog(catalog_path)

    documents: list[dict[str, Any]] = []
    for entry in catalog:
        source_path = sample_dir / entry["filename"]
        document = parse_file(
            str(source_path),
            doc_id=entry["doc_id"],
            domain_id=entry.get("domain_id"),
        )
        document["title"] = entry.get("title") or document.get("title") or source_path.stem
        documents.append(document)
    return documents


def build_chunk_records(documents: list[dict[str, Any]]) -> list[ChunkRecord]:
    chunks: list[ChunkRecord] = []
    for document in documents:
        base_metadata = {
            "doc_id": document["doc_id"],
            "title": document.get("title", ""),
            "domain_id": document.get("domain_id"),
            "function_area": document.get("function_area"),
            "source_path": document.get("source_path", ""),
            "source_type": document.get("source_type", ""),
        }

        sections = document.get("sections") or []
        if sections:
            for idx, section in enumerate(sections, start=1):
                section_text = _compose_chunk_text(document, section.get("text", ""), section.get("heading_path"))
                chunks.append(
                    ChunkRecord(
                        chunk_id=f"{document['doc_id']}#section-{idx}",
                        chunk_type="section",
                        heading_path=section.get("heading_path"),
                        text=section_text,
                        **base_metadata,
                    )
                )
        else:
            chunks.append(
                ChunkRecord(
                    chunk_id=f"{document['doc_id']}#document",
                    chunk_type="document",
                    heading_path=None,
                    text=_compose_chunk_text(document, document.get("content", ""), None),
                    **base_metadata,
                )
            )
    return chunks


def _compose_chunk_text(document: dict[str, Any], body: str, heading_path: str | None) -> str:
    parts = [document.get("title", "")]
    if heading_path:
        parts.append(heading_path)
    parts.append(body)
    return "\n\n".join(part for part in parts if part and part.strip())


def build_faiss_index(
    chunks: list[ChunkRecord],
    embedder: Embedder,
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
) -> FaissVectorIndex:
    if not chunks:
        raise ValueError("At least one chunk is required to build an index")

    texts = [chunk.text for chunk in chunks]
    embeddings = _normalize_embeddings(embedder.encode(texts))
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return FaissVectorIndex(
        index=index,
        chunks=chunks,
        embedder=embedder,
        embedding_model=embedding_model,
    )


def build_sample_documents_index(
    sample_docs_dir: str | Path,
    catalog_path: str | Path,
    output_dir: str | Path | None = None,
    embedder: Embedder | None = None,
) -> FaissVectorIndex:
    actual_embedder = embedder or SentenceTransformerEmbedder()
    documents = build_sample_document_corpus(sample_docs_dir, catalog_path)
    chunks = build_chunk_records(documents)
    embedding_model = getattr(actual_embedder, "model_name", DEFAULT_EMBEDDING_MODEL)
    vector_index = build_faiss_index(chunks, actual_embedder, embedding_model=embedding_model)
    if output_dir is not None:
        vector_index.save(output_dir)
    return vector_index


def evaluate_retrieval(
    vector_index: FaissVectorIndex,
    queries: list[dict[str, Any]],
    ground_truth: dict[str, dict[str, Any]],
    top_k: int = 3,
) -> dict[str, Any]:
    evaluations: list[RetrievalEvaluation] = []
    hit_count = 0

    for query in queries:
        hits = vector_index.search(query["query_text"], top_k=top_k)
        retrieved_doc_ids = _dedupe_doc_ids([hit.doc_id for hit in hits])
        truth_entry = ground_truth.get(query["query_id"], {})
        relevant_doc_ids = truth_entry.get("relevant_doc_ids") or query.get("reference_doc_ids", [])
        hit = any(doc_id in relevant_doc_ids for doc_id in retrieved_doc_ids)
        if hit:
            hit_count += 1
        evaluations.append(
            RetrievalEvaluation(
                query_id=query["query_id"],
                top_k=top_k,
                retrieved_doc_ids=retrieved_doc_ids,
                relevant_doc_ids=relevant_doc_ids,
                hit=hit,
            )
        )

    total = len(evaluations)
    recall_at_k = hit_count / total if total else 0.0
    return {
        "top_k": top_k,
        "query_count": total,
        "hit_count": hit_count,
        "recall_at_k": recall_at_k,
        "evaluations": [asdict(item) for item in evaluations],
    }


def _dedupe_doc_ids(doc_ids: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for doc_id in doc_ids:
        if doc_id not in seen:
            deduped.append(doc_id)
            seen.add(doc_id)
    return deduped


__all__ = [
    "ChunkRecord",
    "DEFAULT_EMBEDDING_MODEL",
    "Embedder",
    "FaissVectorIndex",
    "RetrievalEvaluation",
    "SearchHit",
    "SentenceTransformerEmbedder",
    "build_chunk_records",
    "build_faiss_index",
    "build_sample_document_corpus",
    "build_sample_documents_index",
    "evaluate_retrieval",
    "load_benchmark_queries",
    "load_ground_truth_retrieval",
    "load_sample_document_catalog",
]
