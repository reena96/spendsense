"""
Unit tests for fairness metrics calculation and bias detection.

Tests cover:
1. Demographic attribute detection
2. Demographic parity calculation
3. Equal opportunity calculation
4. Statistical significance testing
5. Bias indicator flagging
6. Edge cases (no data, perfect parity, severe bias)
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import sqlite3
from datetime import datetime
from unittest.mock import patch, MagicMock

from spendsense.evaluation.fairness_metrics import (
    check_demographic_attributes,
    calculate_persona_distribution_by_group,
    calculate_demographic_parity,
    calculate_equal_opportunity,
    test_statistical_significance as calculate_statistical_significance,
    flag_bias_indicators,
    generate_limitations,
    generate_mitigation_recommendations,
    assess_overall_fairness,
    analyze_fairness,
    FairnessMetrics,
    POSITIVE_PERSONAS,
    NEGATIVE_PERSONAS
)


@pytest.fixture
def temp_db_with_demographics():
    """Create temporary database with demographic attributes."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table with demographic attributes
    cursor.execute("""
        CREATE TABLE users (
            user_id VARCHAR PRIMARY KEY,
            name VARCHAR,
            persona VARCHAR,
            annual_income FLOAT,
            age_group VARCHAR,
            income_bracket VARCHAR,
            characteristics JSON
        )
    """)

    # Insert test data with known distributions
    test_users = [
        ("user_1", "Alice", "savings_builder", 75000, "25-34", "50-75K", "{}"),
        ("user_2", "Bob", "savings_builder", 80000, "25-34", "75-100K", "{}"),
        ("user_3", "Carol", "high_utilization", 45000, "35-44", "30-50K", "{}"),
        ("user_4", "Dave", "high_utilization", 40000, "35-44", "30-50K", "{}"),
        ("user_5", "Eve", "cash_flow_optimizer", 90000, "45-54", "75-100K", "{}"),
        ("user_6", "Frank", "debt_overwhelmed", 35000, "45-54", "30-50K", "{}"),
    ]

    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)",
        test_users
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def temp_db_without_demographics():
    """Create temporary database without demographic attributes."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table WITHOUT demographic attributes
    cursor.execute("""
        CREATE TABLE users (
            user_id VARCHAR PRIMARY KEY,
            name VARCHAR,
            persona VARCHAR,
            annual_income FLOAT,
            characteristics JSON
        )
    """)

    # Insert test data
    test_users = [
        ("user_1", "Alice", "savings_builder", 75000, "{}"),
        ("user_2", "Bob", "high_utilization", 45000, "{}"),
    ]

    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
        test_users
    )

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup
    Path(db_path).unlink()


@pytest.fixture
def sample_users_df():
    """Sample user DataFrame for testing."""
    return pd.DataFrame({
        'user_id': ['user_1', 'user_2', 'user_3', 'user_4', 'user_5', 'user_6'],
        'persona': ['savings_builder', 'savings_builder', 'high_utilization',
                   'high_utilization', 'cash_flow_optimizer', 'debt_overwhelmed'],
        'annual_income': [75000, 80000, 45000, 40000, 90000, 35000],
        'age_group': ['25-34', '25-34', '35-44', '35-44', '45-54', '45-54'],
        'income_bracket': ['50-75K', '75-100K', '30-50K', '30-50K', '75-100K', '30-50K']
    })


# Test 1: Check demographic attributes - with demographics
def test_check_demographic_attributes_with_demographics(temp_db_with_demographics):
    """Test demographic attribute detection when attributes are present."""
    result = check_demographic_attributes(temp_db_with_demographics)

    assert isinstance(result, dict)
    assert result['age_group'] is True
    assert result['income_bracket'] is True
    assert result['gender'] is False  # Not in our test schema


# Test 2: Check demographic attributes - without demographics
def test_check_demographic_attributes_without_demographics(temp_db_without_demographics):
    """Test demographic attribute detection when attributes are absent."""
    result = check_demographic_attributes(temp_db_without_demographics)

    assert isinstance(result, dict)
    assert result['age_group'] is False
    assert result['income_bracket'] is False
    assert all(not v for v in result.values())  # All should be False


# Test 3: Persona distribution calculation
def test_calculate_persona_distribution_by_group(sample_users_df):
    """Test persona distribution analysis by demographic group."""
    distribution = calculate_persona_distribution_by_group(
        sample_users_df, 'age_group'
    )

    assert isinstance(distribution, dict)
    assert '25-34' in distribution
    assert '35-44' in distribution
    assert '45-54' in distribution

    # Check specific counts
    assert distribution['25-34']['savings_builder'] == 2
    assert distribution['35-44']['high_utilization'] == 2
    assert distribution['45-54']['cash_flow_optimizer'] == 1
    assert distribution['45-54']['debt_overwhelmed'] == 1


# Test 4: Demographic parity - perfect parity
def test_calculate_demographic_parity_perfect():
    """Test demographic parity calculation with perfect parity (ratio = 1.0)."""
    # Create perfectly balanced data
    df = pd.DataFrame({
        'user_id': ['u1', 'u2', 'u3', 'u4'],
        'persona': ['savings_builder', 'high_utilization', 'savings_builder', 'high_utilization'],
        'age_group': ['young', 'young', 'old', 'old'],
        'annual_income': [50000, 50000, 50000, 50000]
    })

    parity_ratio, group_rates = calculate_demographic_parity(df, 'age_group')

    assert parity_ratio == 1.0  # Perfect parity
    assert group_rates['young'] == 0.5
    assert group_rates['old'] == 0.5


# Test 5: Demographic parity - disparity detected
def test_calculate_demographic_parity_disparity(sample_users_df):
    """Test demographic parity calculation with disparity."""
    parity_ratio, group_rates = calculate_demographic_parity(
        sample_users_df, 'age_group'
    )

    assert 0 <= parity_ratio <= 1.0
    assert len(group_rates) == 3  # Three age groups

    # Group 25-34: 2 positive (savings_builder) out of 2 = 1.0
    # Group 35-44: 0 positive out of 2 = 0.0
    # Group 45-54: 1 positive (cash_flow_optimizer) out of 2 = 0.5
    assert group_rates['25-34'] == 1.0
    assert group_rates['35-44'] == 0.0
    assert group_rates['45-54'] == 0.5


# Test 6: Equal opportunity calculation
def test_calculate_equal_opportunity(sample_users_df):
    """Test equal opportunity difference calculation."""
    equal_opp_diff, group_tpr = calculate_equal_opportunity(
        sample_users_df, 'age_group'
    )

    assert 0 <= equal_opp_diff <= 1.0
    assert isinstance(group_tpr, dict)

    # All groups should have TPR calculated for qualified users (income >= median)
    # Median income = 60000, so qualified: user_1, user_2, user_5
    # This tests true positive rate for qualified users


# Test 7: Statistical significance testing
def test_statistical_significance():
    """Test chi-square statistical significance calculation."""
    # Create distribution with clear differences
    distribution = {
        'group_A': {'persona_1': 50, 'persona_2': 10},
        'group_B': {'persona_1': 10, 'persona_2': 50}
    }

    chi2, p_value = calculate_statistical_significance(distribution)

    assert chi2 > 0
    assert 0 <= p_value <= 1.0
    assert p_value < 0.05  # Should be significant


# Test 8: Statistical significance - no difference
def test_statistical_significance_no_difference():
    """Test chi-square with identical distributions (should not be significant)."""
    distribution = {
        'group_A': {'persona_1': 25, 'persona_2': 25},
        'group_B': {'persona_1': 25, 'persona_2': 25}
    }

    chi2, p_value = calculate_statistical_significance(distribution)

    assert p_value > 0.05  # Should not be significant


# Test 9: Bias indicator flagging - severe disparity
def test_flag_bias_indicators_severe():
    """Test bias indicator flagging with severe disparities."""
    parity_ratio = 0.4  # Severe disparity
    equal_opp_diff = 0.3  # Severe disparity
    significance = {'age_group': 0.001}  # Significant
    distribution = {'group1': {'persona1': 10}}

    indicators = flag_bias_indicators(
        parity_ratio, equal_opp_diff, significance, distribution
    )

    assert len(indicators) >= 2  # Should flag both parity and equal opportunity
    assert any(ind['bias_type'] == 'demographic_parity' for ind in indicators)
    assert any(ind['bias_type'] == 'equal_opportunity' for ind in indicators)
    assert any(ind['severity'] == 'high' for ind in indicators)


# Test 10: Bias indicator flagging - no bias
def test_flag_bias_indicators_no_bias():
    """Test bias indicator flagging when no bias exists."""
    parity_ratio = 0.95  # Good parity
    equal_opp_diff = 0.05  # Good equal opportunity
    significance = {'age_group': 0.5}  # Not significant
    distribution = {}

    indicators = flag_bias_indicators(
        parity_ratio, equal_opp_diff, significance, distribution
    )

    assert len(indicators) == 0  # No bias indicators


# Test 11: Edge case - empty dataset
def test_persona_distribution_empty_dataset():
    """Test persona distribution with empty dataset."""
    df = pd.DataFrame(columns=['user_id', 'persona', 'age_group'])

    distribution = calculate_persona_distribution_by_group(df, 'age_group')

    assert distribution == {}


# Test 12: Edge case - single demographic group
def test_demographic_parity_single_group():
    """Test demographic parity with only one demographic group."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2', 'u3'],
        'persona': ['savings_builder', 'high_utilization', 'savings_builder'],
        'age_group': ['young', 'young', 'young'],
        'annual_income': [50000, 50000, 50000]
    })

    parity_ratio, group_rates = calculate_demographic_parity(df, 'age_group')

    assert parity_ratio == 1.0  # Only one group, so perfect "parity"
    assert len(group_rates) == 1


