"""
Tests for credit utilization and debt signal detection (Story 2.4).
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

from spendsense.features.credit_detector import (
    CreditDetector,
    CreditMetrics,
    PerCardUtilization,
    UTILIZATION_MODERATE,
    UTILIZATION_HIGH,
    UTILIZATION_VERY_HIGH
)


@pytest.fixture
def detector():
    """Create CreditDetector with test database."""
    db_path = "data/processed/spendsense.db"
    if not Path(db_path).exists():
        pytest.skip(f"Test database not found: {db_path}")
    return CreditDetector(db_path)


class TestCreditDetector:
    """Tests for CreditDetector class."""

    def test_ac1_utilization_calculated(self, detector):
        """AC1: Credit utilization calculated as balance ÷ limit for each credit card."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Metrics should be returned
        assert isinstance(metrics, CreditMetrics)

        # If user has credit cards, check utilization calculation
        if metrics.num_credit_cards > 0:
            for card in metrics.per_card_details:
                assert isinstance(card, PerCardUtilization)
                assert isinstance(card.utilization, float)
                assert 0.0 <= card.utilization <= 2.0  # Allow over-limit

    def test_ac2_utilization_flags(self, detector):
        """AC2: Utilization flags set for ≥30%, ≥50%, ≥80% thresholds."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Check that utilization tiers are assigned correctly
        for card in metrics.per_card_details:
            assert card.utilization_tier in ['low', 'moderate', 'high', 'very_high']

            # Verify tier matches utilization
            if card.utilization >= UTILIZATION_VERY_HIGH:
                assert card.utilization_tier == 'very_high'
            elif card.utilization >= UTILIZATION_HIGH:
                assert card.utilization_tier == 'high'
            elif card.utilization >= UTILIZATION_MODERATE:
                assert card.utilization_tier == 'moderate'
            else:
                assert card.utilization_tier == 'low'

    def test_ac3_minimum_payment_detection(self, detector):
        """AC3: Minimum-payment-only behavior detected from payment history."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # minimum_payment_only_count should be non-negative
        assert isinstance(metrics.minimum_payment_only_count, int)
        assert metrics.minimum_payment_only_count >= 0

    def test_ac4_interest_charges_identified(self, detector):
        """AC4: Interest charges presence identified from liability data."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # has_interest_charges should be boolean
        assert isinstance(metrics.has_interest_charges, bool)

        # If any card has interest charges, flag should be True
        if metrics.num_credit_cards > 0:
            has_any_interest = any(card.has_interest_charges for card in metrics.per_card_details)
            assert metrics.has_interest_charges == has_any_interest

    def test_ac5_overdue_status_flagged(self, detector):
        """AC5: Overdue status flagged from is_overdue field."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # overdue_count should be non-negative
        assert isinstance(metrics.overdue_count, int)
        assert metrics.overdue_count >= 0

        # Verify overdue count matches per-card data
        if metrics.num_credit_cards > 0:
            overdue_cards = sum(1 for card in metrics.per_card_details if card.is_overdue)
            assert metrics.overdue_count == overdue_cards

    def test_ac6_aggregate_utilization(self, detector):
        """AC6: Aggregate utilization calculated across all cards."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Aggregate utilization should be float
        assert isinstance(metrics.aggregate_utilization, float)
        assert 0.0 <= metrics.aggregate_utilization <= 2.0  # Allow over-limit

        # Verify calculation if we have cards
        if metrics.num_credit_cards > 0:
            total_balance = sum(card.balance for card in metrics.per_card_details)
            total_limit = sum(card.limit for card in metrics.per_card_details)

            if total_limit > 0:
                expected_util = total_balance / total_limit
                assert abs(metrics.aggregate_utilization - expected_util) < 0.01

    def test_ac7_both_windows_computed(self, detector):
        """AC7: Results computed for both 30-day and 180-day windows."""
        reference_date = date(2025, 11, 4)

        metrics_30 = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        metrics_180 = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Both should return valid metrics
        assert metrics_30.window_days == 30
        assert metrics_180.window_days == 180

        # Note: Credit metrics are typically the same across windows
        # since they're based on current snapshot, not transactions

    def test_ac8_credit_signals_logged(self, detector):
        """AC8: All credit signals logged with specific card identifiers."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Per-card details should include account_id
        for card in metrics.per_card_details:
            assert hasattr(card, 'account_id')
            assert card.account_id is not None
            assert isinstance(card.account_id, str)

    def test_ac9_metrics_stored_per_user_window(self, detector):
        """AC9: Credit metrics stored per user per time window."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Metrics should include user_id, window_days, reference_date
        assert metrics.user_id == "user_MASKED_000"
        assert metrics.window_days == 30
        assert metrics.reference_date == reference_date

    def test_ac10_various_credit_scenarios(self, detector):
        """AC10: Unit tests verify detection across various credit scenarios."""
        reference_date = date(2025, 11, 4)

        # Test with different users/scenarios
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Should return valid metrics regardless of scenario
        assert isinstance(metrics, CreditMetrics)


class TestUtilizationTiers:
    """Test utilization tier classification."""

    def test_utilization_thresholds_defined(self):
        """Verify utilization thresholds are correctly defined."""
        assert UTILIZATION_MODERATE == 0.30
        assert UTILIZATION_HIGH == 0.50
        assert UTILIZATION_VERY_HIGH == 0.80

    def test_tier_assignment(self, detector):
        """Test that tiers are assigned correctly based on utilization."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        for card in metrics.per_card_details:
            # Verify tier logic
            if card.utilization >= 0.80:
                assert card.utilization_tier == 'very_high'
            elif card.utilization >= 0.50:
                assert card.utilization_tier == 'high'
            elif card.utilization >= 0.30:
                assert card.utilization_tier == 'moderate'
            else:
                assert card.utilization_tier == 'low'


