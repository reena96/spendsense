#!/usr/bin/env python3
"""
Interactive validation script for Story 1.4: Synthetic Transaction Data Generator

This script generates data and provides an interactive demo to explore the results.
"""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from collections import defaultdict, Counter

from spendsense.generators.profile_generator import ProfileGenerator
from spendsense.generators.transaction_generator import TransactionGenerator
from spendsense.personas.definitions import PersonaType


def generate_data():
    """Generate profile and transaction data."""
    print("=" * 80)
    print("GENERATING SYNTHETIC DATA")
    print("=" * 80)

    # Create directories
    Path("data/synthetic/users").mkdir(parents=True, exist_ok=True)
    Path("data/synthetic/transactions").mkdir(parents=True, exist_ok=True)

    profiles_path = Path("data/synthetic/users/profiles.json")
    transactions_path = Path("data/synthetic/transactions/transactions.json")

    # Generate profiles
    print("\n[1/2] Generating 50 user profiles...")
    profile_gen = ProfileGenerator(seed=42, num_users=50)
    profiles = profile_gen.generate_all_profiles()
    profile_gen.save_profiles(profiles, profiles_path)
    print(f"      ✓ Saved to {profiles_path}")

    # Load profiles as dicts
    with open(profiles_path) as f:
        profiles_dict = json.load(f)

    # Generate transactions
    print("\n[2/2] Generating 180 days of transactions...")
    txn_gen = TransactionGenerator(profiles_dict, seed=42, days_of_history=180)
    txn_gen.save(transactions_path)
    print(f"      ✓ Saved to {transactions_path}")

    return profiles_dict, profiles_path, transactions_path


def load_data(profiles_path, transactions_path):
    """Load existing data."""
    with open(profiles_path) as f:
        profiles = json.load(f)

    with open(transactions_path) as f:
        transactions = json.load(f)

    return profiles, transactions


