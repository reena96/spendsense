"""
Tests for recommendation assembler.

Tests the assembly of complete recommendation sets combining
educational content, partner offers, rationales, and metadata.
"""

import time
from pathlib import Path
from datetime import datetime

import pytest

from spendsense.recommendations.assembler import (
    RecommendationAssembler,
    AssembledRecommendationSet,
    AssembledRecommendationItem,
    MANDATORY_DISCLAIMER,
)
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
def assembler(content_library, partner_library):
    """Create assembler instance for testing."""
    return RecommendationAssembler(content_library, partner_library)


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "annual_income": 50000,
        "credit_score": 700,
        "existing_accounts": [],
        "credit_utilization": 68,
        "age": 30,
        "is_employed": True,
        "credit_max_utilization_pct": 68,
        "account_name": "Visa ****4523",
        "savings_balance": 500,
        "months_expenses": 0.5,
    }


# Assembly Function Tests (AC1)


def test_assembler_initialization(assembler):
    """Test assembler can be initialized (PRD AC1)."""
    assert assembler is not None
    assert isinstance(assembler, RecommendationAssembler)
    assert assembler.content_library is not None
    assert assembler.partner_library is not None
    assert assembler.matcher is not None
    assert assembler.rationale_generator is not None


def test_assemble_recommendations_accepts_required_parameters(assembler, sample_user_data):
    """Test assemble function accepts required parameters (PRD AC1)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    assert rec_set is not None
    assert isinstance(rec_set, AssembledRecommendationSet)


# Combination Tests (AC2)


def test_assembler_combines_education_and_offers(assembler, sample_user_data):
    """Test assembler combines education items and partner offers (PRD AC2)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    # Should have both types of recommendations
    education_count = sum(
        1 for rec in rec_set.recommendations if rec.item_type == "education"
    )
    offer_count = sum(
        1 for rec in rec_set.recommendations if rec.item_type == "partner_offer"
    )

    assert education_count >= 3, "Should have at least 3 education items"
    assert offer_count >= 1, "Should have at least 1 partner offer"
    assert education_count + offer_count == len(rec_set.recommendations)


def test_assembled_item_has_required_fields(assembler, sample_user_data):
    """Test each assembled item includes required fields (PRD AC2, AC3)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=sample_user_data,
        time_window="30d",
    )

    assert len(rec_set.recommendations) > 0, "Should have recommendations"

    for item in rec_set.recommendations:
        # AC2: Full content/offer details
        assert item.item_type in ["education", "partner_offer"]
        assert item.item_id is not None
        assert item.content is not None
        assert isinstance(item.content, dict)

        # AC3: Rationale with citations
        assert item.rationale is not None
        assert len(item.rationale) > 0

        # AC3: Persona match reason
        assert item.persona_match_reason is not None
        assert len(item.persona_match_reason) > 0

        # AC3: Signal citations
        assert item.signal_citations is not None
        assert isinstance(item.signal_citations, list)


def test_assembled_item_content_has_expected_structure(assembler, sample_user_data):
    """Test assembled item content has expected structure."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    education_items = [r for r in rec_set.recommendations if r.item_type == "education"]
    offer_items = [r for r in rec_set.recommendations if r.item_type == "partner_offer"]

    # Check education content structure
    if education_items:
        edu = education_items[0].content
        assert "id" in edu
        assert "title" in edu
        assert "description" in edu
        assert "type" in edu
        assert "priority" in edu

    # Check offer content structure
    if offer_items:
        offer = offer_items[0].content
        assert "id" in offer
        assert "title" in offer
        assert "description" in offer
        assert "provider" in offer
        assert "eligibility" in offer


# Time Window Tests (AC3)


def test_assembler_generates_for_30d_window(assembler, sample_user_data):
    """Test assembler generates recommendations for 30-day window (PRD AC3)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=sample_user_data,
        time_window="30d",
    )

    assert rec_set.time_window == "30d"
    assert "30d" in rec_set.metadata["time_window"]


def test_assembler_generates_for_180d_window(assembler, sample_user_data):
    """Test assembler generates recommendations for 180-day window (PRD AC3)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="irregular_income",
        signals=["irregular_income"],
        user_data=sample_user_data,
        time_window="180d",
    )

    assert rec_set.time_window == "180d"
    assert "180d" in rec_set.metadata["time_window"]


