"""
Persona definitions for synthetic user profile generation.

This module defines the 4 core personas + control group used for synthetic data generation.
Each persona has specific behavioral rules that drive transaction pattern generation.
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PersonaType(str, Enum):
    """
    User persona types for synthetic data generation.

    Each persona represents a distinct financial behavioral pattern that the
    recommendation engine should detect and respond to appropriately.
    """
    HIGH_UTILIZATION = "high_utilization"
    VARIABLE_INCOME = "variable_income"
    SUBSCRIPTION_HEAVY = "subscription_heavy"
    SAVINGS_BUILDER = "savings_builder"
    YOUNG_PROFESSIONAL = "young_professional"
    CONTROL = "control"


class PersonaCharacteristics(BaseModel):
    """
    Financial characteristics for a persona archetype.

    These characteristics define the financial profile that will be used to
    generate realistic transaction patterns.
    """
    # Income characteristics
    min_annual_income: Decimal = Field(description="Minimum annual income for this persona")
    max_annual_income: Decimal = Field(description="Maximum annual income for this persona")
    income_stability: str = Field(description="Income pattern: 'regular', 'irregular', 'highly_irregular'")
    median_pay_gap_days: Optional[int] = Field(default=None, description="Median days between paychecks (None for regular)")

    # Credit characteristics
    min_credit_limit: Decimal = Field(description="Minimum total credit limit")
    max_credit_limit: Decimal = Field(description="Maximum total credit limit")
    target_credit_utilization_min: Decimal = Field(ge=0, le=1, description="Minimum target credit utilization ratio")
    target_credit_utilization_max: Decimal = Field(ge=0, le=1, description="Maximum target credit utilization ratio")

    # Savings characteristics
    target_savings_monthly_min: Decimal = Field(description="Minimum monthly savings target")
    target_savings_monthly_max: Decimal = Field(description="Maximum monthly savings target")

    # Spending characteristics
    subscription_count_min: int = Field(ge=0, description="Minimum number of recurring subscriptions")
    subscription_count_max: int = Field(ge=0, description="Maximum number of recurring subscriptions")

    # Account structure
    has_checking: bool = Field(default=True, description="Has checking account")
    has_savings: bool = Field(default=False, description="Has savings account")
    credit_card_count_min: int = Field(ge=0, description="Minimum number of credit cards")
    credit_card_count_max: int = Field(ge=0, description="Maximum number of credit cards")

    # Initial balances (relative to monthly income)
    checking_balance_months: Decimal = Field(description="Checking balance as months of income")
    savings_balance_months: Decimal = Field(default=Decimal("0"), description="Savings balance as months of income")


# Persona Definitions
# Each persona is calibrated to trigger specific behavioral signals

PERSONA_HIGH_UTILIZATION = PersonaCharacteristics(
    # Moderate income, high credit usage
    min_annual_income=Decimal("40000"),
    max_annual_income=Decimal("80000"),
    income_stability="regular",
    median_pay_gap_days=None,

    # High credit limits to support 60-80% utilization
    min_credit_limit=Decimal("8000"),
    max_credit_limit=Decimal("20000"),
    target_credit_utilization_min=Decimal("0.60"),
    target_credit_utilization_max=Decimal("0.80"),

    # Minimal savings (focused on credit)
    target_savings_monthly_min=Decimal("0"),
    target_savings_monthly_max=Decimal("100"),

    # Moderate subscriptions
    subscription_count_min=2,
    subscription_count_max=4,

    # 1-2 credit cards with high limits
    has_checking=True,
    has_savings=False,
    credit_card_count_min=1,
    credit_card_count_max=2,

    # Low checking balance (paycheck to paycheck)
    checking_balance_months=Decimal("0.5"),
    savings_balance_months=Decimal("0"),
)

PERSONA_VARIABLE_INCOME = PersonaCharacteristics(
    # Wide income range with irregular patterns
    min_annual_income=Decimal("20000"),
    max_annual_income=Decimal("120000"),
    income_stability="irregular",
    median_pay_gap_days=50,  # >45 day gaps to trigger variable income signal

    # Moderate credit usage
    min_credit_limit=Decimal("3000"),
    max_credit_limit=Decimal("10000"),
    target_credit_utilization_min=Decimal("0.30"),
    target_credit_utilization_max=Decimal("0.60"),

    # Limited savings ability
    target_savings_monthly_min=Decimal("0"),
    target_savings_monthly_max=Decimal("150"),

    # Fewer subscriptions (variable income makes commitments risky)
    subscription_count_min=1,
    subscription_count_max=3,

    # Basic account structure
    has_checking=True,
    has_savings=False,  # Optional savings
    credit_card_count_min=0,
    credit_card_count_max=1,

    # Very low checking balance (income volatility risk)
    checking_balance_months=Decimal("0.25"),
    savings_balance_months=Decimal("0"),
)

PERSONA_SUBSCRIPTION_HEAVY = PersonaCharacteristics(
    # Moderate to good income
    min_annual_income=Decimal("50000"),
    max_annual_income=Decimal("120000"),
    income_stability="regular",
    median_pay_gap_days=None,

    # Moderate credit for subscriptions
    min_credit_limit=Decimal("5000"),
    max_credit_limit=Decimal("15000"),
    target_credit_utilization_min=Decimal("0.20"),
    target_credit_utilization_max=Decimal("0.50"),

    # Moderate savings
    target_savings_monthly_min=Decimal("100"),
    target_savings_monthly_max=Decimal("300"),

    # 5-10 recurring subscriptions (streaming, gym, meal kits, etc.)
    subscription_count_min=5,
    subscription_count_max=10,

    # Standard account structure
    has_checking=True,
    has_savings=True,
    credit_card_count_min=1,
    credit_card_count_max=2,

    # Decent buffer
    checking_balance_months=Decimal("1.0"),
    savings_balance_months=Decimal("1.5"),
)

PERSONA_SAVINGS_BUILDER = PersonaCharacteristics(
    # Good to high income
    min_annual_income=Decimal("60000"),
    max_annual_income=Decimal("200000"),
    income_stability="regular",
    median_pay_gap_days=None,

    # Credit available but low utilization
    min_credit_limit=Decimal("10000"),
    max_credit_limit=Decimal("30000"),
    target_credit_utilization_min=Decimal("0.05"),
    target_credit_utilization_max=Decimal("0.30"),

    # Strong savings habit (>$200/month)
    target_savings_monthly_min=Decimal("200"),
    target_savings_monthly_max=Decimal("1000"),

    # Controlled subscriptions
    subscription_count_min=2,
    subscription_count_max=5,

    # Full account structure with emphasis on savings
    has_checking=True,
    has_savings=True,
    credit_card_count_min=1,
    credit_card_count_max=2,

    # Healthy balances
    checking_balance_months=Decimal("1.5"),
    savings_balance_months=Decimal("3.0"),
)

PERSONA_CONTROL = PersonaCharacteristics(
    # Wide income range
    min_annual_income=Decimal("30000"),
    max_annual_income=Decimal("150000"),
    income_stability="regular",
    median_pay_gap_days=None,

    # Moderate credit
    min_credit_limit=Decimal("5000"),
    max_credit_limit=Decimal("15000"),
    target_credit_utilization_min=Decimal("0.20"),
    target_credit_utilization_max=Decimal("0.50"),

    # Moderate savings
    target_savings_monthly_min=Decimal("50"),
    target_savings_monthly_max=Decimal("300"),

    # Moderate subscriptions
    subscription_count_min=2,
    subscription_count_max=6,

    # Variable account structure
    has_checking=True,
    has_savings=True,  # Sometimes
    credit_card_count_min=0,
    credit_card_count_max=2,

    # Moderate balances
    checking_balance_months=Decimal("0.75"),
    savings_balance_months=Decimal("1.0"),
)


# Persona Registry - maps persona types to their characteristics
PERSONA_REGISTRY: dict[PersonaType, PersonaCharacteristics] = {
    PersonaType.HIGH_UTILIZATION: PERSONA_HIGH_UTILIZATION,
    PersonaType.VARIABLE_INCOME: PERSONA_VARIABLE_INCOME,
    PersonaType.SUBSCRIPTION_HEAVY: PERSONA_SUBSCRIPTION_HEAVY,
    PersonaType.SAVINGS_BUILDER: PERSONA_SAVINGS_BUILDER,
    PersonaType.CONTROL: PERSONA_CONTROL,
}


def get_persona_characteristics(persona_type: PersonaType) -> PersonaCharacteristics:
    """
    Get the characteristics for a given persona type.

    Args:
        persona_type: The persona type to look up

    Returns:
        PersonaCharacteristics for the specified persona

    Raises:
        KeyError: If persona_type is not in registry
    """
    return PERSONA_REGISTRY[persona_type]


# Persona Descriptions (for documentation and testing)
PERSONA_DESCRIPTIONS = {
    PersonaType.HIGH_UTILIZATION: (
        "High credit utilization (60-80%). Moderate income but carrying high balances. "
        "Needs guidance on debt management and interest costs."
    ),
    PersonaType.VARIABLE_INCOME: (
        "Irregular income patterns with >45 day median pay gaps. Income volatility creates "
        "cash flow challenges. Needs guidance on budgeting for irregular income."
    ),
    PersonaType.SUBSCRIPTION_HEAVY: (
        "5-10 recurring subscriptions consuming significant monthly budget. May benefit from "
        "subscription audit and optimization recommendations."
    ),
    PersonaType.SAVINGS_BUILDER: (
        "Strong savings habit with >$200/month contributions. Low credit utilization (<30%). "
        "Good financial health, may benefit from investment and optimization guidance."
    ),
    PersonaType.CONTROL: (
        "Mixed financial behaviors that don't strongly align with any single persona. "
        "Represents baseline/average user for comparison."
    ),
}
