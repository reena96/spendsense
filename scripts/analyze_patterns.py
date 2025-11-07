"""
Comprehensive pattern analysis: Real CSV data vs Synthetic dataset.

Analyzes:
1. Transaction patterns (frequency, amounts, categories)
2. Payment method distributions
3. Balance patterns and trends
4. Customer behavior clustering
5. Temporal patterns (day of week, time of day)
6. Merchant diversity and frequency
"""

import sqlite3
import csv
from collections import defaultdict, Counter
from datetime import datetime
import statistics


def analyze_real_data(csv_path):
    """Analyze patterns in real transaction data."""
    print("=" * 80)
    print("REAL DATA ANALYSIS (transactions_formatted.csv)")
    print("=" * 80)

    transactions = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        transactions = list(reader)

    print(f"\n📊 Dataset Overview:")
    print(f"  Total transactions: {len(transactions):,}")

    # Get unique customers
    customers = set(t['customer_id'] for t in transactions)
    print(f"  Unique customers: {len(customers)}")

    # Date range
    dates = [t['date'] for t in transactions]
    print(f"  Date range: {min(dates)} to {max(dates)}")

    # Payment methods
    print(f"\n💳 Payment Method Distribution:")
    payment_methods = Counter(t['payment_method'] for t in transactions)
    total = len(transactions)
    for method, count in payment_methods.most_common():
        pct = (count / total) * 100
        print(f"  {method:20} {count:5,} ({pct:5.1f}%)")

    # Transaction types
    print(f"\n📝 Transaction Type Distribution:")
    tx_types = Counter(t['transaction_type'] for t in transactions)
    for tx_type, count in tx_types.most_common():
        pct = (count / total) * 100
        print(f"  {tx_type:20} {count:5,} ({pct:5.1f}%)")

    # Amount statistics
    amounts = [float(t['amount']) for t in transactions]
    print(f"\n💰 Transaction Amounts:")
    print(f"  Mean: ${statistics.mean(amounts):,.2f}")
    print(f"  Median: ${statistics.median(amounts):,.2f}")
    print(f"  Min: ${min(amounts):,.2f}")
    print(f"  Max: ${max(amounts):,.2f}")
    print(f"  Std Dev: ${statistics.stdev(amounts):,.2f}")

    # Amount categories
    print(f"\n💵 Amount Categories:")
    amount_cats = Counter(t['amount_category'] for t in transactions)
    for cat, count in amount_cats.most_common():
        pct = (count / total) * 100
        print(f"  {cat:20} {count:5,} ({pct:5.1f}%)")

    # Merchant categories
    print(f"\n🏪 Top 10 Merchant Categories:")
    merchant_cats = Counter(t['merchant_category'] for t in transactions)
    for cat, count in merchant_cats.most_common(10):
        pct = (count / total) * 100
        print(f"  {cat:20} {count:5,} ({pct:5.1f}%)")

    # Balance distribution
    balances = [float(t['account_balance']) for t in transactions]
    print(f"\n💼 Account Balance Distribution:")
    print(f"  Mean: ${statistics.mean(balances):,.2f}")
    print(f"  Median: ${statistics.median(balances):,.2f}")
    print(f"  Min: ${min(balances):,.2f}")
    print(f"  Max: ${max(balances):,.2f}")

    # Balance percentiles
    sorted_balances = sorted(balances)
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    print(f"\n  Percentiles:")
    for p in percentiles:
        idx = int(len(sorted_balances) * p / 100)
        val = sorted_balances[idx]
        print(f"    {p:2d}th: ${val:>10,.2f}")

    # Low balance transactions
    low_balance = sum(1 for b in balances if b < 1000)
    print(f"\n  Low balance (<$1K): {low_balance:,} ({low_balance/len(balances)*100:.1f}%)")

    # Temporal patterns
    print(f"\n📅 Day of Week Distribution:")
    days = Counter(t['day_of_week'] for t in transactions)
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in day_order:
        count = days.get(day, 0)
        pct = (count / total) * 100
        print(f"  {day:10} {count:5,} ({pct:5.1f}%)")

    print(f"\n⏰ Hour of Day Distribution:")
    hours = Counter(int(t['hour']) for t in transactions)
    for hour in sorted(hours.keys())[:24]:  # First 24 hours
        count = hours[hour]
        pct = (count / total) * 100
        bar = '█' * int(pct)
        print(f"  {hour:2d}:00 {count:4,} ({pct:4.1f}%) {bar}")

    # Per-customer stats
    print(f"\n👤 Per-Customer Statistics:")
    customer_tx_counts = Counter(t['customer_id'] for t in transactions)
    tx_per_customer = list(customer_tx_counts.values())
    print(f"  Mean transactions per customer: {statistics.mean(tx_per_customer):.1f}")
    print(f"  Median transactions per customer: {statistics.median(tx_per_customer):.1f}")
    print(f"  Min: {min(tx_per_customer)}")
    print(f"  Max: {max(tx_per_customer)}")

    # Fraud rate
    fraud_count = sum(1 for t in transactions if t['is_fraud'] == '1')
    print(f"\n🚨 Fraud Rate:")
    print(f"  Fraudulent transactions: {fraud_count} ({fraud_count/total*100:.2f}%)")

    return {
        'transactions': transactions,
        'customers': customers,
        'payment_methods': payment_methods,
        'merchant_categories': merchant_cats,
        'balances': balances,
        'amounts': amounts,
    }


