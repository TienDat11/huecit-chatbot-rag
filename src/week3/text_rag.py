from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from src.week2.vector_index import FaissVectorIndex, SearchHit


@dataclass(frozen=True)
class TextRAGConfig:
    top_k: int = 3
    min_score: float = 0.05
    high_confidence_score: float = 0.35
    max_context_chars_per_hit: int = 1200
    max_answer_chars: int = 1600
    relative_score_floor: float = 0.8
    fallback_message: str = (
        "I do not have enough grounded context to answer this safely. "
        "Please contact support with the screen, error code, and recent action."
    )


@dataclass(frozen=True)
class Citation:
    marker: str
    rank: int
    doc_id: str
    chunk_id: str
    title: str
    heading_path: str | None
    score: float


@dataclass(frozen=True)
class TextRAGResponse:
    query: str
    answer: str
    citations: list[Citation]
    prompt: str
    is_fallback: bool
    confidence: str
    latency_ms: float
    retrieved_count: int
    top_score: float | None
    query_id: str | None = None
    conversation_id: str | None = None

    def to_log_record(self) -> dict:
        record = asdict(self)
        record["logged_at"] = datetime.now(timezone.utc).isoformat()
        record["citations"] = [asdict(citation) for citation in self.citations]
        return record


class AnswerGenerator(Protocol):
    def generate(self, query: str, hits: list[SearchHit], prompt: str) -> str: ...


class ExtractiveAnswerGenerator:
    def __init__(self, max_answer_chars: int = 1600) -> None:
        self.max_answer_chars = max_answer_chars

    def generate(self, query: str, hits: list[SearchHit], prompt: str) -> str:
        del query, prompt
        if not hits:
            return ""

        lines = ["Based on the retrieved internal documentation:"]
        for index, hit in enumerate(hits, start=1):
            snippet = _compact_text(hit.text)
            lines.append(f"{index}. {snippet} [{index}]")

        answer = "\n".join(lines)
        if len(answer) <= self.max_answer_chars:
            return answer
        return answer[: self.max_answer_chars].rstrip() + "..."


class PromptAssembler:
    def __init__(self, max_context_chars_per_hit: int = 1200) -> None:
        self.max_context_chars_per_hit = max_context_chars_per_hit

    def assemble(self, query: str, hits: list[SearchHit]) -> str:
        context_blocks = []
        for index, hit in enumerate(hits, start=1):
            text = hit.text[: self.max_context_chars_per_hit].strip()
            heading = hit.heading_path or "N/A"
            context_blocks.append(
                "\n".join(
                    [
                        f"[SOURCE {index}]",
                        f"title: {hit.title}",
                        f"doc_id: {hit.doc_id}",
                        f"chunk_id: {hit.chunk_id}",
                        f"heading_path: {heading}",
                        f"score: {hit.score:.4f}",
                        "content:",
                        text,
                    ]
                )
            )

        context = "\n\n".join(context_blocks)
        return "\n".join(
            [
                "You are a technical support assistant for internal HueCIT software.",
                "Use only the provided sources. Cite every concrete claim with [SOURCE n].",
                "If the sources are weak or unrelated, say that support escalation is needed.",
                "",
                f"User question: {query.strip()}",
                "",
                "Retrieved sources:",
                context,
                "",
                "Answer:",
            ]
        )


