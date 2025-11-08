"""
Validate synthetic data against PRD requirements.

Requirements:
1. 50-100 synthetic users
2. Transaction structure with all required fields
3. Sufficient signals for pattern detection:
   - Recurring merchants (≥3 in 90 days)
   - Minimum-payment detection
   - Payroll ACH detection
   - Payment frequency/variability
"""

import sqlite3
from datetime import date, timedelta
from collections import defaultdict, Counter


def validate_user_count(cursor):
    """Validate user count requirement (50-100 users)."""
    print("=" * 80)
    print("REQUIREMENT 1: USER COUNT (50-100 users)")
    print("=" * 80)

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]

    print(f"\n✓ Total users: {user_count}")

    if 50 <= user_count <= 100:
        print(f"✅ PASS: User count {user_count} is within required range (50-100)")
        return True
    else:
        print(f"❌ FAIL: User count {user_count} outside required range (50-100)")
        return False


def validate_transaction_structure(cursor):
    """Validate transaction structure has all required fields."""
    print("\n\n" + "=" * 80)
    print("REQUIREMENT 2: TRANSACTION STRUCTURE")
    print("=" * 80)

    required_fields = [
        'account_id',
        'date',
        'amount',
        'merchant_name',  # OR merchant_entity_id
        'merchant_entity_id',
        'payment_channel',
        'personal_finance_category'
    ]

    # Get actual schema
    cursor.execute("PRAGMA table_info(transactions)")
    schema = cursor.fetchall()
    actual_fields = {row[1] for row in schema}

    print(f"\n📋 Required fields:")
    all_present = True
    for field in required_fields:
        if field in actual_fields:
            print(f"  ✅ {field}")
        else:
            # Check if it's merchant_name OR merchant_entity_id
            if field == 'merchant_name' and 'merchant_entity_id' in actual_fields:
                print(f"  ✅ {field} (merchant_entity_id present instead)")
            elif field == 'merchant_entity_id' and 'merchant_name' in actual_fields:
                print(f"  ✅ {field} (merchant_name present instead)")
            else:
                print(f"  ❌ {field} MISSING")
                all_present = False

    # Check for data completeness
    print(f"\n📊 Data Completeness:")
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total = cursor.fetchone()[0]

    for field in ['account_id', 'date', 'amount', 'merchant_name', 'payment_channel', 'personal_finance_category']:
        if field in actual_fields:
            cursor.execute(f"SELECT COUNT(*) FROM transactions WHERE {field} IS NOT NULL")
            count = cursor.fetchone()[0]
            pct = (count / total) * 100
            status = "✅" if pct >= 95 else "⚠️" if pct >= 80 else "❌"
            print(f"  {status} {field}: {count:,}/{total:,} ({pct:.1f}%)")

    if all_present:
        print(f"\n✅ PASS: All required fields present")
        return True
    else:
        print(f"\n❌ FAIL: Missing required fields")
        return False


