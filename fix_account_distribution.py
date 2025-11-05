"""
Fix account distribution to match real-world patterns.

Based on analysis of real transaction data (transactions_formatted.csv):
- 96% of users have credit cards
- Significant portion have savings (varies by income)

Current synthetic data:
- Only 57% have credit cards (too low)
- Only 20% have savings (may be too low)

This script adds missing credit cards and savings accounts to match realistic patterns.
"""

import sqlite3
import random
from pathlib import Path


def add_missing_credit_cards(db_path: str):
    """
    Add credit cards to users who don't have them.

    Target distribution:
    - high_utilization: 100% (already have)
    - subscription_heavy: 95%
    - savings_builder: 90%
    - control: 90%
    - variable_income: 75% (lower due to credit access issues)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 70)
    print("ADDING MISSING CREDIT CARDS")
    print("=" * 70)

    # Get current credit card coverage by persona
    cursor.execute("""
        SELECT
            u.persona,
            COUNT(DISTINCT u.user_id) as total_users,
            COUNT(DISTINCT a.user_id) as users_with_credit
        FROM users u
        LEFT JOIN accounts a ON u.user_id = a.user_id AND a.type = 'credit'
        GROUP BY u.persona
        ORDER BY u.persona
    """)

    current_coverage = cursor.fetchall()

    print("\n📊 Current Credit Card Coverage:")
    for persona, total, with_credit in current_coverage:
        pct = (with_credit / total * 100) if total > 0 else 0
        print(f"  {persona:20} {with_credit:2}/{total:2} ({pct:5.1f}%)")

    # Target coverage by persona
    target_coverage = {
        'high_utilization': 1.00,  # 100%
        'subscription_heavy': 0.95,  # 95%
        'savings_builder': 0.90,  # 90%
        'control': 0.90,  # 90%
        'variable_income': 0.75,  # 75%
    }

    added_count = 0

    for persona, coverage_pct in target_coverage.items():
        # Get users without credit cards for this persona
        cursor.execute("""
            SELECT u.user_id, u.annual_income
            FROM users u
            WHERE u.persona = ?
            AND NOT EXISTS (
                SELECT 1 FROM accounts a
                WHERE a.user_id = u.user_id AND a.type = 'credit'
            )
            ORDER BY u.user_id
        """, (persona,))

        users_without_credit = cursor.fetchall()

        if not users_without_credit:
            continue

        # Calculate how many need credit cards
        # Get counts for this specific persona
        persona_total = next((t for p, t, w in current_coverage if p == persona), 0)
        persona_current = next((w for p, t, w in current_coverage if p == persona), 0)
        target_count = int(persona_total * coverage_pct)
        need_count = max(0, target_count - persona_current)

        # Randomly select users to give credit cards to
        random.shuffle(users_without_credit)
        users_to_add = users_without_credit[:need_count]

        for user_id, annual_income in users_to_add:
            # Count existing credit cards for this user
            cursor.execute("""
                SELECT COUNT(*) FROM accounts
                WHERE user_id = ? AND type = 'credit'
            """, (user_id,))
            existing_count = cursor.fetchone()[0]

            account_id = f"acc_{user_id}_credit_{existing_count}"

            # Calculate realistic credit limit based on income
            # Typical credit limit: 10-30% of annual income
            base_limit = annual_income * random.uniform(0.10, 0.30)
            credit_limit = round(base_limit / 100) * 100  # Round to nearest $100

            # Calculate utilization based on persona
            if persona == 'high_utilization':
                utilization = random.uniform(0.70, 0.95)  # 70-95%
            elif persona == 'variable_income':
                utilization = random.uniform(0.40, 0.70)  # 40-70%
            elif persona == 'savings_builder':
                utilization = random.uniform(0.10, 0.35)  # 10-35%
            else:
                utilization = random.uniform(0.20, 0.50)  # 20-50%

            balance = credit_limit * utilization

            cursor.execute("""
                INSERT INTO accounts (
                    account_id, user_id, type, subtype,
                    iso_currency_code, holder_category,
                    balance_current, balance_available, balance_limit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                user_id,
                'credit',
                'credit_card',
                'USD',
                'personal',
                balance,
                credit_limit - balance,
                credit_limit
            ))

            added_count += 1

        if users_to_add:
            print(f"\n✅ {persona}: Added {len(users_to_add)} credit cards")

    conn.commit()

    print(f"\n📈 Total credit cards added: {added_count}")

    # Show new coverage
    cursor.execute("""
        SELECT
            u.persona,
            COUNT(DISTINCT u.user_id) as total_users,
            COUNT(DISTINCT a.user_id) as users_with_credit
        FROM users u
        LEFT JOIN accounts a ON u.user_id = a.user_id AND a.type = 'credit'
        GROUP BY u.persona
        ORDER BY u.persona
    """)

    new_coverage = cursor.fetchall()

    print("\n📊 New Credit Card Coverage:")
    for persona, total, with_credit in new_coverage:
        pct = (with_credit / total * 100) if total > 0 else 0
        print(f"  {persona:20} {with_credit:2}/{total:2} ({pct:5.1f}%)")

    conn.close()


