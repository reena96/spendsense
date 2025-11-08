"""
Add realistic overdue accounts to credit cards.

Based on REAL transaction data analysis:
- Real data shows 6% declined transaction rate (275/5000 transactions)
- Declined transactions often indicate insufficient funds or credit issues
- This aligns with overdue/delinquent account behavior

Target: 5-6% overdue rate (matches real data patterns)

Persona-specific risk (aligned with real-world patterns):
- High utilization (20 users): 10% delinquent (maxed out cards, financial stress)
- Variable income (20 users): 8% delinquent (irregular cash flow)
- Subscription heavy (20 users): 5% delinquent (cash flow stress)
- Control (20 users): 4% delinquent (average)
- Savings builder (20 users): 1% delinquent (financial buffer)

Weighted average: ~5.6% overdue (matches real 6% decline rate)
"""

import sqlite3
import random


def add_overdue_accounts(db_path: str):
    """Add overdue status to ~5% of credit card accounts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("=" * 70)
    print("ADDING REALISTIC OVERDUE ACCOUNTS")
    print("=" * 70)

    # Get all credit card liabilities with account info
    cursor.execute("""
        SELECT
            l.id,
            l.account_id,
            a.user_id,
            u.persona,
            a.balance_current,
            a.balance_limit,
            CASE
                WHEN a.balance_limit > 0 THEN a.balance_current / a.balance_limit
                ELSE 0
            END as utilization
        FROM liabilities l
        JOIN accounts a ON l.account_id = a.account_id
        JOIN users u ON a.user_id = u.user_id
        WHERE l.liability_type = 'credit_card'
        ORDER BY RANDOM()
    """)

    all_cards = cursor.fetchall()
    print(f"\n📊 Total credit cards: {len(all_cards)}")

    # Calculate overdue probability for each card
    overdue_candidates = []

    for liability_id, account_id, user_id, persona, balance, limit, utilization in all_cards:
        # Base probability by persona (aligned with real 6% decline rate)
        persona_risk = {
            'high_utilization': 0.10,    # 10% base (maxed cards, stress)
            'variable_income': 0.08,     # 8% base (irregular income)
            'subscription_heavy': 0.05,  # 5% base (cash flow stress)
            'control': 0.04,             # 4% base (average)
            'savings_builder': 0.01      # 1% base (low risk, buffer)
        }
        prob = persona_risk.get(persona, 0.04)

        # Increase probability based on utilization
        if utilization >= 0.80:
            prob += 0.05  # +5% if very high utilization
        elif utilization >= 0.70:
            prob += 0.03  # +3% if high utilization

        # Increase probability for high balances (debt burden)
        if balance > 25000:
            prob += 0.03  # +3% for high debt

        # Cap at 20% max probability (even worst case shouldn't be certain)
        prob = min(prob, 0.20)

        overdue_candidates.append({
            'liability_id': liability_id,
            'account_id': account_id,
            'user_id': user_id,
            'persona': persona,
            'balance': balance,
            'utilization': utilization,
            'probability': prob
        })

    # Sort by probability (highest first)
    overdue_candidates.sort(key=lambda x: x['probability'], reverse=True)

    # Target: 5-6% overdue (5 out of 90 = 5.6%, matches real 6% decline rate)
    target_overdue = max(4, int(len(all_cards) * 0.056))

    print(f"🎯 Target overdue accounts: {target_overdue} (~5-6%, matching real data)")

    # Select accounts to mark as overdue
    overdue_count = 0
    overdue_by_persona = {}

    for candidate in overdue_candidates:
        if overdue_count >= target_overdue:
            break

        # Use probability to decide
        if random.random() < candidate['probability']:
            cursor.execute("""
                UPDATE liabilities
                SET is_overdue = 1
                WHERE id = ?
            """, (candidate['liability_id'],))

            overdue_count += 1
            persona = candidate['persona']
            overdue_by_persona[persona] = overdue_by_persona.get(persona, 0) + 1

            print(f"  ⚠️  {candidate['user_id']}: {candidate['persona']}, "
                  f"Util: {candidate['utilization']:.1%}, "
                  f"Balance: ${candidate['balance']:,.0f}")

    conn.commit()

    print(f"\n✅ Marked {overdue_count} accounts as overdue")

    # Show breakdown by persona
    print(f"\n📊 Overdue by Persona:")
    for persona in sorted(overdue_by_persona.keys()):
        count = overdue_by_persona[persona]
        print(f"  {persona:20} {count} overdue")

    # Verify final stats
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN is_overdue = 1 THEN 1 ELSE 0 END) as overdue,
            ROUND(100.0 * SUM(CASE WHEN is_overdue = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) as pct
        FROM liabilities
        WHERE liability_type = 'credit_card'
    """)

    total, overdue, pct = cursor.fetchone()

    print(f"\n📈 Final Statistics:")
    print(f"  Total credit cards: {total}")
    print(f"  Overdue: {overdue} ({pct}%)")
    print(f"  Current: {total - overdue} ({100 - pct}%)")

    if 3 <= pct <= 7:
        print(f"\n✅ REALISTIC: {pct}% overdue matches real-world range (3-7%)")
    else:
        print(f"\n⚠️  Outside typical range (3-7%)")

    conn.close()


if __name__ == '__main__':
    db_path = 'data/processed/spendsense.db'

    print("🔧 Adding Realistic Overdue Accounts to Credit Cards\n")

    add_overdue_accounts(db_path)

    print("\n" + "=" * 70)
    print("✅ Complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Restart server to pick up changes")
    print("2. Test credit detection with overdue users")
    print("3. Verify overdue_count field in API responses")
