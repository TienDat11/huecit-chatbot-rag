"""Tests for document quality scorer."""

import csv
import tempfile
from pathlib import Path

import pytest

from src.week1.quality_scorer import DocumentQualityScorer
from src.core.sample_data import SAMPLE_DOCUMENTS


@pytest.fixture
def scorer():
    """Create a default scorer instance."""
    return DocumentQualityScorer()


@pytest.fixture
def good_doc():
    """A well-structured document."""
    return SAMPLE_DOCUMENTS[0]


@pytest.fixture
def medium_doc():
    """A document with some issues."""
    return SAMPLE_DOCUMENTS[1]


@pytest.fixture
def poor_doc():
    """A poorly structured document."""
    return SAMPLE_DOCUMENTS[2]


class TestRuleScoring:
    """Tests for rule-based scoring (B3)."""

    def test_metadata_completeness_full(self, scorer, good_doc):
        """Test metadata completeness with all fields present."""
        score = scorer._score_metadata_completeness(good_doc)
        assert score == 30.0  # All 6 fields present × 5 points

    def test_metadata_completeness_partial(self, scorer, poor_doc):
        """Test metadata completeness with missing fields."""
        score = scorer._score_metadata_completeness(poor_doc)
        assert score < 30.0

    def test_metadata_completeness_empty(self, scorer):
        """Test metadata completeness with empty doc."""
        score = scorer._score_metadata_completeness({})
        assert score == 0.0

    def test_parse_success(self, scorer, good_doc):
        """Test parse success scoring."""
        score = scorer._score_parse_success(good_doc)
        assert score == 25.0

    def test_parse_partial(self, scorer, poor_doc):
        """Test partial parse scoring."""
        score = scorer._score_parse_success(poor_doc)
        assert score == 12.5

    def test_parse_failed(self, scorer):
        """Test failed parse scoring."""
        score = scorer._score_parse_success({"parse_status": "failed"})
        assert score == 0.0

    def test_length_good(self, scorer, good_doc):
        """Test length scoring for good content length."""
        score = scorer._score_length(good_doc)
        assert 10.0 <= score <= 20.0

    def test_length_empty(self, scorer):
        """Test length scoring for empty content."""
        score = scorer._score_length({"content": ""})
        assert score == 0.0

    def test_length_very_short(self, scorer):
        """Test length scoring for very short content."""
        score = scorer._score_length({"content": "short"})
        assert score == 5.0  # Below min_content_length

    def test_structure_presence_good(self, scorer, good_doc):
        """Test structure presence for well-structured doc."""
        score = scorer._score_structure_presence(good_doc)
        assert score >= 15.0

    def test_structure_presence_empty(self, scorer):
        """Test structure presence with no headings or sections."""
        score = scorer._score_structure_presence({})
        assert score == 0.0

    def test_rule_score_total_range(self, scorer, good_doc):
        """Test that rule score is in 0-100 range."""
        result = scorer.score_rule(good_doc)
        assert 0 <= result["rule_quality_score"] <= 100

    def test_rule_score_components_sum(self, scorer, good_doc):
        """Test that components sum to total."""
        result = scorer.score_rule(good_doc)
        expected = (
            result["metadata_completeness_score"]
            + result["parse_success_score"]
            + result["length_score"]
            + result["structure_presence_score"]
        )
        assert result["rule_quality_score"] == expected


