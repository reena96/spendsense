"""
Tests for eligibility filtering system (Epic 5 - Story 5.2).

Comprehensive test suite covering all acceptance criteria.
"""

import pytest
from spendsense.guardrails.eligibility import (
    EligibilityChecker,
    EligibilityResult,
    HARMFUL_PRODUCT_CATEGORIES
)


@pytest.fixture
def eligibility_checker():
    """Create EligibilityChecker instance."""
    return EligibilityChecker()


@pytest.fixture
def base_user_data():
    """Base user data for testing."""
    return {
        "user_id": "test_user_123",
        "annual_income": 60000,
        "credit_score": 720,
        "credit_utilization": 0.3,
        "existing_accounts": []
    }


@pytest.fixture
def base_offer():
    """Base offer for testing."""
    return {
        "offer_id": "test_offer_001",
        "product_id": "savings_account_premium",
        "product_type": "savings_account",
        "category": "banking",
        "minimum_income": 0,
        "minimum_credit_score": 0,
        "apr": 0
    }


# ===== AC1: Income requirement checking =====

def test_income_requirement_met(eligibility_checker, base_user_data, base_offer):
    """Test eligibility passes when income meets minimum (AC1)."""
    base_offer["minimum_income"] = 50000
    base_user_data["annual_income"] = 60000

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is True
    assert result.checks_performed["income"] is True
    assert "Income requirement met" in result.reasons


def test_income_requirement_not_met(eligibility_checker, base_user_data, base_offer):
    """Test eligibility fails when income below minimum (AC1)."""
    base_offer["minimum_income"] = 75000
    base_user_data["annual_income"] = 60000

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["income"] is False
    assert any("Income" in r and "below minimum" in r for r in result.reasons)


def test_no_income_requirement(eligibility_checker, base_user_data, base_offer):
    """Test eligibility passes when no income requirement (AC1)."""
    base_offer["minimum_income"] = 0

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.checks_performed["income"] is True


# ===== AC2: Credit requirement checking =====

def test_credit_requirement_met(eligibility_checker, base_user_data, base_offer):
    """Test eligibility passes when credit score meets minimum (AC2)."""
    base_offer["minimum_credit_score"] = 700
    base_user_data["credit_score"] = 720

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is True
    assert result.checks_performed["credit"] is True


def test_credit_requirement_not_met(eligibility_checker, base_user_data, base_offer):
    """Test eligibility fails when credit score below minimum (AC2)."""
    base_offer["minimum_credit_score"] = 750
    base_user_data["credit_score"] = 680

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["credit"] is False
    assert any("Credit score" in r and "below minimum" in r for r in result.reasons)


def test_credit_utilization_as_proxy(eligibility_checker, base_user_data, base_offer):
    """Test high credit utilization used as credit proxy when no score (AC2)."""
    base_offer["minimum_credit_score"] = 700
    base_user_data["credit_score"] = 0
    base_user_data["credit_utilization"] = 0.8  # 80% utilization

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["credit"] is False
    assert any("High credit utilization" in r for r in result.reasons)


def test_low_credit_utilization_acceptable(eligibility_checker, base_user_data, base_offer):
    """Test low credit utilization acceptable when no score (AC2)."""
    base_offer["minimum_credit_score"] = 700
    base_user_data["credit_score"] = 0
    base_user_data["credit_utilization"] = 0.2  # 20% utilization

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.checks_performed["credit"] is True


# ===== AC3: Duplicate account prevention =====

def test_duplicate_product_id_blocked(eligibility_checker, base_user_data, base_offer):
    """Test duplicate offer by product_id is blocked (AC3)."""
    base_offer["product_id"] = "premium_checking"
    base_user_data["existing_accounts"] = [
        {"product_id": "premium_checking", "product_type": "checking"}
    ]

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["duplicate"] is False
    assert any("already has" in r for r in result.reasons)


def test_duplicate_product_type_blocked(eligibility_checker, base_user_data, base_offer):
    """Test duplicate offer by product_type is blocked (AC3)."""
    base_offer["product_type"] = "savings_account"
    base_user_data["existing_accounts"] = [
        {"product_id": "basic_savings", "product_type": "savings_account"}
    ]

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["duplicate"] is False


def test_no_duplicate_accounts(eligibility_checker, base_user_data, base_offer):
    """Test no duplicates allows eligibility (AC3)."""
    base_offer["product_type"] = "credit_card"
    base_user_data["existing_accounts"] = [
        {"product_id": "basic_savings", "product_type": "savings_account"}
    ]

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.checks_performed["duplicate"] is True


# ===== AC4: Harmful product blocking =====

def test_harmful_product_category_blocked(eligibility_checker, base_user_data, base_offer):
    """Test harmful product category is blocked (AC4, AC10)."""
    base_offer["category"] = "payday_loan"

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["harmful"] is False
    assert any("Harmful product" in r for r in result.reasons)


def test_predatory_apr_blocked(eligibility_checker, base_user_data, base_offer):
    """Test predatory high APR is blocked (AC4, AC10)."""
    base_offer["apr"] = 45  # 45% APR is predatory

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert result.checks_performed["harmful"] is False
    assert any("Predatory APR" in r for r in result.reasons)


