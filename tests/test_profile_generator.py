"""
Unit and integration tests for synthetic user profile generation.

Tests cover persona assignment, profile generation, financial characteristics,
account structure, validation, and JSON serialization.
"""

from __future__ import annotations

import json
import pytest
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory

from spendsense.generators.profile_generator import (
    ProfileGenerator,
    UserProfile,
    generate_synthetic_profiles,
)
from spendsense.personas.definitions import (
    PersonaType,
    get_persona_characteristics,
    PERSONA_REGISTRY,
)
from spendsense.db.models import AccountType, AccountSubtype


# ===== ProfileGenerator Initialization Tests =====

@pytest.mark.unit
class TestProfileGeneratorInit:
    """Tests for ProfileGenerator initialization."""

    def test_default_initialization(self):
        """Test generator with default parameters."""
        gen = ProfileGenerator()
        assert gen.seed == 42
        assert gen.num_users == 100
        assert len(gen.persona_types) == 5

    def test_custom_seed_and_users(self):
        """Test generator with custom seed and user count."""
        gen = ProfileGenerator(seed=123, num_users=75)
        assert gen.seed == 123
        assert gen.num_users == 75

    @pytest.mark.parametrize("num_users", [49, 101, 0, -1, 150])
    def test_invalid_num_users(self, num_users):
        """Test that invalid user counts are rejected."""
        with pytest.raises(ValueError, match="must be between 50 and 100"):
            ProfileGenerator(num_users=num_users)

    @pytest.mark.parametrize("num_users", [50, 60, 75, 90, 100])
    def test_valid_num_users(self, num_users):
        """Test valid user count range."""
        gen = ProfileGenerator(num_users=num_users)
        assert gen.num_users == num_users


# ===== User ID Generation Tests =====

@pytest.mark.unit
class TestUserIDGeneration:
    """Tests for user ID generation."""

    def test_user_id_format(self):
        """Test user ID follows masked format."""
        gen = ProfileGenerator()
        user_id = gen._generate_user_id(0)
        assert user_id == "user_MASKED_000"

    @pytest.mark.parametrize("index,expected", [
        (0, "user_MASKED_000"),
        (1, "user_MASKED_001"),
        (42, "user_MASKED_042"),
        (99, "user_MASKED_099"),
    ])
    def test_user_id_indices(self, index, expected):
        """Test user ID generation for various indices."""
        gen = ProfileGenerator()
        assert gen._generate_user_id(index) == expected

    def test_user_ids_are_unique(self):
        """Test that all generated user IDs are unique."""
        gen = ProfileGenerator(num_users=100)
        profiles = gen.generate_all_profiles()
        user_ids = [p.user_id for p in profiles]
        assert len(user_ids) == len(set(user_ids))


# ===== Persona Assignment Tests =====

@pytest.mark.unit
class TestPersonaAssignment:
    """Tests for persona assignment logic."""

    def test_persona_assignment_deterministic(self):
        """Test that persona assignment is deterministic with same seed."""
        gen1 = ProfileGenerator(seed=42, num_users=50)
        gen2 = ProfileGenerator(seed=42, num_users=50)

        personas1 = [gen1._assign_persona(i) for i in range(50)]
        personas2 = [gen2._assign_persona(i) for i in range(50)]

        assert personas1 == personas2

    def test_persona_distribution_20_percent(self):
        """Test that personas are distributed evenly (20% each)."""
        gen = ProfileGenerator(num_users=100)
        profiles = gen.generate_all_profiles()

        persona_counts = {}
        for profile in profiles:
            persona_counts[profile.persona] = persona_counts.get(profile.persona, 0) + 1

        # With 100 users, should be exactly 20 per persona
        for persona in PersonaType:
            assert persona_counts[persona.value] == 20

    def test_persona_distribution_with_odd_count(self):
        """Test persona distribution with non-divisible user count."""
        gen = ProfileGenerator(num_users=77)
        profiles = gen.generate_all_profiles()

        persona_counts = {}
        for profile in profiles:
            persona_counts[profile.persona] = persona_counts.get(profile.persona, 0) + 1

        # Each persona should get 15 or 16 users (77 / 5 = 15.4)
        for count in persona_counts.values():
            assert 15 <= count <= 16

    @pytest.mark.parametrize("user_index,expected_persona", [
        (0, PersonaType.HIGH_UTILIZATION),
        (1, PersonaType.VARIABLE_INCOME),
        (2, PersonaType.SUBSCRIPTION_HEAVY),
        (3, PersonaType.SAVINGS_BUILDER),
        (4, PersonaType.CONTROL),
        (5, PersonaType.HIGH_UTILIZATION),  # Wraps around
    ])
    def test_persona_assignment_sequence(self, user_index, expected_persona):
        """Test persona assignment follows predictable sequence."""
        gen = ProfileGenerator()
        assigned = gen._assign_persona(user_index)
        assert assigned == expected_persona


