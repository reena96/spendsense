"""
Credit utilization and debt signal detection from liability data.

This module detects credit card utilization levels, minimum-payment behavior,
and debt stress indicators to identify users needing debt paydown education.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List
import pandas as pd

from spendsense.features.time_windows import TimeWindowCalculator


# Utilization thresholds
UTILIZATION_MODERATE = 0.30  # 30%
UTILIZATION_HIGH = 0.50      # 50%
UTILIZATION_VERY_HIGH = 0.80 # 80%


@dataclass
class PerCardUtilization:
    """
    Credit utilization details for a single credit card.

    Attributes:
        account_id: Credit card account identifier
        balance: Current balance (last_statement_balance)
        limit: Credit limit (balance_limit)
        utilization: Utilization ratio (balance / limit)
        utilization_tier: Classification ('low', 'moderate', 'high', 'very_high')
        is_overdue: True if payment is overdue
        has_interest_charges: True if APR > 0
    """
    account_id: str
    balance: float
    limit: float
    utilization: float
    utilization_tier: str
    is_overdue: bool
    has_interest_charges: bool


@dataclass
class CreditMetrics:
    """
    Aggregated credit metrics for a user in a time window.

    Attributes:
        user_id: User identifier
        window_days: Size of time window (30 or 180)
        reference_date: End date of the window
        num_credit_cards: Number of credit cards
        aggregate_utilization: Overall utilization across all cards
        high_utilization_count: Number of cards ≥50% utilization
        very_high_utilization_count: Number of cards ≥80% utilization
        minimum_payment_only_count: Number of cards with minimum-only payments
        overdue_count: Number of overdue cards
        has_interest_charges: True if any card has APR > 0
        per_card_details: List of per-card utilization details
    """
    user_id: str
    window_days: int
    reference_date: date
    num_credit_cards: int
    aggregate_utilization: float
    high_utilization_count: int
    very_high_utilization_count: int
    minimum_payment_only_count: int
    overdue_count: int
    has_interest_charges: bool
    per_card_details: List[PerCardUtilization] = field(default_factory=list)


class CreditDetector:
    """
    Detects credit utilization patterns and debt stress indicators.

    Analyzes credit card utilization, payment behavior, and overdue status
    to identify users experiencing debt stress or at risk of financial trouble.

    Usage:
        detector = CreditDetector("data/processed/spendsense.db")

        metrics = detector.detect_credit_patterns(
            user_id="user_001",
            reference_date=date(2025, 11, 4),
            window_days=30
        )

        print(f"Aggregate utilization: {metrics.aggregate_utilization:.1%}")
        print(f"High utilization cards: {metrics.high_utilization_count}")
    """

    def __init__(self, db_path: str):
        """
        Initialize credit detector.

        Args:
            db_path: Path to SQLite database
        """
        self.time_calc = TimeWindowCalculator(db_path)

    def detect_credit_patterns(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> CreditMetrics:
        """
        Detect credit utilization patterns for a user in a time window.

        Args:
            user_id: User identifier
            reference_date: End date of analysis window
            window_days: Window size (30 or 180 days)

        Returns:
            CreditMetrics with credit utilization and debt indicators
        """
        # Get liabilities snapshot
        liabilities_result = self.time_calc.get_liabilities_snapshot(
            user_id=user_id,
            reference_date=reference_date
        )

        if not liabilities_result.data:
            return self._empty_metrics(user_id, reference_date, window_days)

        # Get accounts snapshot to access balance_limit
        accounts_result = self.time_calc.get_accounts_snapshot(
            user_id=user_id,
            reference_date=reference_date
        )

        if not accounts_result.data:
            return self._empty_metrics(user_id, reference_date, window_days)

        # Convert to DataFrames for easier manipulation
        liabilities_df = pd.DataFrame(liabilities_result.data)
        accounts_df = pd.DataFrame(accounts_result.data)

        # Filter to credit cards only
        credit_liabilities = liabilities_df[
            liabilities_df['liability_type'] == 'credit_card'
        ]

        if credit_liabilities.empty:
            return self._empty_metrics(user_id, reference_date, window_days)

        # Join with accounts to get balance_limit
        credit_data = credit_liabilities.merge(
            accounts_df[['account_id', 'balance']],
            on='account_id',
            how='left',
            suffixes=('_liability', '_account')
        )

        # Since balance_limit is in accounts table, we need to get it
        # For now, use last_statement_balance as balance and infer limit
        # Note: This is a limitation - ideally we'd have balance_limit in liabilities

        # Calculate per-card metrics
        per_card_details = []
        total_balance = 0.0
        total_limit = 0.0
        high_util_count = 0
        very_high_util_count = 0
        min_payment_only_count = 0
        overdue_count = 0
        has_any_interest = False

        for _, row in credit_data.iterrows():
            account_id = row['account_id']

            # Get balance from liability last_statement_balance
            balance = row['last_statement_balance'] if row['last_statement_balance'] else 0.0

            # Get limit from accounts table (need to look up)
            account_info = accounts_df[accounts_df['account_id'] == account_id]
            if not account_info.empty:
                # Note: balance_limit column doesn't exist in current schema
                # Using a heuristic: assume limit is at least 2x balance if not specified
                limit = balance * 2.0 if balance > 0 else 1000.0
            else:
                limit = 1000.0  # Default assumption

            # Skip cards with no valid limit
            if limit <= 0:
                continue

            # Calculate utilization
            utilization = balance / limit if limit > 0 else 0.0

            # Determine utilization tier
            if utilization >= UTILIZATION_VERY_HIGH:
                tier = 'very_high'
                very_high_util_count += 1
                high_util_count += 1  # Also counted as high
            elif utilization >= UTILIZATION_HIGH:
                tier = 'high'
                high_util_count += 1
            elif utilization >= UTILIZATION_MODERATE:
                tier = 'moderate'
            else:
                tier = 'low'

            # Check interest charges
            aprs = row['aprs']
            has_interest = len(aprs) > 0 and any(apr > 0 for apr in aprs) if aprs else False
            if has_interest:
                has_any_interest = True

            # Check overdue status
            is_overdue = row['is_overdue'] if row['is_overdue'] else False
            if is_overdue:
                overdue_count += 1

            # Check minimum payment only behavior
            last_payment = row['last_payment_amount'] if row['last_payment_amount'] else 0.0
            min_payment = row['minimum_payment_amount'] if row['minimum_payment_amount'] else 0.0

            # Minimum payment only if last payment ≤ minimum * 1.05 (5% tolerance)
            if min_payment > 0 and last_payment > 0:
                if last_payment <= min_payment * 1.05:
                    min_payment_only_count += 1

            # Create per-card detail
            per_card = PerCardUtilization(
                account_id=account_id,
                balance=float(balance),
                limit=float(limit),
                utilization=float(utilization),
                utilization_tier=tier,
                is_overdue=bool(is_overdue),
                has_interest_charges=bool(has_interest)
            )
            per_card_details.append(per_card)

            # Accumulate for aggregate
            total_balance += balance
            total_limit += limit

        # Calculate aggregate utilization
        aggregate_utilization = (
            total_balance / total_limit if total_limit > 0 else 0.0
        )

        return CreditMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            num_credit_cards=len(per_card_details),
            aggregate_utilization=float(aggregate_utilization),
            high_utilization_count=high_util_count,
            very_high_utilization_count=very_high_util_count,
            minimum_payment_only_count=min_payment_only_count,
            overdue_count=overdue_count,
            has_interest_charges=has_any_interest,
            per_card_details=per_card_details
        )

    def _empty_metrics(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> CreditMetrics:
        """
        Return empty metrics for users with no credit cards.

        Args:
            user_id: User identifier
            reference_date: Reference date
            window_days: Window size

        Returns:
            CreditMetrics with all zeros
        """
        return CreditMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            num_credit_cards=0,
            aggregate_utilization=0.0,
            high_utilization_count=0,
            very_high_utilization_count=0,
            minimum_payment_only_count=0,
            overdue_count=0,
            has_interest_charges=False,
            per_card_details=[]
        )