# Test 13: Generate limitations
def test_generate_limitations():
    """Test limitation generation."""
    limitations = generate_limitations()

    assert isinstance(limitations, list)
    assert len(limitations) > 0
    assert any('synthetic' in lim.lower() for lim in limitations)
    assert any('sample size' in lim.lower() for lim in limitations)


# Test 14: Generate mitigation recommendations - with bias
def test_generate_mitigation_recommendations_with_bias():
    """Test mitigation recommendation generation when bias is detected."""
    bias_indicators = [
        {'bias_type': 'demographic_parity', 'severity': 'high'}
    ]

    recommendations = generate_mitigation_recommendations(
        has_bias=True, bias_indicators=bias_indicators
    )

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert any('review' in rec.lower() or 'audit' in rec.lower() for rec in recommendations)


# Test 15: Generate mitigation recommendations - without bias
def test_generate_mitigation_recommendations_no_bias():
    """Test mitigation recommendation generation when no bias is detected."""
    recommendations = generate_mitigation_recommendations(
        has_bias=False, bias_indicators=[]
    )

    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert any('monitor' in rec.lower() for rec in recommendations)


# Test 16: Overall fairness assessment
def test_assess_overall_fairness_pass():
    """Test overall fairness assessment - PASS case."""
    assessment = assess_overall_fairness(0.95, 0.03, [])

    assert assessment == "PASS"


