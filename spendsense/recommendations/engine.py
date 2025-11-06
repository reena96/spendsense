"""
Main recommendation engine for generating personalized recommendations.

Orchestrates content library, filtering, personalization, and ranking
to generate relevant, personalized financial recommendations.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from spendsense.recommendations.content_library import ContentLibrary
from spendsense.recommendations.filtering import FilterEngine
from spendsense.recommendations.personalization import PersonalizationEngine
from spendsense.recommendations.ranking import RankingEngine
from spendsense.recommendations.generated_models import (
    PersonalizedRecommendation,
    RecommendationRequest,
    RecommendationResponse,
)
from spendsense.features.behavioral_summary import BehavioralSummary

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Main recommendation engine.

    Generates personalized financial recommendations by:
    1. Loading base recommendations from content library
    2. Filtering based on user context
    3. Personalizing with signal values
    4. Ranking by relevance
    5. Returning top N recommendations

    Usage:
        engine = RecommendationEngine()
        response = engine.generate_recommendations(request, signals)
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize recommendation engine.

        Args:
            config_path: Path to recommendations YAML file
                        If None, uses default path
        """
        if config_path is None:
            config_path = str(
                Path(__file__).parent.parent / "config" / "recommendations.yaml"
            )

        self.content_library = ContentLibrary(config_path)
        self.filter_engine = FilterEngine()
        self.personalizer = PersonalizationEngine()
        self.ranker = RankingEngine()

        logger.info(f"RecommendationEngine initialized with {config_path}")

    def generate_recommendations(
        self,
        request: RecommendationRequest,
        behavioral_signals: BehavioralSummary,
    ) -> RecommendationResponse:
        """
        Generate personalized recommendations for a user.

        Args:
            request: Recommendation request with user_id, persona_id, etc.
            behavioral_signals: User's behavioral signals

        Returns:
            RecommendationResponse with personalized recommendations

        Example:
            >>> engine = RecommendationEngine()
            >>> request = RecommendationRequest(
            ...     user_id="user_MASKED_000",
            ...     persona_id="low_savings",
            ...     time_window="30d",
            ...     limit=10
            ... )
            >>> response = engine.generate_recommendations(request, signals)
            >>> print(f"Generated {len(response.recommendations)} recommendations")
        """
        start_time = time.time()

        try:
            # 1. Load base recommendations for persona
            base_recommendations = self.content_library.get_by_persona(request.persona_id)

            if not base_recommendations:
                logger.warning(f"No recommendations found for persona: {request.persona_id}")
                return self._empty_response(request, start_time)

            logger.info(
                f"Loaded {len(base_recommendations)} base recommendations "
                f"for persona '{request.persona_id}'"
            )

            # 2. Filter based on user context
            filtered_recommendations, filter_reasons = self.filter_engine.filter(
                recommendations=base_recommendations,
                behavioral_signals=behavioral_signals,
                persona_id=request.persona_id,
            )

            if not filtered_recommendations:
                logger.warning("All recommendations filtered out")
                return self._empty_response(request, start_time)

            # 3. Personalize with signal values
            personalized_data = {}
            for rec in filtered_recommendations:
                description, substitutions = self.personalizer.personalize(
                    recommendation=rec,
                    behavioral_signals=behavioral_signals,
                )
                personalized_data[rec.id] = {
                    "description": description,
                    "substitutions": substitutions,
                    "personalized": bool(substitutions),
                }

            # 4. Rank by relevance
            personalized_flags = {
                rec_id: data["personalized"]
                for rec_id, data in personalized_data.items()
            }

            ranked_recommendations = self.ranker.rank(
                recommendations=filtered_recommendations,
                behavioral_signals=behavioral_signals,
                persona_id=request.persona_id,
                personalized_flags=personalized_flags,
            )

            # 5. Convert to PersonalizedRecommendation models and limit
            generated_at = datetime.now()
            personalized_recs = []

            for rank, (rec, relevance_score) in enumerate(ranked_recommendations[:request.limit], 1):
                personalized = PersonalizedRecommendation(
                    # Original fields
                    recommendation_id=rec.id,
                    category=rec.category,
                    title=rec.title,
                    description=personalized_data[rec.id]["description"],
                    original_description=rec.description,
                    priority=rec.priority,
                    difficulty=rec.difficulty,
                    time_commitment=rec.time_commitment,
                    estimated_impact=rec.estimated_impact,
                    content_url=rec.content_url,
                    # Personalization metadata
                    personalized=personalized_data[rec.id]["personalized"],
                    substitutions=personalized_data[rec.id]["substitutions"],
                    relevance_score=relevance_score,
                    rank=rank,
                    # User context
                    user_id=request.user_id,
                    persona_id=request.persona_id,
                    generated_at=generated_at,
                )
                personalized_recs.append(personalized)

            # Calculate generation time
            generation_time_ms = (time.time() - start_time) * 1000

            # Build response
            response = RecommendationResponse(
                user_id=request.user_id,
                persona_id=request.persona_id,
                time_window=request.time_window,
                recommendations=personalized_recs,
                generated_at=generated_at,
                generation_time_ms=generation_time_ms,
                metadata={
                    "base_count": len(base_recommendations),
                    "filtered_count": len(filter_reasons),
                    "personalized_count": sum(1 for r in personalized_recs if r.personalized),
                    "filter_reasons": [str(reason) for reason in filter_reasons] if request.include_metadata else [],
                },
            )

            logger.info(
                f"Generated {len(personalized_recs)} recommendations for {request.user_id} "
                f"in {generation_time_ms:.1f}ms"
            )

            return response

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}", exc_info=True)
            raise

    def _empty_response(
        self,
        request: RecommendationRequest,
        start_time: float,
    ) -> RecommendationResponse:
        """Create empty response when no recommendations available."""
        generation_time_ms = (time.time() - start_time) * 1000

        return RecommendationResponse(
            user_id=request.user_id,
            persona_id=request.persona_id,
            time_window=request.time_window,
            recommendations=[],
            generated_at=datetime.now(),
            generation_time_ms=generation_time_ms,
            metadata={"reason": "No recommendations available after filtering"},
        )

    def generate(
        self,
        user_id: str,
        persona_id: str,
        behavioral_signals: BehavioralSummary,
        time_window: str = "30d",
        limit: int = 10,
        include_metadata: bool = False,
    ) -> List[PersonalizedRecommendation]:
        """
        Convenience method to generate recommendations.

        Args:
            user_id: User to generate recommendations for
            persona_id: Assigned persona
            behavioral_signals: User's behavioral signals
            time_window: Time window for signals (default "30d")
            limit: Maximum recommendations to return (default 10)
            include_metadata: Include filter reasons in metadata

        Returns:
            List of PersonalizedRecommendation objects

        Example:
            >>> engine = RecommendationEngine()
            >>> recs = engine.generate(
            ...     user_id="user_MASKED_000",
            ...     persona_id="low_savings",
            ...     behavioral_signals=signals,
            ...     limit=5
            ... )
        """
        request = RecommendationRequest(
            user_id=user_id,
            persona_id=persona_id,
            time_window=time_window,
            limit=limit,
            include_metadata=include_metadata,
        )

        response = self.generate_recommendations(request, behavioral_signals)
        return response.recommendations
