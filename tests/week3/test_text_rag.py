import json

from src.week2.vector_index import HashingTextEmbedder, build_sample_documents_index
from src.week3.text_rag import TextRAGConfig, TextRAGPipeline, format_citations


def build_test_pipeline(project_root, log_path=None, min_score=0.01):
    vector_index = build_sample_documents_index(
        project_root / "data" / "sample_documents",
        project_root / "data" / "sample_documents" / "catalog.json",
        embedder=HashingTextEmbedder(),
    )
    return TextRAGPipeline(
        vector_index,
        config=TextRAGConfig(min_score=min_score, top_k=3),
        log_path=log_path,
    )


def test_text_rag_returns_grounded_answer_with_citations(project_root, tmp_path):
    log_path = tmp_path / "text_rag.jsonl"
    pipeline = build_test_pipeline(project_root, log_path=log_path)

    response = pipeline.answer(
        "INVALID_CREDENTIALS Caps Lock ten dang nhap",
        query_id="q-test",
        conversation_id="conv-test",
    )

    assert response.is_fallback is False
    assert response.citations
    assert response.citations[0].marker == "[1]"
    assert response.citations[0].doc_id == "doc-D1_authentication_login"
    assert "[SOURCE 1]" in response.prompt
    assert "INVALID_CREDENTIALS Caps Lock ten dang nhap" in response.prompt
    assert "[1]" in response.answer

    logged = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines()]
    assert len(logged) == 1
    assert logged[0]["query_id"] == "q-test"
    assert logged[0]["conversation_id"] == "conv-test"
    assert logged[0]["is_fallback"] is False
    assert logged[0]["citations"][0]["doc_id"] == "doc-D1_authentication_login"
    assert logged[0]["latency_ms"] >= 0


def test_text_rag_falls_back_when_query_is_empty(project_root, tmp_path):
    pipeline = build_test_pipeline(project_root, log_path=tmp_path / "text_rag.jsonl")

    response = pipeline.answer("   ")

    assert response.is_fallback is True
    assert response.confidence == "low"
    assert response.citations == []
    assert "not have enough grounded context" in response.answer


def test_text_rag_falls_back_when_retrieval_score_is_too_low(project_root):
    pipeline = build_test_pipeline(project_root, min_score=999.0)

    response = pipeline.answer("PostgreSQL timeout khi ket noi co so du lieu")

    assert response.is_fallback is True
    assert response.retrieved_count > 0
    assert response.top_score is not None
    assert response.citations == []


def test_format_citations_includes_document_and_heading(project_root):
    pipeline = build_test_pipeline(project_root)
    response = pipeline.answer("VPN khong ket noi duoc")

    formatted = format_citations(response.citations)

    assert "doc-D3_network_config" in formatted
    assert response.citations[0].chunk_id in formatted
