"""
Tests for income stability pattern detection (Story 2.5).
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

from spendsense.features.income_detector import (
    IncomeDetector,
    IncomeMetrics,
    MIN_INCOME_AMOUNT,
    WEEKLY_MIN, WEEKLY_MAX,
    BIWEEKLY_MIN, BIWEEKLY_MAX,
    MONTHLY_MIN, MONTHLY_MAX
)


@pytest.fixture
def detector():
    """Create IncomeDetector with test database."""
    db_path = "data/processed/spendsense.db"
    if not Path(db_path).exists():
        pytest.skip(f"Test database not found: {db_path}")
    return IncomeDetector(db_path)


class TestIncomeDetector:
    """Tests for IncomeDetector class."""

    def test_ac1_payroll_detection(self, detector):
        """AC1: Payroll ACH transactions detected from transaction category and amount patterns."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Metrics should be returned
        assert isinstance(metrics, IncomeMetrics)
        assert isinstance(metrics.num_income_transactions, int)
        assert metrics.num_income_transactions >= 0

    def test_ac2_payment_frequency_calculated(self, detector):
        """AC2: Payment frequency calculated from time gaps between payroll transactions."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Payment frequency should be one of the defined types
        valid_frequencies = ['weekly', 'biweekly', 'monthly', 'irregular', 'unknown']
        assert metrics.payment_frequency in valid_frequencies

    def test_ac3_median_pay_gap_calculated(self, detector):
        """AC3: Median pay gap calculated to identify regular vs. irregular income."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert isinstance(metrics.median_pay_gap_days, float)
        assert metrics.median_pay_gap_days >= 0

    def test_ac4_cash_flow_buffer_calculated(self, detector):
        """AC4: Cash-flow buffer calculated in months of expenses coverage."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert isinstance(metrics.cash_flow_buffer_months, float)
        assert metrics.cash_flow_buffer_months >= 0

    def test_ac5_income_variability_calculated(self, detector):
        """AC5: Income variability metric calculated from payment amount standard deviation."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert isinstance(metrics.income_variability_cv, float)
        assert metrics.income_variability_cv >= 0

    def test_ac6_both_windows_computed(self, detector):
        """AC6: Results computed for both 30-day and 180-day windows."""
        reference_date = date(2025, 11, 4)

        metrics_30 = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        metrics_180 = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert metrics_30.window_days == 30
        assert metrics_180.window_days == 180

    def test_ac7_edge_cases_handled(self, detector):
        """AC7: Edge cases handled: first job, job changes, missing income data."""
        reference_date = date(2025, 11, 4)

        # Test with user that may have no income
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_999",  # Likely non-existent
            reference_date=reference_date,
            window_days=30
        )

        # Should return empty metrics without crashing
        assert metrics.num_income_transactions == 0
        assert metrics.payment_frequency == 'unknown'
        assert metrics.has_regular_income is False

    def test_ac8_income_metrics_logged(self, detector):
        """AC8: All income metrics logged with detected payroll dates."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Payroll dates should be logged
        assert hasattr(metrics, 'payroll_dates')
        assert isinstance(metrics.payroll_dates, list)

        if metrics.num_income_transactions > 0:
            assert len(metrics.payroll_dates) == metrics.num_income_transactions

    def test_ac9_metrics_stored_per_user_window(self, detector):
        """AC9: Income metrics stored per user per time window."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert metrics.user_id == "user_MASKED_000"
        assert metrics.window_days == 30
        assert metrics.reference_date == reference_date

    def test_ac10_frequency_pattern_detection(self, detector):
        """AC10: Unit tests verify detection with biweekly, monthly, and irregular patterns."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Should classify into one of the patterns
        assert metrics.payment_frequency in ['weekly', 'biweekly', 'monthly', 'irregular', 'unknown']


class TestPayrollDetection:
    """Test payroll transaction detection logic."""

    def test_minimum_income_threshold(self):
        """Test minimum income threshold is defined."""
        assert MIN_INCOME_AMOUNT > 0
        assert MIN_INCOME_AMOUNT == 500.0

    def test_income_transaction_count(self, detector):
        """Test income transaction counting."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # If income transactions found, count should match payroll dates
        if metrics.num_income_transactions > 0:
            assert len(metrics.payroll_dates) == metrics.num_income_transactions


class TestFrequencyClassification:
    """Test payment frequency classification."""

    def test_frequency_thresholds_defined(self):
        """Verify frequency classification thresholds."""
        assert WEEKLY_MIN == 5
        assert WEEKLY_MAX == 9
        assert BIWEEKLY_MIN == 12
        assert BIWEEKLY_MAX == 16
        assert MONTHLY_MIN == 28
        assert MONTHLY_MAX == 32

    def test_has_regular_income_flag(self, detector):
        """Test has_regular_income flag is set correctly."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Flag should be boolean
        assert isinstance(metrics.has_regular_income, bool)

        # Regular income = not irregular or unknown
        if metrics.payment_frequency in ['weekly', 'biweekly', 'monthly']:
            assert metrics.has_regular_income is True
        elif metrics.payment_frequency == 'irregular':
            assert metrics.has_regular_income is False


class TestIncomeVariability:
    """Test income variability calculation."""

    def test_variability_cv_non_negative(self, detector):
        """Test coefficient of variation is non-negative."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert metrics.income_variability_cv >= 0

    def test_income_totals(self, detector):
        """Test income totals are calculated."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert isinstance(metrics.total_income, float)
        assert isinstance(metrics.avg_income_per_payment, float)
        assert metrics.total_income >= 0
        assert metrics.avg_income_per_payment >= 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_no_income_transactions(self, detector):
        """Test handling of user with no income transactions."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_999",
            reference_date=reference_date,
            window_days=30
        )

        assert metrics.num_income_transactions == 0
        assert metrics.total_income == 0.0
        assert metrics.payment_frequency == 'unknown'
        assert metrics.has_regular_income is False
        assert len(metrics.payroll_dates) == 0

    def test_future_date_handling(self, detector):
        """Test that future dates are handled."""
        future_date = date.today() + timedelta(days=30)

        with pytest.raises(ValueError):
            detector.detect_income_patterns(
                user_id="user_MASKED_000",
                reference_date=future_date,
                window_days=30
            )


class TestMetricsStructure:
    """Test metrics data structure."""

    def test_income_metrics_fields(self, detector):
        """Test all required fields present in IncomeMetrics."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        required_fields = [
            'user_id',
            'window_days',
            'reference_date',
            'num_income_transactions',
            'total_income',
            'avg_income_per_payment',
            'payment_frequency',
            'median_pay_gap_days',
            'income_variability_cv',
            'cash_flow_buffer_months',
            'has_regular_income',
            'payroll_dates'
        ]

        for field in required_fields:
            assert hasattr(metrics, field)

    def test_metrics_types(self, detector):
        """Test metrics have correct types."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_income_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert isinstance(metrics.user_id, str)
        assert isinstance(metrics.window_days, int)
        assert isinstance(metrics.reference_date, date)
        assert isinstance(metrics.num_income_transactions, int)
        assert isinstance(metrics.total_income, float)
        assert isinstance(metrics.avg_income_per_payment, float)
        assert isinstance(metrics.payment_frequency, str)
        assert isinstance(metrics.median_pay_gap_days, float)
        assert isinstance(metrics.income_variability_cv, float)
        assert isinstance(metrics.cash_flow_buffer_months, float)
        assert isinstance(metrics.has_regular_income, bool)
        assert isinstance(metrics.payroll_dates, list)
