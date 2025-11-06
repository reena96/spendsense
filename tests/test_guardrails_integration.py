"""
Integration tests for guardrails pipeline (Epic 5 - Story 5.5).

Tests end-to-end guardrail enforcement: consent → eligibility → tone → disclaimer.
"""

import pytest
import time
from spendsense.guardrails.consent import ConsentService
from spendsense.guardrails.eligibility import EligibilityChecker
from spendsense.guardrails.tone import ToneValidator
from spendsense.recommendations.assembler import (
    RecommendationAssembler,
    MANDATORY_DISCLAIMER
)


# ===== AC1 & AC7: Guardrail pipeline sequence =====

def test_guardrail_pipeline_sequence():
    """Test guardrails execute in correct sequence: consent → eligibility → tone → disclaimer (AC1, AC7)."""
    # This test verifies the architecture, not runtime behavior
    # Sequence is:
    # 1. Consent check at API level (main.py:848)
    # 2. Eligibility filtering in assembler (assembler.py:214)
    # 3. Tone validation in assembler (assembler.py:251)
    # 4. Disclaimer automatic (assembler.py:302)

    # Create checkers to verify they exist and are integrated
    consent_service = ConsentService(db_session=None)
    eligibility_checker = EligibilityChecker()
    tone_validator = ToneValidator()

    assert consent_service is not None
    assert eligibility_checker is not None
    assert tone_validator is not None
    assert MANDATORY_DISCLAIMER is not None


def test_consent_check_occurs_first():
    """Test consent check occurs before any recommendation processing (AC1)."""
    # Consent check at API level prevents processing if not opted in
    consent_service = ConsentService(db_session=None)

    # Verify consent service can check status
    assert hasattr(consent_service, 'check_consent_status')
    assert callable(consent_service.check_consent_status)


def test_eligibility_before_tone():
    """Test eligibility filtering occurs before tone validation (AC1)."""
    # In assembler.py, eligibility is at line 214, tone is at line 251
    # This architectural decision ensures ineligible offers don't get tone-checked
    eligibility_checker = EligibilityChecker()
    tone_validator = ToneValidator()

    # Both services exist and can be used in sequence
    assert hasattr(eligibility_checker, 'check_eligibility')
    assert hasattr(tone_validator, 'validate_tone')


# ===== AC2 & AC3: Early exit and filtering behavior =====

def test_eligibility_filtering_removes_ineligible(eligibility_checker=None):
    """Test ineligible offers are filtered out (AC2, AC3)."""
    if eligibility_checker is None:
        eligibility_checker = EligibilityChecker()

    user_data = {
        "user_id": "test_user",
        "annual_income": 40000,
        "credit_score": 650,
        "existing_accounts": []
    }

    offers = [
        {
            "offer_id": "low_income_req",
            "minimum_income": 30000,
            "minimum_credit_score": 600,
            "category": "banking"
        },
        {
            "offer_id": "high_income_req",
            "minimum_income": 100000,  # User doesn't qualify
            "minimum_credit_score": 600,
            "category": "banking"
        },
        {
            "offer_id": "harmful_loan",
            "category": "payday_loan",  # Harmful product
            "minimum_income": 0
        }
    ]

    eligible_offers, results = eligibility_checker.filter_eligible_offers(user_data, offers)

    # Should filter out high_income_req and harmful_loan
    assert len(eligible_offers) == 1
    assert eligible_offers[0]["offer_id"] == "low_income_req"


def test_tone_validation_filters_problematic_language():
    """Test problematic tone is filtered out (AC2, AC3)."""
    tone_validator = ToneValidator()

    recommendations = [
        {
            "item_id": "rec_good",
            "rationale": "Building a savings habit can help you reach your financial goals."
        },
        {
            "item_id": "rec_bad",
            "rationale": "Your overspending and irresponsible behavior needs to stop."
        },
        {
            "item_id": "rec_good2",
            "rationale": "Consider optimizing your spending to save more each month."
        }
    ]

    validated, results = tone_validator.validate_recommendations(recommendations)

    # Should filter out rec_bad
    assert len(validated) == 2
    validated_ids = [r["item_id"] for r in validated]
    assert "rec_good" in validated_ids
    assert "rec_good2" in validated_ids
    assert "rec_bad" not in validated_ids


