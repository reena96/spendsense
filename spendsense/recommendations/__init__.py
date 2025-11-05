"""
Recommendation system for personalized financial guidance.

This module provides:
- Content library with curated recommendations per persona
- Recommendation engine for personalization and ranking
- Storage and tracking for user interactions
"""

from spendsense.recommendations.models import Recommendation, RecommendationCategory
from spendsense.recommendations.content_library import ContentLibrary, get_content_library

__all__ = [
    "Recommendation",
    "RecommendationCategory",
    "ContentLibrary",
    "get_content_library",
]