def add_more_savings_accounts(db_path: str):
    """
    Add savings accounts to more users.

    Target: 40-50% of users should have savings accounts.
    Prioritize by income level and persona.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("ADDING MORE SAVINGS ACCOUNTS")
    print("=" * 70)

    # Get users without savings, ordered by income
    cursor.execute("""
        SELECT u.user_id, u.persona, u.annual_income
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM accounts a
            WHERE a.user_id = u.user_id AND a.subtype = 'savings'
        )
        ORDER BY u.annual_income DESC
    """)

    users_without_savings = cursor.fetchall()

    print(f"\n📊 Users without savings: {len(users_without_savings)}")

    # Target 40% overall savings account ownership
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    target_savings_count = int(total_users * 0.40)

    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) FROM accounts WHERE subtype = 'savings'
    """)
    current_savings_count = cursor.fetchone()[0]

    need_count = max(0, target_savings_count - current_savings_count)

    print(f"  Current: {current_savings_count}/{total_users} ({current_savings_count/total_users*100:.1f}%)")
    print(f"  Target: {target_savings_count}/{total_users} (40%)")
    print(f"  Need to add: {need_count}")

    if need_count == 0:
        print("\n✅ Savings account distribution already meets target")
        conn.close()
        return

    # Prioritize higher income users (they're more likely to have savings)
    # But include some lower income users too (diversity)
    users_to_add = users_without_savings[:need_count]

    added_count = 0

    for user_id, persona, annual_income in users_to_add:
        account_id = f"acc_{user_id}_savings_0"

        # Calculate realistic savings balance
        # Typically 10-40% of annual income (3-12 months of expenses)
        # Lower income users: 10-20%
        # Higher income users: 20-40%
        if annual_income < 50000:
            savings_ratio = random.uniform(0.10, 0.20)
        elif annual_income < 80000:
            savings_ratio = random.uniform(0.15, 0.30)
        else:
            savings_ratio = random.uniform(0.20, 0.40)

        savings_balance = annual_income * savings_ratio
        savings_balance = round(savings_balance / 100) * 100  # Round to nearest $100

        cursor.execute("""
            INSERT INTO accounts (
                account_id, user_id, type, subtype,
                iso_currency_code, holder_category,
                balance_current, balance_available, balance_limit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account_id,
            user_id,
            'depository',
            'savings',
            'USD',
            'personal',
            savings_balance,
            savings_balance,
            None
        ))

        added_count += 1

    conn.commit()

    print(f"\n📈 Total savings accounts added: {added_count}")

    # Show new distribution
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) FROM accounts WHERE subtype = 'savings'
    """)
    new_savings_count = cursor.fetchone()[0]

    print(f"\n📊 New Savings Distribution: {new_savings_count}/{total_users} ({new_savings_count/total_users*100:.1f}%)")

    conn.close()


