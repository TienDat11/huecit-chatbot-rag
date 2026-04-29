"""
Report generator for document quality assessment results.

Exports quality reports and lists of accepted documents for the next pipeline stage.
"""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class QualityReportGenerator:
    """Generate quality assessment reports and accepted document lists."""

    def __init__(self, output_dir: str = "output/week_1"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        results: list[dict],
        report_name: str = "quality_report",
        include_summary: bool = True,
    ) -> dict:
        """Generate a comprehensive quality report.

        Args:
            results: List of quality assessment results from DocumentQualityScorer
            report_name: Base name for output files
            include_summary: Whether to include summary statistics

        Returns:
            Dict with paths to generated files and summary stats
        """
        if not results:
            logger.warning("No results to generate report from")
            return {"error": "No results provided"}

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        base_path = self.output_dir / f"{report_name}_{timestamp}"

        # Generate outputs
        output_files = {}

        # 1. Full CSV report
        csv_path = str(base_path) + "_full.csv"
        self._export_csv(results, csv_path)
        output_files["full_report"] = csv_path

        # 2. Accepted documents list
        accepted = [r for r in results if r.get("ready_for_benchmark")]
        accepted_path = str(base_path) + "_accepted.csv"
        self._export_accepted_list(accepted, accepted_path)
        output_files["accepted_list"] = accepted_path

        # 3. Summary statistics
        if include_summary:
            summary = self._compute_summary(results)
            summary_path = str(base_path) + "_summary.json"
            self._export_summary(summary, summary_path)
            output_files["summary"] = summary_path
        else:
            summary = {}

        return {
            "output_files": output_files,
            "summary": summary,
            "total_documents": len(results),
            "accepted_count": len(accepted),
        }

    def _export_csv(self, results: list[dict], output_path: str) -> None:
        """Export full results to CSV."""
        if not results:
            return

        # Get all fields from first result
        fieldnames = list(results[0].keys())

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        logger.info(f"Exported {len(results)} results to {output_path}")

    def _export_accepted_list(
        self, accepted: list[dict], output_path: str
    ) -> None:
        """Export list of accepted documents for chunking pipeline."""
        # Only export relevant fields for next stage
        fields = [
            "doc_id",
            "title",
            "combined_score",
            "rule_quality_score",
            "structure_quality_score",
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=fields, extrasaction="ignore"
            )
            writer.writeheader()
            writer.writerows(accepted)

        logger.info(f"Exported {len(accepted)} accepted documents to {output_path}")

    def _compute_summary(self, results: list[dict]) -> dict:
        """Compute summary statistics from results."""
        if not results:
            return {}

        scores = [r.get("combined_score", 0) for r in results]
        rule_scores = [r.get("rule_quality_score", 0) for r in results]
        struct_scores = [r.get("structure_quality_score", 0) for r in results]

        decisions = [r.get("decision", "unknown") for r in results]
        decision_counts = {
            "accept": decisions.count("accept"),
            "review": decisions.count("review"),
            "reject": decisions.count("reject"),
        }

        def _stats(values: list) -> dict:
            if not values:
                return {"min": 0, "max": 0, "mean": 0, "median": 0}
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            return {
                "min": round(min(sorted_vals), 2),
                "max": round(max(sorted_vals), 2),
                "mean": round(sum(sorted_vals) / n, 2),
                "median": round(
                    sorted_vals[n // 2] if n % 2 else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2,
                    2,
                ),
            }

        return {
            "total_documents": len(results),
            "decision_counts": decision_counts,
            "accept_rate": round(decision_counts["accept"] / len(results) * 100, 1),
            "combined_score": _stats(scores),
            "rule_score": _stats(rule_scores),
            "structure_score": _stats(struct_scores),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _export_summary(self, summary: dict, output_path: str) -> None:
        """Export summary statistics to JSON."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        logger.info(f"Exported summary to {output_path}")

    def generate_jsonl_accepted(
        self,
        documents: list[dict],
        results: list[dict],
        output_path: str,
    ) -> str:
        """Generate JSONL file with accepted document content for chunking.

        Combines original document data with quality scores for documents
        that passed the accept threshold.

        Args:
            documents: Original document metadata list
            results: Quality assessment results
            output_path: Path for output JSONL file

        Returns:
            Path to generated file
        """
        # Create lookup by doc_id
        accepted_ids = {
            r["doc_id"] for r in results if r.get("ready_for_benchmark")
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        count = 0
        with open(output_path, "w", encoding="utf-8") as f:
            for doc in documents:
                if doc.get("doc_id") in accepted_ids:
                    # Add quality score to document
                    doc_with_score = dict(doc)
                    matching_result = next(
                        (r for r in results if r.get("doc_id") == doc.get("doc_id")),
                        None,
                    )
                    if matching_result:
                        doc_with_score["quality_score"] = matching_result.get(
                            "combined_score"
                        )
                    f.write(json.dumps(doc_with_score, ensure_ascii=False) + "\n")
                    count += 1

        logger.info(f"Exported {count} accepted documents to {output_path}")
        return output_path

    def print_summary(self, results: list[dict]) -> None:
        """Print a human-readable summary to console."""
        if not results:
            print("No results to summarize")
            return

        summary = self._compute_summary(results)

        print("\n" + "=" * 60)
        print("DOCUMENT QUALITY ASSESSMENT SUMMARY")
        print("=" * 60)
        print(f"Total documents: {summary['total_documents']}")
        print(f"\nDecision breakdown:")
        print(f"  ✓ Accept: {summary['decision_counts']['accept']} ({summary['accept_rate']}%)")
        print(f"  ⚠ Review: {summary['decision_counts']['review']}")
        print(f"  ✗ Reject: {summary['decision_counts']['reject']}")

        print(f"\nCombined Score:")
        s = summary["combined_score"]
        print(f"  Min: {s['min']}  Max: {s['max']}  Mean: {s['mean']}  Median: {s['median']}")

        print(f"\nRule-based Score:")
        s = summary["rule_score"]
        print(f"  Min: {s['min']}  Max: {s['max']}  Mean: {s['mean']}  Median: {s['median']}")

        print(f"\nStructure Score:")
        s = summary["structure_score"]
        print(f"  Min: {s['min']}  Max: {s['max']}  Mean: {s['mean']}  Median: {s['median']}")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Generate quality reports")
    parser.add_argument("--input", required=True, help="JSONL file with quality results")
    parser.add_argument(
        "--documents",
        help="Original JSONL documents (for JSONL accepted list)",
    )
    parser.add_argument(
        "--output-dir",
        default="output/week_1",
        help="Output directory",
    )
    parser.add_argument(
        "--report-name",
        default="quality_report",
        help="Base name for report files",
    )
    args = parser.parse_args()

    # Load results
    results = []
    with open(args.input, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    # Generate report
    generator = QualityReportGenerator(output_dir=args.output_dir)
    report = generator.generate_report(
        results, report_name=args.report_name, include_summary=True
    )

    generator.print_summary(results)

    print(f"\nOutput files:")
    for name, path in report["output_files"].items():
        print(f"  {name}: {path}")

    # Optionally generate JSONL for accepted documents
    if args.documents:
        docs = []
        with open(args.documents, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    docs.append(json.loads(line))

        jsonl_path = Path(args.output_dir) / "accepted_documents.jsonl"
        generator.generate_jsonl_accepted(docs, results, str(jsonl_path))
        print(f"  accepted_documents: {jsonl_path}")