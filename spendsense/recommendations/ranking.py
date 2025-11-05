"""
Ranking engine for relevance-based recommendation sorting.

Calculates relevance scores and ranks recommendations by combined
priority, impact, and signal-based relevance.
"""

import logging
from typing import List, Tuple

from spendsense.recommendations.models import (
    Recommendation,
    EstimatedImpact,
    TimeCommitment,
    DifficultyLevel,
)
from spendsense.features.behavioral_summary import BehavioralSummary

logger = logging.getLogger(__name__)


class RankingEngine:
    """
    Relevance-based recommendation ranker.

    Calculates relevance scores based on priority, impact, personalization,
    and signal-specific relevance. Sorts recommendations by score.

    Usage:
        ranker = RankingEngine()
        scored_recs = ranker.rank(recs, signals, persona_id, personalized_flags)
    """

    def __init__(self):
        """Initialize ranking engine."""
        pass

    def rank(
        self,
        recommendations: List[Recommendation],
        behavioral_signals: BehavioralSummary,
        persona_id: str,
        personalized_flags: dict[str, bool],
    ) -> List[Tuple[Recommendation, float]]:
        """
        Rank recommendations by relevance score.

        Args:
            recommendations: Filtered recommendations
            behavioral_signals: User's behavioral signals
            persona_id: Assigned persona ID
            personalized_flags: Dict mapping rec ID to whether it was personalized

        Returns:
            List of (recommendation, relevance_score) tuples, sorted by score descending

        Example:
            >>> ranker = RankingEngine()
            >>> scored = ranker.rank(recs, signals, "low_savings", personalized)
            >>> for rec, score in scored[:5]:
            ...     print(f"{rec.title}: {score:.2f}")
        """
        scored_recommendations = []

        for rec in recommendations:
            score = self.calculate_relevance_score(
                recommendation=rec,
                behavioral_signals=behavioral_signals,
                persona_id=persona_id,
                personalized=personalized_flags.get(rec.id, False),
            )
            scored_recommendations.append((rec, score))

        # Sort by score descending (highest first)
        scored_recommendations.sort(key=lambda x: x[1], reverse=True)

        logger.info(
            f"Ranked {len(scored_recommendations)} recommendations "
            f"(scores: {scored_recommendations[0][1]:.2f} to {scored_recommendations[-1][1]:.2f})"
        )

        return scored_recommendations

    def calculate_relevance_score(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
        personalized: bool,
    ) -> float:
        """
        Calculate relevance score for a recommendation.

        Formula:
            base_score = (11 - priority) / 10  # Priority 1 = 1.0, Priority 10 = 0.1

            Boosts:
            - High impact: +0.2
            - Personalized (template used): +0.1
            - Quick win: +0.1
            - Signal-specific relevance: +0.0 to +0.3

            Final score capped at 1.0

        Args:
            recommendation: Recommendation to score
            behavioral_signals: User's behavioral signals
            persona_id: Assigned persona ID
            personalized: Whether recommendation was personalized

        Returns:
            Relevance score (0.0-1.0)
        """
        # Base score from priority (1-10)
        # Priority 1 gets 1.0, Priority 10 gets 0.1
        base_score = (11 - recommendation.priority) / 10

        boosts = 0.0

        # High impact boost
        if recommendation.estimated_impact == EstimatedImpact.HIGH:
            boosts += 0.2

        # Personalized boost
        if personalized:
            boosts += 0.1

        # Quick win boost (beginner or one-time)
        if (
            recommendation.difficulty == DifficultyLevel.BEGINNER
            or recommendation.time_commitment == TimeCommitment.ONE_TIME
        ):
            boosts += 0.1

        # Signal-based relevance (persona-specific)
        signal_boost = self._calculate_signal_relevance(
            recommendation=recommendation,
            behavioral_signals=behavioral_signals,
            persona_id=persona_id,
        )

        # Calculate final score (capped at 1.0)
        final_score = min(1.0, base_score + boosts + signal_boost)

        logger.debug(
            f"{recommendation.id}: base={base_score:.2f}, boosts={boosts:.2f}, "
            f"signal={signal_boost:.2f}, final={final_score:.2f}"
        )

        return final_score

    def _calculate_signal_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
        persona_id: str,
    ) -> float:
        """
        Calculate signal-based relevance boost.

        Persona-specific rules that boost recommendations based on
        signal values.

        Args:
            recommendation: Recommendation to evaluate
            behavioral_signals: User's behavioral signals
            persona_id: Assigned persona ID

        Returns:
            Signal relevance boost (0.0-0.3)
        """
        boost = 0.0

        try:
            # Low Savings persona
            if persona_id == "low_savings":
                boost += self._low_savings_relevance(recommendation, behavioral_signals)

            # High Utilization persona
            elif persona_id == "high_utilization":
                boost += self._high_utilization_relevance(recommendation, behavioral_signals)

            # Subscription Heavy persona
            elif persona_id == "subscription_heavy":
                boost += self._subscription_heavy_relevance(recommendation, behavioral_signals)

            # Irregular Income persona
            elif persona_id == "irregular_income":
                boost += self._irregular_income_relevance(recommendation, behavioral_signals)

            # Cash Flow Optimizer persona
            elif persona_id == "cash_flow_optimizer":
                boost += self._cash_flow_optimizer_relevance(recommendation, behavioral_signals)

            # Young Professional persona
            elif persona_id == "young_professional":
                boost += self._young_professional_relevance(recommendation, behavioral_signals)

        except Exception as e:
            logger.error(f"Error calculating signal relevance: {e}")

        return min(0.3, boost)  # Cap at 0.3

    def _low_savings_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> float:
        """Signal relevance for Low Savings persona."""
        boost = 0.0

        if not behavioral_signals.savings:
            return boost

        emergency_fund_months = behavioral_signals.savings.emergency_fund_months

        # Boost emergency fund recs if user has <1 month saved
        if "emergency_fund" in recommendation.id or "automate" in recommendation.id:
            if emergency_fund_months < 1.0:
                boost += 0.3
            elif emergency_fund_months < 2.0:
                boost += 0.2

        # Boost subscription review if user has high subscription share
        if "subscription" in recommendation.id:
            if behavioral_signals.subscriptions:
                if behavioral_signals.subscriptions.subscription_share > 0.5:
                    boost += 0.2

        return boost

    def _high_utilization_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> float:
        """Signal relevance for High Utilization persona."""
        boost = 0.0

        if not behavioral_signals.credit:
            return boost

        utilization = behavioral_signals.credit.aggregate_utilization
        high_util_count = behavioral_signals.credit.high_utilization_count

        # Boost debt payoff recs if utilization is very high
        if "debt" in recommendation.id or "payoff" in recommendation.id:
            if utilization > 0.7:
                boost += 0.3
            elif utilization > 0.5:
                boost += 0.2

        # Boost balance transfer if multiple cards at high utilization
        if "balance_transfer" in recommendation.id:
            if high_util_count > 2:
                boost += 0.2

        return boost

    def _subscription_heavy_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> float:
        """Signal relevance for Subscription Heavy persona."""
        boost = 0.0

        if not behavioral_signals.subscriptions:
            return boost

        subscription_count = behavioral_signals.subscriptions.subscription_count
        subscription_share = behavioral_signals.subscriptions.subscription_share

        # Boost audit/cancel recs if many subscriptions
        if "audit" in recommendation.id or "cancel" in recommendation.id:
            if subscription_count >= 20:
                boost += 0.3
            elif subscription_count >= 15:
                boost += 0.2

        # Boost management tool if very high subscription share
        if "management" in recommendation.id or "tool" in recommendation.id:
            if subscription_share > 0.7:
                boost += 0.2

        return boost

    def _irregular_income_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> float:
        """Signal relevance for Irregular Income persona."""
        boost = 0.0

        if not behavioral_signals.income:
            return boost

        # Boost emergency fund recs (irregular income needs larger cushion)
        if "emergency_fund" in recommendation.id:
            if behavioral_signals.savings:
                if behavioral_signals.savings.emergency_fund_months < 6.0:
                    boost += 0.3

        # Boost budgeting/averaging recs
        if "budget" in recommendation.id or "averaging" in recommendation.id:
            boost += 0.2

        return boost

    def _cash_flow_optimizer_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> float:
        """Signal relevance for Cash Flow Optimizer persona."""
        boost = 0.0

        # Boost investing recs (this persona is ready to invest)
        if "invest" in recommendation.id or "robo" in recommendation.id:
            boost += 0.3

        # Boost optimization recs
        if "optimize" in recommendation.id or "idle" in recommendation.id:
            if behavioral_signals.savings:
                # If lots of cash sitting idle, boost optimization
                if behavioral_signals.savings.total_savings_balance > 10000:
                    boost += 0.2

        return boost

    def _young_professional_relevance(
        self,
        recommendation: Recommendation,
        behavioral_signals: BehavioralSummary,
    ) -> float:
        """Signal relevance for Young Professional persona."""
        boost = 0.0

        # Boost credit building recs (priority for this persona)
        if "credit" in recommendation.id and "101" in recommendation.id:
            boost += 0.3

        # Boost basics/fundamentals
        if "fundamental" in recommendation.id or "basic" in recommendation.id:
            boost += 0.2

        # Boost first card recommendation
        if "first_credit_card" in recommendation.id:
            if behavioral_signals.credit:
                # If no or very low credit, boost this
                if behavioral_signals.credit.aggregate_utilization == 0:
                    boost += 0.3

        return boost
