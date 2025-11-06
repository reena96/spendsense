"""
Filtering engine for context-aware recommendation filtering.

Filters recommendations based on user's behavioral signals to exclude
irrelevant recommendations.
"""

import logging
from typing import List, Tuple, Optional

from spendsense.recommendations.models import Recommendation
from spendsense.recommendations.generated_models import FilterReason
from spendsense.features.behavioral_summary import BehavioralSummary

logger = logging.getLogger(__name__)


class FilterEngine:
    """
    Context-aware recommendation filter.

    Filters out recommendations that are not relevant to the user's
    current situation based on behavioral signals.

    Usage:
        filter_engine = FilterEngine()
        filtered, reasons = filter_engine.filter(recs, signals, persona_id)
    """

    def __init__(self):
        """Initialize filter engine."""
        self.filter_rules = {
            "emergency_fund_built": self._filter_emergency_fund_built,
            "no_credit_accounts": self._filter_no_credit_accounts,
            "low_subscription_count": self._filter_low_subscription_count,
            "stable_income": self._filter_stable_income,
        }

    def filter(
        self,
        recommendations: List[Recommendation],
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> Tuple[List[Recommendation], List[FilterReason]]:
        """
        Filter recommendations based on user context.

        Args:
            recommendations: Base recommendations from content library
            behavioral_signals: User's behavioral signals
            persona_id: Assigned persona ID

        Returns:
            Tuple of (filtered_recommendations, filter_reasons)

        Example:
            >>> filter_engine = FilterEngine()
            >>> filtered, reasons = filter_engine.filter(recs, signals, "low_savings")
            >>> print(f"Filtered {len(reasons)} recommendations")
        """
        filtered_recs = []
        filter_reasons = []

        for rec in recommendations:
            should_filter, reason = self._should_filter(rec, behavioral_signals, persona_id)

            if should_filter:
                filter_reasons.append(reason)
                logger.debug(f"Filtered: {reason}")
            else:
                filtered_recs.append(rec)

        logger.info(
            f"Filtering: {len(recommendations)} → {len(filtered_recs)} "
            f"({len(filter_reasons)} filtered)"
        )

        return filtered_recs, filter_reasons

    def _should_filter(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> Tuple[bool, Optional[FilterReason]]:
        """
        Check if recommendation should be filtered.

        Args:
            recommendation: Recommendation to check
            behavioral_signals: User's behavioral signals
            persona_id: Assigned persona ID

        Returns:
            Tuple of (should_filter, filter_reason)
        """
        # Apply each filter rule
        for rule_name, rule_func in self.filter_rules.items():
            should_filter, reason = rule_func(recommendation, behavioral_signals, persona_id)
            if should_filter:
                return True, reason

        return False, None

    # === Filter Rules ===

    def _filter_emergency_fund_built(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> Tuple[bool, Optional[FilterReason]]:
        """
        Filter emergency fund recommendations if user has 3+ months saved.

        Logic: If savings_emergency_fund_months >= 3.0, skip emergency fund recs.
        """
        # Emergency fund related recommendation IDs
        emergency_fund_rec_ids = {
            "emergency_fund_start",
            "automate_savings_transfers",
            "emergency_fund_importance",
            "three_month_cushion_goal",
        }

        if recommendation.id not in emergency_fund_rec_ids:
            return False, None

        # Get savings signals (use 30d window)
        savings_signals = behavioral_signals.savings_30d
        if not savings_signals:
            return False, None

        emergency_fund_months = savings_signals.emergency_fund_months

        # Filter if user has 3+ months saved
        if emergency_fund_months >= 3.0:
            return True, FilterReason(
                recommendation_id=recommendation.id,
                reason=f"User has {emergency_fund_months:.1f} months emergency fund (>=3.0 months)",
                rule_name="emergency_fund_built",
                signal_values={
                    "emergency_fund_months": emergency_fund_months,
                },
            )

        return False, None

    def _filter_no_credit_accounts(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> Tuple[bool, Optional[FilterReason]]:
        """
        Filter credit-related recommendations if user has no credit cards.

        Logic: If high_utilization_count == 0, skip credit management recs.
        """
        # Credit-related recommendation IDs
        credit_rec_ids = {
            "understand_credit_utilization",
            "debt_payoff_avalanche",
            "biweekly_payments",
            "request_credit_limit_increase",
            "balance_transfer_zero_apr",
            "debt_payoff_timeline",
            "payment_reminders",
            "monthly_interest_cost",
        }

        if recommendation.id not in credit_rec_ids:
            return False, None

        # Get credit signals (use 30d window)
        credit_signals = behavioral_signals.credit_30d
        if not credit_signals:
            # No credit signals means no credit accounts - filter credit recs
            return True, FilterReason(
                recommendation_id=recommendation.id,
                reason="User has no credit accounts",
                rule_name="no_credit_accounts",
                signal_values={"has_credit_accounts": False},
            )

        high_utilization_count = credit_signals.high_utilization_count
        aggregate_utilization = credit_signals.aggregate_utilization

        # Filter if no credit accounts (utilization count is 0)
        if high_utilization_count == 0 and aggregate_utilization == 0:
            return True, FilterReason(
                recommendation_id=recommendation.id,
                reason="User has no credit card accounts",
                rule_name="no_credit_accounts",
                signal_values={
                    "high_utilization_count": high_utilization_count,
                    "aggregate_utilization": aggregate_utilization,
                },
            )

        return False, None

    def _filter_low_subscription_count(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> Tuple[bool, Optional[FilterReason]]:
        """
        Filter subscription recommendations if user has <5 subscriptions.

        Logic: If subscription_count < 5, skip subscription optimization recs.
        """
        # Subscription-related recommendation IDs
        subscription_rec_ids = {
            "audit_all_subscriptions",
            "cancel_unused_services",
            "subscription_management_tool",
            "negotiate_better_rates",
            "spending_alerts_recurring",
            "subscription_spending_psychology",
            "total_monthly_subscription_cost",
        }

        if recommendation.id not in subscription_rec_ids:
            return False, None

        # Get subscription signals (use 30d window)
        subscription_signals = behavioral_signals.subscriptions_30d
        if not subscription_signals:
            return False, None

        subscription_count = subscription_signals.subscription_count

        # Filter if user has <5 subscriptions
        if subscription_count < 5:
            return True, FilterReason(
                recommendation_id=recommendation.id,
                reason=f"User has only {subscription_count} subscriptions (<5)",
                rule_name="low_subscription_count",
                signal_values={"subscription_count": subscription_count},
            )

        return False, None

    def _filter_stable_income(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> Tuple[bool, Optional[FilterReason]]:
        """
        Filter irregular income recommendations if income is stable.

        Logic: If payment_frequency is "biweekly" or "monthly", skip irregular income recs.
        """
        # Irregular income recommendation IDs
        irregular_income_rec_ids = {
            "variable_income_budgeting",
            "build_larger_emergency_fund",
            "income_averaging_strategy",
            "percentage_based_budgeting",
            "set_aside_estimated_taxes",
            "gig_economy_financial_planning",
            "income_variability_analysis",
        }

        if recommendation.id not in irregular_income_rec_ids:
            return False, None

        # Get income signals (use 30d window)
        income_signals = behavioral_signals.income_30d
        if not income_signals:
            return False, None

        payment_frequency = income_signals.payment_frequency

        # Filter if income is stable (biweekly or monthly)
        stable_frequencies = {"biweekly", "monthly"}
        if payment_frequency in stable_frequencies:
            return True, FilterReason(
                recommendation_id=recommendation.id,
                reason=f"User has stable income ({payment_frequency})",
                rule_name="stable_income",
                signal_values={"payment_frequency": payment_frequency},
            )

        return False, None
