"""
Document quality scorer for the RAG pipeline.

Provides rule-based and structure-aware scoring for document readiness assessment.
"""

import csv
import logging
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)

# Scoring thresholds
ACCEPT_THRESHOLD = 75
REVIEW_THRESHOLD = 65


class DocumentQualityScorer:
    """Score document quality for benchmark readiness.

    Combines rule-based scoring (metadata, parse, length, structure presence)
    with structure-aware scoring (heading density, duplicates, balance, hierarchy).
    """

    def __init__(
        self,
        accept_threshold: int = ACCEPT_THRESHOLD,
        review_threshold: int = REVIEW_THRESHOLD,
        min_content_length: int = 100,
        max_content_length: int = 500_000,
        optimal_content_length: int = 5000,
    ):
        self.accept_threshold = accept_threshold
        self.review_threshold = review_threshold
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length
        self.optimal_content_length = optimal_content_length

    # --- Rule-based scoring (0-100) ---

    def _score_metadata_completeness(self, doc: dict) -> float:
        """Score metadata completeness (0-30 points).

        Checks: doc_id, title, domain_id, source_type, language, headings.
        """
        score = 0.0
        fields = {
            "doc_id": 5,
            "title": 5,
            "domain_id": 5,
            "source_type": 5,
            "language": 5,
            "headings": 5,
        }
        for field, points in fields.items():
            value = doc.get(field)
            if value and value != "" and value != []:
                score += points
        return score

    def _score_parse_success(self, doc: dict) -> float:
        """Score parse success status (0-25 points)."""
        status = doc.get("parse_status", "")
        if status == "success":
            return 25.0
        elif status == "partial":
            return 12.5
        return 0.0

    def _score_length(self, doc: dict) -> float:
        """Score content length appropriateness (0-20 points)."""
        content = doc.get("content", "") or ""
        length = len(content.strip())

        if length == 0:
            return 0.0
        if length < self.min_content_length:
            return 5.0
        if length > self.max_content_length:
            return 10.0

        # Score based on proximity to optimal length
        if length <= self.optimal_content_length:
            ratio = length / self.optimal_content_length
            return 10.0 + 10.0 * ratio
        else:
            ratio = min(1.0, self.optimal_content_length / length)
            return 10.0 + 10.0 * ratio

    def _score_structure_presence(self, doc: dict) -> float:
        """Score structure presence (0-25 points).

        Checks: headings present, sections present, heading hierarchy valid.
        """
        score = 0.0
        headings = doc.get("headings", []) or []
        sections = doc.get("sections", []) or []

        # Headings present (0-10)
        if headings:
            score += min(10.0, len(headings) * 2.0)
        else:
            score += 0.0

        # Sections present (0-10)
        if sections:
            score += min(10.0, len(sections) * 1.0)
        else:
            score += 0.0

        # Heading hierarchy starts at level 1 (0-5)
        if headings and headings[0].get("level") == 1:
            score += 5.0

        return min(25.0, score)

    def score_rule(self, doc: dict) -> dict:
        """Calculate rule-based quality score for a document.

        Returns dict with individual scores and total.
        """
        metadata_score = self._score_metadata_completeness(doc)
        parse_score = self._score_parse_success(doc)
        length_score = self._score_length(doc)
        structure_score = self._score_structure_presence(doc)

        total = metadata_score + parse_score + length_score + structure_score

        return {
            "metadata_completeness_score": metadata_score,
            "parse_success_score": parse_score,
            "length_score": length_score,
            "structure_presence_score": structure_score,
            "rule_quality_score": total,
        }

    # --- Structure-aware scoring (0-100) ---

    def _score_heading_density(self, doc: dict) -> float:
        """Score heading density relative to content length (0-20 points).

        Optimal: 1 heading per 200-500 characters.
        """
        content = doc.get("content", "") or ""
        headings = doc.get("headings", []) or []
        content_len = len(content.strip())

        if content_len == 0 or not headings:
            return 0.0

        chars_per_heading = content_len / len(headings)

        if 200 <= chars_per_heading <= 500:
            return 20.0
        elif 100 <= chars_per_heading < 200:
            return 15.0
        elif 500 < chars_per_heading <= 1000:
            return 15.0
        elif chars_per_heading < 100:
            return 8.0
        else:
            return 5.0

    def _score_duplicate_ratio(self, doc: dict) -> float:
        """Score based on duplicate content ratio (0-20, penalty).

        Lower duplicate ratio = higher score.
        """
        content = doc.get("content", "") or ""
        if not content.strip():
            return 0.0

        lines = [line.strip() for line in content.split("\n") if line.strip()]
        if not lines:
            return 0.0

        line_counts = Counter(lines)
        duplicates = sum(count - 1 for count in line_counts.values() if count > 1)
        duplicate_ratio = duplicates / len(lines)

        if duplicate_ratio == 0:
            return 20.0
        elif duplicate_ratio < 0.05:
            return 18.0
        elif duplicate_ratio < 0.1:
            return 15.0
        elif duplicate_ratio < 0.2:
            return 10.0
        else:
            return 5.0

    def _score_section_balance(self, doc: dict) -> float:
        """Score balance of section sizes (0-20 points).

        Even section sizes = better score.
        """
        sections = doc.get("sections", []) or []
        if len(sections) < 2:
            return 5.0 if len(sections) == 1 else 0.0

        section_lengths = [len(s.get("text", "")) for s in sections]
        avg_length = sum(section_lengths) / len(section_lengths)

        if avg_length == 0:
            return 5.0

        # Coefficient of variation (lower = more balanced)
        variance = sum((l - avg_length) ** 2 for l in section_lengths) / len(
            section_lengths
        )
        std_dev = variance**0.5
        cv = std_dev / avg_length if avg_length > 0 else 1.0

        if cv < 0.5:
            return 20.0
        elif cv < 1.0:
            return 15.0
        elif cv < 1.5:
            return 10.0
        else:
            return 5.0

    def _score_structural_continuity(self, doc: dict) -> float:
        """Score structural continuity - sections follow logically (0-20 points)."""
        headings = doc.get("headings", []) or []
        if len(headings) < 2:
            return 10.0 if len(headings) == 1 else 0.0

        # Check level transitions are reasonable (no jumps > 2)
        smooth_transitions = 0
        total_transitions = len(headings) - 1

        for i in range(total_transitions):
            level_diff = abs(headings[i + 1]["level"] - headings[i]["level"])
            if level_diff <= 1:
                smooth_transitions += 1
            elif level_diff == 2:
                smooth_transitions += 0.5

        if total_transitions == 0:
            return 10.0

        ratio = smooth_transitions / total_transitions
        return 20.0 * ratio

    def _score_heading_hierarchy_consistency(self, doc: dict) -> float:
        """Score heading hierarchy consistency (0-20 points).

        Checks: starts at level 1, proper nesting, no skipping.
        """
        headings = doc.get("headings", []) or []
        if not headings:
            return 0.0

        score = 0.0

        # Starts at level 1 (0-5)
        if headings[0].get("level") == 1:
            score += 5.0

        # Only one level-1 heading (0-5)
        level_1_count = sum(1 for h in headings if h.get("level") == 1)
        if level_1_count == 1:
            score += 5.0
        elif level_1_count <= 3:
            score += 3.0

        # No level skipping (0-5)
        max_skip = 0
        for i in range(1, len(headings)):
            skip = headings[i]["level"] - headings[i - 1]["level"]
            if skip > max_skip:
                max_skip = skip

        if max_skip <= 1:
            score += 5.0
        elif max_skip == 2:
            score += 3.0
        else:
            score += 1.0

        # Has multiple levels (0-5)
        levels = set(h["level"] for h in headings)
        if len(levels) >= 3:
            score += 5.0
        elif len(levels) == 2:
            score += 3.0
        else:
            score += 1.0

        return min(20.0, score)

    def score_structure(self, doc: dict) -> dict:
        """Calculate structure-aware quality score for a document.

        Returns dict with individual scores and total.
        """
        heading_density = self._score_heading_density(doc)
        duplicate_ratio = self._score_duplicate_ratio(doc)
        section_balance = self._score_section_balance(doc)
        continuity = self._score_structural_continuity(doc)
        hierarchy = self._score_heading_hierarchy_consistency(doc)

        total = (
            heading_density + duplicate_ratio + section_balance + continuity + hierarchy
        )

        return {
            "heading_density": heading_density,
            "duplicate_ratio": duplicate_ratio,
            "section_balance": section_balance,
            "structural_continuity": continuity,
            "heading_hierarchy_consistency": hierarchy,
            "structure_quality_score": total,
        }

    # --- Combined assessment ---

    def _make_decision(self, combined_score: float) -> str:
        """Make accept/review/reject decision based on combined score."""
        if combined_score >= self.accept_threshold:
            return "accept"
        elif combined_score >= self.review_threshold:
            return "review"
        return "reject"

    def assess_document(self, doc: dict) -> dict:
        """Full quality assessment of a document.

        Returns combined rule-based and structure-aware scores with decision.
        """
        rule_scores = self.score_rule(doc)
        structure_scores = self.score_structure(doc)

        combined_score = (
            rule_scores["rule_quality_score"] + structure_scores["structure_quality_score"]
        ) / 2

        decision = self._make_decision(combined_score)

        return {
            "doc_id": doc.get("doc_id", "unknown"),
            "title": doc.get("title", ""),
            **rule_scores,
            **structure_scores,
            "combined_score": round(combined_score, 2),
            "rule_decision": rule_scores["rule_quality_score"],
            "decision": decision,
            "ready_for_benchmark": decision == "accept",
        }

    def score_documents(self, documents: list[dict]) -> list[dict]:
        """Score multiple documents and return assessment results."""
        results = []
        for doc in documents:
            result = self.assess_document(doc)
            results.append(result)
        return results

    def get_accepted_documents(self, documents: list[dict]) -> list[dict]:
        """Filter documents that are accepted for benchmark."""
        results = self.score_documents(documents)
        return [r for r in results if r["ready_for_benchmark"]]

    def export_csv(
        self, results: list[dict], output_path: str
    ) -> str:
        """Export scoring results to CSV file."""
        if not results:
            logger.warning("No results to export")
            return output_path

        from pathlib import Path

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        fieldnames = list(results[0].keys())
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        logger.info(f"Exported {len(results)} results to {output_path}")
        return output_path


if __name__ == "__main__":
    import argparse

    import json

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Score document quality")
    parser.add_argument(
        "--input", required=True, help="Input JSONL file with documents"
    )
    parser.add_argument(
        "--output", default="output/week_1/document_quality_scores.csv",
        help="Output CSV path",
    )
    args = parser.parse_args()

    # Load documents
    docs = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))

    # Score
    scorer = DocumentQualityScorer()
    results = scorer.score_documents(docs)

    # Export
    scorer.export_csv(results, args.output)

    # Summary
    accepted = sum(1 for r in results if r["ready_for_benchmark"])
    print(f"Scored {len(results)} documents: {accepted} accepted, {len(results) - accepted} needs review/reject")
