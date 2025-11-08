"""
Fix credit and savings detection by populating missing data.

This script:
1. Links liabilities to credit card accounts
2. Populates savings accounts for savings_builder personas
"""

import sqlite3
from pathlib import Path


def fix_credit_liabilities(db_path: str):
    """Link liabilities to credit card accounts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=== Fixing Credit Detection ===\n")

    # Get all credit card accounts
    cursor.execute("""
        SELECT account_id, user_id, balance_current, balance_limit
        FROM accounts
        WHERE type = 'credit'
        ORDER BY account_id
    """)

    credit_accounts = cursor.fetchall()
    print(f"Found {len(credit_accounts)} credit card accounts")

    # Get existing liabilities (they have no account_id linkage)
    cursor.execute("SELECT id FROM liabilities ORDER BY id LIMIT ?", (len(credit_accounts),))
    liability_ids = [row[0] for row in cursor.fetchall()]

    if len(liability_ids) < len(credit_accounts):
        print(f"Warning: Only {len(liability_ids)} liabilities available for {len(credit_accounts)} credit accounts")
        print("Creating additional liabilities...")

        # Create missing liabilities
        for i in range(len(liability_ids), len(credit_accounts)):
            cursor.execute("""
                INSERT INTO liabilities (
                    account_id, liability_type, interest_rate,
                    minimum_payment_amount, last_payment_amount,
                    last_statement_balance, is_overdue
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (None, 'unknown', None, None, None, None, False))

        conn.commit()

        # Re-fetch liability IDs
        cursor.execute("SELECT id FROM liabilities ORDER BY id LIMIT ?", (len(credit_accounts),))
        liability_ids = [row[0] for row in cursor.fetchall()]

    # Link liabilities to credit accounts and update liability_type
    updated_count = 0
    for liability_id, (account_id, user_id, balance_current, balance_limit) in zip(liability_ids, credit_accounts):
        # Calculate realistic values
        apr = 15.99 + (liability_id % 10) * 1.5  # APR between 15.99% and 30.99%
        min_payment = max(25.0, balance_current * 0.02) if balance_current else 25.0
        last_payment = min_payment * (1.5 + (liability_id % 5) * 0.3)  # Varies between 1.5x and 3x min payment

        cursor.execute("""
            UPDATE liabilities
            SET account_id = ?,
                liability_type = 'credit_card',
                interest_rate = ?,
                minimum_payment_amount = ?,
                last_payment_amount = ?,
                last_statement_balance = ?,
                is_overdue = ?
            WHERE id = ?
        """, (
            account_id,
            apr,
            round(min_payment, 2),
            round(last_payment, 2),
            balance_current,
            False,  # No overdue accounts by default
            liability_id
        ))

        updated_count += 1

        if updated_count % 10 == 0:
            print(f"  Linked {updated_count}/{len(credit_accounts)} credit card liabilities...")

    conn.commit()
    print(f"✅ Successfully linked {updated_count} credit card accounts to liabilities\n")

    # Verify
    cursor.execute("""
        SELECT COUNT(*) FROM liabilities
        WHERE liability_type = 'credit_card' AND account_id IS NOT NULL
    """)

    linked_count = cursor.fetchone()[0]
    print(f"Verification: {linked_count} credit card liabilities now linked to accounts")

    conn.close()


