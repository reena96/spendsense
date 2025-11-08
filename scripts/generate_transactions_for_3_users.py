#!/usr/bin/env python3
"""
Generate transactions for the 3 new young_professional users (117-119).
"""

import sys
from pathlib import Path
from datetime import date, timedelta, datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import User, Account, Transaction
from spendsense.generators.transaction_generator import TransactionGenerator


def main():
    """Generate transactions for user_MASKED_117, 118, 119."""

    print("=" * 60)
    print("Transaction Generator for 3 New Users")
    print("=" * 60)

    session = get_db_session()

    try:
        # Load the 3 new users
        users = session.query(User).filter(
            User.user_id.in_(['user_MASKED_117', 'user_MASKED_118', 'user_MASKED_119'])
        ).all()

        if len(users) != 3:
            print(f"❌ Expected 3 users, found {len(users)}")
            return

        profiles = []
        for user in users:
            # Get user's accounts
            accounts = session.query(Account).filter(Account.user_id == user.user_id).all()

            account_list = []
            for acc in accounts:
                account_list.append({
                    "account_id": acc.account_id,
                    "type": acc.type,
                    "subtype": acc.subtype,
                    "balance": float(acc.balance_current or 0),
                    "limit": float(acc.balance_limit) if acc.balance_limit else None
                })

            profile = {
                "user_id": user.user_id,
                "name": user.name,
                "persona": "young_professional",
                "annual_income": user.annual_income,
                "characteristics": user.characteristics or {},
                "accounts": account_list
            }
            profiles.append(profile)

        print(f"\n🎯 Loaded {len(profiles)} user profiles")

        # Generate transactions
        print(f"\n🎯 Generating transactions for {len(profiles)} users...")
        print(f"   Generating 180 days of history")

        generator = TransactionGenerator(
            profiles=profiles,
            seed=117,  # Different seed for these users
            days_of_history=180,
            start_date=date.today() - timedelta(days=180)
        )

        user_transactions = generator.generate()

        # Flatten and map account IDs
        all_transactions = []

        for profile in profiles:
            user_id = profile['user_id']
            if user_id not in user_transactions:
                continue

            print(f"  Processing {len(user_transactions[user_id])} transactions for {user_id}...")

            # Create account ID mapping
            account_map = {}
            for acc in profile['accounts']:
                acc_type = acc['subtype'].replace(' ', '_')
                generated_id = f"acc_{user_id}_{acc_type}_0"
                account_map[generated_id] = acc['account_id']

            # Map transactions
            for txn in user_transactions[user_id]:
                if txn['account_id'] in account_map:
                    txn['account_id'] = account_map[txn['account_id']]
                    all_transactions.append(txn)

        print(f"\n✅ Generated {len(all_transactions)} total transactions")

        # Save to database
        print(f"\n💾 Saving {len(all_transactions)} transactions to database...")

        for i, txn_data in enumerate(all_transactions):
            # Convert date string to date object if needed
            txn_date = txn_data["date"]
            if isinstance(txn_date, str):
                txn_date = datetime.fromisoformat(txn_date).date()

            # Generate unique transaction ID
            txn_id = f"yp_new_{txn_data['transaction_id']}"

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

            # Commit every 100 transactions
            if (i + 1) % 100 == 0:
                session.commit()
                print(f"  ✓ Committed {i + 1}/{len(all_transactions)} transactions")

        # Final commit
        session.commit()
        print(f"\n✅ Successfully saved all transactions to database!")

        print("\n" + "=" * 60)
        print("✅ Transaction generation complete!")
        print("=" * 60)

        # Verify
        count = session.query(Transaction).join(Account).filter(
            Account.user_id.in_(['user_MASKED_117', 'user_MASKED_118', 'user_MASKED_119'])
        ).count()
        print(f"\n📊 Total transactions for new 3 users: {count}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
