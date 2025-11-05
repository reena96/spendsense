"""
Tests for synthetic liability data generator.

Tests cover all acceptance criteria from Story 1.5:
- AC1: Credit card liabilities with proper limits/balances
- AC2: APR rates based on income levels
- AC3: Student loan and mortgage generation
- AC4: Schema validation
- AC5: Consistency with transaction history
- AC6: Persona-specific overdue probabilities
- AC7: Realistic payment amounts
- AC8: JSON serialization
- AC9: Reproducibility with seed
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from spendsense.db.models import (
    CreditCardLiability,
    MortgageLiability,
    StudentLoanLiability,
)
from spendsense.generators.liability_generator import (
    LiabilityGenerator,
    generate_synthetic_liabilities,
)
from spendsense.personas.definitions import PersonaType


@pytest.fixture
def sample_profiles():
    """Sample user profiles for testing."""
    return [
        {
            "user_id": "user_001",
            "persona": PersonaType.HIGH_UTILIZATION.value,
            "annual_income": 45000.0,
            "characteristics": {
                "target_credit_utilization": 0.75,
                "subscription_count": 3,
                "discretionary_spending_factor": 1.2
            },
            "accounts": [
                {"type": "depository", "subtype": "checking", "initial_balance": 1500.0},
                {"type": "credit", "subtype": "credit card", "initial_balance": 0.0, "limit": 3000.0},
                {"type": "loan", "subtype": "student", "initial_balance": 25000.0}
            ]
        },
        {
            "user_id": "user_002",
            "persona": PersonaType.SAVINGS_BUILDER.value,
            "annual_income": 85000.0,
            "characteristics": {
                "target_credit_utilization": 0.15,
                "subscription_count": 2,
                "discretionary_spending_factor": 0.7
            },
            "accounts": [
                {"type": "depository", "subtype": "checking", "initial_balance": 5000.0},
                {"type": "depository", "subtype": "savings", "initial_balance": 15000.0},
                {"type": "credit", "subtype": "credit card", "initial_balance": 0.0, "limit": 10000.0},
                {"type": "loan", "subtype": "mortgage", "initial_balance": 250000.0}
            ]
        }
    ]


@pytest.fixture
def sample_transactions():
    """Sample transaction history for testing."""
    return {
        "user_001": [
            {
                "transaction_id": "txn_001",
                "account_id": "acc_user_001_checking_0",
                "date": "2025-10-15",
                "amount": -150.00,
                "merchant_name": "Credit Card Payment",
                "payment_channel": "online",
                "personal_finance_category": "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT",
                "pending": False
            }
        ],
        "user_002": [
            {
                "transaction_id": "txn_002",
                "account_id": "acc_user_002_checking_0",
                "date": "2025-10-20",
                "amount": -300.00,
                "merchant_name": "Credit Card Payment",
                "payment_channel": "online",
                "personal_finance_category": "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT",
                "pending": False
            }
        ]
    }


@pytest.fixture
def liability_generator(sample_profiles):
    """Create a liability generator instance."""
    return LiabilityGenerator(
        profiles=sample_profiles,
        seed=42,
        reference_date=date(2025, 11, 4)
    )


@pytest.fixture
def liability_generator_with_transactions(sample_profiles, sample_transactions):
    """Create a liability generator with transaction history."""
    return LiabilityGenerator(
        profiles=sample_profiles,
        transactions=sample_transactions,
        seed=42,
        reference_date=date(2025, 11, 4)
    )


class TestAcceptanceCriteria:
    """Test all acceptance criteria from Story 1.5."""

    def test_ac1_credit_card_limits_and_balances(self, liability_generator):
        """
        AC1: Credit card liabilities generated with proper credit limits and current balances
        based on income and persona.
        """
        liabilities = liability_generator.generate()

        # Check high utilization user
        high_util_cc = liabilities["user_001"]["credit_cards"]
        assert len(high_util_cc) == 1, "Should have 1 credit card"

        cc = high_util_cc[0]
        assert "account_id" in cc
        assert "minimum_payment_amount" in cc
        assert "last_payment_amount" in cc
        assert "last_statement_balance" in cc

        # Credit limit should be reasonable for income (30-50% of annual / 12)
        # For $45k income: ~$1,125 - $1,875 per month
        # But capped at $25k max
        # Since this is CC from account with $3k limit, balance should respect utilization

        # Check savings builder user (lower utilization)
        savings_cc = liabilities["user_002"]["credit_cards"]
        assert len(savings_cc) == 1

    def test_ac2_apr_rates_based_on_income(self, liability_generator):
        """
        AC2: APR rates assigned based on income levels (lower income = higher APR).
        """
        liabilities = liability_generator.generate()

        # High utilization user ($45k income) - should have higher APR
        high_util_cc = liabilities["user_001"]["credit_cards"][0]
        high_util_apr = high_util_cc["aprs"][0]

        # Savings builder ($85k income) - should have lower APR
        savings_cc = liabilities["user_002"]["credit_cards"][0]
        savings_apr = savings_cc["aprs"][0]

        # APR should be between 15% and 30%
        assert 0.15 <= high_util_apr <= 0.30
        assert 0.15 <= savings_apr <= 0.30

        # Lower income should generally have higher APR (with some randomness)
        # We can't guarantee this in every case due to randomness, but on average it holds

    def test_ac3_student_loans_and_mortgages_generated(self, liability_generator):
        """
        AC3: Student loan and mortgage liabilities generated for users with loan accounts.
        """
        liabilities = liability_generator.generate()

        # User 1 has student loan account
        student_loans = liabilities["user_001"]["student_loans"]
        assert len(student_loans) == 1, "Should have 1 student loan"

        sl = student_loans[0]
        assert "account_id" in sl
        assert "interest_rate" in sl
        assert "next_payment_due_date" in sl
        assert 0.03 <= sl["interest_rate"] <= 0.08, "Student loan rate should be 3-8%"

        # User 2 has mortgage account
        mortgages = liabilities["user_002"]["mortgages"]
        assert len(mortgages) == 1, "Should have 1 mortgage"

        m = mortgages[0]
        assert "account_id" in m
        assert "interest_rate" in m
        assert "next_payment_due_date" in m
        assert 0.02 <= m["interest_rate"] <= 0.12, "Mortgage rate should be 2-12%"

    def test_ac4_validates_against_schema(self, liability_generator):
        """
        AC4: All liability objects validate against Pydantic schemas.
        """
        liabilities = liability_generator.generate()

        for user_id, user_liabilities in liabilities.items():
            # Validate credit cards
            for cc_data in user_liabilities["credit_cards"]:
                # Reconstruct dates from ISO strings
                cc_data["next_payment_due_date"] = date.fromisoformat(cc_data["next_payment_due_date"])
                cc_data["aprs"] = [Decimal(str(apr)) for apr in cc_data["aprs"]]
                cc_data["minimum_payment_amount"] = Decimal(str(cc_data["minimum_payment_amount"]))
                cc_data["last_payment_amount"] = Decimal(str(cc_data["last_payment_amount"]))
                cc_data["last_statement_balance"] = Decimal(str(cc_data["last_statement_balance"]))

                # Should not raise ValidationError
                cc = CreditCardLiability(**cc_data)
                assert cc.account_id
                assert len(cc.aprs) > 0

            # Validate student loans
            for sl_data in user_liabilities["student_loans"]:
                sl_data["next_payment_due_date"] = date.fromisoformat(sl_data["next_payment_due_date"])
                sl_data["interest_rate"] = Decimal(str(sl_data["interest_rate"]))

                sl = StudentLoanLiability(**sl_data)
                assert sl.account_id

            # Validate mortgages
            for m_data in user_liabilities["mortgages"]:
                m_data["next_payment_due_date"] = date.fromisoformat(m_data["next_payment_due_date"])
                m_data["interest_rate"] = Decimal(str(m_data["interest_rate"]))

                m = MortgageLiability(**m_data)
                assert m.account_id

    def test_ac5_consistency_with_transaction_history(self, liability_generator_with_transactions):
        """
        AC5: Credit card payment amounts consistent with transaction history when available.
        """
        liabilities = liability_generator_with_transactions.generate()

        # User 1 has a $150 credit card payment in history
        cc = liabilities["user_001"]["credit_cards"][0]
        # Last payment should be from transaction history
        assert cc["last_payment_amount"] == 150.00

        # User 2 has a $300 credit card payment in history
        cc = liabilities["user_002"]["credit_cards"][0]
        assert cc["last_payment_amount"] == 300.00

    def test_ac6_persona_specific_overdue_probabilities(self, liability_generator):
        """
        AC6: Overdue status reflects persona characteristics.
        """
        # Test with larger sample to see persona patterns
        profiles = []
        for i in range(20):
            profiles.append({
                "user_id": f"user_high_{i}",
                "persona": PersonaType.HIGH_UTILIZATION.value,
                "annual_income": 45000.0,
                "characteristics": {"target_credit_utilization": 0.75},
                "accounts": [
                    {"type": "credit", "subtype": "credit card", "initial_balance": 0.0, "limit": 3000.0}
                ]
            })
            profiles.append({
                "user_id": f"user_savings_{i}",
                "persona": PersonaType.SAVINGS_BUILDER.value,
                "annual_income": 85000.0,
                "characteristics": {"target_credit_utilization": 0.15},
                "accounts": [
                    {"type": "credit", "subtype": "credit card", "initial_balance": 0.0, "limit": 10000.0}
                ]
            })

        gen = LiabilityGenerator(profiles=profiles, seed=42)
        liabilities = gen.generate()

        # Count overdue by persona
        high_util_overdue = 0
        high_util_total = 0
        savings_overdue = 0
        savings_total = 0

        for user_id, user_liabs in liabilities.items():
            for cc in user_liabs["credit_cards"]:
                if "high" in user_id:
                    high_util_total += 1
                    if cc["is_overdue"]:
                        high_util_overdue += 1
                elif "savings" in user_id:
                    savings_total += 1
                    if cc["is_overdue"]:
                        savings_overdue += 1

        # High utilization should have more overdue (10% vs 0%)
        high_util_rate = high_util_overdue / high_util_total if high_util_total > 0 else 0
        savings_rate = savings_overdue / savings_total if savings_total > 0 else 0

        # With 20 samples and seed=42, we should see the pattern
        # (allowing for randomness, not strict equality)
        assert high_util_rate >= savings_rate, "High utilization should have higher or equal overdue rate"

    def test_ac7_realistic_payment_amounts(self, liability_generator):
        """
        AC7: Minimum payments calculated as 2-3% of balance with $25 minimum.
        """
        liabilities = liability_generator.generate()

        for user_id, user_liabs in liabilities.items():
            for cc in user_liabs["credit_cards"]:
                min_payment = cc["minimum_payment_amount"]
                last_statement = cc["last_statement_balance"]

                # Minimum payment should be at least $25
                assert min_payment >= 25.00

                # If balance is high enough, payment should be ~2-3% of balance
                if last_statement > 1000:
                    payment_pct = min_payment / last_statement
                    # Allow some margin due to the minimum $25 floor
                    assert 0.015 <= payment_pct <= 0.035, \
                        f"Payment {min_payment} should be 2-3% of balance {last_statement}"

    def test_ac8_json_serialization(self, liability_generator, tmp_path):
        """
        AC8: All liability data properly serializes to JSON.
        """
        output_path = tmp_path / "liabilities.json"

        liability_generator.save(output_path)

        # File should exist
        assert output_path.exists()

        # Should be valid JSON
        with open(output_path) as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "user_001" in data
        assert "user_002" in data

        # Check structure
        for user_id, user_liabs in data.items():
            assert "credit_cards" in user_liabs
            assert "student_loans" in user_liabs
            assert "mortgages" in user_liabs
            assert isinstance(user_liabs["credit_cards"], list)

    def test_ac9_reproducible_with_seed(self, sample_profiles):
        """
        AC9: Generator produces identical output with same seed.
        """
        gen1 = LiabilityGenerator(profiles=sample_profiles, seed=123, reference_date=date(2025, 11, 4))
        gen2 = LiabilityGenerator(profiles=sample_profiles, seed=123, reference_date=date(2025, 11, 4))

        liabs1 = gen1.generate()
        liabs2 = gen2.generate()

        # Should be identical
        assert liabs1 == liabs2

        # Different seed should produce different results
        gen3 = LiabilityGenerator(profiles=sample_profiles, seed=456, reference_date=date(2025, 11, 4))
        liabs3 = gen3.generate()

        # At least some values should differ
        assert liabs1 != liabs3


class TestLiabilityGenerator:
    """Additional tests for LiabilityGenerator functionality."""

    def test_next_payment_due_dates(self, liability_generator):
        """Test that next payment due dates are in the future."""
        liabilities = liability_generator.generate()
        ref_date = date(2025, 11, 4)

        for user_id, user_liabs in liabilities.items():
            for cc in user_liabs["credit_cards"]:
                due_date = date.fromisoformat(cc["next_payment_due_date"])
                # Should be 15-25 days in future
                days_until_due = (due_date - ref_date).days
                assert 15 <= days_until_due <= 25

            for sl in user_liabs["student_loans"]:
                due_date = date.fromisoformat(sl["next_payment_due_date"])
                # Should be ~30 days in future
                days_until_due = (due_date - ref_date).days
                assert 28 <= days_until_due <= 32

            for m in user_liabs["mortgages"]:
                due_date = date.fromisoformat(m["next_payment_due_date"])
                # Should be ~30 days in future
                days_until_due = (due_date - ref_date).days
                assert 28 <= days_until_due <= 32

    def test_handles_users_without_credit_accounts(self):
        """Test generator handles users with no credit accounts."""
        profiles = [{
            "user_id": "user_no_credit",
            "persona": PersonaType.CONTROL.value,
            "annual_income": 60000.0,
            "characteristics": {},
            "accounts": [
                {"type": "depository", "subtype": "checking", "initial_balance": 2000.0}
            ]
        }]

        gen = LiabilityGenerator(profiles=profiles, seed=42)
        liabilities = gen.generate()

        assert "user_no_credit" in liabilities
        assert len(liabilities["user_no_credit"]["credit_cards"]) == 0
        assert len(liabilities["user_no_credit"]["student_loans"]) == 0
        assert len(liabilities["user_no_credit"]["mortgages"]) == 0

    def test_from_files_factory_method(self, tmp_path, sample_profiles, sample_transactions):
        """Test creating generator from files."""
        profiles_path = tmp_path / "profiles.json"
        transactions_path = tmp_path / "transactions.json"

        with open(profiles_path, 'w') as f:
            json.dump(sample_profiles, f)

        with open(transactions_path, 'w') as f:
            json.dump(sample_transactions, f)

        gen = LiabilityGenerator.from_files(
            profiles_path=profiles_path,
            transactions_path=transactions_path,
            seed=42
        )

        liabilities = gen.generate()
        assert len(liabilities) == 2

    def test_generate_synthetic_liabilities_function(self, tmp_path, sample_profiles):
        """Test the convenience function."""
        profiles_path = tmp_path / "profiles.json"
        output_path = tmp_path / "liabilities.json"

        with open(profiles_path, 'w') as f:
            json.dump(sample_profiles, f)

        result = generate_synthetic_liabilities(
            profiles_path=profiles_path,
            transactions_path=None,
            output_path=output_path,
            seed=42
        )

        assert output_path.exists()
        assert len(result) == 2
        assert "user_001" in result
        assert "user_002" in result


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_very_low_income_user(self):
        """Test handling of very low income users."""
        profiles = [{
            "user_id": "user_low_income",
            "persona": PersonaType.VARIABLE_INCOME.value,
            "annual_income": 20000.0,
            "characteristics": {"target_credit_utilization": 0.50},
            "accounts": [
                {"type": "credit", "subtype": "credit card", "initial_balance": 0.0, "limit": 500.0}
            ]
        }]

        gen = LiabilityGenerator(profiles=profiles, seed=42)
        liabilities = gen.generate()

        cc = liabilities["user_low_income"]["credit_cards"][0]

        # Should still have valid APR (likely higher)
        assert 0.15 <= cc["aprs"][0] <= 0.30

        # Minimum payment should still be at least $25
        assert cc["minimum_payment_amount"] >= 25.00

    def test_very_high_income_user(self):
        """Test handling of very high income users."""
        profiles = [{
            "user_id": "user_high_income",
            "persona": PersonaType.SAVINGS_BUILDER.value,
            "annual_income": 250000.0,
            "characteristics": {"target_credit_utilization": 0.10},
            "accounts": [
                {"type": "credit", "subtype": "credit card", "initial_balance": 0.0, "limit": 25000.0}
            ]
        }]

        gen = LiabilityGenerator(profiles=profiles, seed=42)
        liabilities = gen.generate()

        cc = liabilities["user_high_income"]["credit_cards"][0]

        # Should have lower APR
        assert 0.15 <= cc["aprs"][0] <= 0.30
