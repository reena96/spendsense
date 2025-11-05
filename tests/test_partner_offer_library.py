"""
Tests for partner offer library functionality.

Tests loading, validation, and querying of partner offers
from YAML configuration file.
"""

import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from spendsense.recommendations.models import (
    PartnerOffer,
    PartnerOfferType,
    EligibilityCriteria,
)
from spendsense.recommendations.partner_offer_library import (
    PartnerOfferLibrary,
    get_partner_offer_library,
)


# Model Validation Tests


def test_valid_partner_offer_model():
    """Test creating valid PartnerOffer model."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="A test credit card offer with competitive rates and rewards program.",
        personas=["high_utilization", "young_professional"],
        eligibility=EligibilityCriteria(
            min_income=30000,
            min_credit_score=670,
            excluded_accounts=["chase_credit_cards"],
        ),
        priority=1,
        provider="Test Bank",
        key_benefits=["0% intro APR", "No annual fee"],
    )

    assert offer.id == "test_offer"
    assert offer.type == PartnerOfferType.CREDIT_CARD
    assert len(offer.personas) == 2
    assert offer.eligibility.min_income == 30000
    assert offer.eligibility.min_credit_score == 670


def test_partner_offer_missing_required_field():
    """Test PartnerOffer validation fails when required field missing."""
    with pytest.raises(ValidationError) as exc_info:
        PartnerOffer(
            id="test_offer",
            type=PartnerOfferType.SAVINGS_ACCOUNT,
            # Missing title
            description="Test description that is long enough to pass validation.",
            personas=["low_savings"],
            priority=1,
            provider="Test Bank",
        )

    assert "title" in str(exc_info.value)


def test_partner_offer_invalid_enum_value():
    """Test PartnerOffer validation fails with invalid enum value."""
    with pytest.raises(ValidationError):
        PartnerOffer(
            id="test_offer",
            type="invalid_type",  # Should be PartnerOfferType enum
            title="Test Offer",
            description="Test description that is long enough to pass validation.",
            personas=["low_savings"],
            priority=1,
            provider="Test Bank",
        )


def test_partner_offer_priority_validation():
    """Test PartnerOffer priority validation (1-10)."""
    # Valid priority
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.APP,
        title="Test App",
        description="Test description that is long enough to pass validation.",
        personas=["subscription_heavy"],
        priority=5,
        provider="Test Company",
    )
    assert offer.priority == 5

    # Invalid priority (too low)
    with pytest.raises(ValidationError):
        PartnerOffer(
            id="test_offer",
            type=PartnerOfferType.APP,
            title="Test App",
            description="Test description that is long enough to pass validation.",
            personas=["subscription_heavy"],
            priority=0,
            provider="Test Company",
        )

    # Invalid priority (too high)
    with pytest.raises(ValidationError):
        PartnerOffer(
            id="test_offer",
            type=PartnerOfferType.APP,
            title="Test App",
            description="Test description that is long enough to pass validation.",
            personas=["subscription_heavy"],
            priority=11,
            provider="Test Company",
        )


def test_partner_offer_id_format_validation():
    """Test PartnerOffer ID format validation (kebab-case)."""
    # Valid kebab-case IDs
    valid_ids = [
        "balance_transfer_chase",
        "high-yield-savings",
        "app_tracker_2024",
        "test123",
    ]

    for valid_id in valid_ids:
        offer = PartnerOffer(
            id=valid_id,
            type=PartnerOfferType.CREDIT_CARD,
            title="Test Offer",
            description="Test description that is long enough to pass validation.",
            personas=["high_utilization"],
            priority=1,
            provider="Test Bank",
        )
        assert offer.id == valid_id

    # Invalid IDs
    invalid_ids = [
        "CamelCase",
        "Has Spaces",
        "has.dots",
        "-starts-with-hyphen",
        "ends-with-hyphen-",
        "",
    ]

    for invalid_id in invalid_ids:
        with pytest.raises(ValidationError):
            PartnerOffer(
                id=invalid_id,
                type=PartnerOfferType.CREDIT_CARD,
                title="Test Offer",
                description="Test description that is long enough to pass validation.",
                personas=["high_utilization"],
                priority=1,
                provider="Test Bank",
            )


def test_eligibility_criteria_validation():
    """Test EligibilityCriteria validation."""
    # Valid criteria with all fields
    criteria = EligibilityCriteria(
        min_income=25000,
        min_credit_score=650,
        excluded_accounts=["chase_cards", "amex_cards"],
        max_credit_utilization=80,
        min_age=21,
        employment_required=True,
    )

    assert criteria.min_income == 25000
    assert criteria.min_credit_score == 650
    assert len(criteria.excluded_accounts) == 2

    # Valid criteria with optional fields as None
    criteria_minimal = EligibilityCriteria()
    assert criteria_minimal.min_income is None
    assert criteria_minimal.min_credit_score is None
    assert criteria_minimal.excluded_accounts == []

    # Invalid credit score (out of range)
    with pytest.raises(ValidationError):
        EligibilityCriteria(min_credit_score=900)

    # Invalid utilization (negative)
    with pytest.raises(ValidationError):
        EligibilityCriteria(max_credit_utilization=-10)


def test_partner_offer_to_dict():
    """Test PartnerOffer to_dict serialization."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["high_utilization"],
        eligibility=EligibilityCriteria(
            min_income=30000,
            min_credit_score=670,
        ),
        priority=1,
        provider="Test Bank",
        key_benefits=["Benefit 1", "Benefit 2"],
    )

    offer_dict = offer.to_dict()

    assert offer_dict["id"] == "test_offer"
    assert offer_dict["type"] == "credit_card"
    assert offer_dict["title"] == "Test Credit Card"
    assert offer_dict["personas"] == ["high_utilization"]
    assert offer_dict["eligibility"]["min_income"] == 30000
    assert offer_dict["eligibility"]["min_credit_score"] == 670
    assert offer_dict["key_benefits"] == ["Benefit 1", "Benefit 2"]


