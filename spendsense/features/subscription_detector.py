"""
Subscription pattern detection from transaction data.

This module detects recurring subscription patterns by identifying merchants
with regular, recurring charges (Netflix, Spotify, gym memberships, etc.).
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional
import pandas as pd
import numpy as np

from spendsense.features.time_windows import TimeWindowCalculator


@dataclass
class DetectedSubscription:
    """
    A detected recurring subscription.

    Attributes:
        merchant_name: Name of the merchant (e.g., "Netflix")
        cadence: Detected frequency ("monthly", "weekly", "irregular")
        avg_amount: Average charge amount
        transaction_count: Number of transactions detected
        last_charge_date: Date of most recent charge
        median_gap_days: Median number of days between charges
    """
    merchant_name: str
    cadence: str
    avg_amount: float
    transaction_count: int
    last_charge_date: date
    median_gap_days: float


@dataclass
class SubscriptionMetrics:
    """
    Aggregated subscription metrics for a user in a time window.

    Attributes:
        user_id: User identifier
        window_days: Size of time window (30 or 180)
        reference_date: End date of the window
        subscription_count: Number of detected subscriptions
        monthly_recurring_spend: Total monthly recurring charges
        total_spend: Total spend in the window
        subscription_share: Percentage of spend on subscriptions (0-1)
        detected_subscriptions: List of detected subscriptions
    """
    user_id: str
    window_days: int
    reference_date: date
    subscription_count: int
    monthly_recurring_spend: float
    total_spend: float
    subscription_share: float
    detected_subscriptions: List[DetectedSubscription] = field(default_factory=list)


class SubscriptionDetector:
    """
    Detects subscription patterns in transaction data.

    Uses recurring merchant detection and cadence analysis to identify
    subscriptions like Netflix, Spotify, gym memberships, etc.

    Usage:
        detector = SubscriptionDetector("data/processed/spendsense.db")

        metrics = detector.detect_subscriptions(
            user_id="user_001",
            reference_date=date(2025, 11, 4),
            window_days=30
        )

        print(f"Found {metrics.subscription_count} subscriptions")
        print(f"Subscription share: {metrics.subscription_share:.1%}")
    """

    # Cadence detection thresholds
    MONTHLY_MIN_DAYS = 25
    MONTHLY_MAX_DAYS = 35
    MONTHLY_STD_DEV = 7

    WEEKLY_MIN_DAYS = 5
    WEEKLY_MAX_DAYS = 9
    WEEKLY_STD_DEV = 3

    # Amount variation tolerance (±20%)
    AMOUNT_TOLERANCE = 0.20

    # Minimum transactions to consider
    MIN_TRANSACTIONS = 3

    # Lookback period for detecting recurring patterns
    # Use 180 days (supported by TimeWindowCalculator)
    LOOKBACK_DAYS = 180

    def __init__(self, db_path: str):
        """
        Initialize subscription detector.

        Args:
            db_path: Path to SQLite database
        """
        self.time_calc = TimeWindowCalculator(db_path)

    def detect_subscriptions(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> SubscriptionMetrics:
        """
        Detect subscription patterns for a user in a time window.

        Args:
            user_id: User identifier
            reference_date: End date of analysis window
            window_days: Window size (30 or 180 days)

        Returns:
            SubscriptionMetrics with detected subscriptions and aggregated metrics
        """
        # Get transactions in extended window for pattern detection
        lookback_result = self.time_calc.get_transactions_in_window(
            user_id=user_id,
            reference_date=reference_date,
            window_days=self.LOOKBACK_DAYS
        )

        if lookback_result.data.empty:
            return SubscriptionMetrics(
                user_id=user_id,
                window_days=window_days,
                reference_date=reference_date,
                subscription_count=0,
                monthly_recurring_spend=0.0,
                total_spend=0.0,
                subscription_share=0.0,
                detected_subscriptions=[]
            )

        # Detect recurring merchants
        subscriptions = self._detect_recurring_merchants(lookback_result.data)

        # Get transactions in target window for metrics
        window_result = self.time_calc.get_transactions_in_window(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days
        )

        # Calculate metrics
        metrics = self._calculate_metrics(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days,
            window_transactions=window_result.data,
            detected_subscriptions=subscriptions
        )

        return metrics

    def _detect_recurring_merchants(
        self,
        transactions: pd.DataFrame
    ) -> List[DetectedSubscription]:
        """
        Detect merchants with recurring transaction patterns.

        Args:
            transactions: DataFrame of transactions

        Returns:
            List of DetectedSubscription objects
        """
        subscriptions = []

        # Group by merchant
        grouped = transactions.groupby('merchant_name')

        for merchant, group in grouped:
            if len(group) < self.MIN_TRANSACTIONS:
                continue

            # Sort by date
            group = group.sort_values('date')

            # Calculate time gaps between transactions
            dates = group['date'].values
            gaps = []
            for i in range(1, len(dates)):
                gap = (dates[i] - dates[i-1]).days
                gaps.append(gap)

            if not gaps:
                continue

            # Analyze cadence
            median_gap = np.median(gaps)
            std_gap = np.std(gaps) if len(gaps) > 1 else 0

            cadence = self._determine_cadence(median_gap, std_gap)

            if cadence:  # Only include if pattern detected
                # Calculate average amount (handle negatives - subscriptions are debits)
                amounts = group['amount'].abs()
                avg_amount = amounts.mean()

                # Check amount consistency (±20% tolerance)
                amount_std = amounts.std()
                amount_cv = amount_std / avg_amount if avg_amount > 0 else 0

                if amount_cv > self.AMOUNT_TOLERANCE:
                    # Too much variation, might not be subscription
                    cadence = "irregular"

                subscription = DetectedSubscription(
                    merchant_name=merchant,
                    cadence=cadence,
                    avg_amount=float(avg_amount),
                    transaction_count=len(group),
                    last_charge_date=group['date'].max(),
                    median_gap_days=float(median_gap)
                )

                subscriptions.append(subscription)

        return subscriptions

    def _determine_cadence(
        self,
        median_gap: float,
        std_gap: float
    ) -> Optional[str]:
        """
        Determine transaction cadence from gap statistics.

        Args:
            median_gap: Median days between transactions
            std_gap: Standard deviation of gaps

        Returns:
            "monthly", "weekly", "irregular", or None if no pattern
        """
        # Check for monthly pattern
        if (self.MONTHLY_MIN_DAYS <= median_gap <= self.MONTHLY_MAX_DAYS and
            std_gap <= self.MONTHLY_STD_DEV):
            return "monthly"

        # Check for weekly pattern
        if (self.WEEKLY_MIN_DAYS <= median_gap <= self.WEEKLY_MAX_DAYS and
            std_gap <= self.WEEKLY_STD_DEV):
            return "weekly"

        # Recurring but irregular timing
        if median_gap < 60:  # Less than 2 months
            return "irregular"

        return None

    def _calculate_metrics(
        self,
        user_id: str,
        reference_date: date,
        window_days: int,
        window_transactions: pd.DataFrame,
        detected_subscriptions: List[DetectedSubscription]
    ) -> SubscriptionMetrics:
        """
        Calculate subscription metrics for the target window.

        Args:
            user_id: User identifier
            reference_date: Window end date
            window_days: Window size
            window_transactions: Transactions in target window
            detected_subscriptions: All detected subscriptions

        Returns:
            SubscriptionMetrics object
        """
        if window_transactions.empty:
            return SubscriptionMetrics(
                user_id=user_id,
                window_days=window_days,
                reference_date=reference_date,
                subscription_count=0,
                monthly_recurring_spend=0.0,
                total_spend=0.0,
                subscription_share=0.0,
                detected_subscriptions=[]
            )

        # Calculate total spend (absolute value of debits)
        debits = window_transactions[window_transactions['amount'] < 0]
        total_spend = debits['amount'].abs().sum()

        # Filter subscriptions to those with charges in this window
        subscription_merchants = [sub.merchant_name for sub in detected_subscriptions]
        subscription_txns = window_transactions[
            window_transactions['merchant_name'].isin(subscription_merchants) &
            (window_transactions['amount'] < 0)
        ]

        # Calculate subscription spend
        subscription_spend = subscription_txns['amount'].abs().sum()

        # Calculate monthly recurring (annualize to monthly for different windows)
        if window_days == 30:
            monthly_recurring = subscription_spend
        elif window_days == 180:
            # Average monthly over 6 months
            monthly_recurring = subscription_spend / 6
        else:
            monthly_recurring = subscription_spend * (30 / window_days)

        # Calculate subscription share
        subscription_share = (
            subscription_spend / total_spend if total_spend > 0 else 0.0
        )

        # Filter to subscriptions active in this window
        window_start = reference_date - timedelta(days=window_days)
        active_subscriptions = [
            sub for sub in detected_subscriptions
            if sub.last_charge_date >= window_start
        ]

        return SubscriptionMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            subscription_count=len(active_subscriptions),
            monthly_recurring_spend=float(monthly_recurring),
            total_spend=float(total_spend),
            subscription_share=float(subscription_share),
            detected_subscriptions=active_subscriptions
        )