def test_assemble_for_multiple_windows(assembler, sample_user_data):
    """Test assembler generates for both time windows (PRD AC3)."""
    rec_sets = assembler.assemble_for_multiple_windows(
        user_id="user_123",
        persona_id="low_savings",
        signals_30d=["savings_balance"],
        signals_180d=["savings_balance", "irregular_income"],
        user_data=sample_user_data,
    )

    assert "30d" in rec_sets
    assert "180d" in rec_sets

    assert rec_sets["30d"].time_window == "30d"
    assert rec_sets["180d"].time_window == "180d"

    # Both should have recommendations
    assert len(rec_sets["30d"].recommendations) > 0
    assert len(rec_sets["180d"].recommendations) > 0


# Disclaimer Tests (AC4)


def test_recommendation_set_includes_disclaimer(assembler, sample_user_data):
    """Test recommendation set includes mandatory disclaimer (PRD AC4)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="young_professional",
        signals=[],
        user_data=sample_user_data,
        time_window="30d",
    )

    assert rec_set.disclaimer is not None
    assert rec_set.disclaimer == MANDATORY_DISCLAIMER
    assert "educational content" in rec_set.disclaimer.lower()
    assert "not financial advice" in rec_set.disclaimer.lower()
    assert "licensed advisor" in rec_set.disclaimer.lower()


# Metadata Tests (AC7)


def test_recommendation_set_includes_metadata(assembler, sample_user_data):
    """Test recommendation set includes comprehensive metadata (PRD AC7)."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="subscription_heavy",
        signals=["subscription_count"],
        user_data=sample_user_data,
        time_window="30d",
    )

    assert rec_set.metadata is not None
    assert isinstance(rec_set.metadata, dict)

    # Check required metadata fields
    assert "total_recommendations" in rec_set.metadata
    assert "education_count" in rec_set.metadata
    assert "partner_offer_count" in rec_set.metadata
    assert "generation_time_ms" in rec_set.metadata
    assert "time_window" in rec_set.metadata
    assert "signals_detected" in rec_set.metadata

    # Validate metadata values
    assert rec_set.metadata["total_recommendations"] == len(rec_set.recommendations)
    assert rec_set.metadata["generation_time_ms"] > 0
    assert rec_set.metadata["time_window"] == "30d"


def test_metadata_includes_audit_trail(assembler, sample_user_data):
    """Test metadata includes matching audit trail."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="cash_flow_optimizer",
        signals=["credit_utilization", "irregular_income"],
        user_data=sample_user_data,
        time_window="30d",
    )

    assert "matching_audit_trail" in rec_set.metadata
    audit_trail = rec_set.metadata["matching_audit_trail"]

    assert "persona_id" in audit_trail
    assert "signals" in audit_trail
    assert audit_trail["persona_id"] == "cash_flow_optimizer"


# Performance Tests (AC8)


def test_assembly_completes_under_5_seconds(assembler, sample_user_data):
    """Test recommendation assembly completes in <5 seconds (PRD AC8)."""
    start_time = time.time()

    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    elapsed_time = time.time() - start_time

    assert elapsed_time < 5.0, f"Assembly took {elapsed_time:.2f}s (exceeds 5s limit)"
    assert rec_set.metadata["generation_time_ms"] < 5000


def test_assembly_performance_is_consistent(assembler, sample_user_data):
    """Test assembly performance is consistent across multiple runs."""
    times = []

    for _ in range(3):
        start_time = time.time()

        assembler.assemble_recommendations(
            user_id="user_123",
            persona_id="low_savings",
            signals=["savings_balance"],
            user_data=sample_user_data,
            time_window="30d",
        )

        elapsed_time = time.time() - start_time
        times.append(elapsed_time)

    # All runs should be fast
    assert all(t < 5.0 for t in times), "All runs should complete in <5 seconds"

    # Performance should be relatively consistent (within 2x of fastest)
    min_time = min(times)
    max_time = max(times)
    assert max_time < min_time * 3, "Performance should be consistent"


# Serialization Tests


def test_assembled_recommendation_set_to_dict(assembler, sample_user_data):
    """Test recommendation set can be serialized to dict."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="young_professional",
        signals=[],
        user_data=sample_user_data,
        time_window="30d",
    )

    rec_dict = rec_set.to_dict()

    assert isinstance(rec_dict, dict)
    assert rec_dict["user_id"] == "user_123"
    assert rec_dict["persona_id"] == "young_professional"
    assert rec_dict["time_window"] == "30d"
    assert "recommendations" in rec_dict
    assert "disclaimer" in rec_dict
    assert "metadata" in rec_dict
    assert "generated_at" in rec_dict

    # Check recommendations are serialized
    assert isinstance(rec_dict["recommendations"], list)
    if rec_dict["recommendations"]:
        rec_item = rec_dict["recommendations"][0]
        assert "item_type" in rec_item
        assert "item_id" in rec_item
        assert "content" in rec_item
        assert "rationale" in rec_item


