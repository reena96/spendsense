"""
Recommendation matching logic.

Matches educational content and partner offers to users based on
persona and behavioral signals.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

from spendsense.recommendations.models import Recommendation, PartnerOffer
from spendsense.recommendations.content_library import ContentLibrary
from spendsense.recommendations.partner_offer_library import PartnerOfferLibrary

logger = logging.getLogger(__name__)


@dataclass
class MatchingResult:
    """
    Result of recommendation matching process.

    Attributes:
        educational_items: Selected educational content items
        partner_offers: Selected partner offers
        persona_id: Persona used for matching
        signals: Behavioral signals used for matching
        timestamp: When matching was performed
        audit_trail: Detailed matching decisions for transparency
    """

    educational_items: List[Recommendation]
    partner_offers: List[PartnerOffer]
    persona_id: str
    signals: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    audit_trail: Dict[str, Any] = field(default_factory=dict)


class RecommendationMatcher:
    """
    Matches educational content and partner offers to users.

    Implements matching algorithm per PRD Story 4.3:
    - Filters content by persona and signals
    - Ranks by relevance
    - Selects 3-5 educational items with diversity
    - Filters offers by persona and eligibility
    - Selects 1-3 partner offers
    - Prevents duplicates within time window
    """

    def __init__(
        self,
        content_library: ContentLibrary,
        partner_library: PartnerOfferLibrary,
    ):
        """
        Initialize matcher with content and offer libraries.

        Args:
            content_library: Educational content library
            partner_library: Partner offer library
        """
        self.content_library = content_library
        self.partner_library = partner_library

    def match_recommendations(
        self,
        persona_id: str,
        signals: List[str],
        user_data: Dict[str, Any],
        excluded_content_ids: Optional[Set[str]] = None,
        excluded_offer_ids: Optional[Set[str]] = None,
        education_limit: tuple = (3, 5),
        offer_limit: tuple = (1, 3),
    ) -> MatchingResult:
        """
        Match recommendations for user based on persona and signals (PRD AC1).

        Args:
            persona_id: User's assigned persona
            signals: List of behavioral signals detected
            user_data: User data for eligibility checking (income, credit_score, etc.)
            excluded_content_ids: Content IDs to exclude (duplicate prevention - AC7)
            excluded_offer_ids: Offer IDs to exclude (duplicate prevention - AC7)
            education_limit: Tuple of (min, max) educational items to select (AC4)
            offer_limit: Tuple of (min, max) partner offers to select (AC6)

        Returns:
            MatchingResult with selected items and audit trail (AC8)

        Example:
            >>> matcher = RecommendationMatcher(content_lib, offer_lib)
            >>> result = matcher.match_recommendations(
            ...     persona_id="high_utilization",
            ...     signals=["credit_utilization"],
            ...     user_data={"annual_income": 50000, "credit_score": 700},
            ... )
            >>> print(len(result.educational_items))  # 3-5 items
            >>> print(len(result.partner_offers))  # 1-3 offers
        """
        excluded_content_ids = excluded_content_ids or set()
        excluded_offer_ids = excluded_offer_ids or set()

        audit_trail = {
            "persona_id": persona_id,
            "signals": signals,
            "excluded_content_count": len(excluded_content_ids),
            "excluded_offer_count": len(excluded_offer_ids),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # AC2: Filter content catalog for items matching user's persona
        logger.info(f"Matching recommendations for persona: {persona_id}, signals: {signals}")
        persona_content = self.content_library.get_by_persona(persona_id)
        audit_trail["persona_content_count"] = len(persona_content)

        # AC3: Rank content items by relevance to detected signals
        ranked_content = self._rank_by_signals(persona_content, signals)
        audit_trail["ranked_content_count"] = len(ranked_content)

        # AC7: Exclude previously recommended content
        available_content = [
            item for item in ranked_content if item.id not in excluded_content_ids
        ]
        audit_trail["available_content_count"] = len(available_content)

        # AC4: Select top 3-5 educational items with diversity (different types)
        selected_education = self._select_diverse_content(
            available_content, education_limit
        )
        audit_trail["selected_education_count"] = len(selected_education)
        audit_trail["selected_education_types"] = [
            item.type.value for item in selected_education
        ]

        # AC5: Filter partner offers by persona and eligibility checks
        persona_offers = self.partner_library.get_by_persona(persona_id)
        audit_trail["persona_offer_count"] = len(persona_offers)

        eligible_offers = []
        ineligible_reasons = {}
        for offer in persona_offers:
            if offer.id in excluded_offer_ids:
                continue  # AC7: Skip excluded offers

            is_eligible, reasons = self.partner_library.check_eligibility(
                offer, user_data
            )
            if is_eligible:
                eligible_offers.append(offer)
            else:
                ineligible_reasons[offer.id] = reasons

        audit_trail["eligible_offer_count"] = len(eligible_offers)
        audit_trail["ineligible_offer_count"] = len(ineligible_reasons)
        audit_trail["ineligibility_reasons"] = ineligible_reasons

        # AC6: Select 1-3 partner offers matching user eligibility
        selected_offers = self._select_top_offers(eligible_offers, offer_limit)
        audit_trail["selected_offer_count"] = len(selected_offers)
        audit_trail["selected_offer_ids"] = [offer.id for offer in selected_offers]

        logger.info(
            f"Matched {len(selected_education)} education items and "
            f"{len(selected_offers)} partner offers for {persona_id}"
        )

        return MatchingResult(
            educational_items=selected_education,
            partner_offers=selected_offers,
            persona_id=persona_id,
            signals=signals,
            audit_trail=audit_trail,
        )

    def _rank_by_signals(
        self, content: List[Recommendation], signals: List[str]
    ) -> List[Recommendation]:
        """
        Rank content items by relevance to detected signals (PRD AC3).

        Ranking algorithm:
        1. Items with matching signals ranked higher
        2. Higher priority items ranked higher within same signal match count
        3. Items with more signal matches ranked higher

        Args:
            content: List of content items
            signals: Detected behavioral signals

        Returns:
            Content sorted by relevance (highest first)
        """
        if not signals:
            # No signals - just sort by priority
            return sorted(content, key=lambda x: x.priority)

        def relevance_score(item: Recommendation) -> tuple:
            """
            Calculate relevance score for sorting.

            Returns tuple: (signal_match_count, -priority)
            Higher signal matches = more relevant
            Lower priority number = more relevant (1 > 2 > 3)
            """
            signal_matches = len(set(item.triggering_signals) & set(signals))
            return (signal_matches, -item.priority)

        # Sort by signal matches (desc), then priority (asc)
        ranked = sorted(content, key=relevance_score, reverse=True)

        logger.debug(
            f"Ranked {len(ranked)} items by signals {signals}. "
            f"Top item: {ranked[0].id if ranked else 'none'}"
        )

        return ranked

    def _select_diverse_content(
        self, content: List[Recommendation], limit: tuple = (3, 5)
    ) -> List[Recommendation]:
        """
        Select top content items with type diversity (PRD AC4).

        Strategy:
        1. Select items in order of relevance
        2. Prefer different content types (article, template, calculator, video)
        3. Stop when reaching max limit or running out of items
        4. Ensure minimum count if possible

        Args:
            content: Ranked content items (highest relevance first)
            limit: Tuple of (min_count, max_count)

        Returns:
            Selected content items with diverse types
        """
        min_count, max_count = limit
        selected = []
        seen_types = set()

        # First pass: Select items with unique types
        for item in content:
            if len(selected) >= max_count:
                break

            if item.type not in seen_types:
                selected.append(item)
                seen_types.add(item.type)

        # Second pass: Fill up to max_count if needed
        for item in content:
            if len(selected) >= max_count:
                break

            if item not in selected:
                selected.append(item)

        # If we don't have minimum, just take what we can
        if len(selected) < min_count and len(content) > len(selected):
            remaining = [item for item in content if item not in selected]
            needed = min_count - len(selected)
            selected.extend(remaining[:needed])

        logger.debug(
            f"Selected {len(selected)} diverse items (target: {min_count}-{max_count}). "
            f"Types: {[item.type.value for item in selected]}"
        )

        return selected

    def _select_top_offers(
        self, offers: List[PartnerOffer], limit: tuple = (1, 3)
    ) -> List[PartnerOffer]:
        """
        Select top partner offers by priority (PRD AC6).

        Args:
            offers: Eligible partner offers (already filtered by eligibility)
            limit: Tuple of (min_count, max_count)

        Returns:
            Top N offers sorted by priority
        """
        min_count, max_count = limit

        # Sort by priority (1 = highest)
        sorted_offers = sorted(offers, key=lambda x: x.priority)

        # Take up to max_count
        selected = sorted_offers[:max_count]

        logger.debug(
            f"Selected {len(selected)} partner offers (target: {min_count}-{max_count})"
        )

        return selected
