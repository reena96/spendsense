"""Debug credit detector."""

from datetime import date
from spendsense.features.credit_detector import CreditDetector

# Initialize detector
detector = CreditDetector("data/processed/spendsense.db")

# Test credit detection for user_MASKED_000
try:
    metrics = detector.detect_credit_patterns(
        user_id="user_MASKED_000",
        reference_date=date(2025, 11, 4),
        window_days=180
    )

    print("Credit Metrics:")
    print(f"  Num credit cards: {metrics.num_credit_cards}")
    print(f"  Aggregate utilization: {metrics.aggregate_utilization}")
    print(f"  High utilization count: {metrics.high_utilization_count}")
    print(f"  Per-card details: {len(metrics.per_card_details)} cards")
    for card in metrics.per_card_details:
        print(f"    - {card}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