class TestStructureScoring:
    """Tests for structure-aware scoring (B4)."""

    def test_heading_density_good(self, scorer, good_doc):
        """Test heading density for well-structured doc."""
        score = scorer._score_heading_density(good_doc)
        assert score >= 5.0  # Dense headings still score > 0

    def test_heading_density_empty(self, scorer):
        """Test heading density with no content."""
        score = scorer._score_heading_density({})
        assert score == 0.0

    def test_duplicate_ratio_no_duplicates(self, scorer):
        """Test duplicate ratio with unique content."""
        doc = {"content": "Line 1\nLine 2\nLine 3\nLine 4"}
        score = scorer._score_duplicate_ratio(doc)
        assert score == 20.0

    def test_duplicate_ratio_many_duplicates(self, scorer):
        """Test duplicate ratio with lots of duplicates."""
        doc = {"content": "Same line\nSame line\nSame line\nSame line"}
        score = scorer._score_duplicate_ratio(doc)
        assert score < 15.0

    def test_section_balance_balanced(self, scorer):
        """Test section balance with even sections."""
        doc = {
            "sections": [
                {"text": "A" * 100},
                {"text": "B" * 100},
                {"text": "C" * 100},
            ]
        }
        score = scorer._score_section_balance(doc)
        assert score >= 15.0

    def test_section_balance_unbalanced(self, scorer):
        """Test section balance with uneven sections."""
        doc = {
            "sections": [
                {"text": "A" * 10},
                {"text": "B" * 1000},
            ]
        }
        score = scorer._score_section_balance(doc)
        assert score < 20.0

    def test_structural_continuity_smooth(self, scorer, good_doc):
        """Test structural continuity with smooth transitions."""
        score = scorer._score_structural_continuity(good_doc)
        assert score >= 10.0

    def test_heading_hierarchy_consistency_good(self, scorer, good_doc):
        """Test hierarchy consistency with proper structure."""
        score = scorer._score_heading_hierarchy_consistency(good_doc)
        assert score >= 10.0

    def test_heading_hierarchy_no_headings(self, scorer):
        """Test hierarchy consistency with no headings."""
        score = scorer._score_heading_hierarchy_consistency({})
        assert score == 0.0

    def test_structure_score_total_range(self, scorer, good_doc):
        """Test that structure score is in 0-100 range."""
        result = scorer.score_structure(good_doc)
        assert 0 <= result["structure_quality_score"] <= 100

    def test_structure_score_components_sum(self, scorer, good_doc):
        """Test that components sum to total."""
        result = scorer.score_structure(good_doc)
        expected = (
            result["heading_density"]
            + result["duplicate_ratio"]
            + result["section_balance"]
            + result["structural_continuity"]
            + result["heading_hierarchy_consistency"]
        )
        assert result["structure_quality_score"] == expected


class TestCombinedAssessment:
    """Tests for combined scoring and decisions."""

    def test_assess_good_document(self, scorer, good_doc):
        """Test full assessment of a good document."""
        result = scorer.assess_document(good_doc)

        assert "doc_id" in result
        assert "rule_quality_score" in result
        assert "structure_quality_score" in result
        assert "combined_score" in result
        assert "decision" in result
        assert "ready_for_benchmark" in result
        assert 0 <= result["combined_score"] <= 100

    def test_assess_good_doc_accepts(self, scorer, good_doc):
        """Test that good document gets accepted."""
        result = scorer.assess_document(good_doc)
        assert result["decision"] in ("accept", "review")
        assert result["combined_score"] >= 50

    def test_assess_poor_doc_rejects(self, scorer, poor_doc):
        """Test that poor document gets rejected."""
        result = scorer.assess_document(poor_doc)
        assert result["decision"] == "reject"
        assert result["ready_for_benchmark"] is False

    def test_decision_accept(self, scorer):
        """Test accept decision."""
        assert scorer._make_decision(80.0) == "accept"
        assert scorer._make_decision(75.0) == "accept"

    def test_decision_review(self, scorer):
        """Test review decision."""
        assert scorer._make_decision(70.0) == "review"
        assert scorer._make_decision(65.0) == "review"

    def test_decision_reject(self, scorer):
        """Test reject decision."""
        assert scorer._make_decision(50.0) == "reject"
        assert scorer._make_decision(0.0) == "reject"

    def test_score_documents_batch(self, scorer):
        """Test scoring multiple documents."""
        results = scorer.score_documents(SAMPLE_DOCUMENTS)
        assert len(results) == 3
        assert all("combined_score" in r for r in results)

    def test_get_accepted_documents(self, scorer):
        """Test filtering accepted documents."""
        results = scorer.get_accepted_documents(SAMPLE_DOCUMENTS)
        assert len(results) >= 1  # At least good_doc should be accepted


class TestExportCSV:
    """Tests for CSV export functionality."""

    def test_export_csv(self, scorer):
        """Test CSV export."""
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "scores.csv"
            results = scorer.score_documents(SAMPLE_DOCUMENTS)
            scorer.export_csv(results, str(output))

            assert output.exists()
            with open(output, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                assert len(rows) == 3
                assert "combined_score" in rows[0]

    def test_export_csv_creates_dirs(self, scorer):
        """Test that export creates parent directories."""
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "sub" / "dir" / "scores.csv"
            results = scorer.score_documents(SAMPLE_DOCUMENTS)
            scorer.export_csv(results, str(output))
            assert output.exists()

    def test_export_csv_empty(self, scorer):
        """Test export with empty results."""
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "empty.csv"
            scorer.export_csv([], str(output))
            # Should not crash
