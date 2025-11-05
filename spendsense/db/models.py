"""
Data models for SpendSense matching Plaid API structure.

This module defines Pydantic models for accounts, transactions, and liabilities
following Plaid's data structure. These schemas enforce validation rules and
provide type safety for synthetic data generation and ingestion.
"""

from __future__ import annotations

from datetime import date as date_type, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ===== Enums for constrained fields =====

class AccountType(str, Enum):
    """Account type categories matching Plaid structure."""
    DEPOSITORY = "depository"
    CREDIT = "credit"
    LOAN = "loan"


class AccountSubtype(str, Enum):
    """Account subtypes matching Plaid structure."""
    # Depository subtypes
    CHECKING = "checking"
    SAVINGS = "savings"
    CD = "cd"  # Certificate of Deposit
    MONEY_MARKET = "money market"

    # Credit subtypes
    CREDIT_CARD = "credit card"

    # Loan subtypes
    MORTGAGE = "mortgage"
    STUDENT = "student"
    PERSONAL = "personal"


class HolderCategory(str, Enum):
    """Account holder category."""
    PERSONAL = "personal"
    BUSINESS = "business"


class PaymentChannel(str, Enum):
    """Transaction payment channel."""
    ONLINE = "online"
    IN_STORE = "in store"
    OTHER = "other"


class PersonalFinanceCategory(str, Enum):
    """
    Personal finance categories matching Plaid's detailed categorization.

    Plaid uses hierarchical categories with format: PRIMARY_SUBCATEGORY
    """
    # Income categories
    INCOME_WAGES = "INCOME_WAGES"
    INCOME_DIVIDENDS = "INCOME_DIVIDENDS"
    INCOME_INTEREST = "INCOME_INTEREST"
    INCOME_OTHER = "INCOME_OTHER"

    # Transfer categories
    TRANSFER_IN_DEPOSIT = "TRANSFER_IN_DEPOSIT"
    TRANSFER_IN_OTHER = "TRANSFER_IN_OTHER"
    TRANSFER_OUT_SAVINGS = "TRANSFER_OUT_SAVINGS"
    TRANSFER_OUT_INVESTMENT = "TRANSFER_OUT_INVESTMENT"
    TRANSFER_OUT_OTHER = "TRANSFER_OUT_OTHER"

    # Loan payment categories
    LOAN_PAYMENTS_CREDIT_CARD_PAYMENT = "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT"
    LOAN_PAYMENTS_MORTGAGE_PAYMENT = "LOAN_PAYMENTS_MORTGAGE_PAYMENT"
    LOAN_PAYMENTS_STUDENT_LOAN_PAYMENT = "LOAN_PAYMENTS_STUDENT_LOAN_PAYMENT"
    LOAN_PAYMENTS_OTHER = "LOAN_PAYMENTS_OTHER"

    # Bank fees
    BANK_FEES_ATM_FEES = "BANK_FEES_ATM_FEES"
    BANK_FEES_OVERDRAFT_FEES = "BANK_FEES_OVERDRAFT_FEES"
    BANK_FEES_OTHER = "BANK_FEES_OTHER"

    # Food and drink
    FOOD_AND_DRINK_GROCERIES = "FOOD_AND_DRINK_GROCERIES"
    FOOD_AND_DRINK_RESTAURANTS = "FOOD_AND_DRINK_RESTAURANTS"
    FOOD_AND_DRINK_FAST_FOOD = "FOOD_AND_DRINK_FAST_FOOD"
    FOOD_AND_DRINK_COFFEE = "FOOD_AND_DRINK_COFFEE"
    FOOD_AND_DRINK_OTHER = "FOOD_AND_DRINK_OTHER"

    # General merchandise
    GENERAL_MERCHANDISE_GENERAL = "GENERAL_MERCHANDISE_GENERAL"
    GENERAL_MERCHANDISE_BOOKSTORES = "GENERAL_MERCHANDISE_BOOKSTORES"
    GENERAL_MERCHANDISE_CLOTHING = "GENERAL_MERCHANDISE_CLOTHING"
    GENERAL_MERCHANDISE_ELECTRONICS = "GENERAL_MERCHANDISE_ELECTRONICS"
    GENERAL_MERCHANDISE_OTHER = "GENERAL_MERCHANDISE_OTHER"

    # Home
    HOME_UTILITIES = "HOME_UTILITIES"
    HOME_RENT = "HOME_RENT"
    HOME_MORTGAGE = "HOME_MORTGAGE"
    HOME_IMPROVEMENT = "HOME_IMPROVEMENT"
    HOME_OTHER = "HOME_OTHER"

    # Transportation
    TRANSPORTATION_GAS = "TRANSPORTATION_GAS"
    TRANSPORTATION_PUBLIC_TRANSIT = "TRANSPORTATION_PUBLIC_TRANSIT"
    TRANSPORTATION_PARKING = "TRANSPORTATION_PARKING"
    TRANSPORTATION_TOLLS = "TRANSPORTATION_TOLLS"
    TRANSPORTATION_OTHER = "TRANSPORTATION_OTHER"

    # Entertainment
    ENTERTAINMENT_MOVIES = "ENTERTAINMENT_MOVIES"
    ENTERTAINMENT_MUSIC = "ENTERTAINMENT_MUSIC"
    ENTERTAINMENT_SPORTS = "ENTERTAINMENT_SPORTS"
    ENTERTAINMENT_OTHER = "ENTERTAINMENT_OTHER"

    # General services
    GENERAL_SERVICES_SUBSCRIPTION = "GENERAL_SERVICES_SUBSCRIPTION"
    GENERAL_SERVICES_INSURANCE = "GENERAL_SERVICES_INSURANCE"
    GENERAL_SERVICES_PHONE = "GENERAL_SERVICES_PHONE"
    GENERAL_SERVICES_INTERNET = "GENERAL_SERVICES_INTERNET"
    GENERAL_SERVICES_OTHER = "GENERAL_SERVICES_OTHER"

    # Medical
    MEDICAL_HEALTHCARE = "MEDICAL_HEALTHCARE"
    MEDICAL_PHARMACY = "MEDICAL_PHARMACY"
    MEDICAL_OTHER = "MEDICAL_OTHER"

    # Personal care
    PERSONAL_CARE_GYMS = "PERSONAL_CARE_GYMS"
    PERSONAL_CARE_SALON = "PERSONAL_CARE_SALON"
    PERSONAL_CARE_OTHER = "PERSONAL_CARE_OTHER"

    # Travel
    TRAVEL_FLIGHTS = "TRAVEL_FLIGHTS"
    TRAVEL_LODGING = "TRAVEL_LODGING"
    TRAVEL_OTHER = "TRAVEL_OTHER"