def validate_recurring_merchants(cursor):
    """Validate recurring merchant detection (≥3 occurrences in 90 days)."""
    print("\n\n" + "=" * 80)
    print("REQUIREMENT 3a: RECURRING MERCHANTS (≥3 in 90 days)")
    print("=" * 80)

    # For each user, check if they have recurring merchants
    cursor.execute("""
        SELECT a.user_id, COUNT(DISTINCT a.user_id) as user_count
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        GROUP BY a.user_id
    """)

    total_users = cursor.fetchone()[0]

    # Check recurring patterns using subscription detector logic
    # Use 90-day window from most recent date
    cursor.execute("SELECT MAX(date) FROM transactions")
    max_date = cursor.fetchone()[0]

    if not max_date:
        print("❌ FAIL: No transactions found")
        return False

    # Count users with recurring merchants (≥3 transactions, regular cadence)
    users_with_recurring = 0
    users_without_recurring = []

    cursor.execute("SELECT DISTINCT user_id FROM users ORDER BY user_id")
    all_users = [row[0] for row in cursor.fetchall()]

    for user_id in all_users:
        cursor.execute("""
            SELECT
                t.merchant_name,
                COUNT(*) as tx_count,
                COUNT(DISTINCT t.date) as unique_days
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = ?
              AND t.date >= date(?, '-90 days')
              AND t.merchant_name IS NOT NULL
            GROUP BY t.merchant_name
            HAVING COUNT(*) >= 3
            ORDER BY COUNT(*) DESC
        """, (user_id, max_date))

        recurring_merchants = cursor.fetchall()

        if recurring_merchants:
            users_with_recurring += 1
        else:
            users_without_recurring.append(user_id)

    pct = (users_with_recurring / len(all_users)) * 100

    print(f"\n📊 Recurring Merchant Analysis:")
    print(f"  Total users: {len(all_users)}")
    print(f"  Users with recurring merchants (≥3 tx in 90d): {users_with_recurring} ({pct:.1f}%)")

    # Sample some users
    print(f"\n📋 Sample Users with Recurring Merchants:")
    cursor.execute("""
        SELECT
            a.user_id,
            t.merchant_name,
            COUNT(*) as tx_count
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.date >= date(?, '-90 days')
          AND t.merchant_name IS NOT NULL
        GROUP BY a.user_id, t.merchant_name
        HAVING COUNT(*) >= 3
        ORDER BY a.user_id, COUNT(*) DESC
        LIMIT 15
    """, (max_date,))

    for user_id, merchant, count in cursor.fetchall()[:15]:
        print(f"  {user_id}: {merchant} ({count} transactions)")

    # Check if at least 80% of users have recurring merchants
    if pct >= 80:
        print(f"\n✅ PASS: {pct:.1f}% of users have recurring merchants (≥80% threshold)")
        return True
    else:
        print(f"\n⚠️  WARNING: Only {pct:.1f}% of users have recurring merchants")
        print(f"  Users without recurring: {users_without_recurring[:10]}")
        if pct >= 50:
            print(f"  ✅ ACCEPTABLE: Above 50% threshold")
            return True
        else:
            print(f"  ❌ FAIL: Below 50% threshold")
            return False


def validate_payment_detection(cursor):
    """Validate minimum payment and payroll detection."""
    print("\n\n" + "=" * 80)
    print("REQUIREMENT 3b: PAYMENT DETECTION")
    print("=" * 80)

    # Check for credit card data (minimum payment detection)
    print(f"\n💳 Minimum Payment Detection:")
    cursor.execute("""
        SELECT COUNT(DISTINCT l.account_id)
        FROM liabilities l
        WHERE l.liability_type = 'credit_card'
          AND l.minimum_payment_amount IS NOT NULL
          AND l.last_payment_amount IS NOT NULL
    """)
    cc_with_payments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM accounts WHERE type = 'credit'")
    total_cc = cursor.fetchone()[0]

    if total_cc > 0:
        pct = (cc_with_payments / total_cc) * 100
        print(f"  Credit cards: {total_cc}")
        print(f"  With payment data: {cc_with_payments} ({pct:.1f}%)")

        if pct >= 80:
            print(f"  ✅ PASS: {pct:.1f}% have payment data")
            payment_pass = True
        else:
            print(f"  ⚠️  WARNING: Only {pct:.1f}% have payment data")
            payment_pass = False
    else:
        print(f"  ❌ No credit cards found")
        payment_pass = False

    # Check for payroll/income transactions
    print(f"\n💰 Payroll Detection:")
    cursor.execute("""
        SELECT COUNT(DISTINCT a.user_id)
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.personal_finance_category LIKE '%INCOME%'
           OR t.merchant_name LIKE '%Payroll%'
           OR t.merchant_name LIKE '%ADP%'
           OR t.amount > 1000
    """)
    users_with_income = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    pct = (users_with_income / total_users) * 100
    print(f"  Total users: {total_users}")
    print(f"  Users with income transactions: {users_with_income} ({pct:.1f}%)")

    # Check for regular payroll cadence
    cursor.execute("""
        SELECT
            a.user_id,
            COUNT(*) as income_count,
            MIN(t.date) as first_income,
            MAX(t.date) as last_income
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        WHERE t.personal_finance_category LIKE '%INCOME%'
           OR t.merchant_name LIKE '%Payroll%'
        GROUP BY a.user_id
        HAVING COUNT(*) >= 3
    """)

    users_with_regular_income = len(cursor.fetchall())
    regular_pct = (users_with_regular_income / total_users) * 100

    print(f"  Users with ≥3 income transactions: {users_with_regular_income} ({regular_pct:.1f}%)")

    if regular_pct >= 60:
        print(f"  ✅ PASS: {regular_pct:.1f}% have regular income patterns")
        payroll_pass = True
    else:
        print(f"  ⚠️  WARNING: Only {regular_pct:.1f}% have regular income")
        payroll_pass = False

    return payment_pass and payroll_pass