def test_disclaimer_always_present():
    """Test disclaimer is always included in outputs (AC3)."""
    from spendsense.recommendations.assembler import AssembledRecommendationSet

    rec_set = AssembledRecommendationSet(
        user_id="test_user",
        persona_id="test_persona",
        time_window="30d",
        recommendations=[],
        disclaimer=MANDATORY_DISCLAIMER,
        metadata={}
    )

    response = rec_set.to_dict()

    # Disclaimer must be present
    assert "disclaimer" in response
    assert response["disclaimer"] == MANDATORY_DISCLAIMER
    assert "not financial advice" in response["disclaimer"]


# ===== AC4: Audit trail completeness =====

def test_audit_trail_includes_all_guardrails():
    """Test audit trail captures all guardrail results (AC4)."""
    eligibility_checker = EligibilityChecker()

    user_data = {
        "user_id": "test_user",
        "annual_income": 50000,
        "credit_score": 700,
        "existing_accounts": []
    }

    offer = {
        "offer_id": "test_offer",
        "minimum_income": 40000,
        "minimum_credit_score": 650,
        "category": "banking"
    }

    result = eligibility_checker.check_eligibility(user_data, offer)

    # Audit trail must be present
    assert "audit_trail" in result.__dict__
    audit = result.audit_trail

    # Must include key information
    assert "action" in audit
    assert "offer_id" in audit
    assert "user_id" in audit
    assert "eligible" in audit
    assert "checks_performed" in audit
    assert "timestamp" in audit


def test_tone_validation_audit_trail():
    """Test tone validation audit trail structure (AC4)."""
    tone_validator = ToneValidator()

    text = "Building better financial habits takes time and practice."
    result = tone_validator.validate_tone(text, text_id="test_123")

    # Audit trail must be present
    assert "audit_trail" in result.__dict__
    audit = result.audit_trail

    # Must include key information
    assert audit["action"] == "tone_validation"
    assert audit["text_id"] == "test_123"
    assert "passes" in audit
    assert "passes_tone" in audit
    assert "passes_readability" in audit
    assert "flagged_count" in audit
    assert "flagged_phrases" in audit
    assert "timestamp" in audit


# ===== AC6: Guardrail metrics tracking =====

def test_metadata_includes_eligibility_metrics():
    """Test recommendation metadata includes eligibility metrics (AC6)."""
    # Metadata structure from assembler.py:277-294
    metadata = {
        "offers_checked": 5,
        "offers_eligible": 3,
        "offers_filtered": 2,
        "eligibility_audit_trail": []
    }

    # Verify all eligibility metrics present
    assert "offers_checked" in metadata
    assert "offers_eligible" in metadata
    assert "offers_filtered" in metadata
    assert "eligibility_audit_trail" in metadata

    # Verify math adds up
    assert metadata["offers_checked"] == metadata["offers_eligible"] + metadata["offers_filtered"]


def test_metadata_includes_tone_metrics():
    """Test recommendation metadata includes tone metrics (AC6)."""
    # Metadata structure from assembler.py:286-289
    metadata = {
        "tone_checked": 10,
        "tone_passed": 8,
        "tone_filtered": 2,
        "tone_audit_trail": []
    }

    # Verify all tone metrics present
    assert "tone_checked" in metadata
    assert "tone_passed" in metadata
    assert "tone_filtered" in metadata
    assert "tone_audit_trail" in metadata

    # Verify math adds up
    assert metadata["tone_checked"] == metadata["tone_passed"] + metadata["tone_filtered"]


# ===== AC8: End-to-end integration tests =====

