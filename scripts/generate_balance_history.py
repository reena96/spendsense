"""
Generate historical balance snapshots for savings growth rate calculation.

Creates a new table 'balance_snapshots' with daily/weekly balance history
for the 180-day window, allowing us to calculate:
- Savings growth rate
- Net inflow/outflow
- Credit utilization trends over time

Strategy:
1. For savings accounts: Generate growth patterns based on persona
2. For checking accounts: Fluctuate based on transactions
3. For credit accounts: Show utilization changes over time
"""

import sqlite3
from datetime import datetime, timedelta, date
import random


def create_balance_snapshots_table(cursor):
    """Create table for historical balance data."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id VARCHAR NOT NULL,
            snapshot_date DATE NOT NULL,
            balance FLOAT NOT NULL,
            UNIQUE(account_id, snapshot_date)
        )
    """)

    # Create index for fast queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_balance_snapshots_account_date
        ON balance_snapshots(account_id, snapshot_date)
    """)


def generate_savings_history(cursor, account_id, user_id, persona, current_balance, start_date, end_date):
    """Generate realistic savings balance history."""

    # Savings growth patterns by persona
    monthly_contribution = {
        'savings_builder': current_balance * 0.03,  # 3% per month contribution
        'control': current_balance * 0.015,         # 1.5% per month
        'subscription_heavy': current_balance * 0.01, # 1% per month
        'variable_income': current_balance * 0.005,   # 0.5% per month (irregular)
        'high_utilization': current_balance * 0.002   # 0.2% per month (minimal)
    }

    # Get monthly contribution rate
    contribution = monthly_contribution.get(persona, current_balance * 0.01)

    # Calculate starting balance (work backwards from current)
    days_total = (end_date - start_date).days
    months_total = days_total / 30
    total_growth = contribution * months_total
    starting_balance = max(100, current_balance - total_growth)

    # Generate weekly snapshots (26 snapshots over 180 days)
    snapshots = []
    current_date = start_date
    balance = starting_balance

    while current_date <= end_date:
        # Add weekly contribution with some randomness
        if persona == 'variable_income':
            # Irregular contributions
            if random.random() < 0.6:  # 60% chance of contribution
                weekly_contrib = contribution / 4 * random.uniform(0.5, 2.0)
            else:
                weekly_contrib = 0
        else:
            # Regular contributions with slight variance
            weekly_contrib = (contribution / 4) * random.uniform(0.8, 1.2)

        balance += weekly_contrib

        # Occasional withdrawals for non-savings-builder personas
        if persona != 'savings_builder' and random.random() < 0.1:  # 10% chance
            withdrawal = balance * random.uniform(0.05, 0.15)  # 5-15% withdrawal
            balance -= withdrawal

        balance = max(100, balance)  # Never go below $100

        snapshots.append((account_id, current_date.strftime('%Y-%m-%d'), round(balance, 2)))

        current_date += timedelta(days=7)  # Weekly snapshots

    # Add final snapshot at exact end_date with current balance
    snapshots.append((account_id, end_date.strftime('%Y-%m-%d'), current_balance))

    return snapshots


def generate_credit_history(cursor, account_id, user_id, persona, current_balance, limit, start_date, end_date):
    """Generate realistic credit card balance history."""

    # Utilization patterns by persona
    utilization_volatility = {
        'high_utilization': 0.05,    # Low volatility (always high)
        'variable_income': 0.15,     # High volatility (irregular payments)
        'subscription_heavy': 0.08,  # Medium volatility
        'control': 0.10,             # Medium volatility
        'savings_builder': 0.12      # Higher volatility (pay off monthly)
    }

    volatility = utilization_volatility.get(persona, 0.10)
    current_utilization = current_balance / limit if limit > 0 else 0

    # Generate weekly snapshots
    snapshots = []
    current_date = start_date

    # Start at similar utilization (work backwards)
    starting_utilization = current_utilization * random.uniform(0.85, 1.15)
    starting_utilization = max(0.1, min(0.95, starting_utilization))
    balance = starting_utilization * limit

    while current_date <= end_date:
        # Random walk with mean reversion to current utilization
        change = random.gauss(0, volatility * limit)

        # Mean reversion factor (pulls toward current balance)
        days_to_end = (end_date - current_date).days
        if days_to_end > 0:
            reversion = (current_balance - balance) / days_to_end * 7  # Weekly reversion
            change += reversion * 0.3  # 30% reversion strength

        balance += change

        # Keep within realistic bounds
        balance = max(0, min(limit * 0.98, balance))  # Don't exceed 98% utilization

        snapshots.append((account_id, current_date.strftime('%Y-%m-%d'), round(balance, 2)))

        current_date += timedelta(days=7)

    # Add final snapshot with exact current balance
    snapshots.append((account_id, end_date.strftime('%Y-%m-%d'), current_balance))

    return snapshots


def generate_checking_history(cursor, account_id, user_id, persona, current_balance, start_date, end_date):
    """Generate realistic checking account balance history."""

    # Checking accounts fluctuate more based on paychecks and expenses
    # Simplified: maintain average balance with biweekly paycheck bumps

    snapshots = []
    current_date = start_date

    # Average balance stays roughly constant
    avg_balance = current_balance
    balance = avg_balance * random.uniform(0.8, 1.2)

    days_elapsed = 0
    while current_date <= end_date:
        # Biweekly paycheck (every 14 days)
        if days_elapsed % 14 == 0 and days_elapsed > 0:
            paycheck = avg_balance * 0.3  # Paycheck is ~30% of balance
            balance += paycheck

        # Daily spending
        daily_spend = avg_balance * 0.015  # 1.5% of balance per day
        balance -= daily_spend * random.uniform(0.5, 1.5)

        # Keep reasonable bounds
        balance = max(100, min(avg_balance * 2, balance))

        # Weekly snapshots
        if days_elapsed % 7 == 0:
            snapshots.append((account_id, current_date.strftime('%Y-%m-%d'), round(balance, 2)))

        current_date += timedelta(days=1)
        days_elapsed += 1

    # Add final snapshot with exact current balance
    snapshots.append((account_id, end_date.strftime('%Y-%m-%d'), current_balance))

    return snapshots


def generate_all_balance_history(db_path):
    """Generate balance history for all accounts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 80)
    print("GENERATING HISTORICAL BALANCE SNAPSHOTS")
    print("=" * 80)

    # Create table
    create_balance_snapshots_table(cursor)

    # Clear existing data
    cursor.execute("DELETE FROM balance_snapshots")
    conn.commit()

    # Get date range from transactions
    cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
    start_date_str, end_date_str = cursor.fetchone()

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    print(f"\n📅 Date Range: {start_date} to {end_date} ({(end_date - start_date).days} days)")

    # Get all accounts with user persona
    cursor.execute("""
        SELECT
            a.account_id,
            a.user_id,
            a.type,
            a.subtype,
            a.balance_current,
            a.balance_limit,
            u.persona
        FROM accounts a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.balance_current IS NOT NULL
        ORDER BY a.account_id
    """)

    accounts = cursor.fetchall()
    print(f"\n📊 Processing {len(accounts)} accounts...")

    all_snapshots = []
    savings_count = 0
    checking_count = 0
    credit_count = 0

    for account_id, user_id, acc_type, subtype, balance, limit, persona in accounts:
        if subtype == 'savings':
            snapshots = generate_savings_history(
                cursor, account_id, user_id, persona, balance, start_date, end_date
            )
            savings_count += 1
        elif subtype == 'checking':
            snapshots = generate_checking_history(
                cursor, account_id, user_id, persona, balance, start_date, end_date
            )
            checking_count += 1
        elif acc_type == 'credit':
            snapshots = generate_credit_history(
                cursor, account_id, user_id, persona, balance, limit, start_date, end_date
            )
            credit_count += 1
        else:
            # Other account types: simple constant balance
            snapshots = [(account_id, end_date.strftime('%Y-%m-%d'), balance)]

        all_snapshots.extend(snapshots)

    # Bulk insert
    print(f"\n💾 Inserting {len(all_snapshots):,} snapshots...")
    cursor.executemany("""
        INSERT OR REPLACE INTO balance_snapshots (account_id, snapshot_date, balance)
        VALUES (?, ?, ?)
    """, all_snapshots)

    conn.commit()

    print(f"\n✅ Balance history generated:")
    print(f"   Savings accounts: {savings_count} accounts")
    print(f"   Checking accounts: {checking_count} accounts")
    print(f"   Credit accounts: {credit_count} accounts")
    print(f"   Total snapshots: {len(all_snapshots):,}")

    # Show sample
    print(f"\n📋 Sample Balance History (user_MASKED_003 savings):")
    cursor.execute("""
        SELECT snapshot_date, balance
        FROM balance_snapshots
        WHERE account_id LIKE '%user_MASKED_003%savings%'
        ORDER BY snapshot_date
        LIMIT 8
    """)

    for snapshot_date, balance in cursor.fetchall():
        print(f"   {snapshot_date}: ${balance:,.2f}")

    # Verify growth calculation
    cursor.execute("""
        SELECT
            account_id,
            MIN(balance) as start_balance,
            MAX(balance) as end_balance,
            MAX(balance) - MIN(balance) as growth,
            ROUND(100.0 * (MAX(balance) - MIN(balance)) / MIN(balance), 2) as growth_pct
        FROM balance_snapshots
        WHERE account_id LIKE '%savings%'
        GROUP BY account_id
        LIMIT 5
    """)

    print(f"\n📈 Savings Growth Examples:")
    for account_id, start, end, growth, growth_pct in cursor.fetchall():
        print(f"   {account_id}: ${start:,.0f} → ${end:,.0f} (+${growth:,.0f}, {growth_pct}%)")

    conn.close()


if __name__ == '__main__':
    db_path = 'data/processed/spendsense.db'

    print("🔧 Generating Historical Balance Snapshots\n")

    generate_all_balance_history(db_path)

    print("\n" + "=" * 80)
    print("✅ Balance history complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Update savings_detector.py to use balance_snapshots table")
    print("2. Update credit_detector.py to calculate utilization trends")
    print("3. Restart server to pick up new data")
    print("4. Test growth rate calculations")