def validate_frequency_variability(cursor):
    """Validate payment frequency and variability detection."""
    print("\n\n" + "=" * 80)
    print("REQUIREMENT 3c: FREQUENCY & VARIABILITY")
    print("=" * 80)

    # Check transaction frequency per user
    print(f"\n📅 Transaction Frequency:")
    cursor.execute("""
        SELECT
            a.user_id,
            COUNT(*) as tx_count,
            MIN(t.date) as first_tx,
            MAX(t.date) as last_tx,
            JULIANDAY(MAX(t.date)) - JULIANDAY(MIN(t.date)) as days_span
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        GROUP BY a.user_id
    """)

    frequencies = []
    for user_id, tx_count, first_tx, last_tx, days_span in cursor.fetchall():
        if days_span > 0:
            freq = tx_count / (days_span / 30)  # transactions per month
            frequencies.append(freq)

    if frequencies:
        avg_freq = sum(frequencies) / len(frequencies)
        min_freq = min(frequencies)
        max_freq = max(frequencies)

        print(f"  Average: {avg_freq:.1f} transactions/month")
        print(f"  Min: {min_freq:.1f} transactions/month")
        print(f"  Max: {max_freq:.1f} transactions/month")

        # Check if frequencies are reasonable (10-50 tx/month typical)
        if 10 <= avg_freq <= 100:
            print(f"  ✅ PASS: Frequency within reasonable range")
            freq_pass = True
        else:
            print(f"  ⚠️  WARNING: Frequency outside typical range (10-100 tx/month)")
            freq_pass = False
    else:
        print(f"  ❌ FAIL: No frequency data")
        freq_pass = False

    # Check amount variability
    print(f"\n💵 Amount Variability:")
    cursor.execute("""
        SELECT
            a.user_id,
            AVG(ABS(t.amount)) as avg_amount,
            MIN(ABS(t.amount)) as min_amount,
            MAX(ABS(t.amount)) as max_amount
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        GROUP BY a.user_id
    """)

    variabilities = []
    for user_id, avg_amt, min_amt, max_amt in cursor.fetchall():
        if avg_amt > 0:
            variability = (max_amt - min_amt) / avg_amt
            variabilities.append(variability)

    if variabilities:
        avg_variability = sum(variabilities) / len(variabilities)
        print(f"  Average variability ratio: {avg_variability:.2f}")

        if avg_variability > 2:
            print(f"  ✅ PASS: Sufficient amount variability")
            var_pass = True
        else:
            print(f"  ⚠️  WARNING: Low amount variability")
            var_pass = False
    else:
        print(f"  ❌ FAIL: No variability data")
        var_pass = False

    return freq_pass and var_pass