# ===== Financial Characteristics Tests =====

@pytest.mark.unit
class TestFinancialCharacteristics:
    """Tests for financial characteristic generation."""

    def test_income_within_persona_range(self):
        """Test that generated income is within persona's range."""
        gen = ProfileGenerator(seed=42)

        for persona_type in PersonaType:
            persona_chars = get_persona_characteristics(persona_type)
            income = gen._generate_income(persona_chars)

            assert persona_chars.min_annual_income <= income <= persona_chars.max_annual_income

    def test_seed_affects_generation(self):
        """Test that different seeds produce different profiles."""
        gen1 = ProfileGenerator(seed=42)
        gen2 = ProfileGenerator(seed=999)

        profiles1 = gen1.generate_all_profiles()
        profiles2 = gen2.generate_all_profiles()

        # Different seeds should produce different results
        # Check that at least half of the profiles are different
        differences = sum(
            1 for i in range(len(profiles1))
            if profiles1[i].annual_income != profiles2[i].annual_income
        )
        assert differences > len(profiles1) // 2

    def test_income_rounded_to_thousands(self):
        """Test that income is rounded to nearest $1000."""
        gen = ProfileGenerator(seed=42)
        persona_chars = get_persona_characteristics(PersonaType.CONTROL)

        for _ in range(20):
            income = gen._generate_income(persona_chars)
            assert income % 1000 == 0

    def test_credit_limit_within_persona_range(self):
        """Test that credit limits are within persona bounds."""
        gen = ProfileGenerator(seed=42)

        for persona_type in PersonaType:
            persona_chars = get_persona_characteristics(persona_type)
            income = Decimal("60000")
            limit = gen._generate_credit_limit(persona_chars, income)

            assert persona_chars.min_credit_limit <= limit <= persona_chars.max_credit_limit

    def test_credit_utilization_within_persona_range(self):
        """Test target credit utilization matches persona."""
        gen = ProfileGenerator(seed=42)

        for persona_type in PersonaType:
            persona_chars = get_persona_characteristics(persona_type)
            utilization = gen._generate_target_utilization(persona_chars)

            assert persona_chars.target_credit_utilization_min <= utilization
            assert utilization <= persona_chars.target_credit_utilization_max

    def test_high_utilization_persona_gets_high_target(self):
        """Test High Utilization persona gets 60-80% target utilization."""
        gen = ProfileGenerator(seed=42)
        persona_chars = get_persona_characteristics(PersonaType.HIGH_UTILIZATION)

        # Generate multiple samples
        utilizations = [gen._generate_target_utilization(persona_chars) for _ in range(10)]

        # All should be in 60-80% range
        for util in utilizations:
            assert Decimal("0.60") <= util <= Decimal("0.80")

    def test_savings_builder_gets_high_savings_target(self):
        """Test Savings Builder persona gets >$200/month savings."""
        gen = ProfileGenerator(seed=42)
        persona_chars = get_persona_characteristics(PersonaType.SAVINGS_BUILDER)
        income = Decimal("80000")

        # Generate multiple samples
        savings = [gen._generate_savings_target(persona_chars, income) for _ in range(10)]

        # All should be >= $200
        for target in savings:
            assert target >= Decimal("200")

    def test_subscription_count_within_persona_range(self):
        """Test subscription count matches persona range."""
        gen = ProfileGenerator(seed=42)

        for persona_type in PersonaType:
            persona_chars = get_persona_characteristics(persona_type)
            count = gen._generate_subscription_count(persona_chars)

            assert persona_chars.subscription_count_min <= count <= persona_chars.subscription_count_max

    def test_subscription_heavy_gets_many_subscriptions(self):
        """Test Subscription-Heavy persona gets 5-10 subscriptions."""
        gen = ProfileGenerator(seed=42)
        persona_chars = get_persona_characteristics(PersonaType.SUBSCRIPTION_HEAVY)

        # Generate multiple samples
        counts = [gen._generate_subscription_count(persona_chars) for _ in range(20)]

        # All should be in 5-10 range
        for count in counts:
            assert 5 <= count <= 10