# Library Loading Tests


def test_load_valid_yaml_file():
    """Test loading valid partner offers YAML file."""
    # Use the actual partner_offers.yaml file
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"

    library = PartnerOfferLibrary(str(config_path))

    # Verify offers were loaded
    assert len(library._offer_index) >= 10  # PRD AC6: at least 10 offers
    assert len(library.offers) >= 6  # All 6 personas should be covered

    # Verify all expected personas have offers
    expected_personas = {
        "high_utilization",
        "irregular_income",
        "low_savings",
        "subscription_heavy",
        "cash_flow_optimizer",
        "young_professional",
    }
    assert expected_personas.issubset(set(library.offers.keys()))


def test_load_missing_file():
    """Test error handling when YAML file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        PartnerOfferLibrary("/nonexistent/path/to/offers.yaml")


def test_load_invalid_yaml_syntax():
    """Test error handling for invalid YAML syntax."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("invalid: yaml: syntax: [unclosed")
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            PartnerOfferLibrary(temp_path)
        assert "Invalid YAML" in str(exc_info.value)
    finally:
        Path(temp_path).unlink()


def test_load_invalid_offer_structure():
    """Test error handling for invalid offer structure."""
    invalid_yaml = """
partner_offers:
  - id: test_offer
    type: credit_card
    # Missing required fields like title, description
    personas:
    - high_utilization
    priority: 1
    provider: Test Bank
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(invalid_yaml)
        temp_path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            PartnerOfferLibrary(temp_path)
        assert "Invalid partner offer" in str(exc_info.value)
    finally:
        Path(temp_path).unlink()


def test_load_all_personas_present():
    """Test that all 6 personas have partner offers (PRD AC5, AC6)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    expected_personas = [
        "high_utilization",
        "irregular_income",
        "low_savings",
        "subscription_heavy",
        "cash_flow_optimizer",
        "young_professional",
    ]

    for persona in expected_personas:
        offers = library.get_by_persona(persona)
        assert len(offers) > 0, f"No offers found for persona: {persona}"


# Library Query Tests


def test_get_offers_by_persona():
    """Test retrieving partner offers by persona."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # Test each persona
    for persona in ["high_utilization", "low_savings", "subscription_heavy"]:
        offers = library.get_by_persona(persona)
        assert isinstance(offers, list)
        assert len(offers) > 0

        # Verify all offers are for this persona
        for offer in offers:
            assert persona in offer.personas


def test_get_offers_sorted_by_priority():
    """Test that offers are sorted by priority (1=highest)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    offers = library.get_by_persona("high_utilization")
    assert len(offers) > 1

    # Verify ascending priority order (1, 2, 3...)
    for i in range(len(offers) - 1):
        assert offers[i].priority <= offers[i + 1].priority


def test_get_offer_by_id():
    """Test retrieving specific offer by ID."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # Test retrieving existing offer
    offer = library.get_by_id("ally_high_yield_savings")
    assert offer is not None
    assert offer.id == "ally_high_yield_savings"
    assert offer.type == PartnerOfferType.SAVINGS_ACCOUNT

    # Test non-existent offer
    offer = library.get_by_id("nonexistent_offer")
    assert offer is None


def test_get_unknown_persona():
    """Test behavior when querying unknown persona."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    offers = library.get_by_persona("nonexistent_persona")
    assert offers == []


def test_get_by_type():
    """Test retrieving offers by type (PRD AC2)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # Test credit cards
    credit_cards = library.get_by_type("credit_card")
    assert len(credit_cards) > 0
    for offer in credit_cards:
        assert offer.type == PartnerOfferType.CREDIT_CARD

    # Test savings accounts
    savings = library.get_by_type("savings_account")
    assert len(savings) > 0
    for offer in savings:
        assert offer.type == PartnerOfferType.SAVINGS_ACCOUNT

    # Test apps
    apps = library.get_by_type("app")
    assert len(apps) > 0
    for offer in apps:
        assert offer.type == PartnerOfferType.APP


def test_get_offer_count():
    """Test counting offers."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # Total count
    total = library.get_offer_count()
    assert total >= 10  # PRD AC6

    # Count for specific persona
    high_util_count = library.get_offer_count("high_utilization")
    assert high_util_count > 0

    # Count for non-existent persona
    unknown_count = library.get_offer_count("nonexistent")
    assert unknown_count == 0


def test_get_high_priority():
    """Test getting top priority offers."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # Get top 3 for high_utilization
    top_3 = library.get_high_priority("high_utilization", limit=3)
    assert len(top_3) <= 3
    assert all(offer.priority <= 3 for offer in top_3)

    # Verify sorted by priority
    for i in range(len(top_3) - 1):
        assert top_3[i].priority <= top_3[i + 1].priority


# Eligibility Checking Tests (PRD AC3)


def test_check_eligibility_all_criteria_met():
    """Test eligibility check when all criteria are met."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["high_utilization"],
        eligibility=EligibilityCriteria(
            min_income=30000,
            min_credit_score=670,
            excluded_accounts=["chase_credit_cards"],
            max_credit_utilization=80,
            min_age=21,
            employment_required=True,
        ),
        priority=1,
        provider="Test Bank",
    )

    user_data = {
        "annual_income": 50000,
        "credit_score": 700,
        "existing_accounts": ["bank_of_america_checking"],
        "credit_utilization": 60,
        "age": 30,
        "is_employed": True,
    }

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is True
    assert len(reasons) == 0


