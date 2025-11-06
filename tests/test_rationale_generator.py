"""
Tests for rationale generation engine.

Tests the generation of transparent, personalized rationales
for educational content and partner offers.
"""

from datetime import datetime

import pytest

from spendsense.recommendations.rationale_generator import (
    RationaleGenerator,
    GeneratedRationale,
)
from spendsense.recommendations.models import (
    Recommendation,
    RecommendationCategory,
    RecommendationType,
    DifficultyLevel,
    TimeCommitment,
    EstimatedImpact,
    PartnerOffer,
    PartnerOfferType,
    EligibilityCriteria,
)


@pytest.fixture
def generator():
    """Create rationale generator for testing."""
    return RationaleGenerator()


# Template System Tests (AC1)


def test_rationale_generator_initialization(generator):
    """Test rationale generator can be initialized (PRD AC1)."""
    assert generator is not None
    assert isinstance(generator, RationaleGenerator)


# Education Content Tests (AC2, AC4)


def test_generate_rationale_for_recommendation(generator):
    """Test generating rationale for educational content (PRD AC2, AC4)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description for credit utilization article.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You're currently at {credit_max_utilization_pct}% credit utilization on your {account_name}.",
    )

    user_data = {
        "credit_max_utilization_pct": 68,
        "account_name": "Visa ****4523",
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert isinstance(rationale, GeneratedRationale)
    assert rationale.recommendation_id == "test_rec"
    assert rationale.recommendation_type == "education"
    assert "68%" in rationale.rationale_text
    assert "Visa ****4523" in rationale.rationale_text


def test_placeholder_replacement(generator):
    """Test placeholder replacement with actual values (PRD AC4)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.TEMPLATE,
        title="Test Article Title",
        description="Test description for debt payoff template.",
        personas=["high_utilization"],
        category=RecommendationCategory.ACTION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You have {credit_total_balance} in debt across {account_count} accounts.",
    )

    user_data = {
        "credit_total_balance": 12500,
        "account_count": 3,
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert "$12,500" in rationale.rationale_text
    assert "3" in rationale.rationale_text
    assert len(rationale.placeholders_replaced) == 2


# Partner Offer Tests (AC3, AC4)


def test_generate_rationale_for_offer(generator):
    """Test generating rationale for partner offer (PRD AC3, AC4)."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Balance Transfer Card",
        description="Test description for a balance transfer credit card offer.",
        personas=["high_utilization"],
        priority=1,
        provider="Test Bank",
        rationale_template="Your {account_name} is at {utilization_pct}% utilization. Transferring ${balance} to this 0% APR card could save you ${interest_savings}/month.",
    )

    user_data = {
        "account_name": "Visa ****4523",
        "utilization_pct": 68,
        "balance": 3400,
        "interest_savings": 87,
    }

    rationale = generator.generate_for_offer(offer, user_data)

    assert isinstance(rationale, GeneratedRationale)
    assert rationale.recommendation_id == "test_offer"
    assert rationale.recommendation_type == "partner_offer"
    assert "Visa ****4523" in rationale.rationale_text
    assert "68%" in rationale.rationale_text
    assert "$3,400" in rationale.rationale_text
    assert "$87" in rationale.rationale_text


# Data Citation Tests (AC5)


def test_cites_account_numbers_masked(generator):
    """Test rationales cite masked account numbers (PRD AC5)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description with account numbers.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="Your {account_name} account needs attention.",
    )

    user_data = {"account_name": "Chase ****1234"}

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert "****1234" in rationale.rationale_text
    # Should NOT contain full account number
    assert "Chase ****1234" in rationale.rationale_text


def test_cites_dollar_amounts(generator):
    """Test rationales cite specific dollar amounts (PRD AC5)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.CALCULATOR,
        title="Test Article Title",
        description="Test description with dollar amounts.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You have {balance} in debt. Your {limit} credit limit is being maxed out.",
    )

    user_data = {
        "balance": 3400,
        "limit": 5000,
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    # Should format as currency
    assert "$3,400" in rationale.rationale_text
    assert "$5,000" in rationale.rationale_text
    # Check citations extracted
    assert any("$3,400" in c for c in rationale.data_citations)
    assert any("$5,000" in c for c in rationale.data_citations)


def test_cites_percentages(generator):
    """Test rationales cite specific percentages (PRD AC5)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description with percentages.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="At {utilization_pct}% utilization, you're above the recommended 30%.",
    )

    user_data = {"utilization_pct": 68}

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert "68%" in rationale.rationale_text
    # Check citations extracted
    assert any("68%" in c for c in rationale.data_citations)


