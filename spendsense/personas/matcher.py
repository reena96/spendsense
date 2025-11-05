"""
Persona matching engine for evaluating behavioral signals against persona criteria.

This module evaluates user behavioral signals against all persona criteria
to identify which personas match the user's financial behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
import logging

from pydantic import BaseModel
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from spendsense.personas.registry import (
    load_persona_registry,
    Persona,
    PersonaCriteria,
    PersonaCondition,
    ConditionOperator
)
from spendsense.ingestion.database_writer import Transaction, Account

if TYPE_CHECKING:
    from spendsense.features.behavioral_summary import BehavioralSummary

logger = logging.getLogger(__name__)


class PersonaMatch(BaseModel):
    """
    Result of evaluating a persona against user signals.

    Attributes:
        persona_id: Persona identifier
        matched: True if user signals match persona criteria
        evidence: Dictionary of signal values that were evaluated
        matched_conditions: List of conditions that evaluated to True
    """
    persona_id: str
    matched: bool
    evidence: Dict[str, Any]
    matched_conditions: List[str] = []


@dataclass
class ExtendedSignals:
    """
    Extended behavioral signals including calculated values.

    Combines signals from BehavioralSummary with calculated values
    like transaction_history_days and credit_total_limits.

    Note: Both 30d and 180d signals are stored because the matcher
    needs to support both time windows. The time_window parameter
    determines which set of signals is used during evaluation.
    """
    # From BehavioralSummary (30-day window)
    subscription_share_pct_30d: Optional[float] = None
    credit_max_utilization_pct_30d: Optional[float] = None
    savings_emergency_fund_months_30d: Optional[float] = None
    income_median_pay_gap_days_30d: Optional[float] = None
    income_payroll_count_30d: Optional[int] = None

    # From BehavioralSummary (180-day window)
    subscription_share_pct_180d: Optional[float] = None
    credit_max_utilization_pct_180d: Optional[float] = None
    savings_emergency_fund_months_180d: Optional[float] = None
    income_median_pay_gap_days_180d: Optional[float] = None
    income_payroll_count_180d: Optional[int] = None

    # Calculated signals
    transaction_history_days: Optional[int] = None
    credit_total_limits: Optional[float] = None


class PersonaMatcher:
    """
    Matches user behavioral signals against persona criteria.

    Evaluates all personas and returns match results with supporting evidence.

    Usage:
        from spendsense.features.behavioral_summary import BehavioralSummaryGenerator

        # Generate behavioral summary
        generator = BehavioralSummaryGenerator("data/processed/spendsense.db")
        summary = generator.generate_summary("user_001", date(2025, 11, 4))

        # Match personas
        matcher = PersonaMatcher("data/processed/spendsense.db")
        matches = matcher.match_personas(summary, reference_date=date(2025, 11, 4))

        # Check results
        for match in matches:
            if match.matched:
                print(f"Matched: {match.persona_id}")
                print(f"Evidence: {match.evidence}")
    """

    def __init__(self, db_path: str):
        """
        Initialize persona matcher.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        self.registry = load_persona_registry()

    def match_personas(
        self,
        behavioral_summary: 'BehavioralSummary',
        reference_date: date,
        time_window: str = "30d"
    ) -> List[PersonaMatch]:
        """
        Match user behavioral signals against all persona criteria.

        Args:
            behavioral_summary: BehavioralSummary object from Epic 2
            reference_date: Date to use for calculated signals
            time_window: Time window to use ("30d" or "180d")

        Returns:
            List of PersonaMatch objects for all personas

        Raises:
            ValueError: If time_window is not "30d" or "180d"
        """
        if time_window not in ("30d", "180d"):
            raise ValueError(f"Invalid time_window: {time_window}. Must be '30d' or '180d'")

        logger.info(f"Matching personas for user {behavioral_summary.user_id} (window: {time_window})")

        # Extract signals from behavioral summary
        extended_signals = self._extract_signals(
            behavioral_summary,
            time_window,
            reference_date
        )

        # Calculate missing signals
        extended_signals.transaction_history_days = self._calculate_transaction_history_days(
            behavioral_summary.user_id,
            reference_date
        )
        extended_signals.credit_total_limits = self._calculate_credit_total_limits(
            behavioral_summary.user_id
        )

        # Evaluate each persona
        matches = []
        for persona in self.registry.personas:
            match_result = self._evaluate_persona(persona, extended_signals, time_window)
            matches.append(match_result)

            if match_result.matched:
                logger.info(
                    f"Matched persona: {persona.id} "
                    f"(conditions: {', '.join(match_result.matched_conditions)})"
                )
            else:
                logger.debug(f"No match: {persona.id}")

        # Log summary
        qualifying_personas = [m.persona_id for m in matches if m.matched]
        logger.info(
            f"Persona matching complete: {len(qualifying_personas)} qualifying personas: "
            f"{', '.join(qualifying_personas) if qualifying_personas else 'none'}"
        )

        return matches

    def _extract_signals(
        self,
        behavioral_summary: Any,
        time_window: str,
        reference_date: date
    ) -> ExtendedSignals:
        """
        Extract signals from behavioral summary.

        Args:
            behavioral_summary: BehavioralSummary object
            time_window: "30d" or "180d"
            reference_date: Reference date for calculations

        Returns:
            ExtendedSignals with all available signals
        """
        signals = ExtendedSignals()

        # Extract 30-day signals
        if hasattr(behavioral_summary, 'subscriptions_30d'):
            signals.subscription_share_pct_30d = behavioral_summary.subscriptions_30d.subscription_share

        if hasattr(behavioral_summary, 'credit_30d'):
            signals.credit_max_utilization_pct_30d = behavioral_summary.credit_30d.aggregate_utilization

        if hasattr(behavioral_summary, 'savings_30d'):
            signals.savings_emergency_fund_months_30d = behavioral_summary.savings_30d.emergency_fund_months

        if hasattr(behavioral_summary, 'income_30d'):
            signals.income_median_pay_gap_days_30d = behavioral_summary.income_30d.median_pay_gap_days
            signals.income_payroll_count_30d = behavioral_summary.income_30d.num_income_transactions

        # Extract 180-day signals
        if hasattr(behavioral_summary, 'subscriptions_180d'):
            signals.subscription_share_pct_180d = behavioral_summary.subscriptions_180d.subscription_share

        if hasattr(behavioral_summary, 'credit_180d'):
            signals.credit_max_utilization_pct_180d = behavioral_summary.credit_180d.aggregate_utilization

        if hasattr(behavioral_summary, 'savings_180d'):
            signals.savings_emergency_fund_months_180d = behavioral_summary.savings_180d.emergency_fund_months

        if hasattr(behavioral_summary, 'income_180d'):
            signals.income_median_pay_gap_days_180d = behavioral_summary.income_180d.median_pay_gap_days
            signals.income_payroll_count_180d = behavioral_summary.income_180d.num_income_transactions

        return signals

    def _calculate_transaction_history_days(
        self,
        user_id: str,
        reference_date: date
    ) -> Optional[int]:
        """
        Calculate number of days from first transaction to reference date.

        Args:
            user_id: User identifier
            reference_date: Reference date for calculation

        Returns:
            Number of days of transaction history, or None if no transactions
        """
        try:
            with self.Session() as session:
                # Query for first transaction date
                # Transactions are linked through accounts, need to join
                first_txn = session.query(
                    func.min(Transaction.date)
                ).join(
                    Account, Transaction.account_id == Account.account_id
                ).filter(
                    Account.user_id == user_id
                ).scalar()

                if first_txn is None:
                    logger.warning(f"No transactions found for user {user_id}")
                    return None

                # Convert string date to date object if needed
                if isinstance(first_txn, str):
                    from datetime import datetime
                    first_txn = datetime.strptime(first_txn, '%Y-%m-%d').date()

                days = (reference_date - first_txn).days
                logger.debug(f"Transaction history: {days} days (first: {first_txn}, ref: {reference_date})")
                return days

        except Exception as e:
            logger.error(f"Error calculating transaction history for {user_id}: {e}")
            return None

    def _calculate_credit_total_limits(
        self,
        user_id: str
    ) -> Optional[float]:
        """
        Calculate total credit limits across all credit cards.

        Args:
            user_id: User identifier

        Returns:
            Sum of credit limits, or None if no credit accounts
        """
        try:
            with self.Session() as session:
                # Query for sum of credit limits from Account table
                # Credit card accounts have balance_limit field
                total_limits = session.query(
                    func.sum(Account.balance_limit)
                ).filter(
                    Account.user_id == user_id,
                    Account.type == 'credit',
                    Account.balance_limit.isnot(None)
                ).scalar()

                if total_limits is None or total_limits == 0:
                    logger.debug(f"No credit accounts found for user {user_id}")
                    return None

                logger.debug(f"Total credit limits: ${total_limits:,.2f}")
                return float(total_limits)

        except Exception as e:
            logger.error(f"Error calculating credit limits for {user_id}: {e}")
            return None

    def _evaluate_persona(
        self,
        persona: Persona,
        signals: ExtendedSignals,
        time_window: str
    ) -> PersonaMatch:
        """
        Evaluate whether user signals match a persona's criteria.

        Args:
            persona: Persona definition
            signals: Extended signals with calculated values
            time_window: "30d" or "180d"

        Returns:
            PersonaMatch with match result and evidence
        """
        criteria = persona.criteria
        matched, evidence, matched_conditions = self._evaluate_criteria(
            criteria,
            signals,
            time_window
        )

        return PersonaMatch(
            persona_id=persona.id,
            matched=matched,
            evidence=evidence,
            matched_conditions=matched_conditions
        )

    def _evaluate_criteria(
        self,
        criteria: PersonaCriteria,
        signals: ExtendedSignals,
        time_window: str
    ) -> Tuple[bool, Dict[str, Any], List[str]]:
        """
        Evaluate persona criteria against signals.

        Args:
            criteria: Persona criteria with AND/OR operator
            signals: Extended signals
            time_window: "30d" or "180d"

        Returns:
            Tuple of (matched, evidence_dict, matched_conditions_list)
        """
        evidence = {}
        matched_conditions = []
        condition_results = []

        for condition in criteria.conditions:
            result, signal_value = self._evaluate_condition(condition, signals, time_window)
            condition_results.append(result)

            # Store evidence
            evidence[condition.signal] = signal_value

            # Track which conditions matched
            if result:
                matched_conditions.append(
                    f"{condition.signal} {condition.operator.value} {condition.value}"
                )

        # Apply AND/OR logic
        if criteria.operator.value == "AND":
            matched = all(condition_results)
        else:  # OR
            matched = any(condition_results)

        return matched, evidence, matched_conditions

    def _evaluate_condition(
        self,
        condition: PersonaCondition,
        signals: ExtendedSignals,
        time_window: str
    ) -> Tuple[bool, Optional[Any]]:
        """
        Evaluate a single condition against signals.

        Args:
            condition: Persona condition to evaluate
            signals: Extended signals
            time_window: "30d" or "180d"

        Returns:
            Tuple of (condition_met, signal_value)
        """
        # Get signal value (with time window suffix if needed)
        signal_name = condition.signal

        # Handle time-window-specific signals
        # Most signals use time window suffix, but calculated signals don't
        if signal_name in ['transaction_history_days', 'credit_total_limits']:
            signal_value = getattr(signals, signal_name, None)
        else:
            # Append time window suffix
            signal_name_with_window = f"{signal_name}_{time_window}"
            signal_value = getattr(signals, signal_name_with_window, None)

        # Handle missing signals
        if signal_value is None:
            logger.debug(
                f"Signal {signal_name} is None - condition evaluates to False"
            )
            return False, None

        # Evaluate comparison
        try:
            result = self._compare(signal_value, condition.operator, condition.value)
            logger.debug(
                f"Condition: {signal_name}={signal_value} {condition.operator.value} {condition.value} → {result}"
            )
            return result, signal_value
        except Exception as e:
            logger.error(
                f"Error evaluating condition {signal_name} {condition.operator.value} {condition.value}: {e}"
            )
            return False, signal_value

    def _compare(
        self,
        signal_value: Any,
        operator: ConditionOperator,
        threshold: float
    ) -> bool:
        """
        Compare signal value against threshold using operator.

        Args:
            signal_value: Actual signal value
            operator: Comparison operator
            threshold: Threshold value

        Returns:
            True if comparison is satisfied
        """
        # Convert to float for comparison
        try:
            signal_float = float(signal_value)
        except (TypeError, ValueError) as e:
            logger.warning(f"Cannot convert signal value {signal_value} to float: {e}")
            return False

        # Perform comparison
        if operator == ConditionOperator.GTE:
            return signal_float >= threshold
        elif operator == ConditionOperator.LTE:
            return signal_float <= threshold
        elif operator == ConditionOperator.GT:
            return signal_float > threshold
        elif operator == ConditionOperator.LT:
            return signal_float < threshold
        elif operator == ConditionOperator.EQ:
            return abs(signal_float - threshold) < 1e-6  # Float equality with epsilon
        else:
            logger.error(f"Unknown operator: {operator}")
            return False