def add_savings_accounts(db_path: str):
    """Add savings accounts for savings_builder personas."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n=== Adding Savings Accounts ===\n")

    # Get savings_builder users
    cursor.execute("""
        SELECT user_id, annual_income
        FROM users
        WHERE persona = 'savings_builder'
        ORDER BY user_id
    """)

    savings_builders = cursor.fetchall()
    print(f"Found {len(savings_builders)} savings_builder persona users")

    added_count = 0
    for user_id, annual_income in savings_builders:
        # Check if user already has a savings account
        cursor.execute("""
            SELECT COUNT(*) FROM accounts
            WHERE user_id = ? AND subtype = 'savings'
        """, (user_id,))

        if cursor.fetchone()[0] > 0:
            continue  # Already has savings account

        # Calculate realistic savings balance (3-6 months of expenses)
        # Assume expenses = 70% of income, so 3-6 months = 17.5-35% of annual income
        savings_balance = annual_income * (0.175 + (added_count % 10) * 0.0175)  # 17.5% to 35%
        savings_balance = round(savings_balance, 2)

        account_id = f"acc_{user_id}_savings_0"

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

        if added_count % 5 == 0:
            print(f"  Added {added_count}/{len(savings_builders)} savings accounts...")

    conn.commit()
    print(f"✅ Successfully added {added_count} savings accounts\n")

    # Verify
    cursor.execute("""
        SELECT COUNT(*) FROM accounts WHERE subtype = 'savings'
    """)

    total_savings = cursor.fetchone()[0]
    print(f"Verification: {total_savings} total savings accounts in database")

    conn.close()


def show_summary(db_path: str):
    """Show summary statistics after fixes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("\n=== Summary Statistics ===\n")

    # Credit accounts
    cursor.execute("""
        SELECT COUNT(*) FROM accounts WHERE type = 'credit'
    """)
    credit_count = cursor.fetchone()[0]

    # Linked liabilities
    cursor.execute("""
        SELECT COUNT(*) FROM liabilities
        WHERE liability_type = 'credit_card' AND account_id IS NOT NULL
    """)
    linked_liabilities = cursor.fetchone()[0]

    # Savings accounts
    cursor.execute("""
        SELECT COUNT(*) FROM accounts WHERE subtype = 'savings'
    """)
    savings_count = cursor.fetchone()[0]

    print(f"💳 Credit Cards: {credit_count} accounts")
    print(f"🔗 Linked Liabilities: {linked_liabilities} records")
    print(f"💰 Savings Accounts: {savings_count} accounts")

    # Sample credit card with liability
    print("\n📋 Sample Credit Card (with liability):")
    cursor.execute("""
        SELECT
            a.account_id, a.user_id, a.balance_current, a.balance_limit,
            l.liability_type, l.interest_rate, l.minimum_payment_amount
        FROM accounts a
        JOIN liabilities l ON a.account_id = l.account_id
        WHERE a.type = 'credit'
        LIMIT 1
    """)

    row = cursor.fetchone()
    if row:
        print(f"  Account: {row[0]}")
        print(f"  User: {row[1]}")
        print(f"  Balance: ${row[2]:,.2f} / ${row[3]:,.2f} limit")
        print(f"  Liability Type: {row[4]}")
        print(f"  APR: {row[5]:.2f}%")
        print(f"  Min Payment: ${row[6]:,.2f}")

    # Sample savings account
    print("\n💰 Sample Savings Account:")
    cursor.execute("""
        SELECT
            a.account_id, a.user_id, a.balance_current,
            u.persona, u.annual_income
        FROM accounts a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.subtype = 'savings'
        LIMIT 1
    """)

    row = cursor.fetchone()
    if row:
        print(f"  Account: {row[0]}")
        print(f"  User: {row[1]} (persona: {row[3]})")
        print(f"  Balance: ${row[2]:,.2f}")
        print(f"  Annual Income: ${row[4]:,.2f}")
        print(f"  Emergency Fund: {(row[2] / (row[4] * 0.7 / 12)):.1f} months")

    conn.close()


if __name__ == '__main__':
    db_path = 'data/processed/spendsense.db'

    if not Path(db_path).exists():
        print(f"Error: Database not found at {db_path}")
        exit(1)

    print("🔧 Fixing Credit and Savings Detection\n")
    print("=" * 60)

    # Fix credit
    fix_credit_liabilities(db_path)

    # Add savings
    add_savings_accounts(db_path)

    # Show summary
    show_summary(db_path)

    print("\n" + "=" * 60)
    print("✅ All fixes complete!")
    print("\nNext steps:")
    print("1. Restart the server:")
    print("   pkill -9 -f uvicorn")
    print("   python -m uvicorn spendsense.api.main:app --host 127.0.0.1 --port 8000 --reload &")
    print("\n2. Test in UI:")
    print("   - user_MASKED_000 should show credit utilization")
    print("   - user_MASKED_003 should show savings balance")
