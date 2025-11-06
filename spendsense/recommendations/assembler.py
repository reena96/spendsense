"""
Recommendation assembler for combining all components into complete recommendation sets.

Orchestrates content library, partner offers, matching, and rationale generation
to produce complete recommendations with transparency and personalization.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field

from spendsense.recommendations.content_library import ContentLibrary
from spendsense.recommendations.partner_offer_library import PartnerOfferLibrary
from spendsense.recommendations.matcher import RecommendationMatcher, MatchingResult
from spendsense.recommendations.rationale_generator import RationaleGenerator, GeneratedRationale
from spendsense.recommendations.models import Recommendation, PartnerOffer

logger = logging.getLogger(__name__)


# Mandatory disclaimer per PRD AC4
MANDATORY_DISCLAIMER = (
    "This is educational content, not financial advice. "
    "Consult a licensed advisor for personalized guidance."
)


@dataclass
class AssembledRecommendationItem:
    """
    Single recommendation item with full details and rationale.

    Attributes:
        item_type: Type of recommendation (education or partner_offer)
        item_id: Unique identifier
        content: Full content/offer details (dict representation)
        rationale: Generated rationale with personalization
        persona_match_reason: Why this matches the user's persona
        signal_citations: Specific behavioral signals cited
    """

    item_type: str
    item_id: str
    content: Dict[str, Any]
    rationale: str
    persona_match_reason: str
    signal_citations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "item_type": self.item_type,
            "item_id": self.item_id,
            "content": self.content,
            "rationale": self.rationale,
            "persona_match_reason": self.persona_match_reason,
            "signal_citations": self.signal_citations,
        }


@dataclass
class AssembledRecommendationSet:
    """
    Complete recommendation set for a user and time window.

    Attributes:
        user_id: User identifier
        persona_id: User's assigned persona
        time_window: Time window used (30d or 180d)
        recommendations: List of assembled recommendation items
        disclaimer: Mandatory disclaimer text
        metadata: Additional metadata (generation time, counts, etc.)
        generated_at: Timestamp of generation
    """

    user_id: str
    persona_id: str
    time_window: str
    recommendations: List[AssembledRecommendationItem]
    disclaimer: str
    metadata: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response and storage."""
        return {
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "time_window": self.time_window,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "disclaimer": self.disclaimer,
            "metadata": self.metadata,
            "generated_at": self.generated_at.isoformat(),
        }