def test_all_harmful_categories_blocked(eligibility_checker, base_user_data, base_offer):
    """Test all harmful product categories are blocked (AC10)."""
    for harmful_category in HARMFUL_PRODUCT_CATEGORIES:
        base_offer["category"] = harmful_category

        result = eligibility_checker.check_eligibility(base_user_data, base_offer)

        assert result.eligible is False, f"Harmful category {harmful_category} should be blocked"
        assert result.checks_performed["harmful"] is False


# ===== AC5: Eligibility rules from catalog =====

def test_eligibility_rules_from_offer_metadata(eligibility_checker, base_user_data):
    """Test eligibility rules loaded from offer metadata (AC5)."""
    offer_with_rules = {
        "offer_id": "premium_card_001",
        "product_type": "credit_card",
        "category": "credit",
        "minimum_income": 75000,
        "minimum_credit_score": 720,
        "apr": 15.99
    }

    result = eligibility_checker.check_eligibility(base_user_data, offer_with_rules)

    # User doesn't meet income requirement
    assert result.eligible is False
    assert result.checks_performed["income"] is False


# ===== AC6: Failed checks logged =====

def test_failed_eligibility_logged_with_reason(eligibility_checker, base_user_data, base_offer):
    """Test failed eligibility checks include specific reasons (AC6)."""
    base_offer["minimum_income"] = 100000
    base_offer["minimum_credit_score"] = 800

    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert result.eligible is False
    assert len(result.reasons) >= 2  # At least income and credit failures
    assert any("Income" in r for r in result.reasons)
    assert any("Credit" in r for r in result.reasons)


# ===== AC8: Audit trail includes results =====

def test_audit_trail_structure(eligibility_checker, base_user_data, base_offer):
    """Test eligibility check includes comprehensive audit trail (AC8)."""
    result = eligibility_checker.check_eligibility(base_user_data, base_offer)

    assert "audit_trail" in result.__dict__
    audit = result.audit_trail

    assert audit["action"] == "eligibility_check"
    assert audit["offer_id"] == base_offer["offer_id"]
    assert audit["user_id"] == base_user_data["user_id"]
    assert "eligible" in audit
    assert "checks_performed" in audit
    assert "failure_reasons" in audit
    assert "timestamp" in audit


# ===== AC7 & AC9: Integration tests =====

def test_filter_eligible_offers(eligibility_checker, base_user_data):
    """Test filtering multiple offers for eligibility (AC7, AC9)."""
    offers = [
        {
            "offer_id": "good_offer_1",
            "product_type": "savings",
            "category": "banking",
            "minimum_income": 40000,
            "minimum_credit_score": 650
        },
        {
            "offer_id": "bad_income",
            "product_type": "premium_credit",
            "category": "credit",
            "minimum_income": 100000,  # Too high
            "minimum_credit_score": 700
        },
        {
            "offer_id": "harmful_payday",
            "product_type": "payday_loan",
            "category": "payday_loan",  # Harmful
            "minimum_income": 0
        },
        {
            "offer_id": "good_offer_2",
            "product_type": "checking",
            "category": "banking",
            "minimum_income": 30000,
            "minimum_credit_score": 600
        }
    ]

    eligible_offers, all_results = eligibility_checker.filter_eligible_offers(
        base_user_data,
        offers
    )

    # Should filter to 2 eligible offers
    assert len(eligible_offers) == 2
    assert len(all_results) == 4

    eligible_ids = [o["offer_id"] for o in eligible_offers]
    assert "good_offer_1" in eligible_ids
    assert "good_offer_2" in eligible_ids
    assert "bad_income" not in eligible_ids
    assert "harmful_payday" not in eligible_ids


def test_all_checks_pass_scenario(eligibility_checker):
    """Test scenario where all eligibility checks pass (AC9)."""
    user_data = {
        "user_id": "qualified_user",
        "annual_income": 80000,
        "credit_score": 750,
        "credit_utilization": 0.2,
        "existing_accounts": []
    }

    offer = {
        "offer_id": "premium_offer",
        "product_type": "investment_account",
        "category": "investment",
        "minimum_income": 75000,
        "minimum_credit_score": 700,
        "apr": 0
    }

    result = eligibility_checker.check_eligibility(user_data, offer)

    assert result.eligible is True
    assert all(result.checks_performed.values())
    assert "All eligibility checks passed" in result.reasons


def test_multiple_failures_scenario(eligibility_checker):
    """Test scenario with multiple eligibility failures (AC9)."""
    user_data = {
        "user_id": "unqualified_user",
        "annual_income": 30000,
        "credit_score": 580,
        "credit_utilization": 0.7,
        "existing_accounts": [
            {"product_id": "basic_checking", "product_type": "checking"}
        ]
    }

    offer = {
        "offer_id": "premium_checking",
        "product_type": "checking",  # Duplicate
        "category": "banking",
        "minimum_income": 50000,  # Too low income
        "minimum_credit_score": 680,  # Too low credit
        "apr": 0
    }

    result = eligibility_checker.check_eligibility(user_data, offer)

    assert result.eligible is False
    assert not result.checks_performed["income"]
    assert not result.checks_performed["credit"]
    assert not result.checks_performed["duplicate"]
    assert len(result.reasons) >= 3
