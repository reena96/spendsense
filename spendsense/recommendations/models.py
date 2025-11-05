"""
Data models for the recommendation system.

Defines Pydantic models for recommendations with validation.
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class RecommendationCategory(str, Enum):
    """Categories for recommendation types."""
    EDUCATION = "education"
    ACTION = "action"
    TIP = "tip"
    INSIGHT = "insight"


class RecommendationType(str, Enum):
    """Content types per PRD specification."""
    ARTICLE = "article"
    TEMPLATE = "template"
    CALCULATOR = "calculator"
    VIDEO = "video"


class DifficultyLevel(str, Enum):
    """Difficulty levels for recommendations."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TimeCommitment(str, Enum):
    """Time commitment levels for recommendations."""
    ONE_TIME = "one-time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONGOING = "ongoing"


class EstimatedImpact(str, Enum):
    """Estimated impact levels for recommendations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recommendation(BaseModel):
    """
    Individual recommendation model with metadata.

    Attributes:
        id: Unique identifier (kebab-case)
        type: Content type per PRD (article/template/calculator/video) - AC2
        title: Short, action-oriented title (5-10 words)
        description: Detailed explanation (1-3 sentences)
        personas: List of applicable persona IDs - AC3
        triggering_signals: List of signal types that trigger this rec - AC4
        category: Internal classification (education, action, tip, insight)
        priority: Integer ranking (1=highest priority)
        difficulty: Skill level required (beginner, intermediate, advanced)
        time_commitment: Effort required (one-time, daily, weekly, monthly, ongoing)
        estimated_impact: Expected benefit (low, medium, high)
        content_url: Optional link to detailed content
        personalization_template: Optional template string for signal substitution
    """

    id: str = Field(..., description="Unique identifier in kebab-case")
    type: RecommendationType = Field(..., description="Content type (PRD AC2)")
    title: str = Field(..., min_length=5, max_length=100, description="Action-oriented title")
    description: str = Field(..., min_length=10, max_length=500, description="Detailed explanation")
    personas: List[str] = Field(..., min_items=1, description="Applicable persona IDs (PRD AC3)")
    triggering_signals: List[str] = Field(default_factory=list, description="Signal types that trigger this (PRD AC4)")
    category: RecommendationCategory = Field(..., description="Internal classification")
    priority: int = Field(..., ge=1, le=10, description="Priority ranking (1=highest)")
    difficulty: DifficultyLevel = Field(..., description="Skill level required")
    time_commitment: TimeCommitment = Field(..., description="Effort required")
    estimated_impact: EstimatedImpact = Field(..., description="Expected benefit")
    content_url: Optional[str] = Field(None, description="Link to detailed content")
    personalization_template: Optional[str] = Field(None, description="Template for signal substitution")

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID is in kebab-case format."""
        if not v:
            raise ValueError("ID cannot be empty")
        if not all(c.islower() or c.isdigit() or c in "-_" for c in v):
            raise ValueError("ID must be in kebab-case (lowercase, hyphens, underscores only)")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("ID cannot start or end with hyphen")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is concise and action-oriented."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        word_count = len(v.split())
        if word_count < 2:
            raise ValueError("Title should be at least 2 words")
        if word_count > 15:
            raise ValueError("Title should be at most 15 words (aim for 5-10)")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description is clear and detailed."""
        if not v or not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()

    def __str__(self) -> str:
        """String representation for logging."""
        return f"[{self.category.value.upper()}] {self.title} (priority={self.priority})"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return (
            f"Recommendation(id='{self.id}', category={self.category.value}, "
            f"priority={self.priority}, impact={self.estimated_impact.value})"
        )

    @property
    def is_high_priority(self) -> bool:
        """Check if recommendation is high priority (1-3)."""
        return self.priority <= 3

    @property
    def is_quick_win(self) -> bool:
        """Check if recommendation is a quick win (one-time or low difficulty)."""
        return (
            self.time_commitment == TimeCommitment.ONE_TIME
            or self.difficulty == DifficultyLevel.BEGINNER
        )

    @property
    def impact_score(self) -> int:
        """Get numeric impact score for sorting (high=3, medium=2, low=1)."""
        impact_map = {
            EstimatedImpact.HIGH: 3,
            EstimatedImpact.MEDIUM: 2,
            EstimatedImpact.LOW: 1,
        }
        return impact_map[self.estimated_impact]

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "personas": self.personas,
            "triggering_signals": self.triggering_signals,
            "category": self.category.value,
            "priority": self.priority,
            "difficulty": self.difficulty.value,
            "time_commitment": self.time_commitment.value,
            "estimated_impact": self.estimated_impact.value,
            "content_url": self.content_url,
            "personalization_template": self.personalization_template,
        }


# Story 4.2: Partner Offer Catalog Models


class PartnerOfferType(str, Enum):
    """Partner offer types per PRD specification (AC2)."""
    SAVINGS_ACCOUNT = "savings_account"
    CREDIT_CARD = "credit_card"
    APP = "app"
    TOOL = "tool"


class EligibilityCriteria(BaseModel):
    """
    Eligibility criteria for partner offers (PRD AC3).

    Attributes:
        min_income: Minimum annual income required (null = no requirement)
        min_credit_score: Minimum credit score required (null = no requirement)
        excluded_accounts: List of account types user must NOT have
        max_credit_utilization: Maximum credit utilization allowed (0-100)
        min_age: Minimum age requirement
        employment_required: Whether user must be employed
    """

    min_income: Optional[int] = Field(None, ge=0, description="Minimum annual income in dollars")
    min_credit_score: Optional[int] = Field(None, ge=300, le=850, description="Minimum credit score")
    excluded_accounts: List[str] = Field(default_factory=list, description="Account types that disqualify user")
    max_credit_utilization: Optional[int] = Field(None, ge=0, le=100, description="Maximum utilization percentage")
    min_age: Optional[int] = Field(None, ge=18, le=100, description="Minimum age requirement")
    employment_required: bool = Field(False, description="Whether employment is required")


class PartnerOffer(BaseModel):
    """
    Partner offer model with eligibility and persona targeting.

    Attributes:
        id: Unique identifier (kebab-case)
        type: Offer type (savings_account/credit_card/app/tool) - AC2
        title: Short, compelling title (5-15 words)
        description: Plain-language explanation (1-3 sentences) - AC8
        personas: List of applicable persona IDs - AC4
        eligibility: Eligibility criteria (income, credit, exclusions) - AC3
        priority: Integer ranking (1=highest priority)
        provider: Company/institution providing the offer
        offer_url: Link to partner offer landing page
        key_benefits: List of main selling points (3-5 items)
        rationale_template: Template for explaining why this offer matches user
        disclaimer: Legal/regulatory disclaimer text
    """

    id: str = Field(..., description="Unique identifier in kebab-case")
    type: PartnerOfferType = Field(..., description="Offer type (PRD AC2)")
    title: str = Field(..., min_length=5, max_length=150, description="Compelling offer title")
    description: str = Field(..., min_length=20, max_length=500, description="Plain-language summary (AC8)")
    personas: List[str] = Field(..., min_items=1, description="Applicable persona IDs (PRD AC4)")
    eligibility: EligibilityCriteria = Field(default_factory=EligibilityCriteria, description="Eligibility criteria (AC3)")
    priority: int = Field(..., ge=1, le=10, description="Priority ranking (1=highest)")
    provider: str = Field(..., min_length=2, max_length=100, description="Provider name")
    offer_url: Optional[str] = Field(None, description="Link to partner offer page")
    key_benefits: List[str] = Field(default_factory=list, description="Main selling points (3-5 items)")
    rationale_template: Optional[str] = Field(None, description="Template for personalized rationale")
    disclaimer: Optional[str] = Field(None, description="Legal/regulatory disclaimer")

    @field_validator("id")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate ID is in kebab-case format."""
        if not v:
            raise ValueError("ID cannot be empty")
        if not all(c.islower() or c.isdigit() or c in "-_" for c in v):
            raise ValueError("ID must be in kebab-case (lowercase, hyphens, underscores only)")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("ID cannot start or end with hyphen")
        return v

    @field_validator("key_benefits")
    @classmethod
    def validate_key_benefits(cls, v: List[str]) -> List[str]:
        """Validate key benefits list is reasonable."""
        if len(v) > 10:
            raise ValueError("Too many key benefits (max 10)")
        for benefit in v:
            if not benefit or not benefit.strip():
                raise ValueError("Key benefits cannot be empty")
            if len(benefit) > 200:
                raise ValueError("Individual key benefit too long (max 200 chars)")
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "personas": self.personas,
            "eligibility": {
                "min_income": self.eligibility.min_income,
                "min_credit_score": self.eligibility.min_credit_score,
                "excluded_accounts": self.eligibility.excluded_accounts,
                "max_credit_utilization": self.eligibility.max_credit_utilization,
                "min_age": self.eligibility.min_age,
                "employment_required": self.eligibility.employment_required,
            },
            "priority": self.priority,
            "provider": self.provider,
            "offer_url": self.offer_url,
            "key_benefits": self.key_benefits,
            "rationale_template": self.rationale_template,
            "disclaimer": self.disclaimer,
        }
