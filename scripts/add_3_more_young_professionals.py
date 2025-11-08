#!/usr/bin/env python3
"""
Add 3 more young_professional users to reach 20 total.

Adds user_MASKED_117, user_MASKED_118, user_MASKED_119.
"""

import sys
import random
from pathlib import Path
from datetime import datetime
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from faker import Faker
from spendsense.personas.definitions import PersonaType, get_persona_characteristics
from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import User, Account
import numpy as np

def main():
    """Add 3 more young_professional users."""

    print("🎯 Adding 3 more Young Professional users (117-119)...")

    session = get_db_session()
    fake = Faker()
    Faker.seed(117)  # Different seed for variety
    random.seed(117)
    np.random.seed(117)

    try:
        persona_chars = get_persona_characteristics(PersonaType.YOUNG_PROFESSIONAL)

        # Generate 3 young_professional users (117-119)
        for i in range(3):
            user_number = 117 + i
            user_id = f"user_MASKED_{user_number:03d}"

            print(f"  Creating {user_id}...")

            # Generate income within persona range
            min_income = float(persona_chars.min_annual_income)
            max_income = float(persona_chars.max_annual_income)
            normalized = np.random.beta(2, 5)
            annual_income = min_income + (normalized * (max_income - min_income))
            annual_income = round(annual_income / 1000) * 1000

            # Create user
            user = User(
                user_id=user_id,
                name=fake.name(),
                persona="young_professional",
                annual_income=annual_income,
                characteristics={
                    "income_stability": "regular",
                    "subscription_count": random.randint(
                        persona_chars.subscription_count_min,
                        persona_chars.subscription_count_max
                    )
                },
                consent_status="opted_in",
                consent_timestamp=datetime.utcnow(),
                consent_version="1.0"
            )
            session.add(user)

            # Create checking account
            checking_balance = (annual_income / 12) * float(persona_chars.checking_balance_months)
            checking = Account(
                account_id=f"{user_id}_checking",
                user_id=user_id,
                type="depository",
                subtype="checking",
                iso_currency_code="USD",
                holder_category="personal",
                balance_current=checking_balance,
                balance_available=checking_balance * 0.95,
                balance_limit=None
            )
            session.add(checking)

            # Create savings account
            if persona_chars.has_savings:
                savings_balance = (annual_income / 12) * float(persona_chars.savings_balance_months)
                savings = Account(
                    account_id=f"{user_id}_savings",
                    user_id=user_id,
                    type="depository",
                    subtype="savings",
                    iso_currency_code="USD",
                    holder_category="personal",
                    balance_current=savings_balance,
                    balance_available=savings_balance,
                    balance_limit=None
                )
                session.add(savings)

            # Create credit card (50% chance)
            if random.random() > 0.5:
                min_limit = float(persona_chars.min_credit_limit)
                max_limit = float(persona_chars.max_credit_limit)
                credit_limit = min_limit + (random.random() * (max_limit - min_limit))
                credit_limit = round(credit_limit / 100) * 100

                # Calculate balance based on target utilization
                target_util_min = float(persona_chars.target_credit_utilization_min)
                target_util_max = float(persona_chars.target_credit_utilization_max)
                target_util = target_util_min + (random.random() * (target_util_max - target_util_min))
                balance = credit_limit * target_util

                credit_card = Account(
                    account_id=f"{user_id}_credit",
                    user_id=user_id,
                    type="credit",
                    subtype="credit card",
                    iso_currency_code="USD",
                    holder_category="personal",
                    balance_current=balance,
                    balance_available=credit_limit - balance,
                    balance_limit=credit_limit
                )
                session.add(credit_card)

        # Commit all
        session.commit()

        print("\n✅ Successfully added 3 young_professional users!")
        print(f"   User IDs: user_MASKED_117, user_MASKED_118, user_MASKED_119")

        # Verify
        count = session.query(User).filter(User.persona == "young_professional").count()
        print(f"\n📊 Total young_professional users in database: {count}")

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
