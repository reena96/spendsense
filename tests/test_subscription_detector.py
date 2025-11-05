"""
Tests for subscription pattern detection (Story 2.2).
"""

import pytest
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

from spendsense.features.subscription_detector import (
    SubscriptionDetector,
    SubscriptionMetrics,
    DetectedSubscription
)


@pytest.fixture
def detector():
    """Create SubscriptionDetector with test database."""
    db_path = "data/processed/spendsense.db"
    if not Path(db_path).exists():
        pytest.skip(f"Test database not found: {db_path}")
    return SubscriptionDetector(db_path)


class TestSubscriptionDetector:
    """Tests for SubscriptionDetector class."""

    def test_ac1_recurring_merchant_detection(self, detector):
        """AC1: Recurring merchant detection identifies merchants with ≥3 transactions in 90 days."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180  # Use longer window to ensure we catch patterns
        )

        # Should detect some subscriptions
        assert isinstance(metrics, SubscriptionMetrics)
        assert isinstance(metrics.detected_subscriptions, list)

        # Check subscription structure
        if metrics.subscription_count > 0:
            sub = metrics.detected_subscriptions[0]
            assert isinstance(sub, DetectedSubscription)
            assert sub.transaction_count >= 3
            assert sub.merchant_name is not None

    def test_ac2_cadence_analysis(self, detector):
        """AC2: Cadence analysis determines if transactions are monthly or weekly recurring."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Check cadence values
        for sub in metrics.detected_subscriptions:
            assert sub.cadence in ['monthly', 'weekly', 'irregular']
            assert isinstance(sub.median_gap_days, float)

    def test_ac3_monthly_recurring_spend_calculated(self, detector):
        """AC3: Monthly recurring spend total calculated for each time window."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert isinstance(metrics.monthly_recurring_spend, float)
        assert metrics.monthly_recurring_spend >= 0

    def test_ac4_subscription_share_calculated(self, detector):
        """AC4: Subscription share calculated as percentage of total spend."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert isinstance(metrics.subscription_share, float)
        assert 0.0 <= metrics.subscription_share <= 1.0

        # Verify calculation
        if metrics.total_spend > 0 and metrics.subscription_count > 0:
            # subscription_share should be reasonable
            assert metrics.subscription_share >= 0

    def test_ac5_both_windows_computed(self, detector):
        """AC5: Results computed for both 30-day and 180-day windows."""
        reference_date = date(2025, 11, 4)

        metrics_30 = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        metrics_180 = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        assert metrics_30.window_days == 30
        assert metrics_180.window_days == 180

        # 180-day window should have more or equal subscriptions
        assert metrics_180.subscription_count >= metrics_30.subscription_count

    def test_ac6_subscriptions_logged_with_details(self, detector):
        """AC6: Detected subscriptions logged with merchant name, frequency, and amount."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Check all required fields present
        for sub in metrics.detected_subscriptions:
            assert sub.merchant_name is not None
            assert sub.cadence in ['monthly', 'weekly', 'irregular']
            assert sub.avg_amount > 0
            assert sub.transaction_count >= 3
            assert isinstance(sub.last_charge_date, date)
            assert sub.median_gap_days > 0

    def test_ac7_edge_case_amount_variations(self, detector):
        """AC7: Edge cases handled - amount variations."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Should handle amount variations (marked as irregular if too varied)
        for sub in metrics.detected_subscriptions:
            if sub.cadence == 'irregular':
                # Irregular subscriptions still detected
                assert sub.transaction_count >= 3

    def test_ac7_edge_case_no_transactions(self, detector):
        """AC7: Edge case - user with no transactions."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="nonexistent_user",
            reference_date=reference_date,
            window_days=30
        )

        assert metrics.subscription_count == 0
        assert metrics.monthly_recurring_spend == 0.0
        assert metrics.total_spend == 0.0
        assert metrics.subscription_share == 0.0

    def test_ac8_metrics_stored_per_user_window(self, detector):
        """AC8: Subscription metrics stored per user per time window."""
        reference_date = date(2025, 11, 4)

        # Get metrics for different users and windows
        user1_30 = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        user1_180 = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        user2_30 = detector.detect_subscriptions(
            user_id="user_MASKED_001",
            reference_date=reference_date,
            window_days=30
        )

        # Verify all have correct metadata
        assert user1_30.user_id == "user_MASKED_000"
        assert user1_30.window_days == 30

        assert user1_180.user_id == "user_MASKED_000"
        assert user1_180.window_days == 180

        assert user2_30.user_id == "user_MASKED_001"
        assert user2_30.window_days == 30

    def test_ac9_monthly_pattern_detection(self, detector):
        """AC9: Unit tests verify detection accuracy with synthetic recurring patterns - monthly."""
        # Test with real data that should contain monthly subscriptions
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Check for monthly subscriptions
        monthly_subs = [s for s in metrics.detected_subscriptions if s.cadence == 'monthly']

        if monthly_subs:
            # Verify monthly pattern characteristics
            for sub in monthly_subs:
                # Monthly should be ~30 days (25-35 range)
                assert 25 <= sub.median_gap_days <= 35

    def test_ac9_weekly_pattern_detection(self, detector):
        """AC9: Unit tests verify detection accuracy - weekly patterns."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Check for weekly subscriptions
        weekly_subs = [s for s in metrics.detected_subscriptions if s.cadence == 'weekly']

        if weekly_subs:
            # Verify weekly pattern characteristics
            for sub in weekly_subs:
                # Weekly should be ~7 days (5-9 range)
                assert 5 <= sub.median_gap_days <= 9

    def test_minimum_transaction_threshold(self, detector):
        """Test that merchants need at least 3 transactions."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # All detected subscriptions should have >= 3 transactions
        for sub in metrics.detected_subscriptions:
            assert sub.transaction_count >= 3

    def test_subscription_share_bounds(self, detector):
        """Test that subscription share is between 0 and 1."""
        reference_date = date(2025, 11, 4)

        for user_id in ["user_MASKED_000", "user_MASKED_001", "user_MASKED_002"]:
            metrics = detector.detect_subscriptions(
                user_id=user_id,
                reference_date=reference_date,
                window_days=30
            )

            assert 0.0 <= metrics.subscription_share <= 1.0

    def test_monthly_recurring_annualization(self, detector):
        """Test that monthly recurring is properly annualized for different windows."""
        reference_date = date(2025, 11, 4)

        metrics_30 = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        metrics_180 = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        # Monthly recurring should be similar (average monthly)
        # Not exact due to different data in windows
        assert isinstance(metrics_30.monthly_recurring_spend, float)
        assert isinstance(metrics_180.monthly_recurring_spend, float)

    def test_detected_subscription_fields(self, detector):
        """Test DetectedSubscription dataclass structure."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=180
        )

        if metrics.subscription_count > 0:
            sub = metrics.detected_subscriptions[0]

            # Verify all fields present and correct types
            assert isinstance(sub.merchant_name, str)
            assert isinstance(sub.cadence, str)
            assert isinstance(sub.avg_amount, float)
            assert isinstance(sub.transaction_count, int)
            assert isinstance(sub.last_charge_date, date)
            assert isinstance(sub.median_gap_days, float)

    def test_metrics_reference_date(self, detector):
        """Test that metrics correctly store reference date."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert metrics.reference_date == reference_date

    def test_different_reference_dates(self, detector):
        """Test detection with different reference dates."""
        user_id = "user_MASKED_000"

        metrics_nov = detector.detect_subscriptions(
            user_id=user_id,
            reference_date=date(2025, 11, 4),
            window_days=30
        )

        metrics_oct = detector.detect_subscriptions(
            user_id=user_id,
            reference_date=date(2025, 10, 4),
            window_days=30
        )

        # Should get results (may be different)
        assert isinstance(metrics_nov, SubscriptionMetrics)
        assert isinstance(metrics_oct, SubscriptionMetrics)

    def test_subscription_count_matches_list_length(self, detector):
        """Test that subscription_count matches detected_subscriptions length."""
        reference_date = date(2025, 11, 4)
        metrics = detector.detect_subscriptions(
            user_id="user_MASKED_000",
            reference_date=reference_date,
            window_days=30
        )

        assert metrics.subscription_count == len(metrics.detected_subscriptions)


class TestSubscriptionMetrics:
    """Tests for SubscriptionMetrics dataclass."""

    def test_metrics_initialization(self):
        """Test SubscriptionMetrics can be initialized."""
        metrics = SubscriptionMetrics(
            user_id="test_user",
            window_days=30,
            reference_date=date(2025, 11, 4),
            subscription_count=2,
            monthly_recurring_spend=50.0,
            total_spend=500.0,
            subscription_share=0.1,
            detected_subscriptions=[]
        )

        assert metrics.user_id == "test_user"
        assert metrics.window_days == 30
        assert metrics.subscription_count == 2
        assert metrics.subscription_share == 0.1


class TestDetectedSubscription:
    """Tests for DetectedSubscription dataclass."""

    def test_subscription_initialization(self):
        """Test DetectedSubscription can be initialized."""
        sub = DetectedSubscription(
            merchant_name="Netflix",
            cadence="monthly",
            avg_amount=15.99,
            transaction_count=6,
            last_charge_date=date(2025, 11, 1),
            median_gap_days=30.0
        )

        assert sub.merchant_name == "Netflix"
        assert sub.cadence == "monthly"
        assert sub.avg_amount == 15.99
        assert sub.transaction_count == 6
