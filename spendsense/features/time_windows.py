"""
Time window aggregation framework for behavioral signal detection.

This module provides standardized time window calculations supporting
30-day and 180-day analysis periods for consistent behavioral signal
computation across different time horizons.
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.ingestion.database_writer import User, Account, Transaction, Liability


class TimeWindowResult:
    """
    Result container for time window queries with metadata.

    Attributes:
        data: The filtered dataset (DataFrame or list)
        window_start: Start date of the time window
        window_end: End date of the time window
        is_complete: True if sufficient data exists for full window
        record_count: Number of records in the result
    """

    def __init__(
        self,
        data,
        window_start: date,
        window_end: date,
        is_complete: bool,
        record_count: int
    ):
        self.data = data
        self.window_start = window_start
        self.window_end = window_end
        self.is_complete = is_complete
        self.record_count = record_count

    def __repr__(self):
        return (
            f"TimeWindowResult(start={self.window_start}, end={self.window_end}, "
            f"records={self.record_count}, complete={self.is_complete})"
        )


class TimeWindowCalculator:
    """
    Calculator for time-windowed queries on financial data.

    Provides consistent date arithmetic and filtering logic for
    behavioral signal detection across 30-day and 180-day windows.

    Usage:
        calculator = TimeWindowCalculator("data/processed/spendsense.db")

        # Get transactions in 30-day window
        result = calculator.get_transactions_in_window(
            user_id="user_001",
            reference_date=date(2025, 11, 4),
            window_days=30
        )

        if result.is_complete:
            # Analyze result.data DataFrame
            print(f"Found {result.record_count} transactions")
    """

    SUPPORTED_WINDOWS = [30, 180]

    def __init__(self, db_path: str):
        """
        Initialize time window calculator.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {db_path}")

        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.Session = sessionmaker(bind=self.engine)

    def _calculate_window_bounds(
        self,
        reference_date: date,
        window_days: int
    ) -> Tuple[date, date]:
        """
        Calculate window start and end dates.

        Args:
            reference_date: End date of the window (inclusive)
            window_days: Number of days to look back (30 or 180)

        Returns:
            Tuple of (window_start, window_end)

        Raises:
            ValueError: If reference_date is in the future or window_days invalid
        """
        if reference_date > date.today():
            raise ValueError(
                f"Reference date {reference_date} cannot be in the future"
            )

        if window_days not in self.SUPPORTED_WINDOWS:
            raise ValueError(
                f"Window must be one of {self.SUPPORTED_WINDOWS}, got {window_days}"
            )

        window_start = reference_date - timedelta(days=window_days)
        window_end = reference_date

        return window_start, window_end

    def get_transactions_in_window(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> TimeWindowResult:
        """
        Get all transactions for a user within the specified time window.

        Args:
            user_id: User identifier
            reference_date: End date of the window (inclusive)
            window_days: Number of days to look back (30 or 180)

        Returns:
            TimeWindowResult containing filtered transactions DataFrame

        Example:
            result = calc.get_transactions_in_window("user_001", date(2025,11,4), 30)
            df = result.data
            print(f"Found {len(df)} transactions")
            print(f"Date range: {result.window_start} to {result.window_end}")
        """
        window_start, window_end = self._calculate_window_bounds(
            reference_date, window_days
        )

        session = self.Session()
        try:
            # Get user's accounts
            accounts = session.query(Account).filter(
                Account.user_id == user_id
            ).all()

            if not accounts:
                # User has no accounts
                return TimeWindowResult(
                    data=pd.DataFrame(),
                    window_start=window_start,
                    window_end=window_end,
                    is_complete=False,
                    record_count=0
                )

            account_ids = [acc.account_id for acc in accounts]

            # Get transactions in window
            transactions = session.query(Transaction).filter(
                Transaction.account_id.in_(account_ids),
                Transaction.date >= window_start.isoformat(),
                Transaction.date <= window_end.isoformat()
            ).all()

            # Convert to DataFrame
            if transactions:
                df = pd.DataFrame([{
                    'transaction_id': t.transaction_id,
                    'account_id': t.account_id,
                    'date': t.date if isinstance(t.date, date) else datetime.strptime(t.date, '%Y-%m-%d').date(),
                    'amount': float(t.amount),
                    'merchant_name': t.merchant_name,
                    'category': t.personal_finance_category,
                    'payment_channel': t.payment_channel,
                    'pending': t.pending
                } for t in transactions])
            else:
                df = pd.DataFrame()

            # Check if we have data from window start
            is_complete = False
            if not df.empty:
                earliest_txn = df['date'].min()
                # Complete if we have data from near the start of window
                # (within 7 days tolerance)
                is_complete = earliest_txn <= (window_start + timedelta(days=7))

            return TimeWindowResult(
                data=df,
                window_start=window_start,
                window_end=window_end,
                is_complete=is_complete,
                record_count=len(df)
            )

        finally:
            session.close()

    def get_accounts_snapshot(
        self,
        user_id: str,
        reference_date: date
    ) -> TimeWindowResult:
        """
        Get account balances as of the reference date.

        Note: This returns current account balances since we don't track
        historical balance snapshots in the current schema. For proper
        point-in-time balances, we would need to reconstruct from transactions.

        Args:
            user_id: User identifier
            reference_date: Date for snapshot

        Returns:
            TimeWindowResult containing list of Account objects
        """
        if reference_date > date.today():
            raise ValueError(
                f"Reference date {reference_date} cannot be in the future"
            )

        session = self.Session()
        try:
            accounts = session.query(Account).filter(
                Account.user_id == user_id
            ).all()

            # Convert to list of dicts for consistent interface
            account_list = [{
                'account_id': acc.account_id,
                'user_id': acc.user_id,
                'type': acc.type,
                'subtype': acc.subtype,
                'balance': float(acc.balance_current) if acc.balance_current else 0.0
            } for acc in accounts]

            return TimeWindowResult(
                data=account_list,
                window_start=reference_date,
                window_end=reference_date,
                is_complete=len(accounts) > 0,
                record_count=len(accounts)
            )

        finally:
            session.close()

    def get_liabilities_snapshot(
        self,
        user_id: str,
        reference_date: date
    ) -> TimeWindowResult:
        """
        Get liability data as of the reference date.

        Args:
            user_id: User identifier
            reference_date: Date for snapshot

        Returns:
            TimeWindowResult containing liability data
        """
        if reference_date > date.today():
            raise ValueError(
                f"Reference date {reference_date} cannot be in the future"
            )

        session = self.Session()
        try:
            # Get user's accounts first
            accounts = session.query(Account).filter(
                Account.user_id == user_id
            ).all()

            if not accounts:
                return TimeWindowResult(
                    data=[],
                    window_start=reference_date,
                    window_end=reference_date,
                    is_complete=False,
                    record_count=0
                )

            account_ids = [acc.account_id for acc in accounts]

            # Get liabilities for user's accounts
            liabilities = session.query(Liability).filter(
                Liability.account_id.in_(account_ids)
            ).all()

            # Convert to list of dicts
            liability_list = [{
                'account_id': lib.account_id,
                'liability_type': lib.liability_type,
                'aprs': lib.aprs,
                'is_overdue': lib.is_overdue,
                'last_payment_amount': float(lib.last_payment_amount) if lib.last_payment_amount else None,
                'minimum_payment_amount': float(lib.minimum_payment_amount) if lib.minimum_payment_amount else None,
                'last_statement_balance': float(lib.last_statement_balance) if lib.last_statement_balance else None,
                'next_payment_due_date': lib.next_payment_due_date
            } for lib in liabilities]

            return TimeWindowResult(
                data=liability_list,
                window_start=reference_date,
                window_end=reference_date,
                is_complete=len(liabilities) > 0,
                record_count=len(liabilities)
            )

        finally:
            session.close()


def get_default_fallback_values() -> dict:
    """
    Get default fallback values for users with insufficient data.

    Returns:
        Dictionary of default values for behavioral metrics
    """
    return {
        'subscription_count': 0,
        'subscription_spend': 0.0,
        'subscription_share': 0.0,
        'savings_growth_rate': 0.0,
        'emergency_fund_months': 0.0,
        'credit_utilization': 0.0,
        'is_overdue': False,
        'payment_frequency_days': None,
        'income_variability': 0.0,
        'data_completeness': 'insufficient'
    }
