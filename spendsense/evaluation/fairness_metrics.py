"""
Fairness and Bias Analysis for SpendSense Recommendations

This module analyzes recommendation fairness across demographic groups
to detect potential bias in persona assignment and recommendations.

Implements standard fairness metrics:
- Demographic Parity Ratio (threshold: >= 0.8)
- Equal Opportunity Difference (threshold: <= 0.1)
- Statistical Significance Testing (chi-square)
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
from sqlalchemy import create_engine, text


# Personas considered "positive outcomes" (constructive/empowering)
POSITIVE_PERSONAS = ["savings_builder", "cash_flow_optimizer"]

# Personas considered "negative outcomes" (crisis/high-risk indicators)
NEGATIVE_PERSONAS = ["high_utilization", "debt_overwhelmed"]

# Known demographic attributes to check for
DEMOGRAPHIC_ATTRIBUTES = [
    "age_group",
    "income_bracket",
    "gender",
    "location",
    "region",
    "ethnicity",
    "education_level",
]


@dataclass
class FairnessMetrics:
    """Fairness analysis results for recommendation system."""

    demographic_parity_ratio: Optional[float] = None
    equal_opportunity_difference: Optional[float] = None
    persona_distribution_by_group: Dict[str, Dict[str, int]] = field(default_factory=dict)
    recommendation_distribution_by_group: Dict[str, Dict[str, int]] = field(default_factory=dict)
    statistical_significance: Dict[str, float] = field(default_factory=dict)
    bias_indicators: List[Dict[str, Any]] = field(default_factory=list)
    fairness_assessment: str = "UNKNOWN"
    limitations: List[str] = field(default_factory=list)
    mitigation_recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    demographic_attributes_available: Dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def save_json(self, output_path: Path) -> None:
        """Save metrics to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


def check_demographic_attributes(db_path: str) -> Dict[str, bool]:
    """
    Check which demographic attributes are available in the database.

    Args:
        db_path: Path to SQLite database

    Returns:
        Dictionary mapping attribute names to availability (True/False)
    """
    engine = create_engine(f"sqlite:///{db_path}")

    # Check database schema
    available = {}

    with engine.connect() as conn:
        # Get column names from users table
        result = conn.execute(text("PRAGMA table_info(users)"))
        columns = {row[1] for row in result}  # row[1] is column name

        # Check for each demographic attribute
        for attr in DEMOGRAPHIC_ATTRIBUTES:
            available[attr] = attr in columns

    return available


def load_user_data(db_path: str, demographic_attr: Optional[str] = None) -> pd.DataFrame:
    """
    Load user data from database.

    Args:
        db_path: Path to SQLite database
        demographic_attr: Optional demographic attribute to filter by

    Returns:
        DataFrame with user data
    """
    engine = create_engine(f"sqlite:///{db_path}")

    query = "SELECT * FROM users"
    df = pd.read_sql(query, engine)

    # Parse JSON characteristics if present
    if 'characteristics' in df.columns:
        df['characteristics'] = df['characteristics'].apply(
            lambda x: json.loads(x) if pd.notna(x) else {}
        )

    return df


def calculate_persona_distribution_by_group(
    users_df: pd.DataFrame,
    demographic_attr: str
) -> Dict[str, Dict[str, int]]:
    """
    Calculate persona distribution for each demographic group.

    Args:
        users_df: DataFrame with user data including demographic attribute
        demographic_attr: Name of demographic attribute to group by

    Returns:
        Nested dict: {demographic_group: {persona: count}}
    """
    if demographic_attr not in users_df.columns:
        return {}

    # Group by demographic attribute and persona
    grouped = users_df.groupby([demographic_attr, 'persona']).size()

    # Convert to nested dictionary
    distribution = {}
    for (group, persona), count in grouped.items():
        if group not in distribution:
            distribution[group] = {}
        distribution[group][persona] = int(count)

    return distribution


