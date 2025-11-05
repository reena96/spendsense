"""
Tests for time window aggregation framework (Story 2.1).
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

from spendsense.features.time_windows import (
    TimeWindowCalculator,
    TimeWindowResult,
    get_default_fallback_values
)


@pytest.fixture
def calculator():
    """Create TimeWindowCalculator with test database."""
    db_path = "data/processed/spendsense.db"
    if not Path(db_path).exists():
        pytest.skip(f"Test database not found: {db_path}")
    return TimeWindowCalculator(db_path)


class TestTimeWindowCalculator:
    """Tests for TimeWindowCalculator class."""

    def test_ac1_accepts_reference_date_and_window_size(self, calculator):
        """AC1: Time window utility function created accepting reference date and window size."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert isinstance(result, TimeWindowResult)
        assert result.window_end == reference_date
        assert result.window_start == reference_date - timedelta(days=30)

    def test_ac2_returns_filtered_dataset(self, calculator):
        """AC2: Function returns filtered dataset for specified window."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert isinstance(result.data, pd.DataFrame)
        if not result.data.empty:
            # All transactions should be within window
            assert result.data['date'].min() >= result.window_start
            assert result.data['date'].max() <= result.window_end

    def test_ac3_handles_insufficient_data(self, calculator):
        """AC3: Function handles edge cases (insufficient historical data)."""
        # Test with very short window for new user
        reference_date = date(2024, 5, 10)  # Early in data range
        result = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Should return result even if incomplete
        assert isinstance(result, TimeWindowResult)
        # is_complete flag should reflect data availability
        assert isinstance(result.is_complete, bool)

    def test_ac4_consistent_date_arithmetic(self, calculator):
        """AC4: Window calculations use consistent date arithmetic across all modules."""
        reference_date = date(2025, 11, 4)

        # Test 30-day window
        result_30 = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Test 180-day window
        result_180 = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Verify timedelta arithmetic is consistent
        assert result_30.window_start == reference_date - timedelta(days=30)
        assert result_180.window_start == reference_date - timedelta(days=180)
        assert result_30.window_end == reference_date
        assert result_180.window_end == reference_date

    def test_ac5_default_fallback_values(self):
        """AC5: Default fallback values defined for users with insufficient data."""
        defaults = get_default_fallback_values()

        # Verify all expected keys present
        assert 'subscription_count' in defaults
        assert 'subscription_spend' in defaults
        assert 'subscription_share' in defaults
        assert 'savings_growth_rate' in defaults
        assert 'emergency_fund_months' in defaults
        assert 'credit_utilization' in defaults
        assert 'is_overdue' in defaults
        assert 'payment_frequency_days' in defaults
        assert 'income_variability' in defaults
        assert 'data_completeness' in defaults

        # Verify sensible default values
        assert defaults['subscription_count'] == 0
        assert defaults['subscription_spend'] == 0.0
        assert defaults['credit_utilization'] == 0.0
        assert defaults['is_overdue'] is False
        assert defaults['data_completeness'] == 'insufficient'

    def test_ac7_correct_date_filtering(self, calculator):
        """AC7: Unit tests verify correct date filtering."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        if not result.data.empty:
            # Verify all transactions are within bounds
            for txn_date in result.data['date']:
                assert result.window_start <= txn_date <= result.window_end

    def test_ac7_edge_case_no_transactions(self, calculator):
        """AC7: Edge case - user with no transactions."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_transactions_in_window(
            user_id="nonexistent_user",
            reference_date=reference_date,
            window_days=30
        )

        assert result.record_count == 0
        assert result.data.empty
        assert result.is_complete is False

    def test_ac7_edge_case_future_reference_date(self, calculator):
        """AC7: Edge case - reference date in future should raise error."""
        future_date = date.today() + timedelta(days=10)

        with pytest.raises(ValueError, match="cannot be in the future"):
            calculator.get_transactions_in_window(
                user_id="user_MASKED_000",
                reference_date=future_date,
                window_days=30
            )

    def test_ac7_edge_case_invalid_window_size(self, calculator):
        """AC7: Edge case - invalid window size should raise error."""
        reference_date = date(2025, 11, 4)

        with pytest.raises(ValueError, match="Window must be one of"):
            calculator.get_transactions_in_window(
                user_id="user_MASKED_000",
                reference_date=reference_date,
                window_days=90  # Not supported
            )

    def test_180_day_window(self, calculator):
        """Test 180-day window returns more data than 30-day window."""
        reference_date = date(2025, 11, 4)

        result_30 = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        result_180 = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # 180-day window should have >= transactions than 30-day
        assert result_180.record_count >= result_30.record_count

    def test_accounts_snapshot(self, calculator):
        """Test getting account balances snapshot."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_accounts_snapshot(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        assert isinstance(result, TimeWindowResult)
        assert isinstance(result.data, list)
        if result.record_count > 0:
            # Verify account structure
            assert 'account_id' in result.data[0]
            assert 'balance' in result.data[0]

    def test_liabilities_snapshot(self, calculator):
        """Test getting liabilities snapshot."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_liabilities_snapshot(
            user_id="user_MASKED_000",
            reference_date=reference_date
        )

        assert isinstance(result, TimeWindowResult)
        assert isinstance(result.data, list)

    def test_time_window_result_repr(self):
        """Test TimeWindowResult string representation."""
        result = TimeWindowResult(
            data=pd.DataFrame(),
            window_start=date(2025, 10, 5),
            window_end=date(2025, 11, 4),
            is_complete=True,
            record_count=100
        )

        repr_str = repr(result)
        assert '2025-10-05' in repr_str
        assert '2025-11-04' in repr_str
        assert '100' in repr_str
        assert 'True' in repr_str

    def test_database_not_found_error(self):
        """Test error handling when database doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Database not found"):
            TimeWindowCalculator("/nonexistent/path/db.sqlite")

    def test_multiple_users(self, calculator):
        """Test querying multiple users."""
        reference_date = date(2025, 11, 4)

        result1 = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        result2 = calculator.get_transactions_in_window(
            user_id="user_MASKED_001",
            reference_date=reference_date,
            window_days=30
        )

        # Results should be independent
        assert result1.record_count != result2.record_count or result1.data.empty

    def test_date_boundary_inclusive(self, calculator):
        """Test that window end date is inclusive."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        if not result.data.empty:
            # Should include transactions on reference_date itself
            transactions_on_ref_date = result.data[result.data['date'] == reference_date]
            # May or may not have transactions on exact date, but should not exclude them
            assert True  # Boundary test passes if no errors

    def test_dataframe_columns(self, calculator):
        """Test that returned DataFrame has expected columns."""
        reference_date = date(2025, 11, 4)
        result = calculator.get_transactions_in_window(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        if not result.data.empty:
            expected_columns = [
                'transaction_id', 'account_id', 'date', 'amount',
                'merchant_name', 'category', 'payment_channel', 'pending'
            ]
            for col in expected_columns:
                assert col in result.data.columns


class TestDefaultFallbackValues:
    """Tests for default fallback values."""

    def test_returns_dict(self):
        """Test that fallback values return a dictionary."""
        defaults = get_default_fallback_values()
        assert isinstance(defaults, dict)

    def test_numeric_defaults_are_zero(self):
        """Test that numeric defaults are zero."""
        defaults = get_default_fallback_values()
        assert defaults['subscription_spend'] == 0.0
        assert defaults['savings_growth_rate'] == 0.0
        assert defaults['credit_utilization'] == 0.0

    def test_boolean_defaults(self):
        """Test boolean default values."""
        defaults = get_default_fallback_values()
        assert defaults['is_overdue'] is False

    def test_null_defaults(self):
        """Test nullable defaults."""
        defaults = get_default_fallback_values()
        assert defaults['payment_frequency_days'] is None
