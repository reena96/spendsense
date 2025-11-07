"""Debug savings detector."""

from datetime import date
from spendsense.features.savings_detector import SavingsDetector

# Initialize detector
detector = SavingsDetector("data/processed/spendsense.db")

# Test savings detection for user_MASKED_003 (savings_builder)
try:
    metrics = detector.detect_savings_patterns(
        user_id="user_MASKED_003",
        reference_date=date(2025, 11, 4),
        window_days=180
    )

    print("Savings Metrics for user_MASKED_003:")
    print(f"  Has savings accounts: {metrics.has_savings_accounts}")
    print(f"  Total savings balance: ${metrics.total_savings_balance:.2f}")
    print(f"  Net inflow: ${metrics.net_inflow:.2f}")
    print(f"  Growth rate: {metrics.savings_growth_rate:.2%}")
    print(f"  Emergency fund: {metrics.emergency_fund_months:.1f} months")
    print(f"  Avg monthly expenses: ${metrics.avg_monthly_expenses:.2f}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
