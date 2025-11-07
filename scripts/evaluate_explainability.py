#!/usr/bin/env python3
"""
CLI script for evaluating recommendation explainability.

Calculates explainability metrics including rationale presence, quality,
and decision trace completeness.
"""

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.evaluation.explainability_metrics import (
    calculate_explainability_metrics,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_paths(data_dir: Path, db_path: Path) -> bool:
    """
    Validate that required paths exist before attempting operations.

    Args:
        data_dir: Data directory that should contain recommendations
        db_path: Database path for audit logs

    Returns:
        True if validation passes, False otherwise (exits with code 3)
    """
    validation_passed = True

    # Validate data directory
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        logger.error("Please check --data-dir argument.")
        logger.error(f"Expected directory structure: {data_dir}/synthetic/recommendations/")
        validation_passed = False

    # Validate database path
    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        logger.warning("Please check --db-path argument.")
        logger.warning("Will continue without audit logs, but decision trace metrics will be unavailable.")
        # Don't fail validation for missing DB, just warn

    if not validation_passed:
        logger.error("Path validation failed. Exiting.")
        sys.exit(3)

    return True


def load_recommendations_from_json(
    data_dir: Path, user_ids: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Load recommendations from JSON files.

    Args:
        data_dir: Directory containing recommendation JSON files
        user_ids: Optional list of user IDs to filter

    Returns:
        List of all recommendations across users
    """
    recommendations = []
    rec_dir = data_dir / "synthetic" / "recommendations"

    if not rec_dir.exists():
        logger.warning(f"Recommendations directory not found: {rec_dir}")
        return []

    # Iterate through user directories
    for user_dir in rec_dir.iterdir():
        if not user_dir.is_dir():
            continue

        user_id = user_dir.name
        if user_ids and user_id not in user_ids:
            continue

        # Load latest recommendations file
        latest_file = user_dir / "latest_30d.json"
        if not latest_file.exists():
            # Try other patterns
            json_files = list(user_dir.glob("*.json"))
            if json_files:
                latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
            else:
                logger.warning(f"No recommendation files found for user {user_id}")
                continue

        try:
            with open(latest_file, "r") as f:
                data = json.load(f)
                user_recs = data.get("recommendations", [])

                # Enhance each recommendation with user_id and persona
                for rec in user_recs:
                    rec["user_id"] = data.get("user_id", user_id)
                    rec["persona_id"] = data.get("persona_id", "unknown")

                recommendations.extend(user_recs)
                logger.info(
                    f"Loaded {len(user_recs)} recommendations for user {user_id}"
                )

        except Exception as e:
            logger.error(f"Error loading recommendations from {latest_file}: {e}")

    return recommendations


def load_audit_logs_from_db(db_path: Path) -> List[Dict[str, Any]]:
    """
    Load audit logs from database.

    Args:
        db_path: Path to SQLite database

    Returns:
        List of audit log entries
    """
    if not db_path.exists():
        logger.warning(f"Database not found: {db_path}")
        return []

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT log_id, event_type, user_id, recommendation_id,
                   timestamp, event_data
            FROM comprehensive_audit_log
            ORDER BY timestamp DESC
        """
        )

        logs = []
        for row in cursor.fetchall():
            log_entry = dict(row)
            # Parse event_data JSON if present
            if log_entry.get("event_data"):
                try:
                    log_entry["event_data"] = json.loads(log_entry["event_data"])
                except json.JSONDecodeError:
                    pass
            logs.append(log_entry)

        conn.close()
        logger.info(f"Loaded {len(logs)} audit log entries from database")
        return logs

    except Exception as e:
        logger.error(f"Error loading audit logs from database: {e}")
        return []


def save_metrics_to_json(
    metrics: Dict[str, Any], output_path: Path
) -> None:
    """
    Save metrics to JSON file.

    Args:
        metrics: Metrics dictionary to save
        output_path: Output file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2, default=str)

    logger.info(f"Saved metrics to {output_path}")


def print_summary(metrics: Dict[str, Any]) -> None:
    """
    Print summary of metrics to console.

    Args:
        metrics: Calculated metrics dictionary
    """
    print("\n" + "=" * 80)
    print("EXPLAINABILITY METRICS SUMMARY")
    print("=" * 80)

    # Extract metrics from nested structure
    explainability_metrics = metrics.get("explainability_metrics", {})

    print(f"\nRationale Presence Rate: {explainability_metrics.get('rationale_presence_rate', 0):.1%}")
    print(f"Average Quality Score: {explainability_metrics.get('average_quality_score', 0):.1f}/5")
    print(
        f"Decision Trace Completeness: {explainability_metrics.get('decision_trace_completeness', 0):.1%}"
    )

    print("\n--- By Persona ---")
    for persona, rate in sorted(explainability_metrics.get("explainability_by_persona", {}).items()):
        print(f"  {persona}: {rate:.1%}")

    print(f"\n--- Failure Cases ---")
    print(f"Total failures: {len(metrics.get('failure_cases', []))}")

    failure_types = {}
    for failure in metrics.get("failure_cases", []):
        failure_type = failure["failure_type"]
        failure_types[failure_type] = failure_types.get(failure_type, 0) + 1

    for failure_type, count in sorted(failure_types.items()):
        print(f"  {failure_type}: {count}")

    print(f"\n--- Sample Rationales ---")
    print(f"Extracted {len(metrics.get('sample_rationales', []))} samples for manual review")

    print(f"\n--- Improvement Recommendations ---")
    for i, rec in enumerate(metrics.get("improvement_recommendations", []), 1):
        print(f"  {i}. {rec}")

    print("\n" + "=" * 80)


def main():
    """Main entry point for explainability evaluation."""
    parser = argparse.ArgumentParser(
        description="Evaluate recommendation explainability metrics"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="synthetic",
        help="Dataset name (default: synthetic)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/eval"),
        help="Output directory for metrics (default: docs/eval)",
    )
    parser.add_argument(
        "--sample-count",
        type=int,
        default=3,
        help="Number of sample rationales per persona (default: 3)",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Data directory containing recommendations (default: data)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/processed/spendsense.db"),
        help="Database path for audit logs (default: data/processed/spendsense.db)",
    )
    parser.add_argument(
        "--user-ids",
        type=str,
        nargs="+",
        help="Optional: Specific user IDs to evaluate",
    )

    args = parser.parse_args()

    # Validate paths before attempting operations
    logger.info("Validating paths...")
    validate_paths(args.data_dir, args.db_path)

    # Load recommendations
    logger.info(f"Loading recommendations from {args.data_dir}")
    recommendations = load_recommendations_from_json(args.data_dir, args.user_ids)

    if not recommendations:
        logger.error("No recommendations found. Exiting with error.")
        sys.exit(1)

    logger.info(f"Loaded {len(recommendations)} total recommendations")

    # Load audit logs
    logger.info(f"Loading audit logs from {args.db_path}")
    audit_logs = load_audit_logs_from_db(args.db_path)

    # Calculate metrics
    logger.info("Calculating explainability metrics...")
    metrics_obj = calculate_explainability_metrics(
        recommendations=recommendations,
        audit_logs=audit_logs,
        samples_per_persona=args.sample_count,
    )

    # Convert to dict for JSON serialization
    metrics_dict = {
        "timestamp": metrics_obj.timestamp.isoformat(),
        "dataset": args.dataset,
        "total_recommendations": len(recommendations),
        "total_audit_logs": len(audit_logs),
        "explainability_metrics": {
            "rationale_presence_rate": metrics_obj.rationale_presence_rate,
            "average_quality_score": metrics_obj.rationale_quality_score,
            "explainability_by_persona": metrics_obj.explainability_by_persona,
            "decision_trace_completeness": metrics_obj.decision_trace_completeness,
        },
        "failure_cases": metrics_obj.failure_cases,
        "sample_rationales": metrics_obj.sample_rationales,
        "improvement_recommendations": metrics_obj.improvement_recommendations,
    }

    # Save to JSON
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_path = args.output_dir / f"explainability_metrics_{timestamp_str}.json"
    save_metrics_to_json(metrics_dict, output_path)

    # Print summary
    print_summary(metrics_dict)

    # Determine exit code based on targets
    targets_met = (
        metrics_obj.rationale_presence_rate >= 0.95  # Target 100%, allow 95%
        and metrics_obj.rationale_quality_score >= 3.0  # Target ≥3/5
        and metrics_obj.decision_trace_completeness >= 0.90  # Target 90%+
    )

    if targets_met:
        logger.info("✓ All explainability targets met")
        sys.exit(0)
    else:
        logger.warning("✗ Some explainability targets not met")
        sys.exit(1)


if __name__ == "__main__":
    main()
