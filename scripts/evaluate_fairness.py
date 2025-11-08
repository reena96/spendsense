#!/usr/bin/env python3
"""
Fairness & Bias Analysis Evaluation Script

Analyzes recommendation fairness across demographic groups to detect potential bias.

Usage:
    python scripts/evaluate_fairness.py --dataset data/processed/spendsense.db --output-dir docs/eval
    python scripts/evaluate_fairness.py --demographic-attr income_bracket
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.evaluation.fairness_metrics import analyze_fairness
from spendsense.evaluation.fairness_reporting import (
    create_persona_distribution_chart,
    create_demographic_parity_chart,
    create_recommendation_heatmap,
    generate_fairness_report
)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate fairness and detect bias in SpendSense recommendations"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/processed/spendsense.db",
        help="Path to SQLite database (default: data/processed/spendsense.db)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="docs/eval",
        help="Directory for output files (default: docs/eval)"
    )
    parser.add_argument(
        "--demographic-attr",
        type=str,
        default=None,
        help="Specific demographic attribute to analyze (e.g., age_group, income_bracket)"
    )

    args = parser.parse_args()

    # Resolve paths
    db_path = Path(args.dataset)
    output_dir = Path(args.output_dir)

    if not db_path.exists():
        print(f"❌ Error: Database not found at {db_path}")
        sys.exit(1)

    print("=" * 60)
    print("FAIRNESS & BIAS ANALYSIS")
    print("=" * 60)
    print()
    print(f"Database: {db_path}")
    print(f"Output Directory: {output_dir}")
    if args.demographic_attr:
        print(f"Demographic Attribute: {args.demographic_attr}")
    print()

    # Run fairness analysis
    print("🔍 Analyzing fairness metrics...")
    metrics = analyze_fairness(
        db_path=str(db_path),
        demographic_attr=args.demographic_attr
    )

    # Generate timestamp for output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Check if demographic data is available
    available_attrs = [k for k, v in metrics.demographic_attributes_available.items() if v]

    if not available_attrs:
        print()
        print("⚠️  NO DEMOGRAPHIC DATA FOUND")
        print("-" * 60)
        print("The dataset does not contain demographic attributes.")
        print("Fairness analysis requires demographic data to detect bias.")
        print()
        print("Limitations documented:")
        for limitation in metrics.limitations:
            print(f"  - {limitation}")
        print()
        print("Recommendations:")
        for rec in metrics.mitigation_recommendations:
            print(f"  - {rec}")
        print()

        # Save metrics anyway
        output_path = output_dir / f"fairness_metrics_{timestamp}.json"
        metrics.save_json(output_path)
        print(f"📄 Metrics saved: {output_path}")

        sys.exit(0)

    # Demographic data available - continue with full analysis
    print(f"✅ Demographic attributes available: {', '.join(available_attrs)}")
    print()

    # Determine which attribute was analyzed
    analyzed_attr = args.demographic_attr or available_attrs[0]

    # Save JSON metrics
    json_path = output_dir / f"fairness_metrics_{timestamp}.json"
    metrics.save_json(json_path)
    print(f"📄 Metrics saved: {json_path}")

    # Generate visualizations
    print()
    print("📊 Generating visualizations...")

    # Persona distribution chart
    if metrics.persona_distribution_by_group:
        chart_path = output_dir / f"persona_distribution_{analyzed_attr}_{timestamp}.png"
        create_persona_distribution_chart(
            metrics.persona_distribution_by_group,
            chart_path,
            analyzed_attr
        )
        print(f"  ✓ Persona distribution chart: {chart_path}")

    # Demographic parity chart
    if metrics.demographic_parity_ratio is not None:
        # Extract group rates from analysis
        from spendsense.evaluation.fairness_metrics import load_user_data, calculate_demographic_parity
        users_df = load_user_data(str(db_path))
        _, group_rates = calculate_demographic_parity(users_df, analyzed_attr)

        chart_path = output_dir / f"demographic_parity_{analyzed_attr}_{timestamp}.png"
        create_demographic_parity_chart(
            group_rates,
            metrics.demographic_parity_ratio,
            chart_path,
            analyzed_attr
        )
        print(f"  ✓ Demographic parity chart: {chart_path}")

    # Recommendation heatmap (if data available)
    if metrics.recommendation_distribution_by_group:
        chart_path = output_dir / f"recommendation_heatmap_{analyzed_attr}_{timestamp}.png"
        create_recommendation_heatmap(
            metrics.recommendation_distribution_by_group,
            chart_path,
            analyzed_attr
        )
        print(f"  ✓ Recommendation heatmap: {chart_path}")

    # Generate report
    print()
    print("📋 Generating fairness report...")
    report_path = output_dir / f"fairness_report_{timestamp}.md"
    generate_fairness_report(metrics, report_path, analyzed_attr)
    print(f"  ✓ Fairness report: {report_path}")

    # Print summary
    print()
    print("=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print()
    print(f"Overall Assessment: {metrics.fairness_assessment}")
    print()

    if metrics.demographic_parity_ratio is not None:
        status = "✅ PASS" if metrics.demographic_parity_ratio >= 0.8 else "❌ FAIL"
        print(f"Demographic Parity Ratio: {metrics.demographic_parity_ratio:.3f} {status}")
        print(f"  Threshold: ≥ 0.8")

    if metrics.equal_opportunity_difference is not None:
        status = "✅ PASS" if metrics.equal_opportunity_difference <= 0.1 else "❌ FAIL"
        print(f"Equal Opportunity Difference: {metrics.equal_opportunity_difference:.3f} {status}")
        print(f"  Threshold: ≤ 0.1")

    print()
    print(f"Bias Indicators: {len(metrics.bias_indicators)}")

    if metrics.bias_indicators:
        high = sum(1 for ind in metrics.bias_indicators if ind.get("severity") == "high")
        medium = sum(1 for ind in metrics.bias_indicators if ind.get("severity") == "medium")
        low = sum(1 for ind in metrics.bias_indicators if ind.get("severity") == "low")

        print(f"  - High Severity: {high}")
        print(f"  - Medium Severity: {medium}")
        print(f"  - Low Severity: {low}")

        print()
        print("Bias Indicators:")
        for i, indicator in enumerate(metrics.bias_indicators, 1):
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(indicator.get("severity", ""), "")
            print(f"  {i}. [{indicator.get('severity', 'unknown').upper()}] {severity_emoji}")
            print(f"     {indicator.get('description', 'No description')}")

    print()
    print("Statistical Significance:")
    for attr, p_value in metrics.statistical_significance.items():
        if attr != "chi2_statistic":
            sig = "significant" if p_value < 0.05 else "not significant"
            print(f"  {attr}: p={p_value:.4f} ({sig})")

    print()
    print("-" * 60)
    print()

    # Exit code based on assessment
    if metrics.fairness_assessment == "FAIL" or len([i for i in metrics.bias_indicators if i.get("severity") == "high"]) > 0:
        print("⚠️  FAIRNESS CONCERNS DETECTED - Review required")
        sys.exit(1)
    elif metrics.fairness_assessment == "CONCERN":
        print("⚠️  Minor fairness concerns detected - Monitoring recommended")
        sys.exit(0)
    else:
        print("✅ No significant fairness concerns detected")
        sys.exit(0)


if __name__ == "__main__":
    main()