def display_summary(profiles, transactions):
    """Display high-level summary."""
    print("\n" + "=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)

    print(f"\nTotal Users: {len(profiles)}")
    print(f"Total Transactions: {sum(len(txns) for txns in transactions.values()):,}")

    # Persona breakdown
    persona_counts = Counter(p['persona'] for p in profiles)
    print("\nPersona Distribution:")
    for persona, count in sorted(persona_counts.items()):
        print(f"  • {persona}: {count} users")

    # Transaction categories
    all_categories = set()
    for user_txns in transactions.values():
        for txn in user_txns:
            all_categories.add(txn['personal_finance_category'])

    print(f"\nUnique Transaction Categories: {len(all_categories)}")

    # Date range
    all_dates = []
    for user_txns in transactions.values():
        all_dates.extend([date.fromisoformat(t['date']) for t in user_txns])

    min_date = min(all_dates)
    max_date = max(all_dates)
    span = (max_date - min_date).days

    print(f"\nDate Range: {min_date} to {max_date} ({span} days)")


def explore_user(profiles, transactions, user_id=None):
    """Explore a specific user's data."""
    print("\n" + "=" * 80)
    print("USER EXPLORATION")
    print("=" * 80)

    # If no user specified, pick first one
    if user_id is None:
        user_id = list(transactions.keys())[0]

    # Find profile
    profile = next((p for p in profiles if p['user_id'] == user_id), None)
    if not profile:
        print(f"User {user_id} not found!")
        return

    user_txns = transactions[user_id]

    print(f"\nUser ID: {user_id}")
    print(f"Persona: {profile['persona']}")
    print(f"Annual Income: ${profile['annual_income']:,.2f}")
    print(f"Total Transactions: {len(user_txns)}")

    # Account breakdown
    print("\nAccounts:")
    for acc in profile['accounts']:
        balance = acc.get('initial_balance', 0.0)
        limit = acc.get('limit')
        if limit:
            print(f"  • {acc['type']}/{acc['subtype']}: ${balance:,.2f} / ${limit:,.2f} limit")
        else:
            print(f"  • {acc['type']}/{acc['subtype']}: ${balance:,.2f}")

    # Transaction analysis
    income_txns = [t for t in user_txns if t['amount'] > 0]
    expense_txns = [t for t in user_txns if t['amount'] < 0]

    total_income = sum(t['amount'] for t in income_txns)
    total_expenses = sum(abs(t['amount']) for t in expense_txns)

    print(f"\nFinancial Summary (6 months):")
    print(f"  Income: ${total_income:,.2f} ({len(income_txns)} transactions)")
    print(f"  Expenses: ${total_expenses:,.2f} ({len(expense_txns)} transactions)")
    print(f"  Net: ${total_income - total_expenses:,.2f}")
    print(f"  Spending Rate: {(total_expenses/total_income)*100:.1f}%")

    # Category breakdown
    category_totals = defaultdict(float)
    for txn in expense_txns:
        category_totals[txn['personal_finance_category']] += abs(txn['amount'])

    print("\nTop Spending Categories:")
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {category}: ${amount:,.2f}")

    # Sample transactions
    print("\nRecent Transactions (last 10):")
    for txn in sorted(user_txns, key=lambda t: t['date'], reverse=True)[:10]:
        sign = "+" if txn['amount'] > 0 else ""
        print(f"  {txn['date']} | {sign}${txn['amount']:,.2f} | {txn['merchant_name'][:30]:<30} | {txn['personal_finance_category']}")


def compare_personas(profiles, transactions):
    """Compare spending patterns across personas."""
    print("\n" + "=" * 80)
    print("PERSONA COMPARISON")
    print("=" * 80)

    persona_data = defaultdict(lambda: {'income': [], 'spending': [], 'ratio': []})

    for profile in profiles:
        user_id = profile['user_id']
        persona = profile['persona']
        user_txns = transactions[user_id]

        income = sum(t['amount'] for t in user_txns if t['amount'] > 0)
        spending = sum(abs(t['amount']) for t in user_txns if t['amount'] < 0)

        if income > 0:
            persona_data[persona]['income'].append(income)
            persona_data[persona]['spending'].append(spending)
            persona_data[persona]['ratio'].append(spending / income)

    print("\nAverage Spending Patterns (6 months):")
    print(f"{'Persona':<25} {'Avg Income':<15} {'Avg Spending':<15} {'Spending %':<12}")
    print("-" * 70)

    for persona in sorted(persona_data.keys()):
        data = persona_data[persona]
        avg_income = sum(data['income']) / len(data['income'])
        avg_spending = sum(data['spending']) / len(data['spending'])
        avg_ratio = sum(data['ratio']) / len(data['ratio'])

        print(f"{persona:<25} ${avg_income:>12,.0f} ${avg_spending:>12,.0f} {avg_ratio*100:>10.1f}%")


def validate_schema(transactions):
    """Validate transactions against Pydantic schema."""
    print("\n" + "=" * 80)
    print("SCHEMA VALIDATION")
    print("=" * 80)

    from spendsense.db.models import Transaction, PaymentChannel, PersonalFinanceCategory

    # Validate first user's first 10 transactions
    user_id = list(transactions.keys())[0]
    sample_txns = transactions[user_id][:10]

    print(f"\nValidating {len(sample_txns)} sample transactions from {user_id}...")

    errors = []
    for txn in sample_txns:
        try:
            Transaction(
                transaction_id=txn['transaction_id'],
                account_id=txn['account_id'],
                date=date.fromisoformat(txn['date']),
                amount=Decimal(str(txn['amount'])),
                merchant_name=txn.get('merchant_name'),
                merchant_entity_id=txn.get('merchant_entity_id'),
                payment_channel=PaymentChannel(txn['payment_channel']),
                personal_finance_category=PersonalFinanceCategory(txn['personal_finance_category']),
                pending=txn['pending']
            )
        except Exception as e:
            errors.append(f"Transaction {txn['transaction_id']}: {e}")

    if errors:
        print("\n❌ Schema validation errors:")
        for err in errors:
            print(f"  • {err}")
    else:
        print("\n✅ All sample transactions validate successfully!")


def interactive_menu(profiles, transactions):
    """Interactive exploration menu."""
    while True:
        print("\n" + "=" * 80)
        print("INTERACTIVE VALIDATION MENU")
        print("=" * 80)
        print("\n1. Display Data Summary")
        print("2. Explore Specific User")
        print("3. Compare Personas")
        print("4. Validate Schema")
        print("5. List All Users by Persona")
        print("6. Exit")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == '1':
            display_summary(profiles, transactions)
        elif choice == '2':
            user_id = input("Enter user_id (or press Enter for first user): ").strip()
            explore_user(profiles, transactions, user_id if user_id else None)
        elif choice == '3':
            compare_personas(profiles, transactions)
        elif choice == '4':
            validate_schema(transactions)
        elif choice == '5':
            list_users_by_persona(profiles)
        elif choice == '6':
            print("\nExiting...")
            break
        else:
            print("Invalid choice!")


def list_users_by_persona(profiles):
    """List all users grouped by persona."""
    print("\n" + "=" * 80)
    print("USERS BY PERSONA")
    print("=" * 80)

    by_persona = defaultdict(list)
    for profile in profiles:
        by_persona[profile['persona']].append(profile['user_id'])

    for persona in sorted(by_persona.keys()):
        users = by_persona[persona]
        print(f"\n{persona} ({len(users)} users):")
        for i, user_id in enumerate(users[:5], 1):  # Show first 5
            print(f"  {i}. {user_id}")
        if len(users) > 5:
            print(f"  ... and {len(users) - 5} more")


def main():
    """Main validation script."""
    print("\n" + "=" * 80)
    print("STORY 1.4: SYNTHETIC TRANSACTION DATA GENERATOR - VALIDATION")
    print("=" * 80)

    profiles_path = Path("data/synthetic/users/profiles.json")
    transactions_path = Path("data/synthetic/transactions/transactions.json")

    # Check if data exists
    if not profiles_path.exists() or not transactions_path.exists():
        print("\n⚠️  Data files not found. Generating new data...")
        profiles, profiles_path, transactions_path = generate_data()
        profiles, transactions = load_data(profiles_path, transactions_path)
    else:
        print(f"\n✓ Found existing data files")
        print(f"  • Profiles: {profiles_path}")
        print(f"  • Transactions: {transactions_path}")

        regenerate = input("\nRegenerate data? (y/n): ").strip().lower()
        if regenerate == 'y':
            profiles, profiles_path, transactions_path = generate_data()
            profiles, transactions = load_data(profiles_path, transactions_path)
        else:
            profiles, transactions = load_data(profiles_path, transactions_path)

    # Display summary
    display_summary(profiles, transactions)

    # Interactive menu
    interactive_menu(profiles, transactions)


if __name__ == "__main__":
    main()
