"""
Behavioral summary aggregation combining all detected signals.

This module generates comprehensive behavioral summaries per user by aggregating
subscription, savings, credit, and income signals across multiple time windows.
"""

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Dict, List
import logging

from spendsense.features.subscription_detector import SubscriptionDetector, SubscriptionMetrics
from spendsense.features.savings_detector import SavingsDetector, SavingsMetrics
from spendsense.features.credit_detector import CreditDetector, CreditMetrics
from spendsense.features.income_detector import IncomeDetector, IncomeMetrics


logger = logging.getLogger(__name__)


@dataclass
class BehavioralSummary:
    """
    Comprehensive behavioral summary combining all signals.

    Attributes:
        user_id: User identifier
        generated_at: Timestamp when summary was generated
        reference_date: End date for analysis windows

        subscriptions_30d: Subscription metrics for 30-day window
        subscriptions_180d: Subscription metrics for 180-day window

        savings_30d: Savings metrics for 30-day window
        savings_180d: Savings metrics for 180-day window

        credit_30d: Credit metrics for 30-day window
        credit_180d: Credit metrics for 180-day window

        income_30d: Income metrics for 30-day window
        income_180d: Income metrics for 180-day window

        data_completeness: Flags indicating data availability per detector
        fallbacks_applied: List of detectors that returned empty/default values
    """
    user_id: str
    generated_at: datetime
    reference_date: date

    # Subscription signals
    subscriptions_30d: SubscriptionMetrics
    subscriptions_180d: SubscriptionMetrics

    # Savings signals
    savings_30d: SavingsMetrics
    savings_180d: SavingsMetrics

    # Credit signals
    credit_30d: CreditMetrics
    credit_180d: CreditMetrics

    # Income signals
    income_30d: IncomeMetrics
    income_180d: IncomeMetrics

    # Metadata
    data_completeness: Dict[str, bool]
    fallbacks_applied: List[str]

    def to_dict(self) -> dict:
        """
        Convert summary to dictionary for JSON serialization.

        Returns:
            Dictionary representation of the summary
        """
        def convert_dates(obj):
            """Recursively convert date objects to ISO format strings."""
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_dates(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_dates(item) for item in obj]
            else:
                return obj

        result = {
            'user_id': self.user_id,
            'generated_at': self.generated_at.isoformat(),
            'reference_date': self.reference_date.isoformat(),

            # Subscription signals
            'subscriptions': {
                '30d': convert_dates(asdict(self.subscriptions_30d)),
                '180d': convert_dates(asdict(self.subscriptions_180d))
            },

            # Savings signals
            'savings': {
                '30d': convert_dates(asdict(self.savings_30d)),
                '180d': convert_dates(asdict(self.savings_180d))
            },

            # Credit signals
            'credit': {
                '30d': convert_dates(asdict(self.credit_30d)),
                '180d': convert_dates(asdict(self.credit_180d))
            },

            # Income signals
            'income': {
                '30d': convert_dates(asdict(self.income_30d)),
                '180d': convert_dates(asdict(self.income_180d))
            },

            # Metadata
            'metadata': {
                'data_completeness': self.data_completeness,
                'fallbacks_applied': self.fallbacks_applied
            }
        }

        return result