def test_check_eligibility_income_too_low():
    """Test eligibility check fails when income too low."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["high_utilization"],
        eligibility=EligibilityCriteria(min_income=50000),
        priority=1,
        provider="Test Bank",
    )

    user_data = {"annual_income": 30000}

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is False
    assert len(reasons) == 1
    assert "income" in reasons[0].lower()


def test_check_eligibility_credit_score_too_low():
    """Test eligibility check fails when credit score too low."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["high_utilization"],
        eligibility=EligibilityCriteria(min_credit_score=700),
        priority=1,
        provider="Test Bank",
    )

    user_data = {"credit_score": 650}

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is False
    assert "credit score" in reasons[0].lower()


def test_check_eligibility_excluded_accounts():
    """Test eligibility check fails when user has excluded account."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["high_utilization"],
        eligibility=EligibilityCriteria(
            excluded_accounts=["chase_credit_cards", "amex_cards"]
        ),
        priority=1,
        provider="Test Bank",
    )

    user_data = {"existing_accounts": ["chase_credit_cards", "boa_checking"]}

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is False
    assert "excluded" in reasons[0].lower()


def test_check_eligibility_utilization_too_high():
    """Test eligibility check fails when credit utilization too high."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["high_utilization"],
        eligibility=EligibilityCriteria(max_credit_utilization=50),
        priority=1,
        provider="Test Bank",
    )

    user_data = {"credit_utilization": 75}

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is False
    assert "utilization" in reasons[0].lower()