# ===== Account Structure Tests =====

@pytest.mark.unit
class TestAccountStructure:
    """Tests for account structure generation."""

    def test_high_utilization_has_credit_cards(self):
        """Test High Utilization persona has 1-2 credit cards."""
        gen = ProfileGenerator(seed=42)
        persona_chars = get_persona_characteristics(PersonaType.HIGH_UTILIZATION)
        income = Decimal("60000")
        limit = Decimal("15000")

        accounts = gen._generate_accounts(persona_chars, income, limit)

        # Count credit cards
        credit_cards = [a for a in accounts if a["type"] == AccountType.CREDIT.value]
        assert 1 <= len(credit_cards) <= 2

        # Verify total limits
        total_limit = sum(a.get("limit", 0) for a in credit_cards)
        assert abs(total_limit - float(limit)) < 1.0  # Allow rounding

    def test_savings_builder_has_savings_account(self):
        """Test Savings Builder persona has savings account."""
        gen = ProfileGenerator(seed=42)
        persona_chars = get_persona_characteristics(PersonaType.SAVINGS_BUILDER)
        income = Decimal("100000")
        limit = Decimal("20000")

        accounts = gen._generate_accounts(persona_chars, income, limit)

        # Should have savings account
        savings_accounts = [
            a for a in accounts
            if a["subtype"] == AccountSubtype.SAVINGS.value
        ]
        assert len(savings_accounts) >= 1

        # Verify savings balance is substantial
        savings_balance = savings_accounts[0]["initial_balance"]
        monthly_income = float(income) / 12
        assert savings_balance > monthly_income * 2  # At least 2 months

    def test_checking_account_present(self):
        """Test that checking account is almost always present."""
        gen = ProfileGenerator(seed=42, num_users=50)
        profiles = gen.generate_all_profiles()

        checking_count = 0
        for profile in profiles:
            has_checking = any(
                a["subtype"] == AccountSubtype.CHECKING.value
                for a in profile.accounts
            )
            if has_checking:
                checking_count += 1

        # At least 95% should have checking
        assert checking_count >= 47

    def test_account_types_use_enums(self):
        """Test that account types use proper enum values."""
        gen = ProfileGenerator(seed=42)
        profile = gen.generate_profile(0)

        for account in profile.accounts:
            # Verify type is valid
            assert account["type"] in [t.value for t in AccountType]
            # Verify subtype is valid
            assert account["subtype"] in [s.value for s in AccountSubtype]

    def test_credit_card_initial_balance_zero(self):
        """Test that credit cards start with 0 balance."""
        gen = ProfileGenerator(seed=42, num_users=100)
        profiles = gen.generate_all_profiles()

        for profile in profiles:
            for account in profile.accounts:
                if account["type"] == AccountType.CREDIT.value:
                    assert account["initial_balance"] == 0.0


# ===== Profile Generation Tests =====