class TextRAGPipeline:
    def __init__(
        self,
        vector_index: FaissVectorIndex,
        config: TextRAGConfig | None = None,
        answer_generator: AnswerGenerator | None = None,
        log_path: str | Path | None = None,
    ) -> None:
        self.vector_index = vector_index
        self.config = config or TextRAGConfig()
        self.prompt_assembler = PromptAssembler(self.config.max_context_chars_per_hit)
        self.answer_generator = answer_generator or ExtractiveAnswerGenerator(
            max_answer_chars=self.config.max_answer_chars
        )
        self.log_path = Path(log_path) if log_path is not None else None

    def answer(
        self,
        query: str,
        *,
        query_id: str | None = None,
        conversation_id: str | None = None,
        top_k: int | None = None,
    ) -> TextRAGResponse:
        started = time.perf_counter()
        normalized_query = query.strip()

        if not normalized_query:
            response = self._fallback_response(
                query=query,
                prompt="",
                latency_ms=self._elapsed_ms(started),
                query_id=query_id,
                conversation_id=conversation_id,
            )
            self._log(response)
            return response

        requested_top_k = top_k or self.config.top_k
        hits = self.vector_index.search(normalized_query, top_k=requested_top_k)
        top_score = hits[0].score if hits else None

        if not hits or top_score is None or top_score < self.config.min_score:
            prompt = self.prompt_assembler.assemble(normalized_query, hits)
            response = self._fallback_response(
                query=normalized_query,
                prompt=prompt,
                latency_ms=self._elapsed_ms(started),
                query_id=query_id,
                conversation_id=conversation_id,
                retrieved_count=len(hits),
                top_score=top_score,
            )
            self._log(response)
            return response

        usable_hits = self._usable_hits(hits, top_score)
        prompt = self.prompt_assembler.assemble(normalized_query, usable_hits)
        answer = self.answer_generator.generate(normalized_query, usable_hits, prompt)
        citations = build_citations(usable_hits)
        response = TextRAGResponse(
            query=normalized_query,
            answer=answer,
            citations=citations,
            prompt=prompt,
            is_fallback=False,
            confidence=self._confidence(top_score),
            latency_ms=self._elapsed_ms(started),
            retrieved_count=len(usable_hits),
            top_score=top_score,
            query_id=query_id,
            conversation_id=conversation_id,
        )
        self._log(response)
        return response

    def _fallback_response(
        self,
        *,
        query: str,
        prompt: str,
        latency_ms: float,
        query_id: str | None,
        conversation_id: str | None,
        retrieved_count: int = 0,
        top_score: float | None = None,
    ) -> TextRAGResponse:
        return TextRAGResponse(
            query=query,
            answer=self.config.fallback_message,
            citations=[],
            prompt=prompt,
            is_fallback=True,
            confidence="low",
            latency_ms=latency_ms,
            retrieved_count=retrieved_count,
            top_score=top_score,
            query_id=query_id,
            conversation_id=conversation_id,
        )

    def _confidence(self, score: float) -> str:
        if score >= self.config.high_confidence_score:
            return "high"
        return "medium"

    def _usable_hits(self, hits: list[SearchHit], top_score: float) -> list[SearchHit]:
        floor = max(self.config.min_score, top_score * self.config.relative_score_floor)
        return [hit for hit in hits if hit.score >= floor]

    def _elapsed_ms(self, started: float) -> float:
        return round((time.perf_counter() - started) * 1000, 3)

    def _log(self, response: TextRAGResponse) -> None:
        if self.log_path is None:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(response.to_log_record(), ensure_ascii=False) + "\n")


def build_citations(hits: list[SearchHit]) -> list[Citation]:
    return [
        Citation(
            marker=f"[{index}]",
            rank=hit.rank,
            doc_id=hit.doc_id,
            chunk_id=hit.chunk_id,
            title=hit.title,
            heading_path=hit.heading_path,
            score=hit.score,
        )
        for index, hit in enumerate(hits, start=1)
    ]


def format_citations(citations: list[Citation]) -> str:
    return "\n".join(
        (
            f"{citation.marker} {citation.title} "
            f"({citation.doc_id}, {citation.chunk_id}, {citation.heading_path or 'N/A'})"
        )
        for citation in citations
    )


def _compact_text(text: str, max_chars: int = 360) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= max_chars:
        return compacted
    return compacted[:max_chars].rstrip() + "..."


__all__ = [
    "AnswerGenerator",
    "Citation",
    "ExtractiveAnswerGenerator",
    "PromptAssembler",
    "TextRAGConfig",
    "TextRAGPipeline",
    "TextRAGResponse",
    "build_citations",
    "format_citations",
]
