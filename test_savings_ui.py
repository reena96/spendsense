#!/usr/bin/env python3
"""
Quick test script to demonstrate Story 2.3 Savings Detector functionality.

This script shows what savings metrics you can display in the UI.
"""

from datetime import date
from spendsense.features import SavingsDetector

# Initialize detector
db_path = "data/processed/spendsense.db"
detector = SavingsDetector(db_path)

# Test with a real user
user_id = "user_MASKED_000"
reference_date = date(2025, 11, 4)

print("=" * 70)
print("SPENDSENSE - SAVINGS BEHAVIOR DETECTION (Story 2.3)")
print("=" * 70)
print()

# Get 30-day metrics
print(f"📊 30-DAY SAVINGS ANALYSIS for {user_id}")
print("-" * 70)
metrics_30 = detector.detect_savings_patterns(
    user_id=user_id,
    reference_date=reference_date,
    window_days=30
)

print(f"Has Savings Accounts: {'✅ Yes' if metrics_30.has_savings_accounts else '❌ No'}")
print(f"Total Savings Balance: ${metrics_30.total_savings_balance:,.2f}")
print(f"Net Inflow (30 days): ${metrics_30.net_inflow:,.2f}")
print(f"Savings Growth Rate: {metrics_30.savings_growth_rate:.2%}")
print(f"Average Monthly Expenses: ${metrics_30.avg_monthly_expenses:,.2f}")
print(f"Emergency Fund Coverage: {metrics_30.emergency_fund_months:.1f} months")
print()

# Get 180-day metrics
print(f"📊 180-DAY SAVINGS ANALYSIS for {user_id}")
print("-" * 70)
metrics_180 = detector.detect_savings_patterns(
    user_id=user_id,
    reference_date=reference_date,
    window_days=180
)

print(f"Has Savings Accounts: {'✅ Yes' if metrics_180.has_savings_accounts else '❌ No'}")
print(f"Total Savings Balance: ${metrics_180.total_savings_balance:,.2f}")
print(f"Net Inflow (180 days): ${metrics_180.net_inflow:,.2f}")
print(f"Savings Growth Rate: {metrics_180.savings_growth_rate:.2%}")
print(f"Average Monthly Expenses: ${metrics_180.avg_monthly_expenses:,.2f}")
print(f"Emergency Fund Coverage: {metrics_180.emergency_fund_months:.1f} months")
print()

# Interpretation
print("💡 INSIGHTS")
print("-" * 70)

if metrics_30.has_savings_accounts:
    if metrics_30.net_inflow > 0:
        print("✅ User is actively saving (positive net inflow)")
    elif metrics_30.net_inflow < 0:
        print("⚠️  User is withdrawing from savings (negative net inflow)")
    else:
        print("ℹ️  No savings activity in this period")

    if metrics_30.emergency_fund_months >= 6:
        print("✅ Strong emergency fund (6+ months of expenses)")
    elif metrics_30.emergency_fund_months >= 3:
        print("⚠️  Moderate emergency fund (3-6 months of expenses)")
    else:
        print("❌ Low emergency fund (<3 months of expenses)")

    if metrics_30.savings_growth_rate > 0:
        print(f"📈 Savings growing at {metrics_30.savings_growth_rate:.1%} rate")
    elif metrics_30.savings_growth_rate < 0:
        print(f"📉 Savings declining at {abs(metrics_30.savings_growth_rate):.1%} rate")
else:
    print("❌ No savings accounts detected")

print()
print("=" * 70)
print("✅ All metrics calculated successfully!")
print("=" * 70)
