#!/usr/bin/env python3
"""
CLI script for auditability and compliance evaluation.

Epic 7 - Story 7.4: Auditability & Compliance Metrics

Usage:
    python scripts/evaluate_auditability.py --dataset synthetic --output-dir docs/eval/
    python scripts/evaluate_auditability.py --check-retention --verbose

Testing:
    Run all tests (unit + integration):
        pytest tests/evaluation/test_auditability_metrics.py -v

    Run only integration tests (with real database):
        pytest tests/evaluation/test_auditability_metrics.py::TestIntegrationWithRealDatabase -v

    Run with coverage:
        pytest tests/evaluation/test_auditability_metrics.py -v --cov=spendsense.evaluation.auditability_metrics
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from spendsense.evaluation.auditability_metrics import (
    AuditabilityEvaluator,
    generate_compliance_report
)
from spendsense.config.database import get_db_session


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate auditability and compliance metrics for SpendSense recommendations"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="synthetic",
        help="Dataset identifier (default: synthetic)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="docs/eval",
        help="Output directory for evaluation results (default: docs/eval)"
    )
    parser.add_argument(
        "--check-retention",
        action="store_true",
        help="Perform detailed data retention compliance check"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed compliance report to console"
    )
    parser.add_argument(
        "--fail-on-critical",
        action="store_true",
        default=True,
        help="Exit with code 2 if critical violations found (default: True)"
    )
    parser.add_argument(
        "--fail-on-any",
        action="store_true",
        help="Exit with code 1 if any compliance failures found"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("AUDITABILITY & COMPLIANCE EVALUATION")
    print("=" * 80)
    print(f"Dataset: {args.dataset}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 80)
    print()

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Run evaluation
    print("Running compliance evaluation...")
    print()

    try:
        # Create evaluator with database session
        db_session = get_db_session()
        evaluator = AuditabilityEvaluator(db_session=db_session)

        # Run all evaluations
        metrics = evaluator.evaluate_all()

        # Generate compliance report
        compliance_report = generate_compliance_report(metrics)

        # Print summary to console
        print_summary(metrics, compliance_report, args.verbose)

        # Save results to JSON
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        output_file = output_dir / f"auditability_metrics_{args.dataset}_{timestamp_str}.json"

        output_data = {
            "dataset": args.dataset,
            "timestamp": metrics.timestamp.isoformat(),
            "metrics": metrics.to_dict(),
            "compliance_report": compliance_report
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)

        print()
        print(f"Results saved to: {output_file}")
        print()

        # Determine exit code
        exit_code = determine_exit_code(metrics, args.fail_on_critical, args.fail_on_any)

        if exit_code == 0:
            print("✓ EVALUATION COMPLETE - FULLY COMPLIANT")
        elif exit_code == 1:
            print("⚠ EVALUATION COMPLETE - WARNINGS DETECTED")
        elif exit_code == 2:
            print("✗ EVALUATION COMPLETE - CRITICAL VIOLATIONS DETECTED")

        db_session.close()
        sys.exit(exit_code)

    except Exception as e:
        print(f"ERROR: Evaluation failed: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)


def print_summary(metrics, compliance_report, verbose: bool = False):
    """Print compliance summary to console."""
    print("COMPLIANCE SUMMARY")
    print("-" * 80)
    print(f"Overall Compliance Score: {metrics.overall_compliance_score:.1f}%")
    print(f"Critical Issues: {metrics.critical_issues_count}")
    print()

    print("GUARDRAIL STATUS:")
    print("-" * 80)

    # Consent compliance (CRITICAL)
    consent_status = "PASS" if metrics.consent_compliance_rate == 100.0 else "FAIL"
    consent_icon = "✓" if consent_status == "PASS" else "✗"
    print(f"  {consent_icon} Consent Compliance: {consent_status} ({metrics.consent_compliance_rate:.1f}%)")

    # Eligibility compliance
    elig_status = compliance_report["guardrail_status"]["eligibility_compliance"]["status"]
    elig_icon = "✓" if elig_status == "PASS" else "⚠" if elig_status == "WARNING" else "✗"
    print(f"  {elig_icon} Eligibility Compliance: {elig_status} ({metrics.eligibility_compliance_rate:.1f}%)")

    # Tone compliance
    tone_status = compliance_report["guardrail_status"]["tone_compliance"]["status"]
    tone_icon = "✓" if tone_status == "PASS" else "⚠" if tone_status == "WARNING" else "✗"
    print(f"  {tone_icon} Tone Compliance: {tone_status} ({metrics.tone_compliance_rate:.1f}%)")

    # Disclaimer presence
    disc_status = "PASS" if metrics.disclaimer_presence_rate == 100.0 else "FAIL"
    disc_icon = "✓" if disc_status == "PASS" else "✗"
    print(f"  {disc_icon} Disclaimer Presence: {disc_status} ({metrics.disclaimer_presence_rate:.1f}%)")

    # Decision trace completeness
    trace_status = compliance_report["guardrail_status"]["decision_trace_completeness"]["status"]
    trace_icon = "✓" if trace_status == "PASS" else "⚠" if trace_status == "WARNING" else "✗"
    print(f"  {trace_icon} Decision Trace Completeness: {trace_status} ({metrics.decision_trace_completeness:.1f}%)")

    # Audit log completeness
    audit_status = compliance_report["guardrail_status"]["audit_log_completeness"]["status"]
    audit_icon = "✓" if audit_status == "PASS" else "⚠" if audit_status == "WARNING" else "✗"
    print(f"  {audit_icon} Audit Log Completeness: {audit_status} ({metrics.audit_log_completeness:.1f}%)")

    print()

    # Violations summary
    if metrics.critical_issues_count > 0 or len(metrics.compliance_failures) > 0:
        print("VIOLATIONS BY SEVERITY:")
        print("-" * 80)
        for severity, count in compliance_report["violations_by_severity"].items():
            if count > 0:
                print(f"  {severity}: {count}")
        print()

    # Recommendation age summary
    if metrics.recommendation_ages.total_recommendations > 0:
        print("RECOMMENDATION AGE ANALYSIS:")
        print("-" * 80)
        print(f"  Total Recommendations: {metrics.recommendation_ages.total_recommendations}")
        print(f"  Average Age: {metrics.recommendation_ages.average_age_hours:.1f} hours ({metrics.recommendation_ages.average_age_hours/24:.1f} days)")
        if metrics.recommendation_ages.oldest_age_hours:
            print(f"  Oldest Recommendation: {metrics.recommendation_ages.oldest_age_hours:.1f} hours ({metrics.recommendation_ages.oldest_age_hours/24:.1f} days)")
        print(f"  Stale Recommendations (>30d): {len(metrics.recommendation_ages.stale_recommendations)}")
        print()

        print("  Age Distribution:")
        for age_range, count in metrics.recommendation_ages.age_distribution.items():
            print(f"    {age_range}: {count}")
        print()

    # Data retention status
    print(f"DATA RETENTION STATUS: {metrics.data_retention_status}")
    print()

    # Remediation recommendations
    if compliance_report["recommendations_for_remediation"]:
        print("REMEDIATION RECOMMENDATIONS:")
        print("-" * 80)
        for i, rec in enumerate(compliance_report["recommendations_for_remediation"], 1):
            print(f"  {i}. {rec}")
        print()

    # Verbose output - show detailed failures
    if verbose and len(metrics.compliance_failures) > 0:
        print()
        print("DETAILED FAILURE REPORT:")
        print("=" * 80)

        # Group failures by severity
        failures_by_severity = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }

        for failure in metrics.compliance_failures:
            failures_by_severity[failure.severity.value].append(failure)

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            failures = failures_by_severity[severity]
            if not failures:
                continue

            print()
            print(f"{severity} VIOLATIONS ({len(failures)}):")
            print("-" * 80)

            for i, failure in enumerate(failures[:10], 1):  # Show first 10 per severity
                print(f"{i}. [{failure.failure_type}]")
                print(f"   Recommendation: {failure.recommendation_id}")
                print(f"   User: {failure.user_id}")
                print(f"   Details: {failure.details}")
                print(f"   Timestamp: {failure.timestamp}")
                if failure.missing_elements:
                    print(f"   Missing: {', '.join(failure.missing_elements)}")
                print()

            if len(failures) > 10:
                print(f"   ... and {len(failures) - 10} more {severity} violations")
                print()

    print()


def determine_exit_code(metrics, fail_on_critical: bool, fail_on_any: bool) -> int:
    """
    Determine exit code based on compliance results.

    Exit codes:
        0: Fully compliant (100% across all guardrails)
        1: Warnings (some failures but no critical violations)
        2: Critical violations detected
        3: Error during evaluation

    Args:
        metrics: AuditabilityMetrics
        fail_on_critical: Exit with code 2 if critical violations found
        fail_on_any: Exit with code 1 if any compliance failures found

    Returns:
        Exit code (0, 1, or 2)
    """
    # Check for critical violations
    if metrics.critical_issues_count > 0:
        if fail_on_critical:
            return 2
        return 1

    # Check for any compliance failures
    if len(metrics.compliance_failures) > 0:
        if fail_on_any:
            return 1
        return 0

    # Check if all metrics are at 100%
    if (
        metrics.consent_compliance_rate == 100.0 and
        metrics.eligibility_compliance_rate == 100.0 and
        metrics.tone_compliance_rate == 100.0 and
        metrics.disclaimer_presence_rate == 100.0 and
        metrics.decision_trace_completeness == 100.0
    ):
        return 0

    # Some metrics below 100% but no explicit failures
    return 0 if not fail_on_any else 1


if __name__ == "__main__":
    main()