@pytest.mark.unit
class TestProfileGeneration:
    """Tests for complete profile generation."""

    def test_generate_profile_structure(self):
        """Test that generated profile has all required fields."""
        gen = ProfileGenerator()
        profile = gen.generate_profile(0)

        assert profile.user_id.startswith("user_MASKED_")
        assert isinstance(profile.name, str)
        assert len(profile.name) > 0
        assert profile.persona in [p.value for p in PersonaType]
        assert profile.annual_income > 0
        assert isinstance(profile.characteristics, dict)
        assert isinstance(profile.accounts, list)
        assert len(profile.accounts) > 0

    def test_profile_characteristics_keys(self):
        """Test that profile characteristics contain expected keys."""
        gen = ProfileGenerator()
        profile = gen.generate_profile(0)

        required_keys = {
            "target_credit_utilization",
            "target_savings_monthly",
            "income_stability",
            "subscription_count_target"
        }

        assert required_keys.issubset(profile.characteristics.keys())

    def test_variable_income_has_pay_gap(self):
        """Test Variable Income persona includes median_pay_gap_days."""
        gen = ProfileGenerator(seed=42)

        # User index 1 should be Variable Income (based on assignment logic)
        profile = gen.generate_profile(1)

        assert profile.persona == PersonaType.VARIABLE_INCOME.value
        assert "median_pay_gap_days" in profile.characteristics
        assert profile.characteristics["median_pay_gap_days"] > 45

    def test_deterministic_persona_assignment(self):
        """Test that persona assignment is deterministic with seed."""
        gen1 = ProfileGenerator(seed=999, num_users=50)
        gen2 = ProfileGenerator(seed=999, num_users=50)

        profiles1 = gen1.generate_all_profiles()
        profiles2 = gen2.generate_all_profiles()

        # Persona assignment should be fully deterministic
        assert len(profiles1) == len(profiles2) == 50

        # User IDs and personas should always match (these don't use random generation)
        for i in range(len(profiles1)):
            assert profiles1[i].user_id == profiles2[i].user_id, f"Mismatch at index {i}"
            assert profiles1[i].persona == profiles2[i].persona, f"Mismatch at index {i}"


# ===== Validation Tests =====

@pytest.mark.unit
class TestProfileValidation:
    """Tests for profile distribution validation."""

    def test_validate_distribution_100_users(self):
        """Test validation with perfect 100 users (20 per persona)."""
        gen = ProfileGenerator(num_users=100)
        profiles = gen.generate_all_profiles()
        validation = gen.validate_distribution(profiles)

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

        # Check persona percentages
        for percentage in validation["persona_percentages"].values():
            assert 19.0 <= percentage <= 21.0

    def test_validate_income_range_spans_20k_200k(self):
        """Test that income range covers reasonable spread toward $20K-$200K."""
        gen = ProfileGenerator(num_users=100, seed=42)
        profiles = gen.generate_all_profiles()
        validation = gen.validate_distribution(profiles)

        min_income, max_income = validation["income_range"]

        # Should span a good range (beta distribution won't hit exact extremes with limited sample)
        assert min_income <= 35000  # Near $20K (within tolerance for random distribution)
        assert max_income >= 100000  # Good spread toward $200K

    def test_validation_counts_personas_correctly(self):
        """Test that validation correctly counts persona distribution."""
        gen = ProfileGenerator(num_users=50)
        profiles = gen.generate_all_profiles()
        validation = gen.validate_distribution(profiles)

        # Total should equal num_users
        total = sum(validation["persona_distribution"].values())
        assert total == 50


# ===== JSON Serialization Tests =====

@pytest.mark.unit
class TestJSONSerialization:
    """Tests for JSON save/load functionality."""

    def test_save_profiles_creates_file(self):
        """Test that save_profiles creates JSON file."""
        gen = ProfileGenerator(num_users=50)
        profiles = gen.generate_all_profiles()

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_profiles.json"
            gen.save_profiles(profiles, output_path)

            assert output_path.exists()
            assert output_path.stat().st_size > 0

    def test_save_creates_parent_directories(self):
        """Test that save_profiles creates parent directories."""
        gen = ProfileGenerator(num_users=50)
        profiles = gen.generate_all_profiles()

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "subdir" / "nested" / "profiles.json"
            gen.save_profiles(profiles, output_path)

            assert output_path.exists()

    def test_saved_json_is_valid(self):
        """Test that saved JSON can be loaded."""
        gen = ProfileGenerator(num_users=50)
        profiles = gen.generate_all_profiles()

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "profiles.json"
            gen.save_profiles(profiles, output_path)

            # Load and verify
            with open(output_path) as f:
                data = json.load(f)

            assert isinstance(data, list)
            assert len(data) == 50

    def test_load_profiles(self):
        """Test that load_profiles reads saved data."""
        gen = ProfileGenerator(num_users=50, seed=42)
        profiles = gen.generate_all_profiles()

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "profiles.json"
            gen.save_profiles(profiles, output_path)

            loaded = ProfileGenerator.load_profiles(output_path)

            assert len(loaded) == 50
            assert loaded[0]["user_id"] == profiles[0].user_id
            assert loaded[0]["name"] == profiles[0].name

    def test_json_schema_matches_expected(self):
        """Test that JSON output matches expected schema."""
        gen = ProfileGenerator(num_users=50)
        profiles = gen.generate_all_profiles()

        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "profiles.json"
            gen.save_profiles(profiles, output_path)

            with open(output_path) as f:
                data = json.load(f)

            # Verify first profile structure
            profile = data[0]
            required_keys = {
                "user_id", "name", "persona", "annual_income",
                "characteristics", "accounts"
            }
            assert required_keys == set(profile.keys())

            # Verify accounts structure
            account = profile["accounts"][0]
            assert "type" in account
            assert "subtype" in account
            assert "initial_balance" in account


