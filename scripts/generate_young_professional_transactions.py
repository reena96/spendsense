#!/usr/bin/env python3
"""
Generate transactions for young_professional users (user_MASKED_100 through user_MASKED_116).

This script creates realistic transaction history for the 17 young_professional users
that were added to the database.
"""

import sys
import random
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from faker import Faker
from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import User, Account, Transaction
from spendsense.personas.definitions import PersonaType, get_persona_characteristics
from spendsense.generators.transaction_generator import TransactionGenerator


def load_young_professional_profiles():
    """Load young_professional user profiles from database."""
    session = get_db_session()
    profiles = []

    try:
        users = session.query(User).filter(User.persona == "young_professional").all()

        for user in users:
            # Get user's accounts
            accounts = session.query(Account).filter(Account.user_id == user.user_id).all()

            # Build account list in format expected by TransactionGenerator
            account_list = []
            for acc in accounts:
                account_list.append({
                    "account_id": acc.account_id,
                    "type": acc.type,
                    "subtype": acc.subtype,
                    "balance": float(acc.balance_current or 0),
                    "limit": float(acc.balance_limit) if acc.balance_limit else None
                })

            # Build profile dict
            profile = {
                "user_id": user.user_id,
                "name": user.name,
                "persona": "young_professional",
                "annual_income": user.annual_income,
                "characteristics": user.characteristics or {},
                "accounts": account_list
            }
            profiles.append(profile)

        print(f"Loaded {len(profiles)} young_professional user profiles")
        return profiles

    finally:
        session.close()


def generate_transactions_for_profiles(profiles):
    """Generate transactions for the profiles using TransactionGenerator."""

    print(f"\n🎯 Generating transactions for {len(profiles)} users...")
    print(f"   Generating 180 days of history")

    # Initialize generator
    generator = TransactionGenerator(
        profiles=profiles,
        seed=100,  # Different seed from main users
        days_of_history=180,
        start_date=date.today() - timedelta(days=180)
    )

    # Generate all transactions (returns dict of user_id -> transactions)
    user_transactions = generator.generate()

    # Flatten into single list and map account IDs from generated format to database format
    all_transactions = []

    for profile in profiles:
        user_id = profile['user_id']
        if user_id not in user_transactions:
            continue

        print(f"  Processing {len(user_transactions[user_id])} transactions for {user_id}...")

        # Create account ID mapping (generated format -> database format)
        account_map = {}
        for acc in profile['accounts']:
            # The generator creates account_ids like "acc_user_MASKED_100_checking_0"
            # Map these to actual database account_ids like "user_MASKED_100_checking"
            acc_type = acc['subtype'].replace(' ', '_')  # "credit card" -> "credit_card"
            generated_id = f"acc_{user_id}_{acc_type}_0"
            account_map[generated_id] = acc['account_id']

        # Map transactions to correct account_ids
        for txn in user_transactions[user_id]:
            # Map the account_id
            if txn['account_id'] in account_map:
                txn['account_id'] = account_map[txn['account_id']]
                all_transactions.append(txn)

    print(f"\n✅ Generated {len(all_transactions)} total transactions")
    return all_transactions


def save_transactions_to_db(transactions):
    """Save transactions to database."""
    session = get_db_session()

    try:
        print(f"\n💾 Saving {len(transactions)} transactions to database...")

        # Convert transaction dicts to ORM objects
        from datetime import datetime
        for i, txn_data in enumerate(transactions):
            # Convert date string to date object if needed
            txn_date = txn_data["date"]
            if isinstance(txn_date, str):
                txn_date = datetime.fromisoformat(txn_date).date()

            # Generate unique transaction ID (prefix with yp_ for young_professional)
            txn_id = f"yp_{txn_data['transaction_id']}"

            txn = Transaction(
                transaction_id=txn_id,
                account_id=txn_data["account_id"],
                date=txn_date,
                amount=txn_data["amount"],
                merchant_name=txn_data.get("merchant_name"),
                merchant_entity_id=txn_data.get("merchant_entity_id"),
                payment_channel=txn_data.get("payment_channel"),
                personal_finance_category=txn_data.get("category"),
                pending=False
            )
            session.add(txn)

            # Commit every 1000 transactions
            if (i + 1) % 1000 == 0:
                session.commit()
                print(f"  ✓ Committed {i + 1}/{len(transactions)} transactions")

        # Final commit
        session.commit()
        print(f"\n✅ Successfully saved all transactions to database!")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error saving transactions: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


def main():
    """Main execution."""
    print("=" * 60)
    print("Young Professional Transaction Generator")
    print("=" * 60)

    # Step 1: Load profiles from database
    profiles = load_young_professional_profiles()

    if not profiles:
        print("\n❌ No young_professional users found in database!")
        return

    # Step 2: Generate transactions
    transactions = generate_transactions_for_profiles(profiles)

    # Step 3: Save to database
    save_transactions_to_db(transactions)

    print("\n" + "=" * 60)
    print("✅ Transaction generation complete!")
    print("=" * 60)

    # Verify
    session = get_db_session()
    try:
        count = session.query(Transaction).join(Account).filter(
            Account.user_id.like('user_MASKED_1%')
        ).count()
        print(f"\n📊 Total transactions for young_professional users: {count}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