class RecommendationAssembler:
    """
    Assembles complete recommendation sets combining all components.

    Implements Story 4.5 - Recommendation Assembly & Output:
    - Combines educational content and partner offers
    - Generates rationales with persona match reasons and signal citations
    - Handles both 30-day and 180-day windows
    - Includes mandatory disclaimer
    - Completes in <5 seconds per user

    Usage:
        assembler = RecommendationAssembler(content_lib, partner_lib)
        rec_set = assembler.assemble_recommendations(
            user_id="user_123",
            persona_id="low_savings",
            signals=["savings_balance", "irregular_income"],
            user_data={"credit_score": 700, "annual_income": 50000},
            time_window="30d"
        )
    """

    def __init__(
        self,
        content_library: ContentLibrary,
        partner_library: PartnerOfferLibrary,
    ):
        """
        Initialize assembler with content and partner libraries.

        Args:
            content_library: Educational content library
            partner_library: Partner offer library
        """
        self.content_library = content_library
        self.partner_library = partner_library
        self.matcher = RecommendationMatcher(content_library, partner_library)
        self.rationale_generator = RationaleGenerator()

        logger.info("RecommendationAssembler initialized")

    def assemble_recommendations(
        self,
        user_id: str,
        persona_id: str,
        signals: List[str],
        user_data: Dict[str, Any],
        time_window: str = "30d",
        excluded_content_ids: Optional[Set[str]] = None,
        excluded_offer_ids: Optional[Set[str]] = None,
    ) -> AssembledRecommendationSet:
        """
        Assemble complete recommendation set for user (PRD AC1, AC2, AC3).

        Args:
            user_id: User identifier
            persona_id: User's assigned persona
            signals: List of behavioral signals detected
            user_data: User data for eligibility checking and personalization
            time_window: Time window ("30d" or "180d")
            excluded_content_ids: Content IDs to exclude (duplicate prevention)
            excluded_offer_ids: Offer IDs to exclude (duplicate prevention)

        Returns:
            AssembledRecommendationSet with complete recommendation details

        Example:
            >>> assembler = RecommendationAssembler(content_lib, partner_lib)
            >>> rec_set = assembler.assemble_recommendations(
            ...     user_id="user_123",
            ...     persona_id="high_utilization",
            ...     signals=["credit_utilization"],
            ...     user_data={"credit_score": 700, "annual_income": 50000},
            ...     time_window="30d"
            ... )
            >>> print(len(rec_set.recommendations))  # 4-8 items (3-5 education + 1-3 offers)
        """
        start_time = time.time()

        logger.info(
            f"Assembling recommendations for user={user_id}, persona={persona_id}, "
            f"window={time_window}, signals={signals}"
        )

        # AC1: Match recommendations using matcher (combines education and offers)
        matching_result = self.matcher.match_recommendations(
            persona_id=persona_id,
            signals=signals,
            user_data=user_data,
            excluded_content_ids=excluded_content_ids,
            excluded_offer_ids=excluded_offer_ids,
        )

        # AC2: Generate rationales for each recommendation
        assembled_items = []

        # Process educational content items
        for edu_item in matching_result.educational_items:
            rationale = self.rationale_generator.generate_for_recommendation(
                recommendation=edu_item,
                user_data=user_data,
                signals=signals,
            )

            assembled_item = self._create_assembled_item(
                item_type="education",
                item=edu_item,
                rationale=rationale,
                persona_id=persona_id,
                signals=signals,
            )
            assembled_items.append(assembled_item)

        # Process partner offer items
        for offer_item in matching_result.partner_offers:
            rationale = self.rationale_generator.generate_for_offer(
                offer=offer_item,
                user_data=user_data,
                signals=signals,
            )

            assembled_item = self._create_assembled_item(
                item_type="partner_offer",
                item=offer_item,
                rationale=rationale,
                persona_id=persona_id,
                signals=signals,
            )
            assembled_items.append(assembled_item)

        # Calculate generation time
        generation_time_ms = (time.time() - start_time) * 1000

        # AC3, AC7: Build metadata
        metadata = {
            "total_recommendations": len(assembled_items),
            "education_count": len(matching_result.educational_items),
            "partner_offer_count": len(matching_result.partner_offers),
            "generation_time_ms": round(generation_time_ms, 2),
            "time_window": time_window,
            "signals_detected": signals,
            "matching_audit_trail": matching_result.audit_trail,
        }

        # AC4: Create assembled set with mandatory disclaimer
        recommendation_set = AssembledRecommendationSet(
            user_id=user_id,
            persona_id=persona_id,
            time_window=time_window,
            recommendations=assembled_items,
            disclaimer=MANDATORY_DISCLAIMER,
            metadata=metadata,
        )

        logger.info(
            f"Assembled {len(assembled_items)} recommendations "
            f"({metadata['education_count']} education + {metadata['partner_offer_count']} offers) "
            f"in {generation_time_ms:.1f}ms for {user_id}"
        )

        # AC8: Ensure <5 second performance
        if generation_time_ms > 5000:
            logger.warning(
                f"Recommendation assembly took {generation_time_ms:.1f}ms "
                f"(exceeds 5000ms target)"
            )

        return recommendation_set

    def _create_assembled_item(
        self,
        item_type: str,
        item: Any,  # Recommendation or PartnerOffer
        rationale: GeneratedRationale,
        persona_id: str,
        signals: List[str],
    ) -> AssembledRecommendationItem:
        """
        Create assembled recommendation item with full details (PRD AC2, AC3).

        Args:
            item_type: Type of item (education or partner_offer)
            item: Recommendation or PartnerOffer object
            rationale: Generated rationale
            persona_id: User's persona
            signals: Behavioral signals

        Returns:
            AssembledRecommendationItem with complete details
        """
        # AC2: Include full content/offer details
        content = item.to_dict()

        # AC3: Generate persona match reason
        persona_match_reason = self._generate_persona_match_reason(
            item=item,
            persona_id=persona_id,
        )

        # AC3: Extract signal citations from rationale
        signal_citations = rationale.data_citations

        return AssembledRecommendationItem(
            item_type=item_type,
            item_id=item.id,
            content=content,
            rationale=rationale.rationale_text,
            persona_match_reason=persona_match_reason,
            signal_citations=signal_citations,
        )

    def _generate_persona_match_reason(
        self,
        item: Any,
        persona_id: str,
    ) -> str:
        """
        Generate explanation for why item matches user's persona (PRD AC3).

        Args:
            item: Recommendation or PartnerOffer
            persona_id: User's assigned persona

        Returns:
            Human-readable explanation of persona match
        """
        # Map persona IDs to human-readable descriptions
        persona_descriptions = {
            "high_utilization": "users with high credit card utilization",
            "irregular_income": "users with variable income patterns",
            "low_savings": "users building emergency savings",
            "subscription_heavy": "users with multiple subscriptions",
            "cash_flow_optimizer": "users optimizing monthly cash flow",
            "young_professional": "young professionals starting their financial journey",
        }

        persona_desc = persona_descriptions.get(
            persona_id,
            f"users with '{persona_id}' financial profile"
        )

        # Get item title for context
        title = getattr(item, "title", "This recommendation")

        return (
            f"{title} is recommended for {persona_desc} based on your current financial behavior."
        )

    def assemble_for_multiple_windows(
        self,
        user_id: str,
        persona_id: str,
        signals_30d: List[str],
        signals_180d: List[str],
        user_data: Dict[str, Any],
        excluded_content_ids: Optional[Set[str]] = None,
        excluded_offer_ids: Optional[Set[str]] = None,
    ) -> Dict[str, AssembledRecommendationSet]:
        """
        Assemble recommendations for both 30-day and 180-day windows (PRD AC3).

        Args:
            user_id: User identifier
            persona_id: User's assigned persona
            signals_30d: Signals detected in 30-day window
            signals_180d: Signals detected in 180-day window
            user_data: User data for eligibility and personalization
            excluded_content_ids: Content IDs to exclude
            excluded_offer_ids: Offer IDs to exclude

        Returns:
            Dict with keys "30d" and "180d" mapping to recommendation sets

        Example:
            >>> assembler = RecommendationAssembler(content_lib, partner_lib)
            >>> rec_sets = assembler.assemble_for_multiple_windows(
            ...     user_id="user_123",
            ...     persona_id="low_savings",
            ...     signals_30d=["savings_balance"],
            ...     signals_180d=["savings_balance", "irregular_income"],
            ...     user_data={"credit_score": 700, "annual_income": 50000}
            ... )
            >>> print(rec_sets["30d"].time_window)
            "30d"
        """
        logger.info(f"Assembling recommendations for both time windows for user={user_id}")

        # Generate for 30-day window
        rec_set_30d = self.assemble_recommendations(
            user_id=user_id,
            persona_id=persona_id,
            signals=signals_30d,
            user_data=user_data,
            time_window="30d",
            excluded_content_ids=excluded_content_ids,
            excluded_offer_ids=excluded_offer_ids,
        )

        # Generate for 180-day window
        rec_set_180d = self.assemble_recommendations(
            user_id=user_id,
            persona_id=persona_id,
            signals=signals_180d,
            user_data=user_data,
            time_window="180d",
            excluded_content_ids=excluded_content_ids,
            excluded_offer_ids=excluded_offer_ids,
        )

        return {
            "30d": rec_set_30d,
            "180d": rec_set_180d,
        }