def calculate_recommendation_distribution_by_group(
    users_df: pd.DataFrame,
    recommendations_df: pd.DataFrame,
    demographic_attr: str
) -> Dict[str, Dict[str, int]]:
    """
    Calculate recommendation distribution for each demographic group.

    Args:
        users_df: DataFrame with user data including demographic attribute
        recommendations_df: DataFrame with recommendations
        demographic_attr: Name of demographic attribute to group by

    Returns:
        Nested dict: {demographic_group: {recommendation_type: count}}
    """
    if demographic_attr not in users_df.columns:
        return {}

    # Merge users with recommendations
    merged = recommendations_df.merge(
        users_df[['user_id', demographic_attr]],
        on='user_id',
        how='left'
    )

    # Group by demographic and recommendation type
    if 'recommendation_type' in merged.columns:
        grouped = merged.groupby([demographic_attr, 'recommendation_type']).size()
    elif 'type' in merged.columns:
        grouped = merged.groupby([demographic_attr, 'type']).size()
    else:
        return {}

    # Convert to nested dictionary
    distribution = {}
    for (group, rec_type), count in grouped.items():
        if group not in distribution:
            distribution[group] = {}
        distribution[group][rec_type] = int(count)

    return distribution


def calculate_demographic_parity(
    users_df: pd.DataFrame,
    demographic_attr: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate demographic parity ratio.

    Demographic parity: P(Y=1|A=a) ≈ P(Y=1|A=b)
    where Y=1 is a "positive outcome" (constructive persona)

    Args:
        users_df: DataFrame with user data
        demographic_attr: Name of demographic attribute to group by

    Returns:
        Tuple of (parity_ratio, group_rates)
        - parity_ratio: min_rate / max_rate (1.0 = perfect parity)
        - group_rates: {demographic_group: positive_outcome_rate}
    """
    if demographic_attr not in users_df.columns:
        return 1.0, {}

    # Calculate positive outcome rate for each group
    group_rates = {}

    for group in users_df[demographic_attr].unique():
        if pd.isna(group):
            continue

        group_users = users_df[users_df[demographic_attr] == group]
        positive_count = group_users[
            group_users['persona'].isin(POSITIVE_PERSONAS)
        ].shape[0]
        total_count = group_users.shape[0]

        if total_count > 0:
            group_rates[str(group)] = positive_count / total_count

    # Calculate parity ratio (min / max)
    if not group_rates:
        return 1.0, {}

    rates = list(group_rates.values())
    min_rate = min(rates)
    max_rate = max(rates)

    parity_ratio = min_rate / max_rate if max_rate > 0 else 1.0

    return parity_ratio, group_rates


def calculate_equal_opportunity(
    users_df: pd.DataFrame,
    demographic_attr: str
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate equal opportunity difference.

    Equal opportunity: P(Ŷ=1|Y=1,A=a) ≈ P(Ŷ=1|Y=1,A=b)
    True positive rate parity across groups.

    For SpendSense: Among "qualified users" (high income, stable income),
    check if they receive positive personas regardless of demographic.

    Args:
        users_df: DataFrame with user data
        demographic_attr: Name of demographic attribute to group by

    Returns:
        Tuple of (max_difference, group_tpr)
        - max_difference: max absolute difference in TPR across groups
        - group_tpr: {demographic_group: true_positive_rate}
    """
    if demographic_attr not in users_df.columns:
        return 0.0, {}

    # Define "qualified users" - those who should get positive personas
    # Using income threshold as qualification criteria
    income_threshold = users_df['annual_income'].median()
    qualified_users = users_df[users_df['annual_income'] >= income_threshold]

    # Calculate true positive rate for each group
    group_tpr = {}

    for group in qualified_users[demographic_attr].unique():
        if pd.isna(group):
            continue

        group_qualified = qualified_users[qualified_users[demographic_attr] == group]
        true_positives = group_qualified[
            group_qualified['persona'].isin(POSITIVE_PERSONAS)
        ].shape[0]
        total_qualified = group_qualified.shape[0]

        if total_qualified > 0:
            group_tpr[str(group)] = true_positives / total_qualified

    # Calculate max difference
    if not group_tpr:
        return 0.0, {}

    rates = list(group_tpr.values())
    max_difference = max(rates) - min(rates)

    return max_difference, group_tpr


def test_statistical_significance(
    distribution: Dict[str, Dict[str, int]]
) -> Tuple[float, float]:
    """
    Test statistical significance of distribution differences using chi-square test.

    H0: Persona distribution is independent of demographic group

    Args:
        distribution: Nested dict {demographic_group: {category: count}}

    Returns:
        Tuple of (chi2_statistic, p_value)
    """
    if not distribution or len(distribution) < 2:
        return 0.0, 1.0

    # Convert to contingency table
    df = pd.DataFrame(distribution).fillna(0).T

    # Need at least 2x2 table
    if df.shape[0] < 2 or df.shape[1] < 2:
        return 0.0, 1.0

    # Perform chi-square test
    chi2, p_value, dof, expected = chi2_contingency(df)

    return float(chi2), float(p_value)


def flag_bias_indicators(
    parity_ratio: Optional[float],
    equal_opp_diff: Optional[float],
    significance_results: Dict[str, float],
    persona_distribution: Dict[str, Dict[str, int]]
) -> List[Dict[str, Any]]:
    """
    Flag potential bias indicators based on thresholds.

    Thresholds:
    - Demographic parity ratio < 0.8: WARNING
    - Equal opportunity difference > 0.1: WARNING
    - Statistical significance p < 0.05 + large disparities: WARNING

    Args:
        parity_ratio: Demographic parity ratio (or None if N/A)
        equal_opp_diff: Equal opportunity difference (or None if N/A)
        significance_results: {demographic_attr: p_value}
        persona_distribution: Distribution for context

    Returns:
        List of bias indicator dictionaries
    """
    indicators = []

    # Check demographic parity
    if parity_ratio is not None and parity_ratio < 0.8:
        severity = "high" if parity_ratio < 0.6 else "medium"
        indicators.append({
            "bias_type": "demographic_parity",
            "severity": severity,
            "description": f"Demographic parity ratio ({parity_ratio:.3f}) below threshold (0.8)",
            "evidence": {"parity_ratio": parity_ratio, "threshold": 0.8},
            "affected_groups": "varies"
        })

    # Check equal opportunity
    if equal_opp_diff is not None and equal_opp_diff > 0.1:
        severity = "high" if equal_opp_diff > 0.2 else "medium"
        indicators.append({
            "bias_type": "equal_opportunity",
            "severity": severity,
            "description": f"Equal opportunity difference ({equal_opp_diff:.3f}) exceeds threshold (0.1)",
            "evidence": {"difference": equal_opp_diff, "threshold": 0.1},
            "affected_groups": "varies"
        })

    # Check statistical significance with large disparities
    for attr, p_value in significance_results.items():
        if p_value < 0.05:
            # Check if there are also large disparities in the distribution
            if persona_distribution:
                indicators.append({
                    "bias_type": "representation_disparity",
                    "severity": "low",
                    "description": f"Statistically significant distribution differences for {attr} (p={p_value:.4f})",
                    "evidence": {"p_value": p_value, "attribute": attr},
                    "affected_groups": attr
                })

    # Sort by severity
    severity_order = {"high": 0, "medium": 1, "low": 2}
    indicators.sort(key=lambda x: severity_order.get(x["severity"], 99))

    return indicators


def generate_limitations() -> List[str]:
    """
    Generate list of analysis limitations and constraints.

    Returns:
        List of limitation descriptions
    """
    return [
        "Synthetic data may not reflect real-world demographic distributions",
        "Limited demographic attributes available in current dataset",
        "Small sample size may limit statistical power",
        "Persona assignment is deterministic based on financial signals, not demographic attributes",
        "Fairness analysis cannot detect bias in upstream data generation processes",
        "Chi-square test assumes independence and sufficient sample size per cell",
        "Analysis limited to available demographic data; unmeasured attributes not analyzed",
        "Temporal bias (changes over time) not assessed in this snapshot analysis"
    ]


def generate_mitigation_recommendations(
    has_bias: bool,
    bias_indicators: List[Dict[str, Any]]
) -> List[str]:
    """
    Generate mitigation recommendations based on findings.

    Args:
        has_bias: Whether bias was detected
        bias_indicators: List of detected bias indicators

    Returns:
        List of actionable recommendations
    """
    if has_bias:
        recommendations = [
            "Review persona assignment criteria for unintended demographic correlations",
            "Audit behavioral signals for demographic proxies (e.g., income signals correlating with protected attributes)",
            "Consider fairness constraints in persona prioritization logic",
            "Collect more diverse synthetic user data to improve demographic representation",
            "Conduct regular fairness audits with real data when available",
        ]

        # Add specific recommendations based on indicator types
        indicator_types = {ind["bias_type"] for ind in bias_indicators}

        if "demographic_parity" in indicator_types:
            recommendations.append(
                "Investigate why certain demographic groups have lower rates of positive outcomes"
            )

        if "equal_opportunity" in indicator_types:
            recommendations.append(
                "Ensure qualified users receive appropriate personas regardless of demographics"
            )

        return recommendations
    else:
        return [
            "Continue monitoring fairness metrics with each evaluation run",
            "Expand demographic attributes in synthetic data for deeper analysis",
            "Document fairness as a design constraint in future feature development",
            "Establish fairness thresholds as acceptance criteria for new persona logic",
            "Plan for fairness evaluation with real user data post-launch"
        ]


def assess_overall_fairness(
    parity_ratio: Optional[float],
    equal_opp_diff: Optional[float],
    bias_indicators: List[Dict[str, Any]]
) -> str:
    """
    Assess overall fairness status.

    Returns:
        "PASS", "CONCERN", or "FAIL"
    """
    if not bias_indicators:
        return "PASS"

    # Check severity of indicators
    high_severity = any(ind["severity"] == "high" for ind in bias_indicators)
    medium_severity = any(ind["severity"] == "medium" for ind in bias_indicators)

    if high_severity:
        return "FAIL"
    elif medium_severity or len(bias_indicators) >= 2:
        return "CONCERN"
    else:
        return "PASS"


def analyze_fairness(
    db_path: str,
    demographic_attr: Optional[str] = None,
    recommendations_data: Optional[pd.DataFrame] = None
) -> FairnessMetrics:
    """
    Perform comprehensive fairness analysis.

    Args:
        db_path: Path to SQLite database
        demographic_attr: Specific demographic attribute to analyze (or None for auto-detect)
        recommendations_data: Optional DataFrame with recommendation data

    Returns:
        FairnessMetrics object with complete analysis
    """
    metrics = FairnessMetrics()

    # Step 1: Check for demographic attributes
    available_attrs = check_demographic_attributes(db_path)
    metrics.demographic_attributes_available = available_attrs

    # Find available attributes
    available = [attr for attr, exists in available_attrs.items() if exists]

    if not available:
        # No demographic data - document limitation and return early
        metrics.limitations = generate_limitations()
        metrics.limitations.insert(0, "No demographic attributes found in dataset - fairness analysis not possible")
        metrics.fairness_assessment = "N/A"
        metrics.mitigation_recommendations = [
            "Add demographic attributes to synthetic data generation",
            "Design demographic data collection strategy for production system",
            "Ensure demographic data collection follows privacy regulations"
        ]
        return metrics

    # Step 2: Load user data
    users_df = load_user_data(db_path, demographic_attr)

    # Use first available attribute if not specified
    if demographic_attr is None:
        demographic_attr = available[0]

    if demographic_attr not in users_df.columns:
        metrics.limitations = generate_limitations()
        metrics.limitations.insert(0, f"Demographic attribute '{demographic_attr}' not found in dataset")
        metrics.fairness_assessment = "N/A"
        return metrics

    # Step 3: Analyze persona distribution
    persona_dist = calculate_persona_distribution_by_group(users_df, demographic_attr)
    metrics.persona_distribution_by_group = persona_dist

    # Step 4: Analyze recommendation distribution (if data provided)
    if recommendations_data is not None:
        rec_dist = calculate_recommendation_distribution_by_group(
            users_df, recommendations_data, demographic_attr
        )
        metrics.recommendation_distribution_by_group = rec_dist

    # Step 5: Calculate demographic parity
    parity_ratio, group_rates = calculate_demographic_parity(users_df, demographic_attr)
    metrics.demographic_parity_ratio = parity_ratio

    # Step 6: Calculate equal opportunity
    equal_opp_diff, group_tpr = calculate_equal_opportunity(users_df, demographic_attr)
    metrics.equal_opportunity_difference = equal_opp_diff

    # Step 7: Test statistical significance
    if persona_dist:
        chi2, p_value = test_statistical_significance(persona_dist)
        metrics.statistical_significance = {
            demographic_attr: p_value,
            "chi2_statistic": chi2
        }

    # Step 8: Flag bias indicators
    metrics.bias_indicators = flag_bias_indicators(
        parity_ratio,
        equal_opp_diff,
        metrics.statistical_significance,
        persona_dist
    )

    # Step 9: Document limitations
    metrics.limitations = generate_limitations()

    # Step 10: Generate mitigation recommendations
    has_bias = len(metrics.bias_indicators) > 0
    metrics.mitigation_recommendations = generate_mitigation_recommendations(
        has_bias, metrics.bias_indicators
    )

    # Overall assessment
    metrics.fairness_assessment = assess_overall_fairness(
        parity_ratio, equal_opp_diff, metrics.bias_indicators
    )

    return metrics
