#!/usr/bin/env python3
"""
CLI script for evaluating coverage metrics.

Calculates persona assignment and behavioral signal detection rates,
saves results to JSON, and reports summary statistics.

PYTHONPATH Setup:
    This script requires the spendsense package to be in PYTHONPATH.
    Run from the project root directory:

    export PYTHONPATH=/Users/reena/gauntletai/spendsense:$PYTHONPATH
    python scripts/evaluate_coverage.py --dataset synthetic_50_users

    Or use absolute imports from project root:

    PYTHONPATH=/Users/reena/gauntletai/spendsense python scripts/evaluate_coverage.py

Usage:
    python scripts/evaluate_coverage.py --dataset synthetic_50_users --output-dir docs/eval
    python scripts/evaluate_coverage.py --dataset real_production --db-path data/prod.db
"""

import argparse
import sys
import logging
from pathlib import Path

from spendsense.evaluation.coverage_metrics import (
    calculate_coverage_metrics,
    save_coverage_metrics,
    load_previous_metrics,
    calculate_coverage_trends
)


def setup_logging(verbose: bool = False):
    """Configure logging for CLI script."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Evaluate coverage metrics for persona assignment and behavioral signals',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate synthetic dataset
  python scripts/evaluate_coverage.py --dataset synthetic_50_users

  # Evaluate with custom database and output directory
  python scripts/evaluate_coverage.py \\
    --dataset real_production \\
    --db-path data/production/spendsense.db \\
    --output-dir reports/coverage

  # Evaluate both time windows with verbose logging
  python scripts/evaluate_coverage.py \\
    --dataset synthetic_100_users \\
    --time-windows 30d 180d \\
    --verbose

Exit Codes:
  0 - All targets met (100% persona assignment, 100% users with ≥3 signals)
  1 - Targets not met or evaluation failed
        """
    )

    parser.add_argument(
        '--dataset',
        type=str,
        default='synthetic_dataset',
        help='Dataset identifier for tracking (e.g., synthetic_50_users, real_production)'
    )

    parser.add_argument(
        '--db-path',
        type=str,
        default='data/processed/spendsense.db',
        help='Path to SQLite database (default: data/processed/spendsense.db)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='docs/eval',
        help='Output directory for metrics JSON files (default: docs/eval)'
    )

    parser.add_argument(
        '--time-windows',
        nargs='+',
        choices=['30d', '180d'],
        default=['30d', '180d'],
        help='Time windows to evaluate (default: both 30d and 180d)'
    )

    parser.add_argument(
        '--show-trends',
        action='store_true',
        help='Show trends compared to previous evaluation runs'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    return parser.parse_args()


def print_summary(metrics, trends=None):
    """Print human-readable summary of coverage metrics."""
    print("\n" + "=" * 70)
    print("Coverage Metrics Summary")
    print("=" * 70)

    print(f"\nDataset: {metrics.dataset}")
    print(f"Timestamp: {metrics.timestamp}")
    print(f"Total Users: {metrics.total_users}")

    print("\n--- Persona Assignment Coverage ---")
    print(f"  Assignment Rate: {metrics.persona_assignment_rate:.1%}")
    print(f"  Users with Personas: {metrics.users_with_personas}")
    print(f"  Users without Personas: {metrics.total_users - metrics.users_with_personas}")

    if metrics.persona_assignment_rate >= 1.0:
        print("  ✓ Target met: 100% persona assignment")
    else:
        missing_pct = (1.0 - metrics.persona_assignment_rate) * 100
        print(f"  ✗ Target not met: {missing_pct:.1f}% below 100% target")

    print("\n--- Behavioral Signal Coverage ---")
    print(f"  Signal Detection Rate: {metrics.behavioral_signal_rate:.1%} (≥3 signals)")
    print(f"  Users with ≥3 Signals: {metrics.users_with_3plus_signals}")
    print(f"  Users with <3 Signals: {metrics.total_users - metrics.users_with_3plus_signals}")

    if metrics.behavioral_signal_rate >= 1.0:
        print("  ✓ Target met: 100% users with ≥3 signals")
    else:
        missing_pct = (1.0 - metrics.behavioral_signal_rate) * 100
        print(f"  ✗ Target not met: {missing_pct:.1f}% below 100% target")

    print("\n--- Persona Distribution ---")
    for persona, count in sorted(metrics.persona_distribution.items()):
        pct = (count / metrics.total_users * 100) if metrics.total_users > 0 else 0
        print(f"  {persona:25s}: {count:3d} ({pct:5.1f}%)")

    print("\n--- Time Window Completion ---")
    print(f"  30-day window: {metrics.window_completion_30d:.1%}")
    print(f"  180-day window: {metrics.window_completion_180d:.1%}")

    print("\n--- Missing Data Analysis ---")
    print(f"  Users with Issues: {len(metrics.missing_data_users)}")

    if metrics.missing_data_users:
        # Group by issue type
        issue_counts = {}
        for user in metrics.missing_data_users:
            issue_type = user.get('issue_type', 'unknown')
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        print("\n  Issue Breakdown:")
        for issue_type, count in sorted(issue_counts.items(), key=lambda x: -x[1]):
            print(f"    {issue_type:35s}: {count:3d}")

        # Show top 5 high-severity issues
        high_severity = [u for u in metrics.missing_data_users if u.get('severity') == 'high']
        if high_severity:
            print("\n  High-Severity Issues (first 5):")
            for user in high_severity[:5]:
                print(f"    User {user['user_id']}: {user['issue_type']} - {user['details']}")

    if trends:
        print("\n--- Trends (vs Previous Run) ---")
        print(f"  Comparison with: {trends['comparison_timestamp']}")
        print(f"  {trends['improvement_summary']}")

        if trends['persona_distribution_changes']:
            print("\n  Persona Distribution Changes:")
            for persona, change in sorted(trends['persona_distribution_changes'].items()):
                direction = "+" if change > 0 else ""
                print(f"    {persona:25s}: {direction}{change}")

    print("\n" + "=" * 70)


def main():
    """Main CLI entry point."""
    args = parse_args()

    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Validate database exists
        db_path = Path(args.db_path)
        if not db_path.exists():
            logger.error(f"Database not found: {db_path}")
            print(f"Error: Database not found at {db_path}", file=sys.stderr)
            print("Please check the --db-path argument or create the database first.", file=sys.stderr)
            return 1

        # Calculate coverage metrics
        logger.info(f"Calculating coverage metrics for dataset: {args.dataset}")

        metrics = calculate_coverage_metrics(
            db_path=str(db_path),
            dataset=args.dataset,
            time_window_30d=('30d' in args.time_windows),
            time_window_180d=('180d' in args.time_windows)
        )

        # Save metrics to JSON
        output_dir = Path(args.output_dir)
        output_path = save_coverage_metrics(metrics, output_dir)
        logger.info(f"Metrics saved to {output_path}")

        # Calculate trends if requested
        trends = None
        if args.show_trends:
            previous_metrics = load_previous_metrics(output_dir, count=10)
            if previous_metrics:
                trends = calculate_coverage_trends(metrics, previous_metrics)
                logger.info("Trend analysis completed")
            else:
                logger.warning("No previous metrics found for trend analysis")

        # Print summary
        print_summary(metrics, trends)

        # Determine exit code based on targets
        targets_met = (
            metrics.persona_assignment_rate >= 1.0 and
            metrics.behavioral_signal_rate >= 1.0
        )

        if targets_met:
            print("\n✓ All coverage targets met!")
            return 0
        else:
            print("\n✗ Coverage targets not met. See summary above for details.")
            return 1

    except Exception as e:
        logger.exception("Coverage evaluation failed")
        print(f"\nError: Coverage evaluation failed: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
