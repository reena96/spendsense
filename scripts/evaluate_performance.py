#!/usr/bin/env python3
"""
CLI script for performance evaluation.

Measures system performance including latency, throughput, and resource utilization.
Generates visualizations and saves metrics to JSON.

Usage:
    python scripts/evaluate_performance.py --dataset synthetic --output-dir docs/eval --runs 3
    python scripts/evaluate_performance.py --limit 50 --runs 1
    python scripts/evaluate_performance.py --user-ids user_MASKED_000 user_MASKED_001
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.evaluation.performance_metrics import PerformanceEvaluator
# Note: Base import removed - not needed for performance evaluation


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate SpendSense system performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate all users with 3 runs
  python scripts/evaluate_performance.py --dataset synthetic --runs 3

  # Evaluate first 50 users
  python scripts/evaluate_performance.py --limit 50

  # Evaluate specific users
  python scripts/evaluate_performance.py --user-ids user_MASKED_000 user_MASKED_001

  # Custom output directory
  python scripts/evaluate_performance.py --output-dir /tmp/eval --runs 1
        """
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default="synthetic",
        choices=["synthetic"],
        help="Dataset to evaluate (default: synthetic)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="docs/eval",
        help="Output directory for metrics and visualizations (default: docs/eval)"
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of evaluation runs for consistency testing (default: 1)"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of users to evaluate (default: all users)"
    )

    parser.add_argument(
        "--user-ids",
        type=str,
        nargs="+",
        default=None,
        help="Specific user IDs to evaluate (overrides --limit)"
    )

    parser.add_argument(
        "--time-window",
        type=str,
        default="30d",
        help="Time window for behavioral signals (default: 30d)"
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="data/processed/spendsense.db",
        help="Path to SQLite database (default: data/processed/spendsense.db)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Database setup
    db_path = Path(args.db_path)
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        logger.error("Please run data generation scripts first")
        return 1

    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    logger.info("=" * 60)
    logger.info("SpendSense Performance Evaluation")
    logger.info("=" * 60)

    # Create evaluator
    evaluator = PerformanceEvaluator(
        db_session=session,
        output_dir=args.output_dir
    )

    # Prepare evaluation arguments
    eval_kwargs = {
        "time_window": args.time_window,
    }

    if args.user_ids:
        eval_kwargs["user_ids"] = args.user_ids
        logger.info(f"Evaluating {len(args.user_ids)} specific users")
    elif args.limit:
        eval_kwargs["limit"] = args.limit
        logger.info(f"Evaluating up to {args.limit} users")
    else:
        logger.info("Evaluating all users in database")

    # Run evaluation
    try:
        if args.runs > 1:
            logger.info(f"Running {args.runs} evaluation runs for consistency testing")
            metrics_list, consistency = evaluator.evaluate_multiple_runs(
                num_runs=args.runs,
                **eval_kwargs
            )
            # Use the latest run for summary
            metrics = metrics_list[-1]

            # Print consistency results
            print("\n" + "=" * 60)
            print("CONSISTENCY ANALYSIS")
            print("=" * 60)
            print(f"Number of runs: {consistency['num_runs']}")
            print(f"\nTotal Latency:")
            print(f"  Mean: {consistency['total_latency']['mean']:.2f}s")
            print(f"  Std Dev: {consistency['total_latency']['std']:.2f}s")
            print(f"  CV: {consistency['total_latency']['cv_percent']:.1f}%")
            print(f"\nThroughput:")
            print(f"  Mean: {consistency['throughput']['mean']:.2f} users/min")
            print(f"  Std Dev: {consistency['throughput']['std']:.2f} users/min")
            print(f"  CV: {consistency['throughput']['cv_percent']:.1f}%")
            print(f"\np95 Latency:")
            print(f"  Mean: {consistency['p95_latency']['mean']:.2f}s")
            print(f"  Std Dev: {consistency['p95_latency']['std']:.2f}s")
            print(f"  CV: {consistency['p95_latency']['cv_percent']:.1f}%")
            print(f"\nConsistent (CV <10%): {'YES' if consistency['consistent'] else 'NO'}")

        else:
            metrics = evaluator.evaluate(**eval_kwargs)

        # Print summary
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)

        user_count = metrics.run_metadata["user_count"]
        avg_latency = metrics.run_metadata["avg_latency_per_user"]
        target_met = metrics.run_metadata["target_met"]

        print(f"\nDataset: {args.dataset}")
        print(f"Users evaluated: {user_count}")
        print(f"Time window: {args.time_window}")
        print(f"\nLatency Metrics:")
        print(f"  Total time: {metrics.total_latency_seconds:.2f}s")
        print(f"  Average per user: {avg_latency:.2f}s")
        print(f"  p50 (median): {metrics.latency_percentiles['p50']:.2f}s")
        print(f"  p95: {metrics.latency_percentiles['p95']:.2f}s")
        print(f"  p99: {metrics.latency_percentiles['p99']:.2f}s")
        print(f"\nThroughput:")
        print(f"  {metrics.throughput_users_per_minute:.2f} users/minute")
        print(f"  {metrics.throughput_users_per_minute/60:.2f} users/second")

        print(f"\nResource Utilization:")
        print(f"  Memory: {metrics.resource_utilization['peak_memory_mb']:.1f} MB")
        print(f"  CPU: {metrics.resource_utilization['avg_cpu_percent']:.1f}%")
        print(f"  CPU cores: {metrics.resource_utilization['cpu_count']}")
        print(f"  Disk Read: {metrics.resource_utilization.get('disk_read_mb', 0):.1f} MB")
        print(f"  Disk Write: {metrics.resource_utilization.get('disk_write_mb', 0):.1f} MB")

        print(f"\nComponent Breakdown:")
        # Sort by latency descending
        sorted_components = sorted(
            metrics.component_latencies.items(),
            key=lambda x: x[1],
            reverse=True
        )
        total_component_time = sum(metrics.component_latencies.values())
        bottleneck_components = [b['component'] for b in metrics.bottlenecks]
        for component, latency in sorted_components:
            percentage = (latency / total_component_time * 100) if total_component_time > 0 else 0
            bottleneck = " [BOTTLENECK]" if component in bottleneck_components else ""
            print(f"  {component}: {latency:.3f}s ({percentage:.1f}%){bottleneck}")

        if metrics.bottlenecks:
            print(f"\nBottlenecks Detected ({len(metrics.bottlenecks)}):")
            for bottleneck in metrics.bottlenecks:
                print(f"\n  {bottleneck['component']} - {bottleneck['percentage']:.1f}% [{bottleneck['severity'].upper()}]")
                print(f"  Optimization Suggestions:")
                for suggestion in bottleneck['suggestions']:
                    print(f"    - {suggestion}")
        else:
            print(f"\nBottlenecks: None detected")

        print(f"\nScalability Projections (linear):")
        for user_count_proj, time_proj in sorted(metrics.scalability_projections.items()):
            minutes = time_proj / 60
            hours = minutes / 60
            if hours >= 1:
                print(f"  {user_count_proj:,} users: {hours:.1f} hours")
            else:
                print(f"  {user_count_proj:,} users: {minutes:.1f} minutes")

        print(f"\nTarget (<5s per user): {'✓ MET' if target_met else '✗ NOT MET'}")

        # Output files
        print(f"\nOutput Files:")
        json_file = metrics.run_metadata.get("chart_paths", {})
        print(f"  Metrics JSON: {args.output_dir}/performance_metrics_{metrics.run_metadata['run_id']}.json")
        if "latency_distribution" in metrics.run_metadata.get("chart_paths", {}):
            print(f"  Latency chart: {metrics.run_metadata['chart_paths']['latency_distribution']}")
        if "component_breakdown" in metrics.run_metadata.get("chart_paths", {}):
            print(f"  Component chart: {metrics.run_metadata['chart_paths']['component_breakdown']}")

        print("\n" + "=" * 60)

        # Exit code based on target
        return 0 if target_met else 1

    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        return 1

    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