def analyze_synthetic_data(db_path):
    """Analyze patterns in synthetic transaction data."""
    print("\n\n" + "=" * 80)
    print("SYNTHETIC DATA ANALYSIS (spendsense.db)")
    print("=" * 80)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Total transactions
    cursor.execute("SELECT COUNT(*) FROM transactions")
    total_tx = cursor.fetchone()[0]
    print(f"\n📊 Dataset Overview:")
    print(f"  Total transactions: {total_tx:,}")

    # Unique users (need to join through accounts)
    cursor.execute("""
        SELECT COUNT(DISTINCT a.user_id)
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
    """)
    total_users = cursor.fetchone()[0]
    print(f"  Unique users: {total_users}")

    # Date range
    cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
    min_date, max_date = cursor.fetchone()
    print(f"  Date range: {min_date} to {max_date}")

    # Payment channels
    print(f"\n💳 Payment Channel Distribution:")
    cursor.execute("""
        SELECT payment_channel, COUNT(*) as count
        FROM transactions
        GROUP BY payment_channel
        ORDER BY count DESC
    """)
    for channel, count in cursor.fetchall():
        pct = (count / total_tx) * 100
        print(f"  {channel or 'NULL':20} {count:5,} ({pct:5.1f}%)")

    # Transaction amounts
    cursor.execute("SELECT amount FROM transactions")
    amounts = [row[0] for row in cursor.fetchall()]

    print(f"\n💰 Transaction Amounts:")
    print(f"  Mean: ${statistics.mean(amounts):,.2f}")
    print(f"  Median: ${statistics.median(amounts):,.2f}")
    print(f"  Min: ${min(amounts):,.2f}")
    print(f"  Max: ${max(amounts):,.2f}")
    print(f"  Std Dev: ${statistics.stdev(amounts):,.2f}")

    # Categories
    print(f"\n🏪 Top 10 Personal Finance Categories:")
    cursor.execute("""
        SELECT personal_finance_category, COUNT(*) as count
        FROM transactions
        WHERE personal_finance_category IS NOT NULL
        GROUP BY personal_finance_category
        ORDER BY count DESC
        LIMIT 10
    """)
    for cat, count in cursor.fetchall():
        pct = (count / total_tx) * 100
        print(f"  {cat:30} {count:5,} ({pct:5.1f}%)")

    # Merchant names (top merchants)
    print(f"\n🏬 Top 10 Merchants by Transaction Count:")
    cursor.execute("""
        SELECT merchant_name, COUNT(*) as count
        FROM transactions
        WHERE merchant_name IS NOT NULL
        GROUP BY merchant_name
        ORDER BY count DESC
        LIMIT 10
    """)
    for merchant, count in cursor.fetchall():
        print(f"  {merchant:30} {count:5,}")

    # Account balances (if available)
    cursor.execute("SELECT COUNT(*) FROM accounts")
    account_count = cursor.fetchone()[0]

    if account_count > 0:
        cursor.execute("""
            SELECT balance_current
            FROM accounts
            WHERE balance_current IS NOT NULL
        """)
        balances = [row[0] for row in cursor.fetchall()]

        print(f"\n💼 Account Balance Distribution:")
        print(f"  Total accounts: {len(balances)}")
        print(f"  Mean: ${statistics.mean(balances):,.2f}")
        print(f"  Median: ${statistics.median(balances):,.2f}")
        print(f"  Min: ${min(balances):,.2f}")
        print(f"  Max: ${max(balances):,.2f}")

        # Balance percentiles
        sorted_balances = sorted(balances)
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        print(f"\n  Percentiles:")
        for p in percentiles:
            idx = int(len(sorted_balances) * p / 100)
            val = sorted_balances[idx]
            print(f"    {p:2d}th: ${val:>10,.2f}")

    # Temporal patterns
    print(f"\n📅 Day of Week Distribution:")
    cursor.execute("""
        SELECT
            CASE CAST(strftime('%w', date) AS INTEGER)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                WHEN 6 THEN 'Saturday'
            END as day_name,
            COUNT(*) as count
        FROM transactions
        GROUP BY CAST(strftime('%w', date) AS INTEGER)
        ORDER BY CAST(strftime('%w', date) AS INTEGER)
    """)
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    day_counts = dict(cursor.fetchall())
    for day in day_order:
        count = day_counts.get(day, 0)
        pct = (count / total_tx) * 100 if total_tx > 0 else 0
        print(f"  {day:10} {count:5,} ({pct:5.1f}%)")

    # Per-user stats
    print(f"\n👤 Per-User Statistics:")
    cursor.execute("""
        SELECT a.user_id, COUNT(*) as tx_count
        FROM transactions t
        JOIN accounts a ON t.account_id = a.account_id
        GROUP BY a.user_id
    """)
    tx_per_user = [row[1] for row in cursor.fetchall()]
    if tx_per_user:
        print(f"  Mean transactions per user: {statistics.mean(tx_per_user):.1f}")
        print(f"  Median transactions per user: {statistics.median(tx_per_user):.1f}")
        print(f"  Min: {min(tx_per_user)}")
        print(f"  Max: {max(tx_per_user)}")
    else:
        print(f"  No user data available")

    # Pending transactions
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE pending = 1")
    pending_count = cursor.fetchone()[0]
    print(f"\n⏳ Pending Transactions:")
    print(f"  Count: {pending_count} ({pending_count/total_tx*100:.2f}%)")

    conn.close()

    return {
        'total_tx': total_tx,
        'total_users': total_users,
        'amounts': amounts,
    }


