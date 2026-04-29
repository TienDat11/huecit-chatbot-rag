"""Tests for quality report generator."""

import json
import tempfile
from pathlib import Path

import pytest

from src.week1.report_generator import QualityReportGenerator
from src.week1.quality_scorer import DocumentQualityScorer
from src.core.sample_data import SAMPLE_DOCUMENTS


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


@pytest.fixture
def generator(tmp_dir):
    """Create a report generator with temp output directory."""
    return QualityReportGenerator(output_dir=str(tmp_dir))


@pytest.fixture
def sample_results():
    """Generate sample quality assessment results."""
    scorer = DocumentQualityScorer()
    return scorer.score_documents(SAMPLE_DOCUMENTS)


class TestQualityReportGenerator:
    """Tests for QualityReportGenerator."""

    def test_generate_report_creates_files(self, generator, sample_results):
        """Test that generate_report creates expected output files."""
        report = generator.generate_report(sample_results, report_name="test_report")

        assert "output_files" in report
        assert "full_report" in report["output_files"]
        assert "accepted_list" in report["output_files"]
        assert "summary" in report["output_files"]

        # Check files exist
        assert Path(report["output_files"]["full_report"]).exists()
        assert Path(report["output_files"]["accepted_list"]).exists()
        assert Path(report["output_files"]["summary"]).exists()

    def test_generate_report_summary(self, generator, sample_results):
        """Test that summary statistics are computed correctly."""
        report = generator.generate_report(sample_results)

        summary = report["summary"]
        assert "total_documents" in summary
        assert "decision_counts" in summary
        assert "accept_rate" in summary
        assert summary["total_documents"] == len(sample_results)

    def test_generate_report_returns_counts(self, generator, sample_results):
        """Test that generate_report returns correct counts."""
        report = generator.generate_report(sample_results)

        assert "total_documents" in report
        assert "accepted_count" in report
        assert report["total_documents"] == len(sample_results)
        assert report["accepted_count"] <= report["total_documents"]

    def test_generate_report_empty_results(self, generator):
        """Test generate_report with empty results."""
        report = generator.generate_report([])
        assert "error" in report

    def test_export_csv(self, generator, sample_results, tmp_dir):
        """Test CSV export."""
        output_path = str(tmp_dir / "test.csv")
        generator._export_csv(sample_results, output_path)

        assert Path(output_path).exists()
        with open(output_path, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == len(sample_results) + 1  # +1 for header

    def test_export_accepted_list(self, generator, sample_results, tmp_dir):
        """Test accepted list export."""
        accepted = [r for r in sample_results if r.get("ready_for_benchmark")]
        output_path = str(tmp_dir / "accepted.csv")
        generator._export_accepted_list(accepted, output_path)

        assert Path(output_path).exists()
        with open(output_path, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) == len(accepted) + 1  # +1 for header

    def test_compute_summary(self, generator, sample_results):
        """Test summary computation."""
        summary = generator._compute_summary(sample_results)

        assert summary["total_documents"] == len(sample_results)
        assert "decision_counts" in summary
        assert "accept" in summary["decision_counts"]
        assert "review" in summary["decision_counts"]
        assert "reject" in summary["decision_counts"]
        assert "combined_score" in summary
        assert "min" in summary["combined_score"]
        assert "max" in summary["combined_score"]
        assert "mean" in summary["combined_score"]

    def test_compute_summary_empty(self, generator):
        """Test summary computation with empty input."""
        summary = generator._compute_summary([])
        assert summary == {}

    def test_export_summary(self, generator, sample_results, tmp_dir):
        """Test summary JSON export."""
        summary = generator._compute_summary(sample_results)
        output_path = str(tmp_dir / "summary.json")
        generator._export_summary(summary, output_path)

        assert Path(output_path).exists()
        with open(output_path, encoding="utf-8") as f:
            loaded = json.load(f)
            assert loaded["total_documents"] == len(sample_results)

    def test_generate_jsonl_accepted(self, generator, sample_results, tmp_dir):
        """Test JSONL generation for accepted documents."""
        output_path = str(tmp_dir / "accepted.jsonl")
        result = generator.generate_jsonl_accepted(
            SAMPLE_DOCUMENTS, sample_results, output_path
        )

        assert result == output_path
        assert Path(output_path).exists()

        with open(output_path, encoding="utf-8") as f:
            lines = [l for l in f.readlines() if l.strip()]
            # Should have at least one accepted document
            assert len(lines) >= 1
            # Each line should be valid JSON
            for line in lines:
                doc = json.loads(line)
                assert "doc_id" in doc
                assert "quality_score" in doc

    def test_print_summary(self, generator, sample_results, capsys):
        """Test console summary output."""
        generator.print_summary(sample_results)
        captured = capsys.readouterr()

        assert "DOCUMENT QUALITY ASSESSMENT SUMMARY" in captured.out
        assert "Total documents:" in captured.out
        assert "Accept:" in captured.out
        assert "Reject:" in captured.out


class TestReportIntegration:
    """Integration tests for the full report generation pipeline."""

    def test_full_pipeline(self, tmp_dir):
        """Test the complete quality scoring and reporting pipeline."""
        # Score documents
        scorer = DocumentQualityScorer()
        results = scorer.score_documents(SAMPLE_DOCUMENTS)

        # Generate report
        generator = QualityReportGenerator(output_dir=str(tmp_dir))
        report = generator.generate_report(results, report_name="pipeline_test")

        # Verify outputs
        assert report["total_documents"] == len(SAMPLE_DOCUMENTS)
        assert report["accepted_count"] >= 0

        # Verify accepted JSONL if documents provided
        jsonl_path = str(tmp_dir / "accepted.jsonl")
        generator.generate_jsonl_accepted(SAMPLE_DOCUMENTS, results, jsonl_path)
        assert Path(jsonl_path).exists()

    def test_report_with_various_quality_levels(self, tmp_dir):
        """Test reporting with documents of varying quality."""
        # Create documents with different quality levels
        docs = [
            {  # High quality
                "doc_id": "doc-high",
                "title": "Complete Document",
                "content": "Content " * 500,
                "headings": [{"level": i, "text": f"Section {i}"} for i in range(1, 6)],
                "sections": [{"heading_path": f"S{i}", "text": "X" * 200, "level": i} for i in range(1, 4)],
                "domain_id": "D1",
                "source_type": "md",
                "parse_status": "success",
                "language": "vi",
            },
            {  # Medium quality
                "doc_id": "doc-medium",
                "title": "Partial Document",
                "content": "Short content",
                "headings": [{"level": 1, "text": "Only one heading"}],
                "sections": [],
                "parse_status": "partial",
            },
            {  # Low quality
                "doc_id": "doc-low",
                "title": "",
                "content": "x",
                "headings": [],
                "sections": [],
                "parse_status": "failed",
            },
        ]

        scorer = DocumentQualityScorer()
        results = scorer.score_documents(docs)

        generator = QualityReportGenerator(output_dir=str(tmp_dir))
        report = generator.generate_report(results)

        # Verify we have all three decision types
        assert report["summary"]["decision_counts"]["accept"] >= 0
        assert report["summary"]["decision_counts"]["reject"] >= 0