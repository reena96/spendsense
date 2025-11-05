"""
Synthetic Transaction Data Generator

Generates realistic transaction data for synthetic user profiles matching their
persona-specific behavioral patterns. Produces 180+ days of transaction history
including income, subscriptions, spending, and financial transfers.
"""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from faker import Faker

from spendsense.db.models import (
    PaymentChannel,
    PersonalFinanceCategory,
    Transaction,
)
from spendsense.personas.definitions import PersonaType


class TransactionGenerator:
    """
    Generate realistic synthetic transaction data for user profiles.

    Creates persona-driven transaction patterns including:
    - Income transactions (biweekly/monthly/variable)
    - Recurring subscriptions (Netflix, gym, utilities)
    - Spending transactions (groceries, dining, gas, shopping)
    - Financial transfers (savings, credit card payments)

    Generates 180+ days of history with seasonality and pay cycle awareness.
    """

    def __init__(
        self,
        profiles: List[Dict[str, Any]],
        seed: int = 42,
        days_of_history: int = 180,
        start_date: Optional[date] = None
    ):
        """
        Initialize transaction generator.

        Args:
            profiles: List of user profile dicts from ProfileGenerator
            seed: Random seed for reproducibility
            days_of_history: Number of days of transaction history to generate
            start_date: Start date for transaction history (default: 180 days ago)
        """
        if days_of_history < 180:
            raise ValueError(f"days_of_history must be at least 180, got {days_of_history}")

        self.profiles = profiles
        self.seed = seed
        self.days_of_history = days_of_history
        self.start_date = start_date or (date.today() - timedelta(days=days_of_history))
        self.end_date = self.start_date + timedelta(days=days_of_history)

        self._reset_random_state()

        # Transaction counters for unique IDs
        self.transaction_counter = 0

        # Merchant catalogs
        self._init_merchant_catalogs()

    def _reset_random_state(self):
        """Reset all random number generators to initial seed state."""
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.faker = Faker()
        Faker.seed(self.seed)

    def _init_merchant_catalogs(self):
        """Initialize merchant name catalogs for different transaction types."""
        self.subscription_merchants = [
            ("Netflix", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Spotify", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Apple Music", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Amazon Prime", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Hulu", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Disney+", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Planet Fitness", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("LA Fitness", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("Crunch Fitness", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
            ("NYT Digital", PersonalFinanceCategory.GENERAL_SERVICES_SUBSCRIPTION),
        ]

        self.grocery_merchants = [
            "Whole Foods", "Trader Joe's", "Safeway", "Kroger", "Walmart",
            "Target", "Costco", "Sprouts", "Aldi", "Publix"
        ]

        self.restaurant_merchants = [
            "Chipotle", "Starbucks", "McDonald's", "Subway", "Panera Bread",
            "Chick-fil-A", "Taco Bell", "Olive Garden", "The Cheesecake Factory",
            "Local Cafe", "Corner Bistro", "Pizza Hut"
        ]

        self.gas_merchants = [
            "Shell", "Chevron", "BP", "ExxonMobil", "Arco",
            "76", "Valero", "Circle K"
        ]

        self.utility_merchants = [
            ("PG&E", "Electricity"),
            ("Water Company", "Water"),
            ("Verizon", "Internet/Phone"),
            ("AT&T", "Internet/Phone"),
            ("Comcast", "Internet/Cable"),
        ]

    def generate(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate transactions for all user profiles.

        Returns:
            Dict mapping user_id to list of transaction dicts
        """
        all_transactions = {}

        for profile in self.profiles:
            user_id = profile["user_id"]
            transactions = self._generate_user_transactions(profile)
            all_transactions[user_id] = [self._transaction_to_dict(t) for t in transactions]

        return all_transactions

    def _generate_user_transactions(self, profile: Dict[str, Any]) -> List[Transaction]:
        """Generate all transactions for a single user profile."""
        transactions = []
        persona = PersonaType(profile["persona"])
        characteristics = profile["characteristics"]
        accounts = profile["accounts"]
        user_id = profile["user_id"]

        # Find accounts and generate account IDs
        checking_accounts = [acc for acc in accounts if acc.get("type") == "depository" and acc.get("subtype") == "checking"]
        savings_accounts = [acc for acc in accounts if acc.get("type") == "depository" and acc.get("subtype") == "savings"]
        credit_accounts = [acc for acc in accounts if acc.get("type") == "credit" and acc.get("subtype") == "credit card"]

        if not checking_accounts:
            return transactions

        # Generate account IDs (they don't exist in the JSON)
        checking_account_id = f"acc_{user_id}_checking_0"
        savings_account_id = f"acc_{user_id}_savings_0" if savings_accounts else None
        credit_account_id = f"acc_{user_id}_credit_0" if credit_accounts else None

        # 1. Generate income transactions
        income_txns = self._generate_income_transactions(
            profile, checking_account_id, persona, characteristics
        )
        transactions.extend(income_txns)

        # 2. Generate recurring subscriptions
        subscription_txns = self._generate_subscription_transactions(
            profile, checking_account_id if persona != PersonaType.HIGH_UTILIZATION else credit_account_id,
            persona, characteristics
        )
        transactions.extend(subscription_txns)

        # 3. Generate spending transactions
        spending_txns = self._generate_spending_transactions(
            profile, checking_account_id, credit_account_id, persona, characteristics
        )
        transactions.extend(spending_txns)

        # 4. Generate financial transfers
        transfer_txns = self._generate_financial_transfers(
            profile, checking_account_id, savings_account_id, credit_account_id,
            persona, characteristics
        )
        transactions.extend(transfer_txns)

        # Sort by date
        transactions.sort(key=lambda t: t.date)

        return transactions

    def _generate_income_transactions(
        self,
        profile: Dict[str, Any],
        account_id: str,
        persona: PersonaType,
        characteristics: Dict[str, Any]
    ) -> List[Transaction]:
        """Generate income/payroll transactions."""
        transactions = []
        annual_income = profile["annual_income"]
        income_stability = characteristics.get("income_stability", "regular")

        if persona == PersonaType.VARIABLE_INCOME:
            # Variable income: irregular gaps, some months with no income
            transactions.extend(self._generate_variable_income(
                account_id, annual_income
            ))
        elif income_stability == "monthly":
            # Monthly payroll
            transactions.extend(self._generate_monthly_income(
                account_id, annual_income
            ))
        else:
            # Default: biweekly payroll
            transactions.extend(self._generate_biweekly_income(
                account_id, annual_income
            ))

        return transactions

    def _generate_biweekly_income(
        self,
        account_id: str,
        annual_income: Decimal
    ) -> List[Transaction]:
        """Generate biweekly payroll transactions."""
        transactions = []
        annual_income = Decimal(str(annual_income))  # Ensure Decimal type
        biweekly_amount = annual_income / Decimal("26")  # 26 pay periods per year

        # Start on first payday (random day within first 2 weeks)
        pay_day_offset = random.randint(0, 13)
        current_date = self.start_date + timedelta(days=pay_day_offset)

        while current_date <= self.end_date:
            # Small variation in payroll amount
            amount = biweekly_amount * Decimal(str(random.uniform(0.98, 1.02)))

            transactions.append(Transaction(
                transaction_id=self._next_transaction_id(),
                account_id=account_id,
                date=current_date,
                amount=amount,  # Positive for income
                merchant_name="ADP Payroll",
                payment_channel=PaymentChannel.OTHER,
                personal_finance_category=PersonalFinanceCategory.INCOME_WAGES,
                pending=False
            ))

            # Move to next pay period (14 days later)
            current_date = current_date + timedelta(days=14)

        return transactions

    def _generate_monthly_income(
        self,
        account_id: str,
        annual_income: Decimal
    ) -> List[Transaction]:
        """Generate monthly payroll transactions."""
        transactions = []
        annual_income = Decimal(str(annual_income))  # Ensure Decimal type
        monthly_amount = annual_income / Decimal("12")

        pay_day = random.randint(1, 28)  # Same day each month

        current_date = self.start_date
        while current_date <= self.end_date:
            # Find next pay day
            pay_date = date(current_date.year, current_date.month, pay_day)
            if pay_date < current_date:
                # Move to next month
                if current_date.month == 12:
                    pay_date = date(current_date.year + 1, 1, pay_day)
                else:
                    pay_date = date(current_date.year, current_date.month + 1, pay_day)

            if pay_date > self.end_date:
                break

            # Small variation
            amount = monthly_amount * Decimal(str(random.uniform(0.98, 1.02)))

            transactions.append(Transaction(
                transaction_id=self._next_transaction_id(),
                account_id=account_id,
                date=pay_date,
                amount=amount,
                merchant_name="Direct Deposit",
                payment_channel=PaymentChannel.OTHER,
                personal_finance_category=PersonalFinanceCategory.INCOME_WAGES,
                pending=False
            ))

            current_date = pay_date + timedelta(days=28)

        return transactions

    def _generate_variable_income(
        self,
        account_id: str,
        annual_income: Decimal
    ) -> List[Transaction]:
        """Generate variable/irregular income transactions."""
        transactions = []
        annual_income = Decimal(str(annual_income))  # Ensure Decimal type

        # Variable income: irregular gaps (45-90 days), some periods with no income
        current_date = self.start_date
        months_with_income = random.sample(range(6), k=4)  # Only 4 out of 6 months

        for month_offset in months_with_income:
            income_date = self.start_date + timedelta(days=month_offset * 30 + random.randint(1, 28))
            if income_date > self.end_date:
                continue

            # Variable amount (quarterly or project-based)
            amount = annual_income / Decimal("4") * Decimal(str(random.uniform(0.7, 1.3)))

            transactions.append(Transaction(
                transaction_id=self._next_transaction_id(),
                account_id=account_id,
                date=income_date,
                amount=amount,
                merchant_name="Freelance Income" if random.random() > 0.5 else "Contract Payment",
                payment_channel=PaymentChannel.OTHER,
                personal_finance_category=PersonalFinanceCategory.INCOME_WAGES,
                pending=False
            ))

        return transactions

    def _generate_subscription_transactions(
        self,
        profile: Dict[str, Any],
        account_id: str,
        persona: PersonaType,
        characteristics: Dict[str, Any]
    ) -> List[Transaction]:
        """Generate recurring subscription transactions."""
        transactions = []

        # Number of subscriptions based on persona
        if persona == PersonaType.SUBSCRIPTION_HEAVY:
            num_subscriptions = random.randint(5, 10)
        elif persona == PersonaType.CONTROL:
            num_subscriptions = random.randint(2, 4)
        else:
            num_subscriptions = random.randint(1, 3)

        # Select random subscriptions
        selected_subs = random.sample(self.subscription_merchants, min(num_subscriptions, len(self.subscription_merchants)))

        for merchant_name, category in selected_subs:
            # Random subscription day (1-28)
            sub_day = random.randint(1, 28)

            # Subscription amount based on merchant
            if "Gym" in merchant_name or "Fitness" in merchant_name:
                amount = Decimal(str(random.uniform(20, 80)))
            elif "Prime" in merchant_name:
                amount = Decimal("14.99")
            else:
                amount = Decimal(str(random.uniform(8, 20)))

            # Generate monthly recurring transactions
            current_month_date = self.start_date
            while current_month_date <= self.end_date:
                try:
                    sub_date = date(current_month_date.year, current_month_date.month, sub_day)
                    if sub_date < current_month_date:
                        # Move to next month
                        if current_month_date.month == 12:
                            sub_date = date(current_month_date.year + 1, 1, sub_day)
                        else:
                            sub_date = date(current_month_date.year, current_month_date.month + 1, sub_day)
                except ValueError:
                    # Handle day out of range (e.g., Feb 30)
                    sub_date = date(current_month_date.year, current_month_date.month, 28)

                if sub_date > self.end_date:
                    break

                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=account_id,
                    date=sub_date,
                    amount=-amount,  # Negative for expense
                    merchant_name=merchant_name,
                    payment_channel=PaymentChannel.ONLINE,
                    personal_finance_category=category,
                    pending=False
                ))

                # Move to next month
                if current_month_date.month == 12:
                    current_month_date = date(current_month_date.year + 1, 1, 1)
                else:
                    current_month_date = date(current_month_date.year, current_month_date.month + 1, 1)

        # Add monthly utilities
        for utility_name, utility_type in self.utility_merchants[:2]:  # 2 utilities per user
            util_day = random.randint(1, 28)
            base_amount = Decimal(str(random.uniform(50, 150)))

            current_month_date = self.start_date
            while current_month_date <= self.end_date:
                try:
                    util_date = date(current_month_date.year, current_month_date.month, util_day)
                    if util_date < current_month_date:
                        if current_month_date.month == 12:
                            util_date = date(current_month_date.year + 1, 1, util_day)
                        else:
                            util_date = date(current_month_date.year, current_month_date.month + 1, util_day)
                except ValueError:
                    util_date = date(current_month_date.year, current_month_date.month, 28)

                if util_date > self.end_date:
                    break

                # Small variation in utility bill
                amount = base_amount * Decimal(str(random.uniform(0.9, 1.1)))

                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=account_id,
                    date=util_date,
                    amount=-amount,
                    merchant_name=utility_name,
                    payment_channel=PaymentChannel.ONLINE,
                    personal_finance_category=PersonalFinanceCategory.HOME_UTILITIES,
                    pending=False
                ))

                if current_month_date.month == 12:
                    current_month_date = date(current_month_date.year + 1, 1, 1)
                else:
                    current_month_date = date(current_month_date.year, current_month_date.month + 1, 1)

        return transactions

    def _generate_spending_transactions(
        self,
        profile: Dict[str, Any],
        checking_account_id: str,
        credit_account_id: Optional[str],
        persona: PersonaType,
        characteristics: Dict[str, Any]
    ) -> List[Transaction]:
        """Generate daily spending transactions."""
        transactions = []
        annual_income = Decimal(str(profile["annual_income"]))  # Ensure Decimal type

        # Monthly spending budget varies by persona
        if persona == PersonaType.HIGH_UTILIZATION:
            monthly_spending = annual_income / Decimal("12") * Decimal("0.8")  # 80% of monthly income
        elif persona == PersonaType.SAVINGS_BUILDER:
            monthly_spending = annual_income / Decimal("12") * Decimal("0.5")  # 50% of monthly income
        else:
            monthly_spending = annual_income / Decimal("12") * Decimal("0.65")  # 65% of monthly income

        # Total days
        total_days = self.days_of_history

        # Spending distribution (groceries 40%, dining 30%, gas 15%, shopping 15%)
        grocery_budget = monthly_spending * Decimal("0.40") / Decimal("30")  # Per day
        dining_budget = monthly_spending * Decimal("0.30") / Decimal("30")
        gas_budget = monthly_spending * Decimal("0.15") / Decimal("30")
        shopping_budget = monthly_spending * Decimal("0.15") / Decimal("30")

        # Determine which account to use (checking vs credit)
        use_credit = credit_account_id and random.random() > 0.3  # 70% use credit for spending

        current_date = self.start_date
        while current_date <= self.end_date:
            # Grocery shopping (1-2x per week)
            if random.random() < 0.28:  # ~2x per week
                merchant = random.choice(self.grocery_merchants)
                amount = grocery_budget * Decimal(str(random.uniform(3, 7)))  # 3-7 days worth
                account = credit_account_id if use_credit and credit_account_id else checking_account_id

                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=account,
                    date=current_date,
                    amount=-amount,
                    merchant_name=merchant,
                    payment_channel=PaymentChannel.IN_STORE,
                    personal_finance_category=PersonalFinanceCategory.FOOD_AND_DRINK_GROCERIES,
                    pending=False
                ))

            # Dining/restaurants (2-3x per week)
            if random.random() < 0.35:  # ~2.5x per week
                merchant = random.choice(self.restaurant_merchants)
                amount = dining_budget * Decimal(str(random.uniform(1, 3)))
                account = credit_account_id if use_credit and credit_account_id else checking_account_id

                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=account,
                    date=current_date,
                    amount=-amount,
                    merchant_name=merchant,
                    payment_channel=PaymentChannel.IN_STORE,
                    personal_finance_category=PersonalFinanceCategory.FOOD_AND_DRINK_RESTAURANTS,
                    pending=False
                ))

            # Gas (1x per week)
            if random.random() < 0.14:  # ~1x per week
                merchant = random.choice(self.gas_merchants)
                amount = gas_budget * Decimal(str(random.uniform(5, 10)))
                account = credit_account_id if use_credit and credit_account_id else checking_account_id

                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=account,
                    date=current_date,
                    amount=-amount,
                    merchant_name=merchant,
                    payment_channel=PaymentChannel.IN_STORE,
                    personal_finance_category=PersonalFinanceCategory.TRANSPORTATION_GAS,
                    pending=False
                ))

            # Shopping (occasional)
            if random.random() < 0.05:  # ~1-2x per month
                merchant = random.choice(["Amazon", "Target", "Walmart", "Best Buy", "Macy's"])
                amount = shopping_budget * Decimal(str(random.uniform(10, 30)))
                account = credit_account_id if use_credit and credit_account_id else checking_account_id

                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=account,
                    date=current_date,
                    amount=-amount,
                    merchant_name=merchant,
                    payment_channel=PaymentChannel.ONLINE if merchant == "Amazon" else PaymentChannel.IN_STORE,
                    personal_finance_category=PersonalFinanceCategory.GENERAL_MERCHANDISE_GENERAL,
                    pending=False
                ))

            current_date += timedelta(days=1)

        return transactions

    def _generate_financial_transfers(
        self,
        profile: Dict[str, Any],
        checking_account_id: str,
        savings_account_id: Optional[str],
        credit_account_id: Optional[str],
        persona: PersonaType,
        characteristics: Dict[str, Any]
    ) -> List[Transaction]:
        """Generate savings transfers and credit card payments."""
        transactions = []

        # Savings transfers for Savings Builder persona
        if persona == PersonaType.SAVINGS_BUILDER and savings_account_id:
            target_savings = Decimal(str(characteristics.get("target_savings_monthly", 200)))  # Ensure Decimal type
            transfer_day = random.randint(1, 28)

            current_month_date = self.start_date
            while current_month_date <= self.end_date:
                try:
                    transfer_date = date(current_month_date.year, current_month_date.month, transfer_day)
                    if transfer_date < current_month_date:
                        if current_month_date.month == 12:
                            transfer_date = date(current_month_date.year + 1, 1, transfer_day)
                        else:
                            transfer_date = date(current_month_date.year, current_month_date.month + 1, transfer_day)
                except ValueError:
                    transfer_date = date(current_month_date.year, current_month_date.month, 28)

                if transfer_date > self.end_date:
                    break

                amount = target_savings * Decimal(str(random.uniform(0.9, 1.1)))

                # Two transactions: one out of checking, one into savings
                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=checking_account_id,
                    date=transfer_date,
                    amount=-amount,
                    merchant_name="Savings Transfer",
                    payment_channel=PaymentChannel.OTHER,
                    personal_finance_category=PersonalFinanceCategory.TRANSFER_OUT_SAVINGS,
                    pending=False
                ))

                if current_month_date.month == 12:
                    current_month_date = date(current_month_date.year + 1, 1, 1)
                else:
                    current_month_date = date(current_month_date.year, current_month_date.month + 1, 1)

        # Credit card payments
        if credit_account_id:
            # Monthly CC payment
            payment_day = random.randint(1, 28)

            # Payment amount varies by persona
            if persona == PersonaType.HIGH_UTILIZATION:
                # Minimum payment only
                payment_multiplier = Decimal("0.03")  # 3% of balance (minimum)
            else:
                # Full or near-full payment
                payment_multiplier = Decimal("0.95")  # 95% of balance

            # Estimate monthly CC balance from spending
            annual_income = Decimal(str(profile["annual_income"]))  # Ensure Decimal type
            monthly_spending = annual_income / Decimal("12") * Decimal("0.65")
            estimated_balance = monthly_spending * payment_multiplier

            current_month_date = self.start_date
            while current_month_date <= self.end_date:
                try:
                    payment_date = date(current_month_date.year, current_month_date.month, payment_day)
                    if payment_date < current_month_date:
                        if current_month_date.month == 12:
                            payment_date = date(current_month_date.year + 1, 1, payment_day)
                        else:
                            payment_date = date(current_month_date.year, current_month_date.month + 1, payment_day)
                except ValueError:
                    payment_date = date(current_month_date.year, current_month_date.month, 28)

                if payment_date > self.end_date:
                    break

                amount = estimated_balance * Decimal(str(random.uniform(0.9, 1.1)))

                # Payment from checking
                transactions.append(Transaction(
                    transaction_id=self._next_transaction_id(),
                    account_id=checking_account_id,
                    date=payment_date,
                    amount=-amount,
                    merchant_name="Credit Card Payment",
                    payment_channel=PaymentChannel.OTHER,
                    personal_finance_category=PersonalFinanceCategory.LOAN_PAYMENTS_CREDIT_CARD_PAYMENT,
                    pending=False
                ))

                if current_month_date.month == 12:
                    current_month_date = date(current_month_date.year + 1, 1, 1)
                else:
                    current_month_date = date(current_month_date.year, current_month_date.month + 1, 1)

        return transactions

    def _next_transaction_id(self) -> str:
        """Generate next unique transaction ID."""
        self.transaction_counter += 1
        return f"txn_{self.transaction_counter:06d}"

    def _transaction_to_dict(self, transaction: Transaction) -> Dict[str, Any]:
        """Convert Transaction model to dict for JSON serialization."""
        return {
            "transaction_id": transaction.transaction_id,
            "account_id": transaction.account_id,
            "date": transaction.date.isoformat(),
            "amount": float(transaction.amount),
            "merchant_name": transaction.merchant_name,
            "payment_channel": transaction.payment_channel.value,
            "personal_finance_category": transaction.personal_finance_category.value,
            "pending": transaction.pending
        }

    def save(self, output_path: str | Path):
        """
        Generate and save transactions to JSON file.

        Args:
            output_path: Path to output JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        transactions = self.generate()

        with open(output_path, 'w') as f:
            json.dump(transactions, f, indent=2)

        # Calculate statistics
        total_transactions = sum(len(txns) for txns in transactions.values())
        print(f"Generated {total_transactions} transactions for {len(self.profiles)} users")
        print(f"Saved to: {output_path}")

    @classmethod
    def from_profiles_file(
        cls,
        profiles_path: str | Path,
        seed: int = 42,
        days_of_history: int = 180
    ) -> 'TransactionGenerator':
        """
        Create TransactionGenerator from saved profiles JSON file.

        Args:
            profiles_path: Path to profiles JSON file from ProfileGenerator
            seed: Random seed for reproducibility
            days_of_history: Number of days of transaction history

        Returns:
            TransactionGenerator instance
        """
        with open(profiles_path, 'r') as f:
            profiles = json.load(f)

        return cls(profiles, seed=seed, days_of_history=days_of_history)


def generate_synthetic_transactions(
    profiles_path: str | Path,
    output_path: str | Path,
    seed: int = 42,
    days_of_history: int = 180
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convenience function to generate transactions from profiles file.

    Args:
        profiles_path: Path to profiles JSON file
        output_path: Path to output transactions JSON file
        seed: Random seed for reproducibility
        days_of_history: Number of days of transaction history

    Returns:
        Dict mapping user_id to list of transaction dicts
    """
    generator = TransactionGenerator.from_profiles_file(
        profiles_path, seed=seed, days_of_history=days_of_history
    )
    generator.save(output_path)
    return generator.generate()