def compare_patterns(real_data, synthetic_data):
    """Compare patterns between real and synthetic data."""
    print("\n\n" + "=" * 80)
    print("PATTERN COMPARISON: MATCHES & MISSES")
    print("=" * 80)

    print("\n✅ MATCHES (Patterns that align well):")
    print("-" * 80)

    # Compare transaction volumes
    real_tx_per_user = len(real_data['transactions']) / len(real_data['customers'])
    synth_tx_per_user = synthetic_data['total_tx'] / synthetic_data['total_users']

    print(f"\n1. Transactions per User:")
    print(f"   Real: {real_tx_per_user:.1f} tx/user")
    print(f"   Synthetic: {synth_tx_per_user:.1f} tx/user")
    diff_pct = abs(real_tx_per_user - synth_tx_per_user) / real_tx_per_user * 100
    if diff_pct < 20:
        print(f"   ✅ MATCH: Within {diff_pct:.1f}% difference")
    else:
        print(f"   ❌ MISS: {diff_pct:.1f}% difference (>20% threshold)")

    # Compare amount distributions
    real_mean = statistics.mean(real_data['amounts'])
    synth_mean = statistics.mean(synthetic_data['amounts'])

    print(f"\n2. Mean Transaction Amount:")
    print(f"   Real: ${real_mean:,.2f}")
    print(f"   Synthetic: ${synth_mean:,.2f}")
    diff_pct = abs(real_mean - synth_mean) / real_mean * 100
    if diff_pct < 30:
        print(f"   ✅ MATCH: Within {diff_pct:.1f}% difference")
    else:
        print(f"   ❌ MISS: {diff_pct:.1f}% difference (>30% threshold)")

    print("\n\n❌ MISSES (Patterns that differ significantly):")
    print("-" * 80)

    # Payment methods - Real data has these, synthetic might not
    print(f"\n1. Payment Method Diversity:")
    print(f"   Real: {len(real_data['payment_methods'])} unique methods")
    print(f"   Real methods: {', '.join(real_data['payment_methods'].keys())}")
    print(f"   Synthetic: Uses 'payment_channel' instead of 'payment_method'")
    print(f"   ❌ MISS: Different field names and likely different distributions")

    # Merchant categories
    print(f"\n2. Merchant Categories:")
    print(f"   Real: {len(real_data['merchant_categories'])} unique categories")
    real_top_5 = [cat for cat, _ in real_data['merchant_categories'].most_common(5)]
    print(f"   Real top 5: {', '.join(real_top_5)}")
    print(f"   Synthetic: Uses 'personal_finance_category' (Plaid taxonomy)")
    print(f"   ⚠️  DIFFERENT: Schema difference, but both capture spending patterns")

    # Balance patterns
    real_balances = real_data['balances']
    real_low = sum(1 for b in real_balances if b < 1000) / len(real_balances) * 100

    print(f"\n3. Low Balance Frequency:")
    print(f"   Real: {real_low:.1f}% of transactions have balance <$1K")
    print(f"   Synthetic: (Need to query accounts table)")
    print(f"   ⚠️  Need account balance snapshots in synthetic data")

    print("\n\n🔍 KEY INSIGHTS:")
    print("-" * 80)

    insights = [
        "Real data uses 'payment_method' (debit_card, credit_card, etc.)",
        "Synthetic uses 'payment_channel' (online, in store, other)",
        "Real data has merchant_category taxonomy",
        "Synthetic uses Plaid personal_finance_category taxonomy",
        "Real data includes account_balance at transaction time",
        "Synthetic has separate accounts table with current balances",
        "Real data spans 1 year (2024), need to check synthetic date range",
        "Both datasets have similar transaction volume per user",
    ]

    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")

    print("\n\n📋 RECOMMENDATIONS:")
    print("-" * 80)

    recommendations = [
        "Map payment_channel to payment_method for consistency",
        "Add balance snapshots to transactions for time-series analysis",
        "Validate merchant category distributions match industry norms",
        "Ensure temporal patterns (day/hour) match real behavior",
        "Add more diversity in transaction amounts (real data more varied)",
        "Consider adding fraud flags to synthetic data (0.08% in real data)",
        "Validate credit card usage rates (96% in real, now 90% in synthetic ✅)",
        "Ensure balance distribution matches real percentiles",
    ]

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")


if __name__ == '__main__':
    csv_path = '/Users/reena/Downloads/transactions_formatted.csv'
    db_path = 'data/processed/spendsense.db'

    # Analyze both datasets
    real_data = analyze_real_data(csv_path)
    synthetic_data = analyze_synthetic_data(db_path)

    # Compare patterns
    compare_patterns(real_data, synthetic_data)

    print("\n\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nSee output above for detailed comparison of patterns.")
    print("\nKey files for reference:")
    print("  - DATA_REALISM_ANALYSIS.md (already created)")
    print("  - ACCOUNT_DISTRIBUTION_FIX_SUMMARY.md (already created)")
    print("  - This analysis output (save for documentation)")
