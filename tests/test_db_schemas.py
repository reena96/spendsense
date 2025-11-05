"""
Unit tests for SpendSense data schemas (Pydantic models).

Tests cover schema validation, field constraints, and edge cases for
Account, Transaction, and Liability models.
"""

import pytest
from datetime import date
from decimal import Decimal
from pydantic import ValidationError

from spendsense.db.models import (
    Account,
    AccountType,
    AccountSubtype,
    AccountBalances,
    Transaction,
    PaymentChannel,
    CreditCardLiability,
    MortgageLiability,
    StudentLoanLiability
)


# ===== Account Schema Tests =====

@pytest.mark.unit
class TestAccountSchema:
    """Tests for Account schema validation."""

    def test_valid_checking_account(self):
        """Test creating a valid checking account."""
        account = Account(
            account_id="acc_MASKED_123",
            type=AccountType.DEPOSITORY,
            subtype=AccountSubtype.CHECKING,
            balances=AccountBalances(available=Decimal("1000.00"), current=Decimal("1200.00")),
            iso_currency_code="USD"
        )
        assert account.account_id == "acc_MASKED_123"
        assert account.type == AccountType.DEPOSITORY
        assert account.balances.current == Decimal("1200.00")

    def test_valid_credit_card_account(self):
        """Test creating a valid credit card account."""
        account = Account(
            account_id="acc_CC_456",
            type=AccountType.CREDIT,
            subtype=AccountSubtype.CREDIT_CARD,
            balances=AccountBalances(
                available=Decimal("5000.00"),
                current=Decimal("2500.00"),
                limit=Decimal("10000.00")
            ),
            iso_currency_code="USD"
        )
        assert account.type == AccountType.CREDIT
        assert account.balances.limit == Decimal("10000.00")

    @pytest.mark.parametrize("currency_code", ["USD", "EUR", "GBP", "CAD", "AUD"])
    def test_valid_currency_codes(self, currency_code):
        """Test valid ISO 4217 currency codes."""
        account = Account(
            account_id=f"acc_{currency_code}",
            type=AccountType.DEPOSITORY,
            subtype=AccountSubtype.SAVINGS,
            balances=AccountBalances(current=Decimal("1000.00")),
            iso_currency_code=currency_code
        )
        assert account.iso_currency_code == currency_code.upper()

    def test_invalid_currency_code(self):
        """Test that invalid currency codes are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                account_id="acc_INVALID",
                type=AccountType.DEPOSITORY,
                subtype=AccountSubtype.CHECKING,
                balances=AccountBalances(current=Decimal("1000.00")),
                iso_currency_code="XYZ"
            )
        assert "Invalid currency code" in str(exc_info.value)

    def test_negative_balance_rejected(self):
        """Test that negative balances are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                account_id="acc_NEG",
                type=AccountType.DEPOSITORY,
                subtype=AccountSubtype.CHECKING,
                balances=AccountBalances(current=Decimal("-100.00")),
                iso_currency_code="USD"
            )
        assert "Balance cannot be negative" in str(exc_info.value)

    def test_type_subtype_mismatch(self):
        """Test that type/subtype mismatch is caught."""
        with pytest.raises(ValidationError) as exc_info:
            Account(
                account_id="acc_MISMATCH",
                type=AccountType.CREDIT,
                subtype=AccountSubtype.CHECKING,  # Wrong: checking is for depository
                balances=AccountBalances(current=Decimal("1000.00")),
                iso_currency_code="USD"
            )
        assert "Invalid subtype" in str(exc_info.value)


# ===== Transaction Schema Tests =====

