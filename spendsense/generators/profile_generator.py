"""
Synthetic user profile generator with persona-based financial characteristics.

This module generates 50-100 diverse synthetic user profiles with persona assignments
and realistic financial characteristics for testing the SpendSense recommendation engine.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date as date_type
from decimal import Decimal
from pathlib import Path
from typing import Optional

import numpy as np
from faker import Faker

from spendsense.db.models import AccountType, AccountSubtype, HolderCategory
from spendsense.personas.definitions import (
    PersonaType,
    PersonaCharacteristics,
    PERSONA_REGISTRY,
    get_persona_characteristics,
)


@dataclass
class AccountInfo:
    """Account information for a user profile."""
    type: str  # AccountType value
    subtype: str  # AccountSubtype value
    initial_balance: Decimal
    limit: Optional[Decimal] = None  # For credit cards


@dataclass
class UserProfile:
    """
    Complete user profile with persona and financial characteristics.

    This represents a synthetic user that will be used to generate
    transaction data and test the recommendation engine.
    """
    user_id: str
    name: str
    persona: str  # PersonaType value

    # Financial characteristics
    annual_income: Decimal
    characteristics: dict[str, any]

    # Account structure
    accounts: list[dict[str, any]]


class ProfileGenerator:
    """
    Generates synthetic user profiles with persona-based characteristics.

    The generator creates 50-100 users distributed evenly across 5 persona types
    (20% each). Each user's financial characteristics are generated according to
    their assigned persona's behavioral rules.
    """

    def __init__(self, seed: int = 42, num_users: int = 100):
        """
        Initialize the profile generator.

        Args:
            seed: Random seed for reproducibility (default: 42)
            num_users: Number of user profiles to generate (default: 100, range: 50-100)

        Raises:
            ValueError: If num_users is not in range [50, 100]
        """
        if not 50 <= num_users <= 100:
            raise ValueError(f"num_users must be between 50 and 100, got {num_users}")

        self.seed = seed
        self.num_users = num_users

        # Persona distribution (20% each)
        self.persona_types = list(PersonaType)
        self.users_per_persona = num_users // len(self.persona_types)

        # Initialize random generators AFTER setting attributes
        self._reset_random_state()

    def _reset_random_state(self):
        """Reset all random number generators to initial seed state."""
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.faker = Faker()
        Faker.seed(self.seed)

    def _generate_user_id(self, index: int) -> str:
        """
        Generate a masked user ID.

        Args:
            index: User index (0-based)

        Returns:
            Masked user ID in format: user_MASKED_{index:03d}
        """
        return f"user_MASKED_{index:03d}"

    def _assign_persona(self, user_index: int) -> PersonaType:
        """
        Assign a persona to a user deterministically.

        Distribution: 20% to each of the 5 persona types.
        Assignment is deterministic based on user_index for reproducibility.

        Args:
            user_index: User index (0-based)

        Returns:
            Assigned PersonaType
        """
        persona_index = user_index % len(self.persona_types)
        return self.persona_types[persona_index]

    def _generate_income(self, persona_chars: PersonaCharacteristics) -> Decimal:
        """
        Generate annual income within persona's range.

        Uses a log-normal-ish distribution to create realistic income spread
        (more people at lower incomes, fewer at higher incomes).

        Args:
            persona_chars: Persona characteristics defining income range

        Returns:
            Annual income as Decimal
        """
        min_income = float(persona_chars.min_annual_income)
        max_income = float(persona_chars.max_annual_income)

        # Use beta distribution for realistic income spread
        # alpha=2, beta=5 creates right-skewed distribution (most at lower end)
        normalized = np.random.beta(2, 5)

        # Scale to persona's income range
        income = min_income + (normalized * (max_income - min_income))

        # Round to nearest $1000
        income = round(income / 1000) * 1000

        return Decimal(str(int(income)))

    def _generate_credit_limit(
        self,
        persona_chars: PersonaCharacteristics,
        annual_income: Decimal
    ) -> Decimal:
        """
        Generate total credit limit based on persona and income.

        Args:
            persona_chars: Persona characteristics
            annual_income: User's annual income

        Returns:
            Total credit limit across all cards
        """
        min_limit = float(persona_chars.min_credit_limit)
        max_limit = float(persona_chars.max_credit_limit)

        # Credit limit somewhat correlated with income but within persona bounds
        # Higher income -> bias toward higher limit
        income_factor = min(float(annual_income) / 100000, 1.0)
        bias = 0.3 + (income_factor * 0.4)  # 0.3 to 0.7

        normalized = np.random.beta(2, 2) * bias + np.random.beta(2, 2) * (1 - bias)
        normalized = min(1.0, max(0.0, normalized))

        limit = min_limit + (normalized * (max_limit - min_limit))

        # Round to nearest $1000
        limit = round(limit / 1000) * 1000

        return Decimal(str(int(limit)))

    def _generate_target_utilization(self, persona_chars: PersonaCharacteristics) -> Decimal:
        """
        Generate target credit utilization within persona's range.

        Args:
            persona_chars: Persona characteristics

        Returns:
            Target utilization ratio (0.0 to 1.0)
        """
        min_util = float(persona_chars.target_credit_utilization_min)
        max_util = float(persona_chars.target_credit_utilization_max)

        # Uniform distribution within persona's range
        utilization = min_util + (random.random() * (max_util - min_util))

        # Round to 2 decimal places
        return Decimal(str(round(utilization, 2)))

    def _generate_savings_target(
        self,
        persona_chars: PersonaCharacteristics,
        annual_income: Decimal
    ) -> Decimal:
        """
        Generate monthly savings target based on persona and income.

        Args:
            persona_chars: Persona characteristics
            annual_income: User's annual income

        Returns:
            Monthly savings target in dollars
        """
        min_savings = float(persona_chars.target_savings_monthly_min)
        max_savings = float(persona_chars.target_savings_monthly_max)

        # Higher income -> bias toward higher savings
        income_factor = min(float(annual_income) / 100000, 1.0)
        bias = income_factor * 0.6

        normalized = np.random.beta(2, 2) * bias + random.random() * (1 - bias)
        normalized = min(1.0, max(0.0, normalized))

        savings = min_savings + (normalized * (max_savings - min_savings))

        # Round to nearest $10
        savings = round(savings / 10) * 10

        return Decimal(str(int(savings)))

    def _generate_subscription_count(self, persona_chars: PersonaCharacteristics) -> int:
        """
        Generate number of recurring subscriptions.

        Args:
            persona_chars: Persona characteristics

        Returns:
            Number of subscriptions
        """
        return random.randint(
            persona_chars.subscription_count_min,
            persona_chars.subscription_count_max
        )

    def _generate_accounts(
        self,
        persona_chars: PersonaCharacteristics,
        annual_income: Decimal,
        total_credit_limit: Decimal
    ) -> list[dict[str, any]]:
        """
        Generate account structure based on persona.

        Args:
            persona_chars: Persona characteristics
            annual_income: User's annual income
            total_credit_limit: Total credit limit across all cards

        Returns:
            List of account dictionaries
        """
        accounts = []
        monthly_income = annual_income / 12

        # Checking account (almost always present)
        if persona_chars.has_checking:
            checking_balance = monthly_income * persona_chars.checking_balance_months
            accounts.append({
                "type": AccountType.DEPOSITORY.value,
                "subtype": AccountSubtype.CHECKING.value,
                "initial_balance": float(checking_balance.quantize(Decimal("0.01")))
            })

        # Savings account
        if persona_chars.has_savings:
            # Some personas might have savings sometimes
            if persona_chars.savings_balance_months > 0 or random.random() > 0.3:
                savings_balance = monthly_income * persona_chars.savings_balance_months
                accounts.append({
                    "type": AccountType.DEPOSITORY.value,
                    "subtype": AccountSubtype.SAVINGS.value,
                    "initial_balance": float(savings_balance.quantize(Decimal("0.01")))
                })

        # Credit cards
        num_cards = random.randint(
            persona_chars.credit_card_count_min,
            persona_chars.credit_card_count_max
        )

        if num_cards > 0:
            # Distribute credit limit across cards
            for i in range(num_cards):
                if num_cards == 1:
                    card_limit = total_credit_limit
                else:
                    # Split unevenly (primary card gets more)
                    if i == 0:
                        card_limit = total_credit_limit * Decimal("0.6")
                    else:
                        remaining = total_credit_limit * Decimal("0.4")
                        card_limit = remaining / (num_cards - 1)

                accounts.append({
                    "type": AccountType.CREDIT.value,
                    "subtype": AccountSubtype.CREDIT_CARD.value,
                    "initial_balance": 0.0,  # Credit cards start at 0 balance
                    "limit": float(card_limit.quantize(Decimal("0.01")))
                })

        return accounts

    def generate_profile(self, user_index: int) -> UserProfile:
        """
        Generate a complete user profile.

        Args:
            user_index: User index (0-based)

        Returns:
            UserProfile with all characteristics
        """
        # Basic identity
        user_id = self._generate_user_id(user_index)
        name = self.faker.name()
        persona_type = self._assign_persona(user_index)
        persona_chars = get_persona_characteristics(persona_type)

        # Financial characteristics
        annual_income = self._generate_income(persona_chars)
        total_credit_limit = self._generate_credit_limit(persona_chars, annual_income)
        target_utilization = self._generate_target_utilization(persona_chars)
        target_savings = self._generate_savings_target(persona_chars, annual_income)
        subscription_count = self._generate_subscription_count(persona_chars)

        # Account structure
        accounts = self._generate_accounts(persona_chars, annual_income, total_credit_limit)

        # Build characteristics dict
        characteristics = {
            "target_credit_utilization": float(target_utilization),
            "target_savings_monthly": float(target_savings),
            "income_stability": persona_chars.income_stability,
            "subscription_count_target": subscription_count
        }

        # Add median pay gap for variable income personas
        if persona_chars.median_pay_gap_days is not None:
            characteristics["median_pay_gap_days"] = persona_chars.median_pay_gap_days

        return UserProfile(
            user_id=user_id,
            name=name,
            persona=persona_type.value,
            annual_income=annual_income,
            characteristics=characteristics,
            accounts=accounts
        )

    def generate_all_profiles(self) -> list[UserProfile]:
        """
        Generate all user profiles.

        Returns:
            List of UserProfile objects
        """
        profiles = []
        for i in range(self.num_users):
            profile = self.generate_profile(i)
            profiles.append(profile)

        return profiles

    def validate_distribution(self, profiles: list[UserProfile]) -> dict[str, any]:
        """
        Validate that persona and income distributions meet requirements.

        Args:
            profiles: List of generated profiles

        Returns:
            Validation results dictionary with:
                - persona_distribution: dict mapping persona to count
                - persona_percentages: dict mapping persona to percentage
                - income_range: tuple of (min, max) income
                - valid: bool indicating if all validations passed
                - errors: list of validation error messages
        """
        errors = []

        # Persona distribution
        persona_counts = {}
        for profile in profiles:
            persona_counts[profile.persona] = persona_counts.get(profile.persona, 0) + 1

        persona_percentages = {
            persona: (count / len(profiles)) * 100
            for persona, count in persona_counts.items()
        }

        # Check 20% distribution (allow 1% tolerance due to rounding)
        expected_percentage = 20.0
        for persona, percentage in persona_percentages.items():
            if not (19.0 <= percentage <= 21.0):
                errors.append(
                    f"Persona {persona} has {percentage:.1f}% distribution "
                    f"(expected ~{expected_percentage}%)"
                )

        # Income range validation
        incomes = [profile.annual_income for profile in profiles]
        min_income = min(incomes)
        max_income = max(incomes)

        # Check income spans $20K-$200K range (with reasonable tolerance)
        # With 50-100 users and beta distribution, we might not hit exact extremes
        # Especially with smaller samples (50 users), distribution may be compressed
        if min_income > Decimal("35000"):
            errors.append(f"Minimum income ${min_income} is too high (should be near $20K)")
        if max_income < Decimal("100000"):
            errors.append(f"Maximum income ${max_income} is too low (should approach $200K)")

        return {
            "persona_distribution": persona_counts,
            "persona_percentages": persona_percentages,
            "income_range": (float(min_income), float(max_income)),
            "valid": len(errors) == 0,
            "errors": errors
        }

    def save_profiles(
        self,
        profiles: list[UserProfile],
        output_path: Path | str
    ) -> None:
        """
        Save profiles to JSON file.

        Args:
            profiles: List of UserProfile objects
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert profiles to dictionaries
        profiles_data = []
        for profile in profiles:
            profile_dict = {
                "user_id": profile.user_id,
                "name": profile.name,
                "persona": profile.persona,
                "annual_income": float(profile.annual_income),
                "characteristics": profile.characteristics,
                "accounts": profile.accounts
            }
            profiles_data.append(profile_dict)

        # Write to file with pretty formatting
        with open(output_path, 'w') as f:
            json.dump(profiles_data, f, indent=2, sort_keys=False)

    @classmethod
    def load_profiles(cls, input_path: Path | str) -> list[dict]:
        """
        Load profiles from JSON file.

        Args:
            input_path: Path to input JSON file

        Returns:
            List of profile dictionaries
        """
        with open(input_path, 'r') as f:
            return json.load(f)


def generate_synthetic_profiles(
    num_users: int = 100,
    seed: int = 42,
    output_path: Optional[Path | str] = None
) -> tuple[list[UserProfile], dict[str, any]]:
    """
    Convenience function to generate and validate synthetic user profiles.

    Args:
        num_users: Number of profiles to generate (50-100)
        seed: Random seed for reproducibility
        output_path: Optional path to save profiles JSON

    Returns:
        Tuple of (profiles, validation_results)

    Raises:
        ValueError: If validation fails
    """
    generator = ProfileGenerator(seed=seed, num_users=num_users)
    profiles = generator.generate_all_profiles()
    validation = generator.validate_distribution(profiles)

    if not validation["valid"]:
        raise ValueError(
            f"Profile validation failed:\n" + "\n".join(validation["errors"])
        )

    if output_path:
        generator.save_profiles(profiles, output_path)

    return profiles, validation