def test_cites_dates(generator):
    """Test rationales can cite dates (PRD AC5)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description with dates.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="Your account has been open since {account_open_date}.",
    )

    user_data = {"account_open_date": datetime(2020, 3, 15)}

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert "Mar 15, 2020" in rationale.rationale_text


# Formatting Tests (AC5)


def test_formats_currency_with_commas(generator):
    """Test currency values formatted with commas (PRD AC5)."""
    template = "You owe {balance} on your card."
    rationale, placeholders = generator._replace_placeholders(
        template, {"balance": 15000}
    )

    assert "$15,000" in rationale


def test_formats_large_numbers_with_commas(generator):
    """Test large numbers formatted with commas (PRD AC5)."""
    template = "Your income is {annual_income}."
    rationale, placeholders = generator._replace_placeholders(
        template, {"annual_income": 85000}
    )

    assert "$85,000" in rationale


def test_formats_percentages_correctly(generator):
    """Test percentages formatted with % symbol (PRD AC5)."""
    template = "Your utilization is {utilization_pct}."
    rationale, placeholders = generator._replace_placeholders(
        template, {"utilization_pct": 72.5}
    )

    assert "72.5%" in rationale


def test_formats_decimal_months(generator):
    """Test months formatted correctly (PRD AC5)."""
    template = "You have {emergency_fund_months} months saved."
    rationale, placeholders = generator._replace_placeholders(
        template, {"emergency_fund_months": 2.5}
    )

    assert "2.5" in rationale


# Plain Language Tests (AC6)


def test_uses_plain_language(generator):
    """Test generated rationales use plain language (PRD AC6)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description using plain language.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You're at {utilization_pct}% credit use. Bringing this below 30% could help your credit score.",
    )

    user_data = {"utilization_pct": 68}

    rationale = generator.generate_for_recommendation(rec, user_data)

    # Should use simple words
    assert "use" in rationale.rationale_text or "utilization" in rationale.rationale_text
    # Should be readable
    readability = generator.validate_readability(rationale.rationale_text)
    assert readability["is_readable"] is True


def test_readability_validation(generator):
    """Test readability validation function (PRD AC6)."""
    # Simple, readable text
    simple_text = "You have $1,000 in savings. This is good. Keep it up."
    readability = generator.validate_readability(simple_text)

    assert readability["is_readable"] is True
    assert readability["avg_sentence_length"] < 20
    assert readability["avg_word_length"] < 6


def test_readability_fails_for_complex_text(generator):
    """Test readability validation catches complex text (PRD AC6)."""
    # Complex, unreadable text
    complex_text = (
        "The utilization of your revolving credit facilities demonstrates "
        "suboptimal financial management necessitating immediate remediation "
        "through comprehensive debt consolidation strategies."
    )
    readability = generator.validate_readability(complex_text)

    assert readability["is_readable"] is False
    assert readability["complexity_ratio"] > 0.1


# Example Format Tests (AC7)


def test_example_format_credit_utilization(generator):
    """Test example format from PRD (PRD AC7)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description for credit utilization example.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template=(
            "We noticed your {account_name} is at {utilization_pct}% utilization "
            "(${balance} of ${limit} limit). Bringing this below 30% could improve "
            "your credit score and reduce interest charges of ${monthly_interest}/month."
        ),
    )

    user_data = {
        "account_name": "Visa ****4523",
        "utilization_pct": 68,
        "balance": 3400,
        "limit": 5000,
        "monthly_interest": 87,
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    # Verify format matches PRD example
    assert "Visa ****4523" in rationale.rationale_text
    assert "68%" in rationale.rationale_text
    assert "$3,400" in rationale.rationale_text
    assert "$5,000" in rationale.rationale_text
    assert "$87" in rationale.rationale_text


# Because Statement Tests (AC8)


def test_includes_because_statement(generator):
    """Test all rationales include 'because' statement (PRD AC8)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description with because statement.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="We recommend this because your {account_name} is at {utilization_pct}%.",
    )

    user_data = {
        "account_name": "Visa ****4523",
        "utilization_pct": 68,
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    # Should include "because" with data citation
    assert "because" in rationale.rationale_text.lower()
    assert "68%" in rationale.rationale_text


def test_default_template_includes_because(generator):
    """Test default templates include 'because' (PRD AC8)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description for default template.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        # No personalization_template - use default
    )

    user_data = {}

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert "because" in rationale.rationale_text.lower()


# Audit Trail Tests (AC9)


def test_rationale_includes_timestamp(generator):
    """Test generated rationale includes timestamp (PRD AC9)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description with timestamp.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="Test template",
    )

    rationale = generator.generate_for_recommendation(rec, {})

    assert isinstance(rationale.timestamp, datetime)


