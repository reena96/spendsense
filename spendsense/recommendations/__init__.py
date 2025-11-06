"""
Recommendation system for personalized financial guidance.

This module provides:
- Content library with curated recommendations per persona
- Recommendation engine for personalization and ranking
- Storage and tracking for user interactions
"""

from spendsense.recommendations.models import (
    Recommendation,
    RecommendationCategory,
    RecommendationType,
    PartnerOffer,
    PartnerOfferType,
    EligibilityCriteria,
)
from spendsense.recommendations.content_library import ContentLibrary, get_content_library
from spendsense.recommendations.partner_offer_library import PartnerOfferLibrary, get_partner_offer_library
from spendsense.recommendations.generated_models import (
    PersonalizedRecommendation,
    RecommendationRequest,
    RecommendationResponse,
    FilterReason,
)
from spendsense.recommendations.engine import RecommendationEngine
from spendsense.recommendations.filtering import FilterEngine
from spendsense.recommendations.personalization import PersonalizationEngine
from spendsense.recommendations.ranking import RankingEngine

__all__ = [
    # Models
    "Recommendation",
    "RecommendationCategory",
    "RecommendationType",
    "PartnerOffer",
    "PartnerOfferType",
    "EligibilityCriteria",
    "PersonalizedRecommendation",
    "RecommendationRequest",
    "RecommendationResponse",
    "FilterReason",
    # Library
    "ContentLibrary",
    "get_content_library",
    "PartnerOfferLibrary",
    "get_partner_offer_library",
    # Engines
    "RecommendationEngine",
    "FilterEngine",
    "PersonalizationEngine",
    "RankingEngine",
]
