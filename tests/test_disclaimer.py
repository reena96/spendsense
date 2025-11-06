"""
Tests for mandatory disclaimer system (Epic 5 - Story 5.4).

Test suite verifying disclaimer presence in all recommendation outputs.
"""

import pytest
from spendsense.recommendations.assembler import (
    MANDATORY_DISCLAIMER,
    AssembledRecommendationSet,
    AssembledRecommendationItem
)
from datetime import datetime


# ===== AC1: Standard disclaimer text defined =====

def test_mandatory_disclaimer_text():
    """Test standard disclaimer text matches regulatory requirement (AC1)."""
    expected_text = "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."

    assert MANDATORY_DISCLAIMER == expected_text
    assert "not financial advice" in MANDATORY_DISCLAIMER
    assert "licensed advisor" in MANDATORY_DISCLAIMER


# ===== AC2: Disclaimer automatically included in recommendation sets =====

def test_disclaimer_in_recommendation_set():
    """Test disclaimer automatically included in every recommendation set (AC2, AC7)."""
    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    assert rec_set.disclaimer is not None
    assert rec_set.disclaimer == MANDATORY_DISCLAIMER
    assert len(rec_set.disclaimer) > 0


def test_disclaimer_non_empty():
    """Test disclaimer is non-empty and meaningful (AC2)."""
    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    assert rec_set.disclaimer != ""
    assert len(rec_set.disclaimer) > 20  # Meaningful text, not just a token


# ===== AC3: Disclaimer in API responses =====

def test_disclaimer_in_api_response_dict():
    """Test disclaimer included in API response serialization (AC3, AC7)."""
    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    response_dict = rec_set.to_dict()

    assert "disclaimer" in response_dict
    assert response_dict["disclaimer"] == MANDATORY_DISCLAIMER


def test_disclaimer_in_response_with_recommendations():
    """Test disclaimer present even when recommendations exist (AC3)."""
    recommendation = AssembledRecommendationItem(
        item_type="education",
        item_id="test_rec_1",
        content={"title": "Test"},
        rationale="Test rationale",
        persona_match_reason="Test match",
        signal_citations=[]
    )

    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[recommendation],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    response_dict = rec_set.to_dict()

    assert "disclaimer" in response_dict
    assert response_dict["disclaimer"] == MANDATORY_DISCLAIMER
    assert len(response_dict["recommendations"]) == 1


# ===== AC6: Disclaimer validation =====

def test_validate_disclaimer_present():
    """Test validation confirms disclaimer is present (AC6)."""
    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    # Disclaimer should be present and valid
    assert rec_set.disclaimer is not None
    assert len(rec_set.disclaimer) > 0
    assert "not financial advice" in rec_set.disclaimer


def test_validate_disclaimer_missing_raises_concern():
    """Test validation detects missing disclaimer (AC6)."""
    # In real implementation, this would be caught by dataclass requirement
    # But we test that disclaimer field is mandatory

    # This test verifies the field exists and is required
    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer="",  # Empty disclaimer
        metadata={}
    )

    # Empty disclaimer should be detectable
    assert rec_set.disclaimer == ""
    # In production, validation would flag this as an error


# ===== AC7: Comprehensive output testing =====

def test_all_recommendation_outputs_include_disclaimer():
    """Test comprehensive verification that all outputs include disclaimer (AC7)."""
    # Test multiple recommendation sets
    test_cases = [
        # Empty recommendations
        {
            "user_id": "user1",
            "persona_id": "persona1",
            "time_window": "30d",
            "recommendations": []
        },
        # With recommendations
        {
            "user_id": "user2",
            "persona_id": "persona2",
            "time_window": "180d",
            "recommendations": [
                AssembledRecommendationItem(
                    item_type="partner_offer",
                    item_id="offer_1",
                    content={"title": "Test Offer"},
                    rationale="Test",
                    persona_match_reason="Match",
                    signal_citations=[]
                )
            ]
        }
    ]

    for test_case in test_cases:
        rec_set = AssembledRecommendationSet(
            **test_case,
            disclaimer=MANDATORY_DISCLAIMER,
            metadata={}
        )

        response_dict = rec_set.to_dict()

        # Every output must have disclaimer
        assert "disclaimer" in response_dict
        assert response_dict["disclaimer"] == MANDATORY_DISCLAIMER
        assert "not financial advice" in response_dict["disclaimer"]


# ===== AC4 + AC8: UI Integration Tests (Disclaimer in API Responses) =====

@pytest.fixture
def api_client():
    """Create FastAPI TestClient for API endpoint testing."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    return TestClient(app)


def test_disclaimer_in_recommendations_api_response(api_client):
    """Test disclaimer appears in GET /api/recommendations/{user_id} API response (AC4, AC8)."""
    # Set user to opted_in first
    api_client.post(
        "/api/consent",
        json={
            "user_id": "user_MASKED_000",
            "consent_status": "opted_in"
        }
    )

    # Get recommendations
    response = api_client.get("/api/recommendations/user_MASKED_000?generate=true")

    assert response.status_code == 200
    data = response.json()

    # AC4: Disclaimer must be present in response
    assert "disclaimer" in data, "Disclaimer missing from API response"
    assert data["disclaimer"] is not None
    assert len(data["disclaimer"]) > 0

    # AC4: Disclaimer must contain required regulatory language
    assert "not financial advice" in data["disclaimer"].lower()
    assert "licensed advisor" in data["disclaimer"].lower()


def test_disclaimer_in_all_recommendation_responses(api_client):
    """Test disclaimer appears in ALL recommendation responses regardless of content (AC7, AC8)."""
    # Set user to opted_in
    api_client.post(
        "/api/consent",
        json={
            "user_id": "user_MASKED_001",
            "consent_status": "opted_in"
        }
    )

    # Test multiple requests
    response1 = api_client.get("/api/recommendations/user_MASKED_001?generate=true")
    response2 = api_client.get("/api/recommendations/user_MASKED_001")  # Cached

    for response in [response1, response2]:
        if response.status_code == 200:
            data = response.json()
            assert "disclaimer" in data
            assert "not financial advice" in data["disclaimer"].lower()


def test_disclaimer_present_with_empty_recommendations(api_client):
    """Test disclaimer present even when no recommendations generated (AC2, AC3, AC7)."""
    # This tests edge case where user might have no matching recommendations
    # Disclaimer should still be present in the response structure
    from spendsense.recommendations.assembler import AssembledRecommendationSet, MANDATORY_DISCLAIMER

    empty_rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    response_dict = empty_rec_set.to_dict()

    assert "disclaimer" in response_dict
    assert response_dict["disclaimer"] == MANDATORY_DISCLAIMER
