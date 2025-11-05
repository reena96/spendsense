"""
Data models for generated (personalized) recommendations.

Extends base Recommendation model with personalization metadata.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from spendsense.recommendations.models import (
    RecommendationCategory,
    DifficultyLevel,
    TimeCommitment,
    EstimatedImpact,
)


class PersonalizedRecommendation(BaseModel):
    """
    Personalized recommendation for a specific user.

    Extends base Recommendation with personalization metadata, relevance scoring,
    and user context.

    Attributes:
        # Original recommendation fields
        recommendation_id: Unique identifier from content library
        category: Type of recommendation (education, action, tip, insight)
        title: Action-oriented title
        description: Personalized description (after template substitution)
        original_description: Original description before personalization
        priority: Content library priority (1=highest)
        difficulty: Skill level required
        time_commitment: Effort required
        estimated_impact: Expected benefit
        content_url: Optional link to detailed content

        # Personalization metadata
        personalized: Whether template substitution was performed
        substitutions: Signal values used in personalization
        relevance_score: Calculated relevance (0.0-1.0, higher is better)
        rank: Final ranking position (1=top recommendation)

        # User context
        user_id: User this recommendation is for
        persona_id: Assigned persona
        generated_at: Timestamp of generation
    """

    # Original recommendation fields
    recommendation_id: str = Field(..., description="Unique identifier from content library")
    category: RecommendationCategory = Field(..., description="Recommendation category")
    title: str = Field(..., description="Action-oriented title")
    description: str = Field(..., description="Personalized description")
    original_description: str = Field(..., description="Original description before personalization")
    priority: int = Field(..., ge=1, le=10, description="Content library priority")
    difficulty: DifficultyLevel = Field(..., description="Skill level required")
    time_commitment: TimeCommitment = Field(..., description="Effort required")
    estimated_impact: EstimatedImpact = Field(..., description="Expected benefit")
    content_url: Optional[str] = Field(None, description="Link to detailed content")

    # Personalization metadata
    personalized: bool = Field(..., description="Was template substitution performed?")
    substitutions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Signal values used in personalization"
    )
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0.0-1.0)")
    rank: int = Field(..., ge=1, description="Final ranking position (1=top)")

    # User context
    user_id: str = Field(..., description="User this recommendation is for")
    persona_id: str = Field(..., description="Assigned persona")
    generated_at: datetime = Field(..., description="Timestamp of generation")

    def __str__(self) -> str:
        """String representation for logging."""
        personalized_flag = "✓" if self.personalized else "✗"
        return (
            f"#{self.rank} [{self.category.value.upper()}] {self.title} "
            f"(relevance={self.relevance_score:.2f}, personalized={personalized_flag})"
        )

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"PersonalizedRecommendation(id='{self.recommendation_id}', "
            f"rank={self.rank}, relevance={self.relevance_score:.2f}, "
            f"personalized={self.personalized})"
        )

    @property
    def is_high_relevance(self) -> bool:
        """Check if recommendation has high relevance (>0.7)."""
        return self.relevance_score > 0.7

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "recommendation_id": self.recommendation_id,
            "category": self.category.value,
            "title": self.title,
            "description": self.description,
            "original_description": self.original_description,
            "priority": self.priority,
            "difficulty": self.difficulty.value,
            "time_commitment": self.time_commitment.value,
            "estimated_impact": self.estimated_impact.value,
            "content_url": self.content_url,
            "personalized": self.personalized,
            "substitutions": self.substitutions,
            "relevance_score": self.relevance_score,
            "rank": self.rank,
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "generated_at": self.generated_at.isoformat(),
        }


class RecommendationRequest(BaseModel):
    """
    Request for generating recommendations.

    Attributes:
        user_id: User to generate recommendations for
        persona_id: Assigned persona (from Epic 3)
        time_window: Time window for signals ("30d" or "180d")
        limit: Maximum number of recommendations to return
        include_metadata: Include personalization metadata in response
    """

    user_id: str = Field(..., description="User to generate recommendations for")
    persona_id: str = Field(..., description="Assigned persona")
    time_window: str = Field(..., description="Time window for signals (30d or 180d)")
    limit: int = Field(10, ge=1, le=50, description="Maximum recommendations to return")
    include_metadata: bool = Field(False, description="Include personalization metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_MASKED_000",
                "persona_id": "low_savings",
                "time_window": "30d",
                "limit": 10,
                "include_metadata": False,
            }
        }


class RecommendationResponse(BaseModel):
    """
    Response with generated recommendations.

    Attributes:
        user_id: User recommendations were generated for
        persona_id: Assigned persona used
        time_window: Time window for signals used
        recommendations: List of personalized recommendations
        generated_at: Timestamp of generation
        generation_time_ms: Time taken to generate (milliseconds)
        metadata: Optional additional metadata (filtering stats, etc.)
    """

    user_id: str = Field(..., description="User recommendations were generated for")
    persona_id: str = Field(..., description="Assigned persona used")
    time_window: str = Field(..., description="Time window for signals used")
    recommendations: List[PersonalizedRecommendation] = Field(
        ...,
        description="List of personalized recommendations"
    )
    generated_at: datetime = Field(..., description="Timestamp of generation")
    generation_time_ms: float = Field(..., description="Generation time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "user_id": self.user_id,
            "persona_id": self.persona_id,
            "time_window": self.time_window,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "generated_at": self.generated_at.isoformat(),
            "generation_time_ms": self.generation_time_ms,
            "metadata": self.metadata,
        }

    def __str__(self) -> str:
        """String representation for logging."""
        return (
            f"RecommendationResponse(user={self.user_id}, persona={self.persona_id}, "
            f"count={len(self.recommendations)}, time={self.generation_time_ms:.1f}ms)"
        )


class FilterReason(BaseModel):
    """
    Reason for filtering out a recommendation.

    Tracks why recommendations were excluded during filtering phase.
    """

    recommendation_id: str = Field(..., description="Filtered recommendation ID")
    reason: str = Field(..., description="Human-readable filter reason")
    rule_name: str = Field(..., description="Filter rule that triggered")
    signal_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Signal values that caused filtering"
    )

    def __str__(self) -> str:
        """String representation for logging."""
        return f"{self.recommendation_id}: {self.reason} (rule={self.rule_name})"
