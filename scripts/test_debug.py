"""Debug script to test TimeWindowCalculator."""

from datetime import date
from spendsense.features.time_windows import TimeWindowCalculator

# Initialize calculator
calc = TimeWindowCalculator("data/processed/spendsense.db")

# Test getting transactions for user_MASKED_000
result = calc.get_transactions_in_window(
    user_id="user_MASKED_000",
    reference_date=date(2025, 11, 4),
    window_days=180
)

print(f"Window: {result.window_start} to {result.window_end}")
print(f"Record count: {result.record_count}")
print(f"Is complete: {result.is_complete}")
print(f"\nDataFrame shape: {result.data.shape if not result.data.empty else 'Empty'}")

if not result.data.empty:
    print(f"\nFirst 5 transactions:")
    print(result.data.head())
    print(f"\nCategories:")
    print(result.data['category'].value_counts())
else:
    print("\n⚠️  DataFrame is EMPTY!")
    print("This means get_transactions_in_window returned no data.")