def show_final_summary(db_path: str):
    """Show final account distribution summary."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("FINAL ACCOUNT DISTRIBUTION SUMMARY")
    print("=" * 70)

    # Overall statistics
    cursor.execute("""
        SELECT
            COUNT(DISTINCT u.user_id) as total_users,
            COUNT(DISTINCT CASE WHEN a.type = 'credit' THEN u.user_id END) as with_credit,
            COUNT(DISTINCT CASE WHEN a.subtype = 'savings' THEN u.user_id END) as with_savings,
            COUNT(CASE WHEN a.type = 'credit' THEN 1 END) as total_credit_accounts,
            COUNT(CASE WHEN a.subtype = 'savings' THEN 1 END) as total_savings_accounts
        FROM users u
        LEFT JOIN accounts a ON u.user_id = a.user_id
    """)

    total, with_credit, with_savings, credit_accounts, savings_accounts = cursor.fetchone()

    print(f"\n📊 Overall Statistics:")
    print(f"  Total users: {total}")
    print(f"  Users with credit cards: {with_credit} ({with_credit/total*100:.1f}%)")
    print(f"  Users with savings: {with_savings} ({with_savings/total*100:.1f}%)")
    print(f"  Total credit card accounts: {credit_accounts}")
    print(f"  Total savings accounts: {savings_accounts}")

    # By persona
    cursor.execute("""
        SELECT
            u.persona,
            COUNT(DISTINCT u.user_id) as total,
            COUNT(DISTINCT CASE WHEN a.type = 'credit' THEN u.user_id END) as with_credit,
            COUNT(DISTINCT CASE WHEN a.subtype = 'savings' THEN u.user_id END) as with_savings
        FROM users u
        LEFT JOIN accounts a ON u.user_id = a.user_id
        GROUP BY u.persona
        ORDER BY u.persona
    """)

    print(f"\n📊 By Persona:")
    print(f"  {'Persona':<20} {'Total':>5} {'Credit':>10} {'Savings':>10}")
    print(f"  {'-'*20} {'-'*5} {'-'*10} {'-'*10}")

    for persona, total, credit, savings in cursor.fetchall():
        credit_pct = f"{credit}/{total} ({credit/total*100:.0f}%)"
        savings_pct = f"{savings}/{total} ({savings/total*100:.0f}%)"
        print(f"  {persona:<20} {total:>5} {credit_pct:>10} {savings_pct:>10}")

    # Sample users
    print(f"\n👤 Sample Users (first 5):")
    cursor.execute("""
        SELECT
            u.user_id,
            u.persona,
            COUNT(CASE WHEN a.type = 'credit' THEN 1 END) as credit_count,
            COUNT(CASE WHEN a.subtype = 'savings' THEN 1 END) as savings_count
        FROM users u
        LEFT JOIN accounts a ON u.user_id = a.user_id
        GROUP BY u.user_id
        ORDER BY u.user_id
        LIMIT 5
    """)

    for user_id, persona, credit, savings in cursor.fetchall():
        print(f"  {user_id}: {persona:20} | CC: {credit} | Savings: {savings}")

    conn.close()


if __name__ == '__main__':
    db_path = 'data/processed/spendsense.db'

    if not Path(db_path).exists():
        print(f"❌ Error: Database not found at {db_path}")
        exit(1)

    print("🔧 Fixing Account Distribution to Match Real-World Patterns\n")

    # Step 1: Add missing credit cards
    add_missing_credit_cards(db_path)

    # Step 2: Add more savings accounts
    add_more_savings_accounts(db_path)

    # Step 3: Show final summary
    show_final_summary(db_path)

    print("\n" + "=" * 70)
    print("✅ Account distribution fixed!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Run fix_credit_and_savings.py to link liabilities")
    print("2. Restart server and test with random user IDs")
    print("3. Most users should now show credit/savings data")
