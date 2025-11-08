"""
Fairness Reporting and Visualization

Generates reports, visualizations, and charts for fairness analysis results.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import pandas as pd
import numpy as np

from spendsense.evaluation.fairness_metrics import FairnessMetrics


def create_persona_distribution_chart(
    distribution: Dict[str, Dict[str, int]],
    output_path: Path,
    demographic_attr: str
) -> None:
    """
    Create stacked bar chart of persona distribution by demographic group.

    Args:
        distribution: {demographic_group: {persona: count}}
        output_path: Path to save PNG file
        demographic_attr: Name of demographic attribute
    """
    if not distribution:
        return

    # Convert to DataFrame for plotting
    df = pd.DataFrame(distribution).fillna(0).T

    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 6))

    df.plot(kind='bar', stacked=True, ax=ax, colormap='tab10')

    ax.set_title(f'Persona Distribution by {demographic_attr}', fontsize=14, fontweight='bold')
    ax.set_xlabel(demographic_attr.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel('Number of Users', fontsize=12)
    ax.legend(title='Persona', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', alpha=0.3)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_demographic_parity_chart(
    group_rates: Dict[str, float],
    parity_ratio: float,
    output_path: Path,
    demographic_attr: str
) -> None:
    """
    Create bar chart showing positive outcome rates per demographic group.

    Args:
        group_rates: {demographic_group: positive_outcome_rate}
        parity_ratio: Overall parity ratio
        output_path: Path to save PNG file
        demographic_attr: Name of demographic attribute
    """
    if not group_rates:
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    groups = list(group_rates.keys())
    rates = list(group_rates.values())

    bars = ax.bar(groups, rates, color='steelblue', alpha=0.7)

    # Add threshold line
    ax.axhline(y=0.8, color='red', linestyle='--', label='Parity Threshold (0.8)', alpha=0.7)

    # Color bars based on threshold
    for i, bar in enumerate(bars):
        if rates[i] < 0.8:
            bar.set_color('coral')

    ax.set_title(f'Demographic Parity Analysis\nParity Ratio: {parity_ratio:.3f}',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel(demographic_attr.replace('_', ' ').title(), fontsize=12)
    ax.set_ylabel('Positive Outcome Rate', fontsize=12)
    ax.set_ylim(0, 1.0)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_recommendation_heatmap(
    distribution: Dict[str, Dict[str, int]],
    output_path: Path,
    demographic_attr: str
) -> None:
    """
    Create heatmap of recommendation types by demographic group.

    Args:
        distribution: {demographic_group: {recommendation_type: count}}
        output_path: Path to save PNG file
        demographic_attr: Name of demographic attribute
    """
    if not distribution:
        return

    # Convert to DataFrame
    df = pd.DataFrame(distribution).fillna(0).T

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create heatmap
    im = ax.imshow(df.values, cmap='YlOrRd', aspect='auto')

    # Set ticks
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_xticklabels(df.columns)
    ax.set_yticklabels(df.index)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Recommendation Count", rotation=-90, va="bottom")

    # Add text annotations
    for i in range(len(df.index)):
        for j in range(len(df.columns)):
            text = ax.text(j, i, int(df.iloc[i, j]),
                          ha="center", va="center", color="black", fontsize=8)

    ax.set_title(f'Recommendation Distribution Heatmap\nby {demographic_attr}',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Recommendation Type', fontsize=12)
    ax.set_ylabel(demographic_attr.replace('_', ' ').title(), fontsize=12)

    plt.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_fairness_report(
    metrics: FairnessMetrics,
    output_path: Path,
    demographic_attr: Optional[str] = None
) -> None:
    """
    Generate comprehensive fairness report in Markdown format.

    Args:
        metrics: FairnessMetrics object with analysis results
        output_path: Path to save Markdown file
        demographic_attr: Name of demographic attribute analyzed
    """
    report_lines = [
        "# Fairness & Bias Analysis Report",
        "",
        f"**Generated:** {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"**Overall Assessment:** {metrics.fairness_assessment}",
        "",
    ]

    # Add demographic attributes status
    if metrics.demographic_attributes_available:
        available = [k for k, v in metrics.demographic_attributes_available.items() if v]
        if available:
            report_lines.extend([
                f"**Demographic Attributes Available:** {', '.join(available)}",
                ""
            ])
        else:
            report_lines.extend([
                "**Demographic Attributes Available:** None",
                "",
                "⚠️ **Note:** Fairness analysis requires demographic data. No demographic attributes found in dataset.",
                ""
            ])

    # Add key metrics
    if metrics.demographic_parity_ratio is not None:
        status = "✅ PASS" if metrics.demographic_parity_ratio >= 0.8 else "⚠️ FAIL"
        report_lines.extend([
            f"**Demographic Parity Ratio:** {metrics.demographic_parity_ratio:.3f} {status}",
            ""
        ])

    if metrics.equal_opportunity_difference is not None:
        status = "✅ PASS" if metrics.equal_opportunity_difference <= 0.1 else "⚠️ FAIL"
        report_lines.extend([
            f"**Equal Opportunity Difference:** {metrics.equal_opportunity_difference:.3f} {status}",
            ""
        ])

    # Bias indicators summary
    if metrics.bias_indicators:
        high = sum(1 for ind in metrics.bias_indicators if ind.get("severity") == "high")
        medium = sum(1 for ind in metrics.bias_indicators if ind.get("severity") == "medium")
        low = sum(1 for ind in metrics.bias_indicators if ind.get("severity") == "low")

        report_lines.extend([
            f"**Bias Indicators Found:** {len(metrics.bias_indicators)} total",
            f"  - High Severity: {high}",
            f"  - Medium Severity: {medium}",
            f"  - Low Severity: {low}",
            ""
        ])
    else:
        report_lines.extend([
            "**Bias Indicators Found:** None",
            ""
        ])

    report_lines.append("---\n")

    # Detailed Analysis Section
    report_lines.extend([
        "## Detailed Analysis",
        "",
        "### Demographic Parity Analysis",
        ""
    ])

    if metrics.demographic_parity_ratio is not None:
        report_lines.extend([
            f"Demographic parity measures whether positive outcomes (constructive personas like",
            f"Savings Builder or Cash Flow Optimizer) are distributed equally across demographic groups.",
            "",
            f"**Parity Ratio:** {metrics.demographic_parity_ratio:.3f}",
            f"- Threshold: ≥ 0.8 (closer to 1.0 is better)",
            f"- Interpretation: {'PASS - Fair distribution' if metrics.demographic_parity_ratio >= 0.8 else 'FAIL - Disparity detected'}",
            ""
        ])
    else:
        report_lines.extend([
            "⚠️ Demographic parity analysis not available - insufficient demographic data.",
            ""
        ])

    # Equal Opportunity Section
    report_lines.extend([
        "### Equal Opportunity Analysis",
        ""
    ])

    if metrics.equal_opportunity_difference is not None:
        report_lines.extend([
            f"Equal opportunity measures whether qualified users (high income, stable) receive",
            f"positive personas at similar rates across demographic groups.",
            "",
            f"**Max Difference:** {metrics.equal_opportunity_difference:.3f}",
            f"- Threshold: ≤ 0.1 (closer to 0.0 is better)",
            f"- Interpretation: {'PASS - Equal treatment' if metrics.equal_opportunity_difference <= 0.1 else 'FAIL - Unequal treatment detected'}",
            ""
        ])
    else:
        report_lines.extend([
            "⚠️ Equal opportunity analysis not available - insufficient demographic data.",
            ""
        ])

    # Statistical Significance
    if metrics.statistical_significance:
        report_lines.extend([
            "### Statistical Significance Testing",
            ""
        ])

        for attr, p_value in metrics.statistical_significance.items():
            if attr != "chi2_statistic":
                significance = "statistically significant" if p_value < 0.05 else "not statistically significant"
                report_lines.extend([
                    f"**{attr}:** p-value = {p_value:.4f} ({significance})",
                    ""
                ])

    # Bias Indicators
    if metrics.bias_indicators:
        report_lines.extend([
            "### Bias Indicators",
            "",
            "The following potential bias indicators were detected:",
            ""
        ])

        for i, indicator in enumerate(metrics.bias_indicators, 1):
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(indicator.get("severity", ""), "")
            report_lines.extend([
                f"#### {i}. {indicator.get('bias_type', 'Unknown').replace('_', ' ').title()} {severity_emoji}",
                "",
                f"**Severity:** {indicator.get('severity', 'unknown').upper()}",
                f"**Description:** {indicator.get('description', 'No description')}",
                f"**Evidence:** {indicator.get('evidence', {})}",
                ""
            ])

    # Limitations
    report_lines.extend([
        "---",
        "",
        "## Limitations & Constraints",
        "",
        "This analysis has the following limitations:",
        ""
    ])

    for limitation in metrics.limitations:
        report_lines.append(f"- {limitation}")

    report_lines.append("")

    # Mitigation Recommendations
    report_lines.extend([
        "---",
        "",
        "## Mitigation Recommendations",
        ""
    ])

    if metrics.mitigation_recommendations:
        for i, rec in enumerate(metrics.mitigation_recommendations, 1):
            report_lines.append(f"{i}. {rec}")
    else:
        report_lines.append("No specific recommendations at this time.")

    report_lines.extend([
        "",
        "---",
        "",
        "## Appendix: Methodology",
        "",
        "### Fairness Metrics",
        "",
        "**Demographic Parity:** P(Y=1|A=a) ≈ P(Y=1|A=b)",
        "- Y=1: Positive outcome (constructive persona assignment)",
        "- A: Demographic attribute",
        "- Threshold: Ratio ≥ 0.8",
        "",
        "**Equal Opportunity:** P(Ŷ=1|Y=1,A=a) ≈ P(Ŷ=1|Y=1,A=b)",
        "- True positive rate parity for qualified users",
        "- Threshold: Max difference ≤ 0.1",
        "",
        "**Statistical Significance:** Chi-square test",
        "- H0: Distribution independent of demographic group",
        "- Threshold: p < 0.05",
        ""
    ])

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write('\n'.join(report_lines))
