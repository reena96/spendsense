#!/usr/bin/env python3
"""
Export database users to profiles.json format for API compatibility.

This ensures the /api/profiles endpoint can serve all 120 users including
the 20 young_professional users from the database.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import User, Account


def main():
    """Export database users to profiles.json."""

    print("=" * 70)
    print("Export Database Users to profiles.json")
    print("=" * 70)

    session = get_db_session()

    try:
        # Query all users
        users = session.query(User).order_by(User.user_id).all()

        print(f"\n📊 Found {len(users)} users in database")

        # Build profiles list
        profiles = []

        for user in users:
            # Get user's accounts
            accounts = session.query(Account).filter(
                Account.user_id == user.user_id
            ).all()

            account_list = []
            for acc in accounts:
                account_dict = {
                    "type": acc.type,
                    "subtype": acc.subtype,
                    "initial_balance": float(acc.balance_current or 0)
                }

                # Add limit if it's a credit account
                if acc.balance_limit:
                    account_dict["limit"] = float(acc.balance_limit)

                account_list.append(account_dict)

            # Build profile
            profile = {
                "user_id": user.user_id,
                "name": user.name,
                "persona": user.persona,
                "annual_income": float(user.annual_income) if user.annual_income else 0.0,
                "characteristics": user.characteristics or {},
                "accounts": account_list
            }

            profiles.append(profile)

        # Calculate persona distribution
        from collections import Counter
        persona_counts = Counter(p["persona"] for p in profiles)

        print(f"\n📊 Persona Distribution:")
        for persona, count in sorted(persona_counts.items()):
            pct = (count / len(profiles)) * 100
            print(f"   {persona}: {count} ({pct:.1f}%)")

        # Write to file
        output_path = Path(__file__).parent.parent / "data" / "synthetic" / "users" / "profiles.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(profiles, f, indent=2)

        print(f"\n✅ Successfully exported {len(profiles)} profiles to:")
        print(f"   {output_path}")

        print("\n" + "=" * 70)
        print("Export complete!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