# ===== Account Schema =====

class AccountBalances(BaseModel):
    """Account balance information."""
    available: Optional[Decimal] = Field(None, description="Available balance")
    current: Decimal = Field(..., description="Current balance")
    limit: Optional[Decimal] = Field(None, description="Credit limit (for credit accounts)")

    @field_validator("available", "current", "limit")
    @classmethod
    def validate_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Ensure balances are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Balance cannot be negative")
        return v


class Account(BaseModel):
    """
    Account schema matching Plaid structure.

    Represents a financial account (checking, savings, credit card, etc.)
    with balances and metadata.
    """
    account_id: str = Field(..., description="Unique masked account identifier")
    type: AccountType = Field(..., description="Account type category")
    subtype: AccountSubtype = Field(..., description="Specific account subtype")
    balances: AccountBalances = Field(..., description="Account balance information")
    iso_currency_code: str = Field(..., description="ISO 4217 currency code (e.g., USD)")
    holder_category: HolderCategory = Field(
        default=HolderCategory.PERSONAL,
        description="Account holder category"
    )

    @field_validator("iso_currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate ISO 4217 currency codes."""
        valid_codes = {"USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF"}
        if v.upper() not in valid_codes:
            raise ValueError(f"Invalid currency code: {v}. Must be one of {valid_codes}")
        return v.upper()

    @model_validator(mode="after")
    def validate_account_type_consistency(self) -> "Account":
        """Ensure account type and subtype are consistent."""
        type_subtype_map = {
            AccountType.DEPOSITORY: {
                AccountSubtype.CHECKING,
                AccountSubtype.SAVINGS,
                AccountSubtype.CD,
                AccountSubtype.MONEY_MARKET
            },
            AccountType.CREDIT: {AccountSubtype.CREDIT_CARD},
            AccountType.LOAN: {
                AccountSubtype.MORTGAGE,
                AccountSubtype.STUDENT,
                AccountSubtype.PERSONAL
            }
        }

        valid_subtypes = type_subtype_map.get(self.type, set())
        if self.subtype not in valid_subtypes:
            raise ValueError(
                f"Invalid subtype '{self.subtype}' for account type '{self.type}'. "
                f"Valid subtypes: {valid_subtypes}"
            )
        return self


# ===== Transaction Schema =====

class Transaction(BaseModel):
    """
    Transaction schema matching Plaid Transactions API structure.

    Represents a financial transaction with merchant info, amount, and categorization.
    """
    transaction_id: str = Field(..., description="Unique transaction identifier")
    account_id: str = Field(..., description="Account this transaction belongs to")
    date: date_type = Field(..., description="Transaction date")
    amount: Decimal = Field(..., description="Transaction amount (positive = debit, negative = credit)")
    merchant_name: Optional[str] = Field(None, description="Merchant or payee name")
    merchant_entity_id: Optional[str] = Field(None, description="Unique merchant identifier")
    payment_channel: PaymentChannel = Field(..., description="How payment was made")
    personal_finance_category: PersonalFinanceCategory = Field(..., description="Transaction category using Plaid's detailed categorization")
    pending: bool = Field(default=False, description="Whether transaction is pending")


# ===== Liability Schemas =====

class CreditCardLiability(BaseModel):
    """
    Credit card liability schema matching Plaid Liabilities API.

    Represents credit card debt and payment information.
    """
    account_id: str = Field(..., description="Associated credit account ID")
    aprs: list[Decimal] = Field(..., description="Annual Percentage Rates (as decimals, e.g., 0.1999 for 19.99%)")
    minimum_payment_amount: Decimal = Field(..., description="Minimum payment due")
    last_payment_amount: Optional[Decimal] = Field(None, description="Last payment made")
    last_statement_balance: Decimal = Field(..., description="Balance on last statement")
    is_overdue: bool = Field(default=False, description="Whether account is overdue")
    next_payment_due_date: Optional[date_type] = Field(None, description="Next payment due date")

    @field_validator("aprs")
    @classmethod
    def validate_apr_range(cls, v: list[Decimal]) -> list[Decimal]:
        """Validate APR is in reasonable range (0-100%)."""
        for apr in v:
            if apr < 0 or apr > 1.0:
                raise ValueError(f"APR must be between 0 and 1.0 (0-100%), got {apr}")
        return v

    @field_validator("minimum_payment_amount", "last_payment_amount", "last_statement_balance")
    @classmethod
    def validate_non_negative_amount(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Ensure amounts are non-negative."""
        if v is not None and v < 0:
            raise ValueError("Payment amounts cannot be negative")
        return v


class MortgageLiability(BaseModel):
    """
    Mortgage liability schema matching Plaid Liabilities API.

    Represents mortgage loan information.
    """
    account_id: str = Field(..., description="Associated loan account ID")
    interest_rate: Decimal = Field(..., description="Interest rate (as decimal, e.g., 0.045 for 4.5%)")
    next_payment_due_date: Optional[date_type] = Field(None, description="Next payment due date")

    @field_validator("interest_rate")
    @classmethod
    def validate_interest_rate(cls, v: Decimal) -> Decimal:
        """Validate mortgage interest rate is in realistic range (2-12%)."""
        if v < Decimal("0.02") or v > Decimal("0.12"):
            raise ValueError(f"Mortgage interest rate should be between 2% and 12%, got {float(v) * 100}%")
        return v


class StudentLoanLiability(BaseModel):
    """
    Student loan liability schema matching Plaid Liabilities API.

    Represents student loan information.
    """
    account_id: str = Field(..., description="Associated loan account ID")
    interest_rate: Decimal = Field(..., description="Interest rate (as decimal, e.g., 0.0650 for 6.5%)")
    next_payment_due_date: Optional[date_type] = Field(None, description="Next payment due date")

    @field_validator("interest_rate")
    @classmethod
    def validate_interest_rate(cls, v: Decimal) -> Decimal:
        """Validate student loan interest rate is in realistic range (3-8%)."""
        if v < 0.03 or v > 0.08:
            raise ValueError(f"Student loan interest rate should be between 3% and 8%, got {float(v) * 100}%")
        return v