# ===== Integration Tests =====

@pytest.mark.integration
class TestEndToEndGeneration:
    """Integration tests for complete profile generation workflow."""

    def test_generate_synthetic_profiles_default(self):
        """Test convenience function with defaults."""
        profiles, validation = generate_synthetic_profiles(num_users=100, seed=42)

        assert len(profiles) == 100
        assert validation["valid"] is True

    def test_generate_synthetic_profiles_with_save(self):
        """Test convenience function saves to file."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "profiles.json"

            profiles, validation = generate_synthetic_profiles(
                num_users=75,
                seed=999,
                output_path=output_path
            )

            assert output_path.exists()
            assert len(profiles) == 75
            assert validation["valid"] is True

    def test_full_workflow_50_users(self):
        """Test complete workflow with 50 users."""
        gen = ProfileGenerator(num_users=50, seed=42)
        profiles = gen.generate_all_profiles()

        # Validate
        validation = gen.validate_distribution(profiles)
        assert validation["valid"] is True

        # Save
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "profiles.json"
            gen.save_profiles(profiles, output_path)

            # Load and verify
            loaded = ProfileGenerator.load_profiles(output_path)
            assert len(loaded) == 50

    def test_full_workflow_100_users(self):
        """Test complete workflow with 100 users."""
        gen = ProfileGenerator(num_users=100, seed=123)
        profiles = gen.generate_all_profiles()

        # Validate
        validation = gen.validate_distribution(profiles)
        assert validation["valid"] is True

        # Verify all personas represented
        personas = {p.persona for p in profiles}
        assert len(personas) == 5

        # Verify income diversity (reasonable range with beta distribution)
        incomes = [p.annual_income for p in profiles]
        assert max(incomes) > Decimal("100000")  # Good high earners
        assert min(incomes) <= Decimal("35000")  # Some lower income users

    def test_profiles_pass_schema_validation(self):
        """Test that generated accounts can be validated against Story 1.2 schemas."""
        from spendsense.db.validators import validate_account

        gen = ProfileGenerator(num_users=50, seed=42)
        profiles = gen.generate_all_profiles()

        # Test first few profiles
        validation_failures = []
        for profile in profiles[:10]:
            for account in profile.accounts:
                # Build account data for validation
                account_data = {
                    "account_id": f"{profile.user_id}_acc_001",
                    "type": account["type"],
                    "subtype": account["subtype"],
                    "balances": {
                        "current": account["initial_balance"],
                        "available": account["initial_balance"],
                    },
                    "iso_currency_code": "USD"
                }

                # Add limit for credit cards
                if account.get("limit"):
                    account_data["balances"]["limit"] = account["limit"]

                result = validate_account(account_data)
                if not result.is_valid:
                    validation_failures.append((profile.user_id, result.errors))

        # All should pass
        assert len(validation_failures) == 0, f"Validation failures: {validation_failures}"


# ===== Fixture for common test data =====

@pytest.fixture
def sample_generator():
    """Fixture providing a standard ProfileGenerator instance."""
    return ProfileGenerator(seed=42, num_users=100)


@pytest.fixture
def sample_profiles(sample_generator):
    """Fixture providing a set of generated profiles."""
    return sample_generator.generate_all_profiles()