def test_rationale_tracks_placeholders_replaced(generator):
    """Test rationale tracks what placeholders were replaced (PRD AC9)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description tracking placeholders.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You have {balance} in debt at {rate}% APR.",
    )

    user_data = {
        "balance": 5000,
        "rate": 18.99,
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert "balance" in rationale.placeholders_replaced
    assert "rate" in rationale.placeholders_replaced
    assert "$5,000" in rationale.placeholders_replaced["balance"]
    assert "18.99%" in rationale.placeholders_replaced["rate"]


def test_rationale_includes_data_citations(generator):
    """Test rationale includes list of data citations (PRD AC9)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description with data citations.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="Your {account_name} has ${balance} at {rate}%.",
    )

    user_data = {
        "account_name": "Visa ****4523",
        "balance": 3400,
        "rate": 18.99,
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    assert len(rationale.data_citations) > 0
    # Should include account, amount, and percentage
    citation_text = " ".join(rationale.data_citations)
    assert "4523" in citation_text or "$3,400" in citation_text or "18.99%" in citation_text


# Missing Placeholder Tests (AC10)


def test_handles_missing_placeholders_gracefully(generator):
    """Test graceful handling of missing placeholders (PRD AC10)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description handling missing placeholders.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You have {balance} in debt and {missing_value} in savings.",
    )

    user_data = {
        "balance": 5000,
        # missing_value not provided
    }

    rationale = generator.generate_for_recommendation(rec, user_data)

    # Should still generate rationale
    assert "$5,000" in rationale.rationale_text
    # Missing placeholder tracked
    assert "missing_value" in rationale.placeholders_replaced


def test_logs_missing_placeholders(generator, caplog):
    """Test missing placeholders are logged (PRD AC9)."""
    rec = Recommendation(
        id="test_rec",
        type=RecommendationType.ARTICLE,
        title="Test Article Title",
        description="Test description logging missing placeholders.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template="You have {missing_field} in debt.",
    )

    user_data = {}

    with caplog.at_level("WARNING"):
        rationale = generator.generate_for_recommendation(rec, user_data)

    # Should log warning about missing placeholder
    assert "missing_field" in caplog.text


# Integration Tests


def test_complete_rationale_generation_workflow(generator):
    """Test complete rationale generation workflow."""
    # Educational content
    rec = Recommendation(
        id="understand_utilization",
        type=RecommendationType.ARTICLE,
        title="Understanding Credit Utilization",
        description="Learn how credit utilization affects your credit score.",
        personas=["high_utilization"],
        category=RecommendationCategory.EDUCATION,
        priority=1,
        difficulty=DifficultyLevel.BEGINNER,
        time_commitment=TimeCommitment.ONE_TIME,
        estimated_impact=EstimatedImpact.HIGH,
        personalization_template=(
            "Your {account_name} is at {utilization_pct}% utilization "
            "(${balance} of ${limit}). Keeping utilization below 30% helps "
            "your credit score because it shows lenders you manage credit responsibly."
        ),
    )

    # Partner offer
    offer = PartnerOffer(
        id="balance_transfer_card",
        type=PartnerOfferType.CREDIT_CARD,
        title="0% Balance Transfer Card",
        description="Transfer balances at 0% APR for 18 months.",
        personas=["high_utilization"],
        priority=1,
        provider="Test Bank",
        rationale_template=(
            "Transferring your ${balance} from {account_name} to this card "
            "could save you ${interest_savings}/month in interest charges "
            "because you'll pay 0% APR instead of {current_rate}%."
        ),
    )

    user_data = {
        "account_name": "Chase ****8765",
        "utilization_pct": 72,
        "balance": 4500,
        "limit": 6250,
        "interest_savings": 92,
        "current_rate": 19.99,
    }

    # Generate both rationales
    rec_rationale = generator.generate_for_recommendation(rec, user_data)
    offer_rationale = generator.generate_for_offer(offer, user_data)

    # Verify education rationale
    assert "Chase ****8765" in rec_rationale.rationale_text
    assert "72%" in rec_rationale.rationale_text
    assert "$4,500" in rec_rationale.rationale_text
    assert "$6,250" in rec_rationale.rationale_text
    assert "because" in rec_rationale.rationale_text

    # Verify offer rationale
    assert "$4,500" in offer_rationale.rationale_text
    assert "$92" in offer_rationale.rationale_text
    assert "19.99%" in offer_rationale.rationale_text
    assert "because" in offer_rationale.rationale_text

    # Verify audit trails
    assert len(rec_rationale.data_citations) > 0
    assert len(offer_rationale.data_citations) > 0
