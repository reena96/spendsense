"""
Tests for persona matching engine.

Tests persona criteria evaluation, AND/OR logic, edge cases,
and integration with behavioral signals.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch
from dataclasses import dataclass

from spendsense.personas.matcher import (
    PersonaMatcher,
    PersonaMatch,
    ExtendedSignals
)
from spendsense.personas.registry import (
    load_persona_registry,
    clear_registry_cache
)


# Mock BehavioralSummary and related metrics for testing
@dataclass
class MockSubscriptionMetrics:
    subscription_count: int = 0
    subscription_share: float = 0.0


@dataclass
class MockCreditMetrics:
    aggregate_utilization: float = 0.0
    num_credit_cards: int = 0


@dataclass
class MockSavingsMetrics:
    emergency_fund_months: float = 0.0


@dataclass
class MockIncomeMetrics:
    median_pay_gap_days: float = 0.0
    num_income_transactions: int = 0


@dataclass
class MockBehavioralSummary:
    user_id: str
    generated_at: datetime
    reference_date: date
    subscriptions_30d: MockSubscriptionMetrics
    subscriptions_180d: MockSubscriptionMetrics
    credit_30d: MockCreditMetrics
    credit_180d: MockCreditMetrics
    savings_30d: MockSavingsMetrics
    savings_180d: MockSavingsMetrics
    income_30d: MockIncomeMetrics
    income_180d: MockIncomeMetrics


@pytest.fixture
def mock_db_path(tmp_path):
    """Create a mock database path (tests don't need real DB)."""
    db_file = tmp_path / "test.db"
    db_file.touch()
    return str(db_file)


@pytest.fixture
def matcher(mock_db_path):
    """Create PersonaMatcher with mocked database."""
    with patch('spendsense.personas.matcher.create_engine'):
        with patch('spendsense.personas.matcher.sessionmaker'):
            matcher = PersonaMatcher(mock_db_path)
            return matcher


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear registry cache before each test."""
    clear_registry_cache()
    yield
    clear_registry_cache()


class TestPersonaMatcher:
    """Test PersonaMatcher class."""

    def test_initialization(self, mock_db_path):
        """Test matcher initializes correctly."""
        with patch('spendsense.personas.matcher.create_engine'):
            with patch('spendsense.personas.matcher.sessionmaker'):
                matcher = PersonaMatcher(mock_db_path)
                assert matcher.db_path == mock_db_path
                assert matcher.registry is not None
                assert len(matcher.registry.personas) == 6

    def test_invalid_time_window_raises_error(self, matcher):
        """Test that invalid time_window parameter raises ValueError."""
        summary = MockBehavioralSummary(
            user_id="test_user",
            generated_at=datetime.now(),
            reference_date=date(2025, 11, 5),
            subscriptions_30d=MockSubscriptionMetrics(),
            subscriptions_180d=MockSubscriptionMetrics(),
            credit_30d=MockCreditMetrics(),
            credit_180d=MockCreditMetrics(),
            savings_30d=MockSavingsMetrics(),
            savings_180d=MockSavingsMetrics(),
            income_30d=MockIncomeMetrics(),
            income_180d=MockIncomeMetrics()
        )

        with pytest.raises(ValueError, match="Invalid time_window.*Must be '30d' or '180d'"):
            matcher.match_personas(summary, date(2025, 11, 5), time_window="invalid")

    def test_extract_signals_30d(self, matcher):
        """Test signal extraction from 30-day behavioral summary."""
        summary = MockBehavioralSummary(
            user_id="test_user",
            generated_at=datetime.now(),
            reference_date=date(2025, 11, 5),
            subscriptions_30d=MockSubscriptionMetrics(subscription_share=0.25),
            subscriptions_180d=MockSubscriptionMetrics(),
            credit_30d=MockCreditMetrics(aggregate_utilization=60.0),
            credit_180d=MockCreditMetrics(),
            savings_30d=MockSavingsMetrics(emergency_fund_months=2.5),
            savings_180d=MockSavingsMetrics(),
            income_30d=MockIncomeMetrics(median_pay_gap_days=50.0, num_income_transactions=1),
            income_180d=MockIncomeMetrics()
        )

        signals = matcher._extract_signals(summary, "30d", date(2025, 11, 5))

        assert signals.subscription_share_pct_30d == 0.25
        assert signals.credit_max_utilization_pct_30d == 60.0
        assert signals.savings_emergency_fund_months_30d == 2.5
        assert signals.income_median_pay_gap_days_30d == 50.0
        assert signals.income_payroll_count_30d == 1

    def test_extract_signals_180d(self, matcher):
        """Test signal extraction from 180-day behavioral summary."""
        summary = MockBehavioralSummary(
            user_id="test_user",
            generated_at=datetime.now(),
            reference_date=date(2025, 11, 5),
            subscriptions_30d=MockSubscriptionMetrics(),
            subscriptions_180d=MockSubscriptionMetrics(subscription_share=0.15),
            credit_30d=MockCreditMetrics(),
            credit_180d=MockCreditMetrics(aggregate_utilization=45.0),
            savings_30d=MockSavingsMetrics(),
            savings_180d=MockSavingsMetrics(emergency_fund_months=7.0),
            income_30d=MockIncomeMetrics(),
            income_180d=MockIncomeMetrics(median_pay_gap_days=30.0, num_income_transactions=5)
        )

        signals = matcher._extract_signals(summary, "180d", date(2025, 11, 5))

        assert signals.subscription_share_pct_180d == 0.15
        assert signals.credit_max_utilization_pct_180d == 45.0
        assert signals.savings_emergency_fund_months_180d == 7.0
        assert signals.income_median_pay_gap_days_180d == 30.0
        assert signals.income_payroll_count_180d == 5


class TestConditionEvaluation:
    """Test individual condition evaluation."""

    def test_compare_gte_true(self, matcher):
        """Test >= operator returns True when condition met."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare(60.0, ConditionOperator.GTE, 50.0)
        assert result is True

    def test_compare_gte_false(self, matcher):
        """Test >= operator returns False when condition not met."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare(40.0, ConditionOperator.GTE, 50.0)
        assert result is False

    def test_compare_gte_exact(self, matcher):
        """Test >= operator returns True for exact match."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare(50.0, ConditionOperator.GTE, 50.0)
        assert result is True

    def test_compare_lt_true(self, matcher):
        """Test < operator returns True when condition met."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare(2.5, ConditionOperator.LT, 3.0)
        assert result is True

    def test_compare_lt_false(self, matcher):
        """Test < operator returns False when condition not met."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare(3.5, ConditionOperator.LT, 3.0)
        assert result is False

    def test_compare_eq_true(self, matcher):
        """Test == operator with float epsilon."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare(50.0000001, ConditionOperator.EQ, 50.0)
        assert result is True

    def test_compare_invalid_value(self, matcher):
        """Test comparison with invalid signal value."""
        from spendsense.personas.registry import ConditionOperator
        result = matcher._compare("invalid", ConditionOperator.GTE, 50.0)
        assert result is False


class TestPersonaMatching:
    """Test matching against actual personas."""

    def test_high_utilization_match(self, matcher):
        """Test matching Persona 1 (High Credit Utilization)."""
        # Create signals that match: credit_max_utilization_pct >= 50.0
        signals = ExtendedSignals(
            credit_max_utilization_pct_30d=60.0,
            subscription_share_pct_30d=0.10,
            savings_emergency_fund_months_30d=5.0
        )

        persona = matcher.registry.get_persona_by_id("high_utilization")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "high_utilization"
        assert "credit_max_utilization_pct" in match.evidence
        assert match.evidence["credit_max_utilization_pct"] == 60.0

    def test_high_utilization_no_match(self, matcher):
        """Test non-matching Persona 1."""
        # Create signals that DON'T match: credit_max_utilization_pct < 50.0
        signals = ExtendedSignals(
            credit_max_utilization_pct_30d=30.0,
            subscription_share_pct_30d=0.10,
            savings_emergency_fund_months_30d=5.0
        )

        persona = matcher.registry.get_persona_by_id("high_utilization")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False
        assert match.persona_id == "high_utilization"

    def test_irregular_income_match_condition1(self, matcher):
        """Test matching Persona 2 (Variable Income) - condition 1 (pay gap > 45)."""
        # OR logic: income_median_pay_gap_days > 45 OR income_payroll_count < 2
        signals = ExtendedSignals(
            income_median_pay_gap_days_30d=50.0,  # Matches condition 1
            income_payroll_count_30d=3,  # Doesn't match condition 2
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("irregular_income")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "irregular_income"

    def test_irregular_income_match_condition2(self, matcher):
        """Test matching Persona 2 (Variable Income) - condition 2 (payroll < 2)."""
        # OR logic: income_median_pay_gap_days > 45 OR income_payroll_count < 2
        signals = ExtendedSignals(
            income_median_pay_gap_days_30d=30.0,  # Doesn't match condition 1
            income_payroll_count_30d=1,  # Matches condition 2
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("irregular_income")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "irregular_income"

    def test_irregular_income_match_both_conditions(self, matcher):
        """Test matching Persona 2 when both OR conditions are True."""
        signals = ExtendedSignals(
            income_median_pay_gap_days_30d=50.0,  # Matches condition 1
            income_payroll_count_30d=1,  # Matches condition 2
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("irregular_income")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True

    def test_irregular_income_no_match(self, matcher):
        """Test non-matching Persona 2 when both conditions are False."""
        signals = ExtendedSignals(
            income_median_pay_gap_days_30d=30.0,  # Doesn't match
            income_payroll_count_30d=3,  # Doesn't match
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("irregular_income")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False

    def test_low_savings_match(self, matcher):
        """Test matching Persona 3 (Low Savings)."""
        # savings_emergency_fund_months < 3.0
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=2.5,
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("low_savings")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "low_savings"

    def test_low_savings_no_match(self, matcher):
        """Test non-matching Persona 3."""
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=5.0,
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("low_savings")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False

    def test_subscription_heavy_match(self, matcher):
        """Test matching Persona 4 (Subscription-Heavy)."""
        # subscription_share_pct >= 0.20
        signals = ExtendedSignals(
            subscription_share_pct_30d=0.25,
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("subscription_heavy")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "subscription_heavy"

    def test_subscription_heavy_exact_threshold(self, matcher):
        """Test matching Persona 4 with exact threshold value."""
        signals = ExtendedSignals(
            subscription_share_pct_30d=0.20,  # Exact threshold
            credit_max_utilization_pct_30d=20.0
        )

        persona = matcher.registry.get_persona_by_id("subscription_heavy")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True

    def test_cash_flow_optimizer_match(self, matcher):
        """Test matching Persona 5 (Cash Flow Optimizer) - AND logic."""
        # AND logic: savings >= 6.0 AND credit_utilization < 10.0
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=7.0,  # Matches condition 1
            credit_max_utilization_pct_30d=5.0,  # Matches condition 2
        )

        persona = matcher.registry.get_persona_by_id("cash_flow_optimizer")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "cash_flow_optimizer"

    def test_cash_flow_optimizer_no_match_condition1(self, matcher):
        """Test non-matching Persona 5 when first AND condition fails."""
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=4.0,  # Doesn't match
            credit_max_utilization_pct_30d=5.0,  # Matches
        )

        persona = matcher.registry.get_persona_by_id("cash_flow_optimizer")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False

    def test_cash_flow_optimizer_no_match_condition2(self, matcher):
        """Test non-matching Persona 5 when second AND condition fails."""
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=7.0,  # Matches
            credit_max_utilization_pct_30d=15.0,  # Doesn't match
        )

        persona = matcher.registry.get_persona_by_id("cash_flow_optimizer")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False

    def test_young_professional_match_history(self, matcher):
        """Test matching Persona 6 (Young Professional) - transaction history."""
        # OR logic: transaction_history_days < 180 OR credit_total_limits < 3000
        signals = ExtendedSignals(
            transaction_history_days=150,  # Matches condition 1
            credit_total_limits=5000.0,  # Doesn't match condition 2
        )

        persona = matcher.registry.get_persona_by_id("young_professional")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert match.persona_id == "young_professional"

    def test_young_professional_match_credit_limits(self, matcher):
        """Test matching Persona 6 - credit limits."""
        signals = ExtendedSignals(
            transaction_history_days=200,  # Doesn't match
            credit_total_limits=2500.0,  # Matches condition 2
        )

        persona = matcher.registry.get_persona_by_id("young_professional")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True


class TestMissingSignals:
    """Test handling of missing/None signal values."""

    def test_missing_signal_no_match(self, matcher):
        """Test that missing signals cause condition to fail."""
        signals = ExtendedSignals(
            credit_max_utilization_pct_30d=None,  # Missing
        )

        persona = matcher.registry.get_persona_by_id("high_utilization")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False

    def test_missing_signal_or_logic_still_matches(self, matcher):
        """Test OR logic can still match with one missing signal."""
        signals = ExtendedSignals(
            income_median_pay_gap_days_30d=None,  # Missing - condition 1 fails
            income_payroll_count_30d=1,  # Matches condition 2
        )

        persona = matcher.registry.get_persona_by_id("irregular_income")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True  # OR logic: one True is enough

    def test_all_signals_missing_and_logic(self, matcher):
        """Test AND logic fails when all signals are missing."""
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=None,
            credit_max_utilization_pct_30d=None,
        )

        persona = matcher.registry.get_persona_by_id("cash_flow_optimizer")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is False


class TestMultiplePersonaMatching:
    """Test matching against multiple personas simultaneously."""

    def test_multiple_matches(self, matcher):
        """Test user matching multiple personas."""
        # Create signals that match multiple personas
        signals = ExtendedSignals(
            credit_max_utilization_pct_30d=60.0,  # Matches high_utilization
            savings_emergency_fund_months_30d=2.0,  # Matches low_savings
            subscription_share_pct_30d=0.10,
        )

        matches = []
        for persona in matcher.registry.personas:
            match = matcher._evaluate_persona(persona, signals, "30d")
            if match.matched:
                matches.append(match)

        assert len(matches) == 2
        persona_ids = [m.persona_id for m in matches]
        assert "high_utilization" in persona_ids
        assert "low_savings" in persona_ids

    def test_no_matches(self, matcher):
        """Test user matching zero personas."""
        # Create signals that don't match any persona
        signals = ExtendedSignals(
            credit_max_utilization_pct_30d=20.0,
            savings_emergency_fund_months_30d=4.0,
            subscription_share_pct_30d=0.10,
            income_median_pay_gap_days_30d=30.0,
            income_payroll_count_30d=3,
            transaction_history_days=200,
            credit_total_limits=5000.0,
        )

        matches = []
        for persona in matcher.registry.personas:
            match = matcher._evaluate_persona(persona, signals, "30d")
            if match.matched:
                matches.append(match)

        assert len(matches) == 0


class TestEvidenceCapture:
    """Test that evidence dict captures signal values correctly."""

    def test_evidence_contains_evaluated_signals(self, matcher):
        """Test evidence dict contains all evaluated signal values."""
        signals = ExtendedSignals(
            credit_max_utilization_pct_30d=60.0,
        )

        persona = matcher.registry.get_persona_by_id("high_utilization")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert "credit_max_utilization_pct" in match.evidence
        assert match.evidence["credit_max_utilization_pct"] == 60.0

    def test_evidence_contains_matched_conditions(self, matcher):
        """Test matched_conditions list contains condition descriptions."""
        signals = ExtendedSignals(
            savings_emergency_fund_months_30d=7.0,
            credit_max_utilization_pct_30d=5.0,
        )

        persona = matcher.registry.get_persona_by_id("cash_flow_optimizer")
        match = matcher._evaluate_persona(persona, signals, "30d")

        assert match.matched is True
        assert len(match.matched_conditions) == 2
        assert any("savings_emergency_fund_months" in cond for cond in match.matched_conditions)
        assert any("credit_max_utilization_pct" in cond for cond in match.matched_conditions)


class TestDatabaseCalculations:
    """Test database queries for calculated signals (mocked)."""

    def test_calculate_transaction_history_days(self, matcher):
        """Test transaction history calculation."""
        # Mock database query with context manager
        mock_session = MagicMock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)

        mock_query = mock_session.query.return_value
        mock_join = mock_query.join.return_value
        mock_filter = mock_join.filter.return_value
        mock_filter.scalar.return_value = date(2025, 5, 1)

        with patch.object(matcher, 'Session', return_value=mock_session):
            result = matcher._calculate_transaction_history_days(
                "user_001",
                date(2025, 11, 5)
            )

        assert result == 188  # Days from May 1 to Nov 5

    def test_calculate_transaction_history_no_transactions(self, matcher):
        """Test transaction history with no transactions."""
        # Mock database query with context manager
        mock_session = MagicMock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)

        mock_query = mock_session.query.return_value
        mock_join = mock_query.join.return_value
        mock_filter = mock_join.filter.return_value
        mock_filter.scalar.return_value = None

        with patch.object(matcher, 'Session', return_value=mock_session):
            result = matcher._calculate_transaction_history_days(
                "user_001",
                date(2025, 11, 5)
            )

        assert result is None

    def test_calculate_credit_total_limits(self, matcher):
        """Test credit limits calculation."""
        # Mock database query with context manager
        mock_session = MagicMock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)

        mock_session.query.return_value.filter.return_value.scalar.return_value = 15000.0

        with patch.object(matcher, 'Session', return_value=mock_session):
            result = matcher._calculate_credit_total_limits("user_001")

        assert result == 15000.0

    def test_calculate_credit_total_limits_no_credit(self, matcher):
        """Test credit limits with no credit accounts."""
        # Mock database query with context manager
        mock_session = MagicMock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=False)

        mock_session.query.return_value.filter.return_value.scalar.return_value = None

        with patch.object(matcher, 'Session', return_value=mock_session):
            result = matcher._calculate_credit_total_limits("user_001")

        assert result is None