class BehavioralSummaryGenerator:
    """
    Generates comprehensive behavioral summaries per user.

    Aggregates signals from all behavioral detectors (subscription, savings,
    credit, income) across multiple time windows to provide complete feature
    set for persona classification and recommendations.

    Usage:
        generator = BehavioralSummaryGenerator("data/processed/spendsense.db")

        summary = generator.generate_summary(
            user_id="user_001",
            reference_date=date(2025, 11, 4)
        )

        # Convert to JSON
        summary_dict = summary.to_dict()
    """

    def __init__(self, db_path: str):
        """
        Initialize behavioral summary generator.

        Args:
            db_path: Path to SQLite database
        """
        self.subscription_detector = SubscriptionDetector(db_path)
        self.savings_detector = SavingsDetector(db_path)
        self.credit_detector = CreditDetector(db_path)
        self.income_detector = IncomeDetector(db_path)

    def generate_summary(
        self,
        user_id: str,
        reference_date: date
    ) -> BehavioralSummary:
        """
        Generate comprehensive behavioral summary for a user.

        Args:
            user_id: User identifier
            reference_date: End date for analysis windows

        Returns:
            BehavioralSummary with all detected signals
        """
        logger.info(f"Generating behavioral summary for user {user_id}")
        start_time = datetime.now()

        # Track data completeness and fallbacks
        data_completeness = {}
        fallbacks_applied = []

        # Detect subscriptions (30 and 180 days)
        try:
            subscriptions_30d = self.subscription_detector.detect_subscriptions(
                user_id=user_id,
                reference_date=reference_date,
                window_days=30
            )
            subscriptions_180d = self.subscription_detector.detect_subscriptions(
                user_id=user_id,
                reference_date=reference_date,
                window_days=180
            )

            # Check if data is complete
            has_subscriptions = subscriptions_30d.subscription_count > 0 or subscriptions_180d.subscription_count > 0
            data_completeness['subscriptions'] = has_subscriptions

            if not has_subscriptions:
                fallbacks_applied.append('subscriptions')

        except Exception as e:
            logger.error(f"Error detecting subscriptions for {user_id}: {e}")
            # Return empty metrics on error
            subscriptions_30d = SubscriptionMetrics(
                user_id=user_id, window_days=30, reference_date=reference_date,
                subscription_count=0, monthly_recurring_spend=0.0,
                total_spend=0.0, subscription_share=0.0, detected_subscriptions=[]
            )
            subscriptions_180d = SubscriptionMetrics(
                user_id=user_id, window_days=180, reference_date=reference_date,
                subscription_count=0, monthly_recurring_spend=0.0,
                total_spend=0.0, subscription_share=0.0, detected_subscriptions=[]
            )
            data_completeness['subscriptions'] = False
            fallbacks_applied.append('subscriptions')

        # Detect savings (30 and 180 days)
        try:
            savings_30d = self.savings_detector.detect_savings_patterns(
                user_id=user_id,
                reference_date=reference_date,
                window_days=30
            )
            savings_180d = self.savings_detector.detect_savings_patterns(
                user_id=user_id,
                reference_date=reference_date,
                window_days=180
            )

            # Check if data is complete
            has_savings = savings_30d.has_savings_accounts or savings_180d.has_savings_accounts
            data_completeness['savings'] = has_savings

            if not has_savings:
                fallbacks_applied.append('savings')

        except Exception as e:
            logger.error(f"Error detecting savings for {user_id}: {e}")
            savings_30d = SavingsMetrics(
                user_id=user_id, window_days=30, reference_date=reference_date,
                net_inflow=0.0, savings_growth_rate=0.0, emergency_fund_months=0.0,
                total_savings_balance=0.0, avg_monthly_expenses=0.0, has_savings_accounts=False
            )
            savings_180d = SavingsMetrics(
                user_id=user_id, window_days=180, reference_date=reference_date,
                net_inflow=0.0, savings_growth_rate=0.0, emergency_fund_months=0.0,
                total_savings_balance=0.0, avg_monthly_expenses=0.0, has_savings_accounts=False
            )
            data_completeness['savings'] = False
            fallbacks_applied.append('savings')

        # Detect credit (30 and 180 days)
        try:
            credit_30d = self.credit_detector.detect_credit_patterns(
                user_id=user_id,
                reference_date=reference_date,
                window_days=30
            )
            credit_180d = self.credit_detector.detect_credit_patterns(
                user_id=user_id,
                reference_date=reference_date,
                window_days=180
            )

            # Check if data is complete
            has_credit = credit_30d.num_credit_cards > 0 or credit_180d.num_credit_cards > 0
            data_completeness['credit'] = has_credit

            if not has_credit:
                fallbacks_applied.append('credit')

        except Exception as e:
            logger.error(f"Error detecting credit for {user_id}: {e}")
            credit_30d = CreditMetrics(
                user_id=user_id, window_days=30, reference_date=reference_date,
                num_credit_cards=0, aggregate_utilization=0.0, high_utilization_count=0,
                very_high_utilization_count=0, minimum_payment_only_count=0,
                overdue_count=0, has_interest_charges=False, per_card_details=[]
            )
            credit_180d = CreditMetrics(
                user_id=user_id, window_days=180, reference_date=reference_date,
                num_credit_cards=0, aggregate_utilization=0.0, high_utilization_count=0,
                very_high_utilization_count=0, minimum_payment_only_count=0,
                overdue_count=0, has_interest_charges=False, per_card_details=[]
            )
            data_completeness['credit'] = False
            fallbacks_applied.append('credit')

        # Detect income (30 and 180 days)
        try:
            income_30d = self.income_detector.detect_income_patterns(
                user_id=user_id,
                reference_date=reference_date,
                window_days=30
            )
            income_180d = self.income_detector.detect_income_patterns(
                user_id=user_id,
                reference_date=reference_date,
                window_days=180
            )

            # Check if data is complete
            has_income = income_30d.num_income_transactions > 0 or income_180d.num_income_transactions > 0
            data_completeness['income'] = has_income

            if not has_income:
                fallbacks_applied.append('income')

        except Exception as e:
            logger.error(f"Error detecting income for {user_id}: {e}")
            income_30d = IncomeMetrics(
                user_id=user_id, window_days=30, reference_date=reference_date,
                num_income_transactions=0, total_income=0.0, avg_income_per_payment=0.0,
                payment_frequency='unknown', median_pay_gap_days=0.0, income_variability_cv=0.0,
                cash_flow_buffer_months=0.0, has_regular_income=False, payroll_dates=[]
            )
            income_180d = IncomeMetrics(
                user_id=user_id, window_days=180, reference_date=reference_date,
                num_income_transactions=0, total_income=0.0, avg_income_per_payment=0.0,
                payment_frequency='unknown', median_pay_gap_days=0.0, income_variability_cv=0.0,
                cash_flow_buffer_months=0.0, has_regular_income=False, payroll_dates=[]
            )
            data_completeness['income'] = False
            fallbacks_applied.append('income')

        # Create summary
        summary = BehavioralSummary(
            user_id=user_id,
            generated_at=datetime.now(),
            reference_date=reference_date,
            subscriptions_30d=subscriptions_30d,
            subscriptions_180d=subscriptions_180d,
            savings_30d=savings_30d,
            savings_180d=savings_180d,
            credit_30d=credit_30d,
            credit_180d=credit_180d,
            income_30d=income_30d,
            income_180d=income_180d,
            data_completeness=data_completeness,
            fallbacks_applied=fallbacks_applied
        )

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Generated summary for {user_id} in {elapsed:.2f}s")

        return summary
