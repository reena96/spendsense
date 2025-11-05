"""
Synthetic liability data generator for SpendSense.

This module generates realistic liability data (credit cards, student loans, mortgages)
matching user profiles and transaction histories. Follows Plaid's liability structure.
"""

from __future__ import annotations

import json
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from spendsense.db.models import (
    CreditCardLiability,
    MortgageLiability,
    StudentLoanLiability,
)
from spendsense.personas.definitions import PersonaType


class LiabilityGenerator:
    """
    Generate synthetic liability data for user profiles.

    Creates realistic credit card, student loan, and mortgage liabilities
    based on user characteristics and transaction history.
    """

    def __init__(
        self,
        profiles: List[Dict[str, Any]],
        transactions: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        seed: int = 42,
        reference_date: Optional[date] = None
    ):
        """
        Initialize liability generator.

        Args:
            profiles: List of user profile dicts from ProfileGenerator
            transactions: Optional transaction history for consistency validation
            seed: Random seed for reproducibility
            reference_date: Reference date for liability calculations (default: today)
        """
        self.profiles = profiles
        self.transactions = transactions or {}
        self.seed = seed
        self.reference_date = reference_date or date.today()

        self._reset_random_state()

    def _reset_random_state(self):
        """Reset all random number generators to initial seed state."""
        random.seed(self.seed)
        np.random.seed(self.seed)

    def generate(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Generate liabilities for all user profiles.

        Returns:
            Dict mapping user_id to liability data:
            {
                "user_001": {
                    "credit_cards": [...],
                    "student_loans": [...],
                    "mortgages": [...]
                },
                ...
            }
        """
        # Reset random state for reproducibility
        self._reset_random_state()

        all_liabilities = {}

        for profile in self.profiles:
            user_id = profile["user_id"]
            liabilities = self._generate_user_liabilities(profile)
            all_liabilities[user_id] = liabilities

        return all_liabilities

    def _generate_user_liabilities(
        self,
        profile: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all liabilities for a single user profile."""
        user_id = profile["user_id"]
        persona = PersonaType(profile["persona"])
        annual_income = Decimal(str(profile["annual_income"]))
        characteristics = profile["characteristics"]
        accounts = profile["accounts"]

        liabilities = {
            "credit_cards": [],
            "student_loans": [],
            "mortgages": []
        }

        # Find relevant accounts
        credit_accounts = [
            acc for acc in accounts
            if acc.get("type") == "credit" and acc.get("subtype") == "credit card"
        ]
        loan_accounts = [
            acc for acc in accounts
            if acc.get("type") == "loan"
        ]

        # Generate credit card liabilities
        for i, acc in enumerate(credit_accounts):
            account_id = f"acc_{user_id}_credit_{i}"
            cc_liability = self._generate_credit_card_liability(
                account_id, annual_income, persona, characteristics, user_id
            )
            liabilities["credit_cards"].append(cc_liability)

        # Generate loan liabilities
        for i, acc in enumerate(loan_accounts):
            subtype = acc.get("subtype")
            account_id = f"acc_{user_id}_{subtype}_{i}"

            if subtype == "student":
                loan_liability = self._generate_student_loan_liability(account_id)
                liabilities["student_loans"].append(loan_liability)
            elif subtype == "mortgage":
                loan_liability = self._generate_mortgage_liability(account_id)
                liabilities["mortgages"].append(loan_liability)

        return liabilities

    def _generate_credit_card_liability(
        self,
        account_id: str,
        annual_income: Decimal,
        persona: PersonaType,
        characteristics: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Generate credit card liability data."""
        # Calculate credit limit based on income (30-50% of annual income)
        income_multiplier = random.uniform(0.30, 0.50)
        credit_limit = (annual_income * Decimal(str(income_multiplier)) / Decimal("12")).quantize(Decimal("0.01"))
        credit_limit = max(Decimal("500"), min(Decimal("25000"), credit_limit))

        # Get target utilization from profile
        target_utilization = Decimal(str(characteristics.get("target_credit_utilization", 0.35)))

        # Add some variation to utilization
        actual_utilization = target_utilization * Decimal(str(random.uniform(0.9, 1.1)))
        actual_utilization = max(Decimal("0.05"), min(Decimal("0.95"), actual_utilization))

        # Calculate current balance
        current_balance = (credit_limit * actual_utilization).quantize(Decimal("0.01"))

        # Assign APR based on income (lower income = higher APR)
        if annual_income < 40000:
            apr_rate = Decimal(str(random.uniform(0.22, 0.30)))
        elif annual_income < 80000:
            apr_rate = Decimal(str(random.uniform(0.17, 0.23)))
        else:
            apr_rate = Decimal(str(random.uniform(0.15, 0.19)))

        # Calculate minimum payment (2-3% of balance, minimum $25)
        min_payment_pct = Decimal(str(random.uniform(0.02, 0.03)))
        minimum_payment = max(
            Decimal("25"),
            (current_balance * min_payment_pct).quantize(Decimal("0.01"))
        )

        # Get last payment from transaction history
        last_payment_amount = self._get_last_cc_payment(user_id)
        if last_payment_amount is None:
            # Default to slightly above minimum
            last_payment_amount = (minimum_payment * Decimal(str(random.uniform(1.0, 1.5)))).quantize(Decimal("0.01"))

        # Calculate last statement balance (previous month's balance)
        last_statement_balance = (current_balance * Decimal(str(random.uniform(0.9, 1.1)))).quantize(Decimal("0.01"))

        # Determine overdue status based on persona
        overdue_probability = self._get_overdue_probability(persona)
        is_overdue = random.random() < overdue_probability

        # Set next payment due date (15-25 days from reference)
        days_until_due = random.randint(15, 25)
        next_payment_due_date = self.reference_date + timedelta(days=days_until_due)

        # Create liability using Pydantic model
        liability = CreditCardLiability(
            account_id=account_id,
            aprs=[apr_rate],
            minimum_payment_amount=minimum_payment,
            last_payment_amount=last_payment_amount,
            last_statement_balance=last_statement_balance,
            is_overdue=is_overdue,
            next_payment_due_date=next_payment_due_date
        )

        # Convert to dict for JSON serialization
        return self._liability_to_dict(liability)

    def _generate_student_loan_liability(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """Generate student loan liability data."""
        # Realistic student loan interest rate (3-8%)
        interest_rate = Decimal(str(random.uniform(0.03, 0.08)))

        # Next payment due (1 month from reference)
        next_payment_due_date = self.reference_date + timedelta(days=30)

        # Create liability using Pydantic model
        liability = StudentLoanLiability(
            account_id=account_id,
            interest_rate=interest_rate,
            next_payment_due_date=next_payment_due_date
        )

        return self._liability_to_dict(liability)

    def _generate_mortgage_liability(
        self,
        account_id: str
    ) -> Dict[str, Any]:
        """Generate mortgage liability data."""
        # Realistic mortgage interest rate (2-12%)
        interest_rate = Decimal(str(random.uniform(0.02, 0.12)))

        # Next payment due (1 month from reference)
        next_payment_due_date = self.reference_date + timedelta(days=30)

        # Create liability using Pydantic model
        liability = MortgageLiability(
            account_id=account_id,
            interest_rate=interest_rate,
            next_payment_due_date=next_payment_due_date
        )

        return self._liability_to_dict(liability)

    def _get_last_cc_payment(self, user_id: str) -> Optional[Decimal]:
        """Get last credit card payment from transaction history."""
        if user_id not in self.transactions:
            return None

        user_txns = self.transactions[user_id]
        cc_payments = [
            abs(Decimal(str(t["amount"]))) for t in user_txns
            if t.get("personal_finance_category") == "LOAN_PAYMENTS_CREDIT_CARD_PAYMENT"
        ]

        if cc_payments:
            # Return most recent payment (last in sorted list)
            return cc_payments[-1]

        return None

    def _get_overdue_probability(self, persona: PersonaType) -> float:
        """Get probability of being overdue based on persona."""
        overdue_probs = {
            PersonaType.HIGH_UTILIZATION: 0.10,
            PersonaType.VARIABLE_INCOME: 0.15,
            PersonaType.SUBSCRIPTION_HEAVY: 0.05,
            PersonaType.SAVINGS_BUILDER: 0.00,
            PersonaType.CONTROL: 0.02
        }
        return overdue_probs.get(persona, 0.05)

    def _liability_to_dict(self, liability) -> Dict[str, Any]:
        """Convert Pydantic liability model to dict for JSON serialization."""
        data = liability.model_dump()

        # Convert date objects to ISO format strings
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.isoformat()
            elif isinstance(value, Decimal):
                data[key] = float(value)
            elif isinstance(value, list):
                # Handle list of Decimals (APRs)
                data[key] = [float(v) if isinstance(v, Decimal) else v for v in value]

        return data

    def save(self, output_path: Path) -> None:
        """Save liabilities to JSON file."""
        liabilities = self.generate()

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to JSON
        with open(output_path, 'w') as f:
            json.dump(liabilities, f, indent=2, default=str)

        print(f"✓ Saved {len(liabilities)} user liabilities to {output_path}")

    @classmethod
    def from_files(
        cls,
        profiles_path: Path,
        transactions_path: Optional[Path] = None,
        seed: int = 42,
        reference_date: Optional[date] = None
    ) -> "LiabilityGenerator":
        """
        Create generator from profile and transaction files.

        Args:
            profiles_path: Path to profiles JSON file
            transactions_path: Optional path to transactions JSON file
            seed: Random seed
            reference_date: Reference date for calculations

        Returns:
            LiabilityGenerator instance
        """
        # Load profiles
        with open(profiles_path, 'r') as f:
            profiles = json.load(f)

        # Load transactions if provided
        transactions = None
        if transactions_path and transactions_path.exists():
            with open(transactions_path, 'r') as f:
                transactions = json.load(f)

        return cls(
            profiles=profiles,
            transactions=transactions,
            seed=seed,
            reference_date=reference_date
        )


def generate_synthetic_liabilities(
    profiles_path: Path,
    transactions_path: Optional[Path],
    output_path: Path,
    seed: int = 42,
    reference_date: Optional[date] = None
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    Convenience function to generate and save liabilities.

    Args:
        profiles_path: Path to profiles JSON
        transactions_path: Optional path to transactions JSON
        output_path: Path to save liabilities JSON
        seed: Random seed
        reference_date: Reference date

    Returns:
        Generated liabilities dict
    """
    generator = LiabilityGenerator.from_files(
        profiles_path=profiles_path,
        transactions_path=transactions_path,
        seed=seed,
        reference_date=reference_date
    )

    generator.save(output_path)

    return generator.generate()