def test_check_eligibility_age_too_young():
    """Test eligibility check fails when user too young."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["young_professional"],
        eligibility=EligibilityCriteria(min_age=21),
        priority=1,
        provider="Test Bank",
    )

    user_data = {"age": 19}

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is False
    assert "age" in reasons[0].lower()


def test_check_eligibility_employment_required():
    """Test eligibility check fails when employment required but user unemployed."""
    offer = PartnerOffer(
        id="test_offer",
        type=PartnerOfferType.CREDIT_CARD,
        title="Test Credit Card",
        description="Test description that is long enough to pass validation.",
        personas=["young_professional"],
        eligibility=EligibilityCriteria(employment_required=True),
        priority=1,
        provider="Test Bank",
    )

    user_data = {"is_employed": False}

    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    is_eligible, reasons = library.check_eligibility(offer, user_data)
    assert is_eligible is False
    assert "employment" in reasons[0].lower()


def test_get_eligible_offers():
    """Test getting only eligible offers for a user."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # User with good qualifications
    user_data = {
        "annual_income": 60000,
        "credit_score": 720,
        "existing_accounts": [],
        "credit_utilization": 25,
        "age": 28,
        "is_employed": True,
    }

    eligible_offers = library.get_eligible_offers("high_utilization", user_data, limit=3)

    # Should get some eligible offers
    assert len(eligible_offers) > 0
    assert len(eligible_offers) <= 3

    # Verify all are actually eligible
    for offer in eligible_offers:
        is_eligible, _ = library.check_eligibility(offer, user_data)
        assert is_eligible is True


def test_get_eligible_offers_with_strict_criteria():
    """Test that ineligible offers are filtered out."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    # User with poor qualifications
    user_data = {
        "annual_income": 15000,
        "credit_score": 550,
        "existing_accounts": ["chase_credit_cards"],
        "credit_utilization": 95,
        "age": 19,
        "is_employed": False,
    }

    # Should get fewer or no offers for high_utilization (credit cards have requirements)
    eligible_offers = library.get_eligible_offers("high_utilization", user_data)

    # Verify none of the returned offers are ineligible
    for offer in eligible_offers:
        is_eligible, _ = library.check_eligibility(offer, user_data)
        assert is_eligible is True


def test_catalog_has_no_predatory_products():
    """Test that catalog excludes predatory products (PRD AC7)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"

    # Load and parse YAML directly to check for predatory terms
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)

    offers_text = str(data).lower()

    # Check for predatory product indicators
    predatory_terms = [
        "payday loan",
        "payday advance",
        "cash advance loan",
        "title loan",
        "car title loan",
        "pawn",
        "rent-to-own",
        "subprime",
    ]

    for term in predatory_terms:
        assert term not in offers_text, f"Found predatory term: {term}"


def test_offers_have_plain_language_descriptions():
    """Test that all offers have plain-language descriptions (PRD AC8)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    for offer in library._offer_index.values():
        # Description should be at least 20 characters (enforced by model)
        assert len(offer.description) >= 20

        # Should not have overly technical jargon
        description_lower = offer.description.lower()
        # Basic readability check - should have common words
        common_words = ["a", "the", "and", "or", "with", "for", "to"]
        assert any(word in description_lower for word in common_words)


def test_offers_catalog_schema_validated():
    """Test that catalog schema is validated (PRD AC9)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"

    # Should load without errors (validates schema via Pydantic)
    library = PartnerOfferLibrary(str(config_path))

    # Verify all offers have required fields
    for offer in library._offer_index.values():
        assert offer.id
        assert offer.type in PartnerOfferType
        assert offer.title
        assert offer.description
        assert len(offer.personas) > 0
        assert offer.priority >= 1
        assert offer.provider


def test_singleton_library_instance():
    """Test singleton pattern for library instance (PRD AC10)."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"

    # Get first instance
    library1 = get_partner_offer_library(str(config_path))

    # Get second instance
    library2 = get_partner_offer_library()

    # Should be same instance
    assert library1 is library2


def test_library_repr():
    """Test library string representation."""
    config_path = Path(__file__).parent.parent / "spendsense" / "config" / "partner_offers.yaml"
    library = PartnerOfferLibrary(str(config_path))

    repr_str = repr(library)
    assert "PartnerOfferLibrary" in repr_str
    assert "total" in repr_str
    assert "personas" in repr_str
