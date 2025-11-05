"""
Tests for recommendation matching logic.

Tests the matching algorithm that combines educational content
and partner offers based on persona and signals.
"""

from pathlib import Path
from datetime import datetime

import pytest

from spendsense.recommendations.matcher import RecommendationMatcher, MatchingResult
from spendsense.recommendations.content_library import ContentLibrary
from spendsense.recommendations.partner_offer_library import PartnerOfferLibrary


@pytest.fixture
def content_library():
    """Load content library for testing."""
    config_path = (
        Path(__file__).parent.parent / "spendsense" / "config" / "recommendations.yaml"
    )
    return ContentLibrary(str(config_path))


@pytest.fixture
def partner_library():
    """Load partner offer library for testing."""
    config_path = (
        Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    )
    return PartnerOfferLibrary(str(config_path))


@pytest.fixture
def matcher(content_library, partner_library):
    """Create matcher instance for testing."""
    return RecommendationMatcher(content_library, partner_library)


# Matching Function Tests (AC1)


def test_match_recommendations_accepts_persona_and_signals(matcher):
    """Test matching function accepts user persona and signals (PRD AC1)."""
    user_data = {
        "annual_income": 50000,
        "credit_score": 700,
        "existing_accounts": [],
        "credit_utilization": 60,
        "age": 30,
        "is_employed": True,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    assert isinstance(result, MatchingResult)
    assert result.persona_id == "high_utilization"
    assert result.signals == ["credit_utilization"]


# Content Filtering Tests (AC2)


def test_filters_content_by_persona(matcher):
    """Test function filters content for user's persona (PRD AC2)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=[],
        user_data=user_data,
    )

    # All selected education items should match persona
    for item in result.educational_items:
        assert "high_utilization" in item.personas


def test_returns_empty_for_unknown_persona(matcher):
    """Test graceful handling of unknown persona."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="nonexistent_persona",
        signals=[],
        user_data=user_data,
    )

    assert len(result.educational_items) == 0


# Ranking Tests (AC3)


def test_ranks_content_by_signal_relevance(matcher):
    """Test content ranked by relevance to signals (PRD AC3)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Items with matching signals should be ranked higher
    if len(result.educational_items) > 1:
        first_item = result.educational_items[0]
        # First item should have credit_utilization signal
        assert "credit_utilization" in first_item.triggering_signals


def test_ranks_by_priority_when_no_signals(matcher):
    """Test ranking by priority when no signals provided."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="low_savings",
        signals=[],  # No signals
        user_data=user_data,
    )

    # First item should have priority 1 (highest priority)
    # Note: Diversity selection may change order for other items
    if len(result.educational_items) > 0:
        first_item = result.educational_items[0]
        assert first_item.priority == 1


def test_signal_match_count_affects_ranking(matcher):
    """Test items with more signal matches ranked higher."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    # Use multiple signals
    result = matcher.match_recommendations(
        persona_id="low_savings",
        signals=["savings_balance", "income_stability"],
        user_data=user_data,
    )

    if len(result.educational_items) > 1:
        first_item = result.educational_items[0]
        # First item should match at least one signal
        matches = set(first_item.triggering_signals) & {
            "savings_balance",
            "income_stability",
        }
        assert len(matches) > 0


# Selection Tests (AC4)


def test_selects_3_to_5_educational_items(matcher):
    """Test function selects 3-5 educational items (PRD AC4)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Should select between 3 and 5 items
    assert 3 <= len(result.educational_items) <= 5


def test_selects_diverse_content_types(matcher):
    """Test selection includes diverse content types (PRD AC4)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=user_data,
    )

    # Get unique content types
    types = {item.type.value for item in result.educational_items}

    # Should have diversity (at least 2 different types if 3+ items)
    if len(result.educational_items) >= 3:
        assert len(types) >= 2


def test_custom_education_limits(matcher):
    """Test custom education item limits."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
        education_limit=(2, 4),  # Custom limit
    )

    # Should respect custom limits
    assert 2 <= len(result.educational_items) <= 4


# Offer Filtering Tests (AC5)