@pytest.mark.unit
class TestTransactionSchema:
    """Tests for Transaction schema validation."""

    def test_valid_purchase_transaction(self):
        """Test creating a valid purchase transaction."""
        txn = Transaction(
            transaction_id="txn_001",
            account_id="acc_123",
            date=date(2024, 11, 4),
            amount=Decimal("45.67"),
            merchant_name="Whole Foods",
            payment_channel=PaymentChannel.IN_STORE,
            personal_finance_category="FOOD_AND_DRINK"
        )
        assert txn.amount == Decimal("45.67")
        assert txn.payment_channel == PaymentChannel.IN_STORE

    def test_valid_income_transaction(self):
        """Test creating a valid income transaction (negative amount)."""
        txn = Transaction(
            transaction_id="txn_INCOME",
            account_id="acc_123",
            date=date(2024, 11, 1),
            amount=Decimal("-3500.00"),
            merchant_name="Acme Corp Payroll",
            payment_channel=PaymentChannel.OTHER,
            personal_finance_category="INCOME"
        )
        assert txn.amount == Decimal("-3500.00")
        assert txn.personal_finance_category == "INCOME"

    @pytest.mark.parametrize("category", [
        "INCOME", "TRANSFER_IN", "FOOD_AND_DRINK", "ENTERTAINMENT",
        "TRANSPORTATION", "MEDICAL", "RENT_AND_UTILITIES"
    ])
    def test_valid_transaction_categories(self, category):
        """Test valid transaction categories."""
        txn = Transaction(
            transaction_id=f"txn_{category}",
            account_id="acc_123",
            date=date(2024, 11, 4),
            amount=Decimal("50.00"),
            payment_channel=PaymentChannel.ONLINE,
            personal_finance_category=category
        )
        assert txn.personal_finance_category == category

    def test_invalid_category_rejected(self):
        """Test that invalid categories are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            Transaction(
                transaction_id="txn_INVALID",
                account_id="acc_123",
                date=date(2024, 11, 4),
                amount=Decimal("50.00"),
                payment_channel=PaymentChannel.ONLINE,
                personal_finance_category="SHOPPING"  # Invalid
            )
        assert "Invalid personal_finance_category" in str(exc_info.value)

    def test_pending_transaction(self):
        """Test pending transaction flag."""
        txn = Transaction(
            transaction_id="txn_PENDING",
            account_id="acc_123",
            date=date(2024, 11, 4),
            amount=Decimal("100.00"),
            payment_channel=PaymentChannel.ONLINE,
            personal_finance_category="GENERAL_MERCHANDISE",
            pending=True
        )
        assert txn.pending is True


# ===== Credit Card Liability Tests =====

@pytest.mark.unit
class TestCreditCardLiability:
    """Tests for CreditCardLiability schema validation."""

    def test_valid_credit_card_liability(self):
        """Test creating a valid credit card liability."""
        liability = CreditCardLiability(
            account_id="acc_CC_123",
            aprs=[Decimal("0.1999"), Decimal("0.2499")],
            minimum_payment_amount=Decimal("75.00"),
            last_payment_amount=Decimal("150.00"),
            last_statement_balance=Decimal("2500.00"),
            is_overdue=False,
            next_payment_due_date=date(2024, 12, 1)
        )
        assert len(liability.aprs) == 2
        assert liability.minimum_payment_amount == Decimal("75.00")

    def test_apr_range_validation(self):
        """Test that APR must be between 0 and 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            CreditCardLiability(
                account_id="acc_CC_INVALID",
                aprs=[Decimal("1.50")],  # 150% - too high
                minimum_payment_amount=Decimal("50.00"),
                last_statement_balance=Decimal("1000.00")
            )
        assert "APR must be between 0 and 1.0" in str(exc_info.value)

    def test_negative_payment_amount_rejected(self):
        """Test that negative payment amounts are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CreditCardLiability(
                account_id="acc_CC_NEG",
                aprs=[Decimal("0.1999")],
                minimum_payment_amount=Decimal("-50.00"),  # Negative
                last_statement_balance=Decimal("1000.00")
            )
        assert "Payment amounts cannot be negative" in str(exc_info.value)

    def test_overdue_credit_card(self):
        """Test overdue credit card liability."""
        liability = CreditCardLiability(
            account_id="acc_CC_OVERDUE",
            aprs=[Decimal("0.2999")],
            minimum_payment_amount=Decimal("100.00"),
            last_statement_balance=Decimal("3000.00"),
            is_overdue=True
        )
        assert liability.is_overdue is True


# ===== Mortgage Liability Tests =====

@pytest.mark.unit
class TestMortgageLiability:
    """Tests for MortgageLiability schema validation."""

    def test_valid_mortgage_liability(self):
        """Test creating a valid mortgage liability."""
        liability = MortgageLiability(
            account_id="acc_MORT_123",
            interest_rate=Decimal("0.0450"),
            next_payment_due_date=date(2024, 12, 1)
        )
        assert liability.interest_rate == Decimal("0.0450")

    @pytest.mark.parametrize("rate", [
        Decimal("0.02"),   # 2% - minimum
        Decimal("0.045"),  # 4.5% - typical
        Decimal("0.07"),   # 7% - high but valid
        Decimal("0.12")    # 12% - maximum
    ])
    def test_valid_mortgage_interest_rates(self, rate):
        """Test valid mortgage interest rate range (2-12%)."""
        liability = MortgageLiability(
            account_id="acc_MORT_RATE",
            interest_rate=rate
        )
        assert liability.interest_rate == rate

    def test_mortgage_rate_too_high_rejected(self):
        """Test that mortgage rate > 12% is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MortgageLiability(
                account_id="acc_MORT_HIGH",
                interest_rate=Decimal("0.15")  # 15% - too high
            )
        assert "should be between 2% and 12%" in str(exc_info.value)

    def test_mortgage_rate_too_low_rejected(self):
        """Test that mortgage rate < 2% is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            MortgageLiability(
                account_id="acc_MORT_LOW",
                interest_rate=Decimal("0.01")  # 1% - too low
            )
        assert "should be between 2% and 12%" in str(exc_info.value)


# ===== Student Loan Liability Tests =====

@pytest.mark.unit
class TestStudentLoanLiability:
    """Tests for StudentLoanLiability schema validation."""

    def test_valid_student_loan_liability(self):
        """Test creating a valid student loan liability."""
        liability = StudentLoanLiability(
            account_id="acc_SL_123",
            interest_rate=Decimal("0.0550"),
            next_payment_due_date=date(2024, 12, 15)
        )
        assert liability.interest_rate == Decimal("0.0550")

    @pytest.mark.parametrize("rate", [
        Decimal("0.03"),   # 3% - minimum
        Decimal("0.05"),   # 5% - typical federal
        Decimal("0.065"),  # 6.5% - typical private
        Decimal("0.08")    # 8% - maximum
    ])
    def test_valid_student_loan_interest_rates(self, rate):
        """Test valid student loan interest rate range (3-8%)."""
        liability = StudentLoanLiability(
            account_id="acc_SL_RATE",
            interest_rate=rate
        )
        assert liability.interest_rate == rate

    def test_student_loan_rate_too_high_rejected(self):
        """Test that student loan rate > 8% is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StudentLoanLiability(
                account_id="acc_SL_HIGH",
                interest_rate=Decimal("0.10")  # 10% - too high
            )
        assert "should be between 3% and 8%" in str(exc_info.value)

    def test_student_loan_rate_too_low_rejected(self):
        """Test that student loan rate < 3% is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            StudentLoanLiability(
                account_id="acc_SL_LOW",
                interest_rate=Decimal("0.01")  # 1% - too low
            )
        assert "should be between 3% and 8%" in str(exc_info.value)
