"""
Populate the accounts table from existing transaction account_ids.

This script extracts unique account_ids from transactions and creates
corresponding account records with appropriate types and metadata.
"""

import sqlite3
import re
from pathlib import Path


def extract_account_info(account_id: str) -> dict:
    """
    Extract user_id, account type, and subtype from account_id format.

    Format: acc_{user_id}_{type}_{index}
    Examples:
        - acc_user_MASKED_000_checking_0 -> user_MASKED_000, depository, checking
        - acc_user_MASKED_000_credit_0 -> user_MASKED_000, credit, credit_card
    """
    # Parse account_id: acc_{user_id}_{account_type}_{index}
    pattern = r'acc_(user_MASKED_\d+)_(\w+)_(\d+)'
    match = re.match(pattern, account_id)

    if not match:
        raise ValueError(f"Invalid account_id format: {account_id}")

    user_id = match.group(1)
    account_subtype = match.group(2)  # checking, credit, savings, etc.
    index = match.group(3)

    # Map subtypes to Plaid account types
    type_mapping = {
        'checking': ('depository', 'checking'),
        'savings': ('depository', 'savings'),
        'credit': ('credit', 'credit_card'),
        'money_market': ('depository', 'money_market'),
        'cd': ('depository', 'cd'),
        'hsa': ('depository', 'hsa'),
    }

    if account_subtype not in type_mapping:
        # Default to depository/other
        account_type = 'depository'
        account_subtype_clean = account_subtype
    else:
        account_type, account_subtype_clean = type_mapping[account_subtype]

    return {
        'account_id': account_id,
        'user_id': user_id,
        'type': account_type,
        'subtype': account_subtype_clean,
        'index': index
    }


def calculate_balances(conn, account_id: str, account_type: str) -> dict:
    """
    Calculate account balances from transaction history.

    For credit cards: sum of positive amounts (charges)
    For depository: sum of all transaction amounts from starting balance
    """
    cursor = conn.cursor()

    # Get all transactions for this account
    cursor.execute("""
        SELECT SUM(amount) as total_spent, COUNT(*) as tx_count
        FROM transactions
        WHERE account_id = ?
    """, (account_id,))

    result = cursor.fetchone()
    total_spent = result[0] or 0.0
    tx_count = result[1] or 0

    if account_type == 'credit':
        # Credit card: positive balance = amount owed
        # Assume average utilization based on total charges
        balance_current = abs(total_spent) if total_spent < 0 else total_spent

        # Estimate credit limit based on charges (assume 50-80% utilization)
        if balance_current > 0:
            balance_limit = round(balance_current / 0.65, 2)  # Assume 65% util on average
        else:
            balance_limit = 10000.0  # Default $10k limit

        balance_available = balance_limit - balance_current

    else:
        # Depository account: estimate balance from income/spend patterns
        # For checking: start with reasonable balance
        # Net flow = income - expenses

        # Get income transactions
        cursor.execute("""
            SELECT SUM(amount) as total_income
            FROM transactions
            WHERE account_id = ?
            AND personal_finance_category LIKE 'INCOME%'
        """, (account_id,))

        total_income = cursor.fetchone()[0] or 0.0

        # Simplified: balance = income - total_spent + starting balance estimate
        starting_balance = 5000.0  # Assume $5k starting balance
        balance_current = starting_balance + abs(total_income) - abs(total_spent)

        # Keep realistic minimum
        if balance_current < 0:
            balance_current = max(500.0, total_income * 0.1)  # At least 10% of income

        balance_available = balance_current
        balance_limit = None

    return {
        'balance_current': round(balance_current, 2),
        'balance_available': round(balance_available, 2),
        'balance_limit': round(balance_limit, 2) if balance_limit else None
    }


def populate_accounts_table(db_path: str):
    """
    Populate accounts table from transaction account_ids.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Fetching unique account_ids from transactions...")
    cursor.execute("SELECT DISTINCT account_id FROM transactions ORDER BY account_id")
    account_ids = [row[0] for row in cursor.fetchall()]

    print(f"Found {len(account_ids)} unique accounts")

    # Check if accounts table already has data
    cursor.execute("SELECT COUNT(*) FROM accounts")
    existing_count = cursor.fetchone()[0]

    if existing_count > 0:
        print(f"Warning: accounts table already has {existing_count} records")
        response = input("Do you want to DELETE existing accounts and repopulate? (yes/no): ")
        if response.lower() == 'yes':
            cursor.execute("DELETE FROM accounts")
            conn.commit()
            print("Deleted existing accounts")
        else:
            print("Aborted - no changes made")
            conn.close()
            return

    print("\nPopulating accounts table...")
    inserted = 0

    for account_id in account_ids:
        try:
            # Extract account metadata
            info = extract_account_info(account_id)

            # Calculate balances
            balances = calculate_balances(conn, account_id, info['type'])

            # Insert account record
            cursor.execute("""
                INSERT INTO accounts (
                    account_id, user_id, type, subtype,
                    iso_currency_code, holder_category,
                    balance_current, balance_available, balance_limit
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                info['account_id'],
                info['user_id'],
                info['type'],
                info['subtype'],
                'USD',
                'personal',
                balances['balance_current'],
                balances['balance_available'],
                balances['balance_limit']
            ))

            inserted += 1

            if inserted % 20 == 0:
                print(f"  Inserted {inserted}/{len(account_ids)} accounts...")

        except Exception as e:
            print(f"Error processing {account_id}: {e}")
            continue

    conn.commit()
    print(f"\n✅ Successfully inserted {inserted} accounts")

    # Verify the data
    print("\n📊 Account Summary:")
    cursor.execute("""
        SELECT type, subtype, COUNT(*) as count
        FROM accounts
        GROUP BY type, subtype
        ORDER BY type, subtype
    """)

    for row in cursor.fetchall():
        print(f"  {row[0]}/{row[1]}: {row[2]} accounts")

    # Sample accounts
    print("\n🔍 Sample accounts:")
    cursor.execute("""
        SELECT account_id, user_id, type, subtype, balance_current, balance_limit
        FROM accounts
        LIMIT 5
    """)

    for row in cursor.fetchall():
        acc_id, user_id, acc_type, subtype, bal_curr, bal_lim = row
        limit_str = f", limit=${bal_lim:.2f}" if bal_lim else ""
        print(f"  {acc_id[:30]:30} | {user_id:18} | {acc_type:10}/{subtype:12} | ${bal_curr:.2f}{limit_str}")

    conn.close()
    print("\n✅ Done! Accounts table populated successfully.")


if __name__ == '__main__':
    db_path = 'data/processed/spendsense.db'

    if not Path(db_path).exists():
        print(f"Error: Database not found at {db_path}")
        exit(1)

    populate_accounts_table(db_path)