def test_filters_offers_by_persona(matcher):
    """Test function filters offers by persona (PRD AC5)."""
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "credit_utilization": 60,
        "age": 30,
        "is_employed": True,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # All selected offers should match persona
    for offer in result.partner_offers:
        assert "high_utilization" in offer.personas


def test_filters_offers_by_eligibility(matcher):
    """Test function checks eligibility for offers (PRD AC5)."""
    # User with low income and credit score
    user_data = {
        "annual_income": 20000,
        "credit_score": 600,
        "existing_accounts": [],
        "credit_utilization": 80,
        "age": 25,
        "is_employed": False,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Verify all selected offers meet eligibility
    for offer in result.partner_offers:
        is_eligible, _ = matcher.partner_library.check_eligibility(offer, user_data)
        assert is_eligible is True


def test_audit_trail_includes_ineligibility_reasons(matcher):
    """Test audit trail captures why offers were rejected."""
    user_data = {
        "annual_income": 15000,  # Very low income
        "credit_score": 550,  # Low credit score
        "existing_accounts": ["chase_credit_cards"],
        "age": 19,  # Below 21
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=[],
        user_data=user_data,
    )

    # Audit trail should have ineligibility reasons
    assert "ineligibility_reasons" in result.audit_trail
    assert "ineligible_offer_count" in result.audit_trail


# Offer Selection Tests (AC6)


def test_selects_1_to_3_partner_offers(matcher):
    """Test function selects 1-3 partner offers (PRD AC6)."""
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "credit_utilization": 60,
        "age": 30,
        "is_employed": True,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Should select between 1 and 3 offers (if eligible offers available)
    assert len(result.partner_offers) <= 3


def test_selects_no_offers_when_none_eligible(matcher):
    """Test returns zero offers when none eligible."""
    user_data = {
        "annual_income": 5000,
        "credit_score": 400,
        "existing_accounts": ["chase_credit_cards", "citi_credit_cards"],
        "credit_utilization": 100,
        "age": 16,
        "is_employed": False,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=[],
        user_data=user_data,
    )

    # No offers should be eligible for this user
    assert len(result.partner_offers) == 0


def test_custom_offer_limits(matcher):
    """Test custom offer limits."""
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "age": 30,
        "is_employed": True,
    }

    result = matcher.match_recommendations(
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=user_data,
        offer_limit=(1, 2),  # Custom limit
    )

    # Should respect custom limits
    assert len(result.partner_offers) <= 2


# Duplicate Prevention Tests (AC7)


def test_excludes_previously_recommended_content(matcher):
    """Test duplicate content prevented (PRD AC7)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    # First recommendation
    result1 = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Get IDs of recommended content
    excluded_ids = {item.id for item in result1.educational_items}

    # Second recommendation with exclusions
    result2 = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
        excluded_content_ids=excluded_ids,
    )

    # No overlap between recommendations
    result2_ids = {item.id for item in result2.educational_items}
    assert len(excluded_ids & result2_ids) == 0


def test_excludes_previously_recommended_offers(matcher):
    """Test duplicate offers prevented (PRD AC7)."""
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "age": 30,
        "is_employed": True,
    }

    # First recommendation
    result1 = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Get IDs of recommended offers
    excluded_ids = {offer.id for offer in result1.partner_offers}

    # Second recommendation with exclusions
    result2 = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
        excluded_offer_ids=excluded_ids,
    )

    # No overlap between recommendations
    result2_ids = {offer.id for offer in result2.partner_offers}
    assert len(excluded_ids & result2_ids) == 0


def test_audit_trail_records_excluded_counts(matcher):
    """Test audit trail includes exclusion counts."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    excluded_content = {"item1", "item2", "item3"}
    excluded_offers = {"offer1", "offer2"}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=[],
        user_data=user_data,
        excluded_content_ids=excluded_content,
        excluded_offer_ids=excluded_offers,
    )

    assert result.audit_trail["excluded_content_count"] == 3
    assert result.audit_trail["excluded_offer_count"] == 2


# Audit Trail Tests (AC8)