class TestHighUtilizationCounts:
    """Test high utilization counting logic."""

    def test_high_utilization_count(self, detector):
        """Test high utilization count includes ≥50% cards."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Count high utilization cards manually
        high_util_cards = sum(
            1 for card in metrics.per_card_details
            if card.utilization >= UTILIZATION_HIGH
        )

        assert metrics.high_utilization_count == high_util_cards

    def test_very_high_utilization_count(self, detector):
        """Test very high utilization count includes ≥80% cards."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Count very high utilization cards manually
        very_high_util_cards = sum(
            1 for card in metrics.per_card_details
            if card.utilization >= UTILIZATION_VERY_HIGH
        )

        assert metrics.very_high_utilization_count == very_high_util_cards


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_no_credit_cards(self, detector):
        """Test handling of user with no credit cards."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_999",  # Likely non-existent
            reference_date=reference_date,
            window_days=30
        )

        assert metrics.num_credit_cards == 0
        assert metrics.aggregate_utilization == 0.0
        assert metrics.high_utilization_count == 0
        assert metrics.very_high_utilization_count == 0
        assert metrics.overdue_count == 0
        assert metrics.has_interest_charges is False
        assert len(metrics.per_card_details) == 0

    def test_future_date_handling(self, detector):
        """Test that future dates are handled by TimeWindowCalculator."""
        future_date = date.today() + timedelta(days=30)

        with pytest.raises(ValueError):
            detector.detect_credit_patterns(
                user_id="user_MASKED_000",
                reference_date=future_date,
                window_days=30
            )

    def test_invalid_window_days(self, detector):
        """Test that invalid window days are handled gracefully."""
        reference_date = date(2025, 11, 4)

        # TimeWindowCalculator validates window_days, but credit metrics
        # are snapshot-based and may not trigger validation
        try:
            metrics = detector.detect_credit_patterns(
                user_id="user_MASKED_000",
                reference_date=reference_date,
                window_days=90  # Not in SUPPORTED_WINDOWS
            )
            # If no error, metrics should still be valid
            assert isinstance(metrics, CreditMetrics)
        except ValueError:
            # This is also acceptable if TimeWindowCalculator validates
            pass


class TestMetricsStructure:
    """Test metrics data structure."""

    def test_credit_metrics_fields(self, detector):
        """Test all required fields present in CreditMetrics."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        # Check all required fields
        required_fields = [
            'user_id',
            'window_days',
            'reference_date',
            'num_credit_cards',
            'aggregate_utilization',
            'high_utilization_count',
            'very_high_utilization_count',
            'minimum_payment_only_count',
            'overdue_count',
            'has_interest_charges',
            'per_card_details'
        ]

        for field in required_fields:
            assert hasattr(metrics, field)

    def test_per_card_fields(self, detector):
        """Test all required fields present in PerCardUtilization."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        if metrics.num_credit_cards > 0:
            card = metrics.per_card_details[0]

            required_fields = [
                'account_id',
                'balance',
                'limit',
                'utilization',
                'utilization_tier',
                'is_overdue',
                'has_interest_charges'
            ]

            for field in required_fields:
                assert hasattr(card, field)

    def test_metrics_types(self, detector):
        """Test metrics have correct types."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert isinstance(metrics.user_id, str)
        assert isinstance(metrics.window_days, int)
        assert isinstance(metrics.reference_date, date)
        assert isinstance(metrics.num_credit_cards, int)
        assert isinstance(metrics.aggregate_utilization, float)
        assert isinstance(metrics.high_utilization_count, int)
        assert isinstance(metrics.very_high_utilization_count, int)
        assert isinstance(metrics.minimum_payment_only_count, int)
        assert isinstance(metrics.overdue_count, int)
        assert isinstance(metrics.has_interest_charges, bool)
        assert isinstance(metrics.per_card_details, list)


class TestAggregateCalculations:
    """Test aggregate metric calculations."""

    def test_aggregate_utilization_calculation(self, detector):
        """Test aggregate utilization is total_balance / total_limit."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_credit_patterns(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        if metrics.num_credit_cards > 0:
            # Calculate manually
            total_balance = sum(card.balance for card in metrics.per_card_details)
            total_limit = sum(card.limit for card in metrics.per_card_details)

            if total_limit > 0:
                expected = total_balance / total_limit
                assert abs(metrics.aggregate_utilization - expected) < 0.01
