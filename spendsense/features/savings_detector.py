"""
Savings behavior pattern detection from account and transaction data.

This module detects savings patterns by analyzing account growth, net inflow,
and emergency fund coverage to identify users building financial resilience.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List
import pandas as pd
import numpy as np

from spendsense.features.time_windows import TimeWindowCalculator


# Savings account types per story requirements
SAVINGS_ACCOUNT_TYPES = {
    'savings',
    'money_market',
    'cd',  # certificate of deposit
    'hsa'  # health savings account
}


@dataclass
class SavingsMetrics:
    """
    Aggregated savings metrics for a user in a time window.

    Attributes:
        user_id: User identifier
        window_days: Size of time window (30 or 180)
        reference_date: End date of the window
        net_inflow: Net deposits minus withdrawals to savings accounts
        savings_growth_rate: Percentage change in savings balance
        emergency_fund_months: Months of expenses covered by savings
        total_savings_balance: Current total savings balance
        avg_monthly_expenses: Average monthly spending
        has_savings_accounts: True if user has any savings accounts
    """
    user_id: str
    window_days: int
    reference_date: date
    net_inflow: float
    savings_growth_rate: float
    emergency_fund_months: float
    total_savings_balance: float
    avg_monthly_expenses: float
    has_savings_accounts: bool


class SavingsDetector:
    """
    Detects savings behavior patterns in account and transaction data.

    Analyzes savings account growth, inflow patterns, and emergency fund
    coverage to identify users actively building financial resilience.

    Usage:
        detector = SavingsDetector("data/processed/spendsense.db")

        metrics = detector.detect_savings_patterns(
            user_id="user_001",
            reference_date=date(2025, 11, 4),
            window_days=30
        )

        print(f"Savings growth rate: {metrics.savings_growth_rate:.1%}")
        print(f"Emergency fund: {metrics.emergency_fund_months:.1f} months")
    """

    def __init__(self, db_path: str):
        """
        Initialize savings detector.

        Args:
            db_path: Path to SQLite database
        """
        self.time_calc = TimeWindowCalculator(db_path)

    def detect_savings_patterns(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> SavingsMetrics:
        """
        Detect savings patterns for a user in a time window.

        Args:
            user_id: User identifier
            reference_date: End date of analysis window
            window_days: Window size (30 or 180 days)

        Returns:
            SavingsMetrics with savings behavior indicators
        """
        # Get account snapshot
        accounts_result = self.time_calc.get_accounts_snapshot(
            user_id=user_id,
            reference_date=reference_date
        )

        # Filter to savings accounts
        if not accounts_result.data:
            return self._empty_metrics(user_id, reference_date, window_days)

        accounts_df = pd.DataFrame(accounts_result.data)
        savings_accounts = accounts_df[
            accounts_df['subtype'].isin(SAVINGS_ACCOUNT_TYPES)
        ]

        if savings_accounts.empty:
            return self._empty_metrics(user_id, reference_date, window_days)

        # Calculate total savings balance
        total_savings_balance = savings_accounts['balance'].sum()

        # Get transactions in window
        window_result = self.time_calc.get_transactions_in_window(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days
        )

        # Calculate savings-specific metrics
        net_inflow = self._calculate_net_inflow(
            window_result.data,
            savings_accounts['account_id'].tolist()
        )

        savings_growth_rate = self._calculate_growth_rate(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days,
            current_balance=total_savings_balance
        )

        avg_monthly_expenses = self._calculate_avg_monthly_expenses(
            window_result.data,
            window_days
        )

        emergency_fund_months = self._calculate_emergency_fund_months(
            total_savings_balance,
            avg_monthly_expenses
        )

        return SavingsMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            net_inflow=float(net_inflow),
            savings_growth_rate=float(savings_growth_rate),
            emergency_fund_months=float(emergency_fund_months),
            total_savings_balance=float(total_savings_balance),
            avg_monthly_expenses=float(avg_monthly_expenses),
            has_savings_accounts=True
        )

    def _calculate_net_inflow(
        self,
        transactions: pd.DataFrame,
        savings_account_ids: List[str]
    ) -> float:
        """
        Calculate net inflow to savings accounts (deposits - withdrawals).

        Note: Savings transfers appear as negative amounts on checking accounts
        with merchant_name "Savings Transfer". We need to sum these as positive
        inflows to savings.

        Args:
            transactions: All transactions in window
            savings_account_ids: List of savings account IDs

        Returns:
            Net inflow amount (positive = net deposits)
        """
        if transactions.empty:
            return 0.0

        # Look for savings transfer transactions (from checking TO savings)
        # Check if columns exist before filtering
        has_merchant = 'merchant_name' in transactions.columns
        has_category = 'personal_finance_category' in transactions.columns

        if has_merchant:
            savings_transfers = transactions[
                transactions['merchant_name'].str.contains('Savings Transfer', case=False, na=False)
            ]
        elif has_category:
            savings_transfers = transactions[
                transactions['personal_finance_category'].str.contains('TRANSFER.*SAVINGS', case=False, na=False)
            ]
        else:
            return 0.0

        if savings_transfers.empty:
            return 0.0

        # These are negative on checking side, so negate them to get positive inflow
        net_inflow = -savings_transfers['amount'].sum()

        return net_inflow

    def _calculate_growth_rate(
        self,
        user_id: str,
        reference_date: date,
        window_days: int,
        current_balance: float
    ) -> float:
        """
        Calculate savings growth rate over the window.

        Growth rate = (ending_balance - starting_balance) / starting_balance

        Note: Since we don't have point-in-time historical balances,
        we approximate starting balance by subtracting net inflow from
        current balance. This is a simplification.

        Args:
            user_id: User identifier
            reference_date: End date of window
            window_days: Window size
            current_balance: Current total savings balance

        Returns:
            Growth rate as decimal (0.10 = 10% growth)
        """
        # Get transactions to calculate starting balance
        window_result = self.time_calc.get_transactions_in_window(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days
        )

        if window_result.data.empty:
            return 0.0

        # Get accounts snapshot
        accounts_result = self.time_calc.get_accounts_snapshot(
            user_id=user_id,
            reference_date=reference_date
        )

        if not accounts_result.data:
            return 0.0

        accounts_df = pd.DataFrame(accounts_result.data)
        savings_accounts = accounts_df[
            accounts_df['subtype'].isin(SAVINGS_ACCOUNT_TYPES)
        ]

        if savings_accounts.empty:
            return 0.0

        savings_account_ids = savings_accounts['account_id'].tolist()

        # Calculate net inflow
        net_inflow = self._calculate_net_inflow(
            window_result.data,
            savings_account_ids
        )

        # Approximate starting balance
        starting_balance = current_balance - net_inflow

        # Handle zero or negative starting balance
        if starting_balance <= 0:
            # If starting balance was zero or negative, any positive ending
            # balance represents infinite growth - cap at 100%
            if current_balance > 0:
                return 1.0  # 100% growth
            return 0.0

        # Calculate growth rate
        growth_rate = (current_balance - starting_balance) / starting_balance

        return growth_rate

    def _calculate_avg_monthly_expenses(
        self,
        transactions: pd.DataFrame,
        window_days: int
    ) -> float:
        """
        Calculate average monthly expenses from transaction data.

        Args:
            transactions: All transactions in window
            window_days: Size of the window

        Returns:
            Average monthly expense amount (positive value)
        """
        if transactions.empty:
            return 0.0

        # Get all debit transactions (negative amounts = spending)
        debits = transactions[transactions['amount'] < 0]

        if debits.empty:
            return 0.0

        # Sum total spending (absolute value)
        total_spending = debits['amount'].abs().sum()

        # Convert to monthly average
        months_in_window = window_days / 30.0
        avg_monthly_expenses = total_spending / months_in_window

        return avg_monthly_expenses

    def _calculate_emergency_fund_months(
        self,
        total_savings: float,
        avg_monthly_expenses: float
    ) -> float:
        """
        Calculate emergency fund coverage in months.

        Args:
            total_savings: Total savings balance
            avg_monthly_expenses: Average monthly spending

        Returns:
            Number of months of expenses covered by savings
        """
        if avg_monthly_expenses <= 0:
            # If no expenses tracked, can't calculate coverage
            # Return 0 to avoid division by zero
            return 0.0

        months_coverage = total_savings / avg_monthly_expenses

        return months_coverage

    def _empty_metrics(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> SavingsMetrics:
        """
        Return empty metrics for users with no savings accounts.

        Args:
            user_id: User identifier
            reference_date: Reference date
            window_days: Window size

        Returns:
            SavingsMetrics with all zeros
        """
        return SavingsMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            net_inflow=0.0,
            savings_growth_rate=0.0,
            emergency_fund_months=0.0,
            total_savings_balance=0.0,
            avg_monthly_expenses=0.0,
            has_savings_accounts=False
        )