def test_assembled_recommendation_item_to_dict(assembler, sample_user_data):
    """Test assembled item can be serialized to dict."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    item = rec_set.recommendations[0]
    item_dict = item.to_dict()

    assert isinstance(item_dict, dict)
    assert "item_type" in item_dict
    assert "item_id" in item_dict
    assert "content" in item_dict
    assert "rationale" in item_dict
    assert "persona_match_reason" in item_dict
    assert "signal_citations" in item_dict


# Edge Cases


def test_assembler_handles_no_signals(assembler, sample_user_data):
    """Test assembler handles case with no signals."""
    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="young_professional",
        signals=[],  # No signals
        user_data=sample_user_data,
        time_window="30d",
    )

    # Should still generate recommendations based on persona
    assert len(rec_set.recommendations) > 0
    assert rec_set.metadata["signals_detected"] == []


def test_assembler_handles_minimal_user_data(assembler):
    """Test assembler handles minimal user data."""
    minimal_data = {
        "annual_income": 50000,
        "credit_score": 700,
        "existing_accounts": [],
        "credit_utilization": 0,
        "age": 25,
        "is_employed": True,
    }

    rec_set = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="young_professional",
        signals=[],
        user_data=minimal_data,
        time_window="30d",
    )

    # Should still work with minimal data
    assert len(rec_set.recommendations) > 0


def test_assembler_with_excluded_content_ids(assembler, sample_user_data):
    """Test assembler respects excluded content IDs."""
    # First assembly
    rec_set_1 = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=sample_user_data,
        time_window="30d",
    )

    # Extract IDs
    excluded_content_ids = {
        r.item_id for r in rec_set_1.recommendations if r.item_type == "education"
    }

    # Second assembly with exclusions
    rec_set_2 = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="low_savings",
        signals=["savings_balance"],
        user_data=sample_user_data,
        time_window="30d",
        excluded_content_ids=excluded_content_ids,
    )

    # Check no excluded IDs appear
    rec_2_content_ids = {
        r.item_id for r in rec_set_2.recommendations if r.item_type == "education"
    }

    assert len(excluded_content_ids & rec_2_content_ids) == 0, "Should not include excluded content"


def test_assembler_with_excluded_offer_ids(assembler, sample_user_data):
    """Test assembler respects excluded offer IDs."""
    # First assembly
    rec_set_1 = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    # Extract offer IDs
    excluded_offer_ids = {
        r.item_id for r in rec_set_1.recommendations if r.item_type == "partner_offer"
    }

    # Second assembly with exclusions
    rec_set_2 = assembler.assemble_recommendations(
        user_id="user_123",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
        excluded_offer_ids=excluded_offer_ids,
    )

    # Check no excluded IDs appear
    rec_2_offer_ids = {
        r.item_id for r in rec_set_2.recommendations if r.item_type == "partner_offer"
    }

    overlap = excluded_offer_ids & rec_2_offer_ids
    assert len(overlap) == 0, f"Should not include excluded offers, but found: {overlap}"


# Integration Tests


def test_end_to_end_recommendation_assembly(assembler, sample_user_data):
    """Test complete end-to-end recommendation assembly."""
    # Assemble recommendations
    rec_set = assembler.assemble_recommendations(
        user_id="test_user_001",
        persona_id="high_utilization",
        signals=["credit_utilization"],
        user_data=sample_user_data,
        time_window="30d",
    )

    # Verify complete structure
    assert rec_set.user_id == "test_user_001"
    assert rec_set.persona_id == "high_utilization"
    assert rec_set.time_window == "30d"
    assert len(rec_set.recommendations) >= 4  # At least 3 education + 1 offer
    assert rec_set.disclaimer == MANDATORY_DISCLAIMER
    assert rec_set.generated_at is not None
    assert isinstance(rec_set.generated_at, datetime)

    # Verify all recommendations have complete data
    for rec in rec_set.recommendations:
        assert rec.item_id is not None
        assert rec.item_type in ["education", "partner_offer"]
        assert len(rec.rationale) > 0
        assert len(rec.persona_match_reason) > 0
        assert isinstance(rec.content, dict)

    # Verify serialization works
    rec_dict = rec_set.to_dict()
    assert isinstance(rec_dict, dict)
    assert "recommendations" in rec_dict
    assert len(rec_dict["recommendations"]) == len(rec_set.recommendations)