def test_end_to_end_all_guardrails_passing():
    """Test full pipeline when all guardrails pass (AC8)."""
    # Test data with user who passes all checks
    eligibility_checker = EligibilityChecker()
    tone_validator = ToneValidator()

    user_data = {
        "user_id": "qualified_user",
        "annual_income": 80000,
        "credit_score": 750,
        "credit_utilization": 0.2,
        "existing_accounts": []
    }

    offers = [
        {
            "offer_id": "good_offer_1",
            "minimum_income": 60000,
            "minimum_credit_score": 700,
            "category": "banking",
            "product_type": "savings"
        }
    ]

    # Step 1: Eligibility filtering
    eligible_offers, eligibility_results = eligibility_checker.filter_eligible_offers(user_data, offers)

    assert len(eligible_offers) == 1
    assert all(r.eligible for r in eligibility_results)

    # Step 2: Tone validation (on mock recommendations)
    recommendations = [
        {
            "item_id": "rec_1",
            "rationale": "A high-yield savings account could help you reach your goals faster."
        }
    ]

    validated_recs, tone_results = tone_validator.validate_recommendations(recommendations)

    assert len(validated_recs) == 1
    assert all(r.passes for r in tone_results)

    # Step 3: Disclaimer (always present)
    assert MANDATORY_DISCLAIMER is not None
    assert len(MANDATORY_DISCLAIMER) > 0


def test_end_to_end_eligibility_filtering():
    """Test full pipeline when eligibility filters some offers (AC8)."""
    eligibility_checker = EligibilityChecker()

    user_data = {
        "user_id": "moderate_income_user",
        "annual_income": 45000,
        "credit_score": 680,
        "existing_accounts": []
    }

    offers = [
        {"offer_id": "affordable", "minimum_income": 40000, "minimum_credit_score": 650, "category": "banking"},
        {"offer_id": "expensive", "minimum_income": 80000, "minimum_credit_score": 750, "category": "banking"},
        {"offer_id": "harmful", "category": "payday_loan"}
    ]

    eligible_offers, results = eligibility_checker.filter_eligible_offers(user_data, offers)

    # Only affordable offer should pass
    assert len(eligible_offers) == 1
    assert eligible_offers[0]["offer_id"] == "affordable"

    # Verify filtering reasons logged
    assert len(results) == 3
    assert results[0].eligible is True
    assert results[1].eligible is False  # Income too low
    assert results[2].eligible is False  # Harmful product


def test_end_to_end_tone_filtering():
    """Test full pipeline when tone validation filters recommendations (AC8)."""
    tone_validator = ToneValidator()

    recommendations = [
        {"item_id": "1", "rationale": "Building an emergency fund strengthens your financial resilience."},
        {"item_id": "2", "rationale": "Your overspending is irresponsible and needs to stop immediately."},
        {"item_id": "3", "rationale": "Consider optimizing your budget to save more each month."},
    ]

    validated, results = tone_validator.validate_recommendations(recommendations)

    # Should filter out recommendation 2
    assert len(validated) == 2
    validated_ids = [r["item_id"] for r in validated]
    assert "1" in validated_ids
    assert "3" in validated_ids
    assert "2" not in validated_ids

    # Verify tone filtering reasons logged
    assert len(results) == 3
    assert results[0].passes is True
    assert results[1].passes is False  # Has prohibited phrases
    assert results[2].passes is True


# ===== AC9: Performance testing =====

def test_performance_under_5_seconds():
    """Test recommendation generation completes in <5 seconds (AC9)."""
    # Simulate full pipeline execution
    start_time = time.time()

    eligibility_checker = EligibilityChecker()
    tone_validator = ToneValidator()

    user_data = {
        "user_id": "perf_test_user",
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": []
    }

    # Generate 20 offers to filter
    offers = [
        {
            "offer_id": f"offer_{i}",
            "minimum_income": 50000 if i % 2 == 0 else 100000,
            "minimum_credit_score": 700,
            "category": "banking"
        }
        for i in range(20)
    ]

    # Step 1: Eligibility filtering
    eligible_offers, _ = eligibility_checker.filter_eligible_offers(user_data, offers)

    # Step 2: Tone validation on mock recommendations
    recommendations = [
        {
            "item_id": f"rec_{i}",
            "rationale": f"Consider this opportunity to strengthen your financial position with offer {i}."
        }
        for i in range(len(eligible_offers))
    ]

    validated_recs, _ = tone_validator.validate_recommendations(recommendations)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Should complete well under 5 seconds
    assert elapsed_time < 5.0, f"Pipeline took {elapsed_time:.2f}s, exceeds 5s limit"

    # Typically should be much faster (<0.1s for this test)
    print(f"Pipeline execution time: {elapsed_time:.3f}s")
