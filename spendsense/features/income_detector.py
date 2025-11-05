"""
Income stability and pattern detection from transaction data.

This module detects payroll patterns, payment frequency, and income variability
to help identify users with variable income who need specialized budgeting guidance.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import List
import pandas as pd
import numpy as np

from spendsense.features.time_windows import TimeWindowCalculator


# Minimum income amount to consider (filter out small credits)
MIN_INCOME_AMOUNT = 500.0

# Payment frequency classifications (in days)
WEEKLY_MIN, WEEKLY_MAX = 5, 9
BIWEEKLY_MIN, BIWEEKLY_MAX = 12, 16
MONTHLY_MIN, MONTHLY_MAX = 28, 32


@dataclass
class IncomeMetrics:
    """
    Aggregated income metrics for a user in a time window.

    Attributes:
        user_id: User identifier
        window_days: Size of time window (30 or 180)
        reference_date: End date of the window
        num_income_transactions: Number of detected income transactions
        total_income: Total income received in window
        avg_income_per_payment: Average income per payment
        payment_frequency: Classification ('weekly', 'biweekly', 'monthly', 'irregular')
        median_pay_gap_days: Median days between payments
        income_variability_cv: Coefficient of variation (std/mean)
        cash_flow_buffer_months: Liquid balance / monthly expenses
        has_regular_income: True if regular pattern detected
        payroll_dates: List of detected payroll transaction dates
    """
    user_id: str
    window_days: int
    reference_date: date
    num_income_transactions: int
    total_income: float
    avg_income_per_payment: float
    payment_frequency: str
    median_pay_gap_days: float
    income_variability_cv: float
    cash_flow_buffer_months: float
    has_regular_income: bool
    payroll_dates: List[date] = field(default_factory=list)


class IncomeDetector:
    """
    Detects income stability patterns from transaction data.

    Analyzes payroll transaction patterns, payment frequency, and income
    variability to identify users with regular vs. irregular income streams.

    Usage:
        detector = IncomeDetector("data/processed/spendsense.db")

        metrics = detector.detect_income_patterns(
            user_id="user_001",
            reference_date=date(2025, 11, 4),
            window_days=180
        )

        print(f"Payment frequency: {metrics.payment_frequency}")
        print(f"Income variability: {metrics.income_variability_cv:.2f}")
    """

    def __init__(self, db_path: str):
        """
        Initialize income detector.

        Args:
            db_path: Path to SQLite database
        """
        self.time_calc = TimeWindowCalculator(db_path)

    def detect_income_patterns(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> IncomeMetrics:
        """
        Detect income stability patterns for a user in a time window.

        Args:
            user_id: User identifier
            reference_date: End date of analysis window
            window_days: Window size (30 or 180 days)

        Returns:
            IncomeMetrics with income pattern indicators
        """
        # Get transactions in window
        window_result = self.time_calc.get_transactions_in_window(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days
        )

        if window_result.data.empty:
            return self._empty_metrics(user_id, reference_date, window_days)

        # Detect payroll transactions
        income_txns = self._detect_payroll_transactions(window_result.data)

        if income_txns.empty or len(income_txns) < 2:
            # Need at least 2 income transactions to establish pattern
            return self._empty_metrics(user_id, reference_date, window_days)

        # Calculate metrics
        total_income = income_txns['amount'].sum()
        avg_income = income_txns['amount'].mean()
        num_income = len(income_txns)

        # Calculate payment frequency
        pay_gaps = self._calculate_pay_gaps(income_txns)
        median_gap = np.median(pay_gaps) if pay_gaps else 0.0
        frequency = self._classify_frequency(median_gap, pay_gaps)
        has_regular = frequency != 'irregular'

        # Calculate income variability
        income_cv = (
            income_txns['amount'].std() / avg_income
            if avg_income > 0 else 0.0
        )

        # Calculate cash flow buffer
        cash_buffer = self._calculate_cash_flow_buffer(
            user_id=user_id,
            reference_date=reference_date,
            window_days=window_days,
            transactions=window_result.data
        )

        # Extract payroll dates
        payroll_dates = sorted(income_txns['date'].tolist())

        return IncomeMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            num_income_transactions=num_income,
            total_income=float(total_income),
            avg_income_per_payment=float(avg_income),
            payment_frequency=frequency,
            median_pay_gap_days=float(median_gap),
            income_variability_cv=float(income_cv),
            cash_flow_buffer_months=float(cash_buffer),
            has_regular_income=has_regular,
            payroll_dates=payroll_dates
        )

    def _detect_payroll_transactions(self, transactions: pd.DataFrame) -> pd.DataFrame:
        """
        Detect payroll transactions from transaction data.

        Args:
            transactions: All transactions in window

        Returns:
            DataFrame of income transactions
        """
        if transactions.empty:
            return pd.DataFrame()

        # Filter for positive (credit) transactions
        income_txns = transactions[transactions['amount'] > 0].copy()

        if income_txns.empty:
            return pd.DataFrame()

        # Filter by INCOME category or large regular deposits
        # Income categories might include: INCOME, PAYROLL, etc.
        income_categories = income_txns[
            income_txns['category'].str.contains('INCOME', case=False, na=False)
        ]

        # Also include large deposits (≥ MIN_INCOME_AMOUNT) even if not categorized
        large_deposits = income_txns[income_txns['amount'] >= MIN_INCOME_AMOUNT]

        # Combine and deduplicate
        combined = pd.concat([income_categories, large_deposits]).drop_duplicates()

        # Sort by date
        combined = combined.sort_values('date')

        return combined

    def _calculate_pay_gaps(self, income_txns: pd.DataFrame) -> List[float]:
        """
        Calculate time gaps between income transactions.

        Args:
            income_txns: Income transactions DataFrame (sorted by date)

        Returns:
            List of gaps in days
        """
        if len(income_txns) < 2:
            return []

        dates = income_txns['date'].values
        gaps = []

        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days
            gaps.append(gap)

        return gaps

    def _classify_frequency(
        self,
        median_gap: float,
        gaps: List[float]
    ) -> str:
        """
        Classify payment frequency based on gaps.

        Args:
            median_gap: Median days between payments
            gaps: List of all gaps

        Returns:
            Frequency classification string
        """
        if not gaps:
            return 'irregular'

        # Calculate variability in gaps
        gap_std = np.std(gaps) if len(gaps) > 1 else 0.0

        # High variability = irregular
        if gap_std > 7:  # More than 1 week variation
            return 'irregular'

        # Classify by median gap
        if WEEKLY_MIN <= median_gap <= WEEKLY_MAX:
            return 'weekly'
        elif BIWEEKLY_MIN <= median_gap <= BIWEEKLY_MAX:
            return 'biweekly'
        elif MONTHLY_MIN <= median_gap <= MONTHLY_MAX:
            return 'monthly'
        else:
            return 'irregular'

    def _calculate_cash_flow_buffer(
        self,
        user_id: str,
        reference_date: date,
        window_days: int,
        transactions: pd.DataFrame
    ) -> float:
        """
        Calculate cash flow buffer in months.

        Args:
            user_id: User identifier
            reference_date: Reference date
            window_days: Window size
            transactions: All transactions

        Returns:
            Cash flow buffer in months
        """
        # Get liquid account balances
        accounts_result = self.time_calc.get_accounts_snapshot(
            user_id=user_id,
            reference_date=reference_date
        )

        if not accounts_result.data:
            return 0.0

        accounts_df = pd.DataFrame(accounts_result.data)

        # Sum checking and savings accounts (liquid assets)
        liquid_types = {'checking', 'savings'}
        liquid_accounts = accounts_df[accounts_df['type'].isin(liquid_types)]

        total_liquid = liquid_accounts['balance'].sum() if not liquid_accounts.empty else 0.0

        # Calculate monthly expenses
        if transactions.empty:
            return 0.0

        debits = transactions[transactions['amount'] < 0]
        if debits.empty:
            return 0.0

        total_expenses = debits['amount'].abs().sum()
        months_in_window = window_days / 30.0
        monthly_expenses = total_expenses / months_in_window

        if monthly_expenses <= 0:
            return 0.0

        return total_liquid / monthly_expenses

    def _empty_metrics(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> IncomeMetrics:
        """
        Return empty metrics for users with insufficient income data.

        Args:
            user_id: User identifier
            reference_date: Reference date
            window_days: Window size

        Returns:
            IncomeMetrics with zeros/defaults
        """
        return IncomeMetrics(
            user_id=user_id,
            window_days=window_days,
            reference_date=reference_date,
            num_income_transactions=0,
            total_income=0.0,
            avg_income_per_payment=0.0,
            payment_frequency='unknown',
            median_pay_gap_days=0.0,
            income_variability_cv=0.0,
            cash_flow_buffer_months=0.0,
            has_regular_income=False,
            payroll_dates=[]
        )