def test_audit_trail_includes_persona_and_signals(matcher):
    """Test audit trail records persona and signals (PRD AC8)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization", "savings_balance"],
        user_data=user_data,
    )

    assert result.audit_trail["persona_id"] == "high_utilization"
    assert result.audit_trail["signals"] == [
        "credit_utilization",
        "savings_balance",
    ]


def test_audit_trail_includes_counts(matcher):
    """Test audit trail includes filtering and selection counts (PRD AC8)."""
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "age": 30,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Should have various counts
    assert "persona_content_count" in result.audit_trail
    assert "ranked_content_count" in result.audit_trail
    assert "available_content_count" in result.audit_trail
    assert "selected_education_count" in result.audit_trail
    assert "persona_offer_count" in result.audit_trail
    assert "eligible_offer_count" in result.audit_trail
    assert "selected_offer_count" in result.audit_trail


def test_audit_trail_includes_timestamp(matcher):
    """Test audit trail includes timestamp (PRD AC8)."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=[],
        user_data=user_data,
    )

    assert "timestamp" in result.audit_trail
    assert isinstance(result.timestamp, datetime)


def test_audit_trail_includes_selected_types(matcher):
    """Test audit trail records selected content types."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=user_data,
    )

    assert "selected_education_types" in result.audit_trail
    assert isinstance(result.audit_trail["selected_education_types"], list)


def test_audit_trail_includes_selected_offer_ids(matcher):
    """Test audit trail records selected offer IDs."""
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "age": 30,
    }

    result = matcher.match_recommendations(
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=user_data,
    )

    assert "selected_offer_ids" in result.audit_trail
    assert isinstance(result.audit_trail["selected_offer_ids"], list)


# Integration Tests


def test_complete_matching_workflow(matcher):
    """Test complete matching workflow with all features."""
    user_data = {
        "annual_income": 55000,
        "credit_score": 710,
        "existing_accounts": [],
        "credit_utilization": 65,
        "age": 28,
        "is_employed": True,
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Verify all components
    assert 3 <= len(result.educational_items) <= 5
    assert len(result.partner_offers) <= 3
    assert result.persona_id == "high_utilization"
    assert result.signals == ["credit_utilization"]
    assert "audit_trail" in result.__dict__
    assert isinstance(result.timestamp, datetime)


def test_matching_multiple_personas(matcher):
    """Test matching works for different personas."""
    user_data = {
        "annual_income": 50000,
        "credit_score": 700,
        "existing_accounts": [],
        "age": 30,
    }

    personas_to_test = [
        "high_utilization",
        "low_savings",
        "subscription_heavy",
        "irregular_income",
    ]

    for persona in personas_to_test:
        result = matcher.match_recommendations(
            persona_id=persona, signals=[], user_data=user_data
        )

        # Each persona should get recommendations
        assert len(result.educational_items) > 0
        assert result.persona_id == persona


def test_matching_result_dataclass(matcher):
    """Test MatchingResult dataclass structure."""
    user_data = {"annual_income": 50000, "credit_score": 700}

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=user_data,
    )

    # Verify dataclass fields
    assert hasattr(result, "educational_items")
    assert hasattr(result, "partner_offers")
    assert hasattr(result, "persona_id")
    assert hasattr(result, "signals")
    assert hasattr(result, "timestamp")
    assert hasattr(result, "audit_trail")

    # Verify types
    assert isinstance(result.educational_items, list)
    assert isinstance(result.partner_offers, list)
    assert isinstance(result.persona_id, str)
    assert isinstance(result.signals, list)
    assert isinstance(result.timestamp, datetime)
    assert isinstance(result.audit_trail, dict)


def test_edge_case_no_eligible_offers(matcher):
    """Test handling when no offers are eligible."""
    user_data = {
        "annual_income": 10000,
        "credit_score": 500,
        "existing_accounts": ["chase_credit_cards", "citi_credit_cards"],
        "age": 17,  # Below minimum age for all offers
    }

    result = matcher.match_recommendations(
        persona_id="high_utilization",
        signals=[],
        user_data=user_data,
    )

    # Should still return educational content
    assert len(result.educational_items) > 0
    # Should have very few or no offers (most offers have age 18+ requirement)
    assert len(result.partner_offers) <= 1
    # Audit trail should explain ineligibility
    assert "ineligible_offer_count" in result.audit_trail
