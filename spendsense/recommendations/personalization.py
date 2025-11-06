"""
Personalization engine for template-based recommendation customization.

Substitutes signal values into recommendation templates to create
personalized descriptions.
"""

import logging
import re
from typing import Dict, Any, Tuple, Optional

from spendsense.recommendations.models import Recommendation
from spendsense.features.behavioral_summary import BehavioralSummary

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """
    Template-based personalization engine.

    Substitutes behavioral signal values into recommendation templates
    to create personalized descriptions.

    Usage:
        personalizer = PersonalizationEngine()
        description, substitutions = personalizer.personalize(rec, signals)
    """

    # Regex to find {placeholder} patterns
    PLACEHOLDER_PATTERN = re.compile(r'\{([a-z_0-9]+)\}')

    def __init__(self):
        """Initialize personalization engine."""
        pass

    def personalize(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Personalize recommendation description using template substitution.

        Args:
            recommendation: Base recommendation with optional template
            behavioral_signals: User's behavioral signals

        Returns:
            Tuple of (personalized_description, substitutions_dict)
            If no template or substitution fails, returns original description

        Example:
            >>> personalizer = PersonalizationEngine()
            >>> template = "You have {subscription_count} subscriptions"
            >>> desc, subs = personalizer.personalize(rec_with_template, signals)
            >>> print(desc)  # "You have 23 subscriptions"
            >>> print(subs)  # {"subscription_count": 23}
        """
        # No template, return original
        if not recommendation.personalization_template:
            return recommendation.description, {}

        template = recommendation.personalization_template
        substitutions = {}

        try:
            # Find all placeholders in template
            placeholders = self.PLACEHOLDER_PATTERN.findall(template)

            if not placeholders:
                logger.debug(f"No placeholders found in template for {recommendation.id}")
                return recommendation.description, {}

            # Get values for each placeholder
            personalized = template
            for placeholder in placeholders:
                value = self._get_signal_value(placeholder, behavioral_signals)

                if value is None:
                    logger.warning(
                        f"Signal '{placeholder}' not found for {recommendation.id}, "
                        f"using original description"
                    )
                    return recommendation.description, {}

                # Format value appropriately
                formatted_value = self._format_value(placeholder, value)
                substitutions[placeholder] = value

                # Replace placeholder in template
                personalized = personalized.replace(f"{{{placeholder}}}", str(formatted_value))

            logger.debug(
                f"Personalized {recommendation.id}: "
                f"{len(substitutions)} substitutions made"
            )

            return personalized, substitutions

        except Exception as e:
            logger.error(
                f"Personalization failed for {recommendation.id}: {e}, "
                f"using original description"
            )
            return recommendation.description, {}

    def _get_signal_value(
        self,
        placeholder: str,
        behavioral_signals: BehavioralSummary,
    ) -> Optional[Any]:
        """
        Get signal value for placeholder.

        Args:
            placeholder: Placeholder name (e.g., "subscription_count")
            behavioral_signals: User's behavioral signals

        Returns:
            Signal value or None if not found

        Signal mapping:
            - credit_max_utilization_pct: aggregate_utilization * 100
            - credit_total_balance: Sum of credit balances (estimated)
            - savings_total_balance: total_savings_balance
            - savings_emergency_fund_months: emergency_fund_months
            - subscription_count: subscription_count
            - subscription_share: subscription_share * 100
            - monthly_expenses: Estimated from spending
            - income_payment_frequency: payment_frequency
            - transaction_history_days: Calculated from signals
            - credit_total_limits: Estimated from credit data
        """
        try:
            # Credit signals (use 30d window)
            if placeholder == "credit_max_utilization_pct":
                if behavioral_signals.credit_30d:
                    return behavioral_signals.credit_30d.aggregate_utilization * 100
                return None

            if placeholder == "credit_total_balance":
                if behavioral_signals.credit_30d:
                    # Estimate from utilization (rough approximation)
                    # This would need actual balance data for precision
                    return None  # Skip if not available
                return None

            # Savings signals (use 30d window)
            if placeholder == "savings_total_balance":
                if behavioral_signals.savings_30d:
                    return behavioral_signals.savings_30d.total_savings_balance
                return None

            if placeholder == "savings_emergency_fund_months":
                if behavioral_signals.savings_30d:
                    return behavioral_signals.savings_30d.emergency_fund_months
                return None

            # Subscription signals (use 30d window)
            if placeholder == "subscription_count":
                if behavioral_signals.subscriptions_30d:
                    return behavioral_signals.subscriptions_30d.subscription_count
                return None

            if placeholder == "subscription_share":
                if behavioral_signals.subscriptions_30d:
                    return behavioral_signals.subscriptions_30d.subscription_share * 100
                return None

            # Income signals (use 30d window)
            if placeholder == "income_payment_frequency":
                if behavioral_signals.income_30d:
                    return behavioral_signals.income_30d.payment_frequency
                return None

            # Monthly expenses (estimated from signals)
            if placeholder == "monthly_expenses":
                # Estimate from savings data if available
                if behavioral_signals.savings_30d and behavioral_signals.savings_30d.avg_monthly_expenses > 0:
                    return behavioral_signals.savings_30d.avg_monthly_expenses
                # Fallback: estimate from spending if available
                if behavioral_signals.subscriptions_30d:
                    return behavioral_signals.subscriptions_30d.total_spend
                return None

            # Three-month emergency fund target
            if placeholder == "three_month_fund_target":
                # Calculate: 3 months × monthly expenses
                if behavioral_signals.savings_30d and behavioral_signals.savings_30d.avg_monthly_expenses > 0:
                    return behavioral_signals.savings_30d.avg_monthly_expenses * 3
                # Fallback: estimate from total spending
                if behavioral_signals.subscriptions_30d:
                    return behavioral_signals.subscriptions_30d.total_spend * 3
                return None

            # Transaction history days
            if placeholder == "transaction_history_days":
                # Would need to be calculated from transaction data
                return None

            # Credit total limits
            if placeholder == "credit_total_limits":
                # Would need actual credit limit data
                return None

            # Unknown placeholder
            logger.warning(f"Unknown placeholder: {placeholder}")
            return None

        except Exception as e:
            logger.error(f"Error getting signal value for {placeholder}: {e}")
            return None

    def _format_value(self, placeholder: str, value: Any) -> str:
        """
        Format value appropriately for display.

        Args:
            placeholder: Placeholder name (determines format)
            value: Raw value to format

        Returns:
            Formatted string

        Formatting rules:
            - *_pct: Format as percentage (65.3 → "65.3")
            - *_balance: Format as currency (1234.56 → "$1,234.56")
            - *_count: Format as integer (23 → "23")
            - *_share: Format as percentage (82.7 → "82.7")
            - *_months: Format as decimal (2.5 → "2.5")
            - *_frequency: Format as string ("biweekly")
        """
        try:
            # Percentage values
            if "_pct" in placeholder or "_share" in placeholder:
                return f"{float(value):.1f}"

            # Currency values
            if "_balance" in placeholder or "expenses" in placeholder:
                return f"${float(value):,.2f}"

            # Count values
            if "_count" in placeholder:
                return str(int(value))

            # Month values
            if "_months" in placeholder:
                return f"{float(value):.1f}"

            # Frequency/string values
            if "_frequency" in placeholder:
                return str(value)

            # Default: return as string
            return str(value)

        except Exception as e:
            logger.error(f"Error formatting value for {placeholder}: {e}")
            return str(value)

    def can_personalize(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> bool:
        """
        Check if recommendation can be personalized.

        Args:
            recommendation: Recommendation to check
            behavioral_signals: User's behavioral signals

        Returns:
            True if recommendation has template and all signals available
        """
        if not recommendation.personalization_template:
            return False

        template = recommendation.personalization_template
        placeholders = self.PLACEHOLDER_PATTERN.findall(template)

        for placeholder in placeholders:
            value = self._get_signal_value(placeholder, behavioral_signals)
            if value is None:
                return False

        return True
