import json

import numpy as np

from src.week2.vector_index import (
    FaissVectorIndex,
    build_chunk_records,
    build_sample_document_corpus,
    build_sample_documents_index,
    evaluate_retrieval,
    load_benchmark_queries,
    load_ground_truth_retrieval,
)


class HashingEmbedder:
    def __init__(self, dimension: int = 256) -> None:
        self.dimension = dimension
        self.model_name = "test-hashing-embedder"

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for row, text in enumerate(texts):
            for token in text.lower().split():
                index = hash(token) % self.dimension
                vectors[row, index] += 1.0
        return vectors


def test_build_sample_document_corpus_reads_all_catalog_entries(project_root):
    documents = build_sample_document_corpus(
        project_root / "data" / "sample_documents",
        project_root / "data" / "sample_documents" / "catalog.json",
    )

    assert len(documents) == 7
    assert {doc["doc_id"] for doc in documents} == {
        "doc-D1_authentication_login",
        "doc-D2_database_connection",
        "doc-D3_network_config",
        "doc-D4_application_portal",
        "doc-D5_filesystem_management",
        "doc-D6_security_access_control",
        "doc-D7_performance_optimization",
    }
    assert all(doc["parse_status"] == "success" for doc in documents)


def test_build_chunk_records_prefers_sections(project_root):
    documents = build_sample_document_corpus(
        project_root / "data" / "sample_documents",
        project_root / "data" / "sample_documents" / "catalog.json",
    )

    chunks = build_chunk_records(documents)

    assert chunks
    assert all(chunk.chunk_type == "section" for chunk in chunks)
    assert any(chunk.doc_id == "doc-D1_authentication_login" for chunk in chunks)
    assert any(chunk.heading_path for chunk in chunks)


def test_build_sample_documents_index_searches_relevant_document(project_root):
    vector_index = build_sample_documents_index(
        project_root / "data" / "sample_documents",
        project_root / "data" / "sample_documents" / "catalog.json",
        embedder=HashingEmbedder(),
    )

    hits = vector_index.search("đăng nhập hệ thống CIT", top_k=3)

    assert hits
    assert hits[0].doc_id == "doc-D1_authentication_login"
    assert hits[0].rank == 1


def test_vector_index_save_and_load_round_trip(project_root, tmp_path):
    vector_index = build_sample_documents_index(
        project_root / "data" / "sample_documents",
        project_root / "data" / "sample_documents" / "catalog.json",
        embedder=HashingEmbedder(),
    )
    output_dir = tmp_path / "vector_index"

    saved_dir = vector_index.save(output_dir)
    reloaded = FaissVectorIndex.load(saved_dir, embedder=HashingEmbedder())

    assert (saved_dir / "index.faiss").exists()
    assert (saved_dir / "metadata.json").exists()
    assert reloaded.search("timeout kết nối cơ sở dữ liệu", top_k=1)[0].doc_id == "doc-D2_database_connection"

    metadata = json.loads((saved_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["chunk_count"] == len(vector_index.chunks)
    assert metadata["embedding_model"] == "test-hashing-embedder"


def test_evaluate_retrieval_hits_ground_truth_on_known_queries(project_root):
    vector_index = build_sample_documents_index(
        project_root / "data" / "sample_documents",
        project_root / "data" / "sample_documents" / "catalog.json",
        embedder=HashingEmbedder(),
    )
    queries = load_benchmark_queries(project_root / "data" / "benchmark_inputs" / "query_set.json")
    ground_truth = load_ground_truth_retrieval(
        project_root / "data" / "benchmark_inputs" / "ground_truth_retrieval.json"
    )

    subset = [query for query in queries if query["query_id"] in {"q-001", "q-009", "q-025"}]
    report = evaluate_retrieval(vector_index, subset, ground_truth, top_k=3)

    assert report["query_count"] == 3
    assert report["hit_count"] == 3
    assert report["recall_at_k"] == 1.0
