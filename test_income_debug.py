"""Debug income detector."""

from datetime import date
from spendsense.features.income_detector import IncomeDetector

# Initialize detector
detector = IncomeDetector("data/processed/spendsense.db")

# Test income detection for user_MASKED_000
metrics = detector.detect_income_patterns(
    user_id="user_MASKED_000",
    reference_date=date(2025, 11, 4),
    window_days=180
)

print("Income Metrics:")
print(f"  Num income transactions: {metrics.num_income_transactions}")
print(f"  Total income: ${metrics.total_income:.2f}")
print(f"  Payment frequency: {metrics.payment_frequency}")
print(f"  Has regular income: {metrics.has_regular_income}")
print(f"  Payroll dates: {metrics.payroll_dates}")