def test_assess_overall_fairness_concern():
    """Test overall fairness assessment - CONCERN case."""
    indicators = [
        {'severity': 'medium'},
        {'severity': 'low'}
    ]
    assessment = assess_overall_fairness(0.75, 0.08, indicators)

    assert assessment == "CONCERN"


def test_assess_overall_fairness_fail():
    """Test overall fairness assessment - FAIL case."""
    indicators = [{'severity': 'high'}]
    assessment = assess_overall_fairness(0.4, 0.3, indicators)

    assert assessment == "FAIL"


# Test 17: Full analysis with demographics
def test_analyze_fairness_with_demographics(temp_db_with_demographics):
    """Test full fairness analysis with demographic data."""
    metrics = analyze_fairness(temp_db_with_demographics)

    assert isinstance(metrics, FairnessMetrics)
    assert metrics.demographic_parity_ratio is not None
    assert metrics.equal_opportunity_difference is not None
    assert len(metrics.persona_distribution_by_group) > 0
    assert len(metrics.limitations) > 0
    assert len(metrics.mitigation_recommendations) > 0
    assert metrics.fairness_assessment in ["PASS", "CONCERN", "FAIL"]


# Test 18: Full analysis without demographics
def test_analyze_fairness_without_demographics(temp_db_without_demographics):
    """Test full fairness analysis without demographic data (graceful degradation)."""
    metrics = analyze_fairness(temp_db_without_demographics)

    assert isinstance(metrics, FairnessMetrics)
    assert metrics.demographic_parity_ratio is None
    assert metrics.equal_opportunity_difference is None
    assert len(metrics.persona_distribution_by_group) == 0
    assert len(metrics.limitations) > 0
    assert "No demographic attributes found" in metrics.limitations[0]
    assert metrics.fairness_assessment == "N/A"


# Test 19: FairnessMetrics to_dict
def test_fairness_metrics_to_dict():
    """Test FairnessMetrics serialization to dictionary."""
    metrics = FairnessMetrics(
        demographic_parity_ratio=0.85,
        equal_opportunity_difference=0.08,
        fairness_assessment="PASS",
        timestamp=datetime(2025, 1, 1, 12, 0, 0)
    )

    data = metrics.to_dict()

    assert isinstance(data, dict)
    assert data['demographic_parity_ratio'] == 0.85
    assert data['equal_opportunity_difference'] == 0.08
    assert data['fairness_assessment'] == "PASS"
    assert '2025-01-01' in data['timestamp']


# Test 20: FairnessMetrics save JSON
def test_fairness_metrics_save_json(tmp_path):
    """Test FairnessMetrics JSON saving."""
    metrics = FairnessMetrics(
        demographic_parity_ratio=0.85,
        fairness_assessment="PASS"
    )

    output_path = tmp_path / "test_metrics.json"
    metrics.save_json(output_path)

    assert output_path.exists()

    # Verify JSON can be read back
    import json
    with open(output_path) as f:
        data = json.load(f)

    assert data['demographic_parity_ratio'] == 0.85
    assert data['fairness_assessment'] == "PASS"


# Test 21: Missing demographic attribute in DataFrame
def test_persona_distribution_missing_attribute():
    """Test persona distribution when demographic attribute doesn't exist."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2'],
        'persona': ['savings_builder', 'high_utilization']
        # Missing 'age_group' column
    })

    distribution = calculate_persona_distribution_by_group(df, 'age_group')

    assert distribution == {}


# Test 22: Edge case - all users have same persona
def test_demographic_parity_same_persona():
    """Test demographic parity when all users have the same persona."""
    df = pd.DataFrame({
        'user_id': ['u1', 'u2', 'u3', 'u4'],
        'persona': ['savings_builder'] * 4,
        'age_group': ['young', 'young', 'old', 'old'],
        'annual_income': [50000] * 4
    })

    parity_ratio, group_rates = calculate_demographic_parity(df, 'age_group')

    assert parity_ratio == 1.0  # Perfect parity (both groups 100%)
    assert group_rates['young'] == 1.0
    assert group_rates['old'] == 1.0