def validate_window_coverage(cursor):
    """Validate data covers 30-day and 180-day windows."""
    print("\n\n" + "=" * 80)
    print("REQUIREMENT 3d: WINDOW COVERAGE (30d & 180d)")
    print("=" * 80)

    cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
    min_date, max_date = cursor.fetchone()

    if not min_date or not max_date:
        print("❌ FAIL: No date data")
        return False

    from datetime import datetime
    start = datetime.strptime(min_date, '%Y-%m-%d')
    end = datetime.strptime(max_date, '%Y-%m-%d')
    span_days = (end - start).days

    print(f"\n📅 Date Range:")
    print(f"  Start: {min_date}")
    print(f"  End: {max_date}")
    print(f"  Span: {span_days} days")

    # Check 30-day window
    if span_days >= 30:
        print(f"  ✅ 30-day window: COVERED")
        window_30_pass = True
    else:
        print(f"  ❌ 30-day window: NOT COVERED (only {span_days} days)")
        window_30_pass = False

    # Check 180-day window
    if span_days >= 180:
        print(f"  ✅ 180-day window: COVERED")
        window_180_pass = True
    else:
        print(f"  ⚠️  180-day window: Partial ({span_days} days)")
        window_180_pass = False

    # Check transaction distribution across time
    cursor.execute("""
        SELECT
            CAST((JULIANDAY(date) - JULIANDAY(?)) / 30 AS INTEGER) as month_bucket,
            COUNT(*) as tx_count
        FROM transactions
        GROUP BY month_bucket
        ORDER BY month_bucket
    """, (min_date,))

    print(f"\n📊 Transaction Distribution by Month:")
    month_counts = cursor.fetchall()
    for month, count in month_counts:
        print(f"  Month {month}: {count:,} transactions")

    # Check if transactions are reasonably distributed
    counts = [count for _, count in month_counts]
    if counts:
        avg_count = sum(counts) / len(counts)
        min_count = min(counts)
        max_count = max(counts)

        # Check if no month is too sparse (at least 50% of average)
        if min_count >= avg_count * 0.5:
            print(f"  ✅ PASS: Transactions reasonably distributed")
            distribution_pass = True
        else:
            print(f"  ⚠️  WARNING: Some months have sparse data")
            distribution_pass = False
    else:
        distribution_pass = False

    return window_30_pass and window_180_pass and distribution_pass


def generate_summary(results):
    """Generate final summary of validation."""
    print("\n\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    print(f"\n📋 Requirement Validation Results:")

    total = len(results)
    passed = sum(results.values())

    for req, status in results.items():
        icon = "✅" if status else "❌"
        print(f"  {icon} {req}")

    pct = (passed / total) * 100
    print(f"\n📊 Overall: {passed}/{total} requirements satisfied ({pct:.0f}%)")

    if passed == total:
        print(f"\n🎉 ✅ ALL REQUIREMENTS SATISFIED")
        print(f"   Synthetic data is ready for Epic 2 behavioral signal detection!")
    elif pct >= 80:
        print(f"\n✅ MOSTLY SATISFIED ({pct:.0f}%)")
        print(f"   Synthetic data is sufficient for Epic 2 with minor gaps.")
    elif pct >= 60:
        print(f"\n⚠️  PARTIALLY SATISFIED ({pct:.0f}%)")
        print(f"   Some requirements need attention.")
    else:
        print(f"\n❌ INSUFFICIENT ({pct:.0f}%)")
        print(f"   Multiple requirements not met.")


if __name__ == '__main__':
    db_path = 'data/processed/spendsense.db'

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    results = {
        "1. User Count (50-100)": validate_user_count(cursor),
        "2. Transaction Structure": validate_transaction_structure(cursor),
        "3a. Recurring Merchants": validate_recurring_merchants(cursor),
        "3b. Payment Detection": validate_payment_detection(cursor),
        "3c. Frequency & Variability": validate_frequency_variability(cursor),
        "3d. Window Coverage (30d/180d)": validate_window_coverage(cursor),
    }

    generate_summary(results)

    conn.close()

    print("\n" + "=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
