"""
Integration tests for recommendation engine.

Tests the complete pipeline: load → filter → personalize → rank
"""

import pytest
from datetime import date
from spendsense.recommendations.engine import RecommendationEngine
from spendsense.recommendations.generated_models import RecommendationRequest
from spendsense.features.behavioral_summary import BehavioralSummaryGenerator


@pytest.fixture
def engine():
    """Recommendation engine instance."""
    return RecommendationEngine()


@pytest.fixture
def signal_gen():
    """Behavioral summary generator."""
    return BehavioralSummaryGenerator("data/processed/spendsense.db")


# === End-to-End Integration Tests ===


def test_generate_recommendations_low_savings(engine, signal_gen):
    """Test generating recommendations for low_savings persona."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=10,
    )

    response = engine.generate_recommendations(request, signals)

    # Verify response structure
    assert response.user_id == user_id
    assert response.persona_id == "low_savings"
    assert len(response.recommendations) > 0
    assert len(response.recommendations) <= 10

    # Verify performance
    assert response.generation_time_ms < 100  # <100ms requirement

    # Verify recommendations are ranked
    for i in range(len(response.recommendations) - 1):
        assert response.recommendations[i].rank == i + 1
        assert (
            response.recommendations[i].relevance_score >=
            response.recommendations[i + 1].relevance_score
        )

    # Verify metadata
    assert "base_count" in response.metadata
    assert "filtered_count" in response.metadata
    assert "personalized_count" in response.metadata


def test_personalization_works(engine, signal_gen):
    """Test that personalization substitutes signal values."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=10,
    )

    response = engine.generate_recommendations(request, signals)

    # Should have at least one personalized recommendation
    personalized_recs = [r for r in response.recommendations if r.personalized]
    assert len(personalized_recs) > 0

    # Check personalized rec has substitutions
    for rec in personalized_recs:
        assert len(rec.substitutions) > 0
        assert rec.description != rec.original_description


def test_filtering_works(engine, signal_gen):
    """Test that filtering removes irrelevant recommendations."""
    # User with stable income should not get irregular income recs
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    # This user has biweekly income (stable)
    assert signals.income_30d.payment_frequency == "biweekly"

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=20,
        include_metadata=True,
    )

    response = engine.generate_recommendations(request, signals)

    # Should have filtered out some recommendations
    assert response.metadata["filtered_count"] >= 0

    # Verify no irregular income recs in results
    irregular_income_recs = [
        "variable_income_budgeting",
        "income_averaging_strategy",
    ]
    rec_ids = [r.recommendation_id for r in response.recommendations]
    for rec_id in irregular_income_recs:
        assert rec_id not in rec_ids


def test_ranking_by_relevance(engine, signal_gen):
    """Test that recommendations are ranked by relevance score."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=10,
    )

    response = engine.generate_recommendations(request, signals)

    # Top recommendation should have highest relevance score
    assert response.recommendations[0].rank == 1
    assert response.recommendations[0].relevance_score >= 0.7  # High relevance

    # Scores should be descending
    scores = [r.relevance_score for r in response.recommendations]
    assert scores == sorted(scores, reverse=True)


def test_performance_requirement(engine, signal_gen):
    """Test that generation meets <100ms performance requirement."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=10,
    )

    response = engine.generate_recommendations(request, signals)

    # Performance requirement: <100ms
    assert response.generation_time_ms < 100


def test_limit_parameter(engine, signal_gen):
    """Test that limit parameter controls number of recommendations."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    # Request 3 recommendations
    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=3,
    )

    response = engine.generate_recommendations(request, signals)

    # Should return exactly 3
    assert len(response.recommendations) == 3
    assert response.recommendations[-1].rank == 3


def test_high_priority_recommendations_ranked_first(engine, signal_gen):
    """Test that high-priority recommendations rank highly."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="low_savings",
        time_window="30d",
        limit=10,
    )

    response = engine.generate_recommendations(request, signals)

    # Top 3 should be priority 1-3 from content library
    top_3 = response.recommendations[:3]
    for rec in top_3:
        assert rec.priority <= 3  # Low priority number = high priority


def test_generate_convenience_method(engine, signal_gen):
    """Test convenience generate() method."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    # Use convenience method
    recommendations = engine.generate(
        user_id=user_id,
        persona_id="low_savings",
        behavioral_signals=signals,
        limit=5,
    )

    assert len(recommendations) == 5
    assert all(r.user_id == user_id for r in recommendations)
    assert all(r.persona_id == "low_savings" for r in recommendations)


def test_empty_persona_returns_empty_response(engine, signal_gen):
    """Test handling of unknown persona."""
    user_id = "user_MASKED_000"
    signals = signal_gen.generate_summary(user_id, date(2025, 11, 5))

    request = RecommendationRequest(
        user_id=user_id,
        persona_id="nonexistent_persona",
        time_window="30d",
        limit=10,
    )

    response = engine.generate_recommendations(request, signals)

    # Should return empty list
    assert len(response.recommendations) == 0
    assert "reason" in response.metadata
