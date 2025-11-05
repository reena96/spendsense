# Story 2.2: Subscription Pattern Detection

**Epic:** 2 - Behavioral Signal Detection Pipeline
**Story ID:** 2.2
**Status:** drafted

## Story

As a **data scientist**,
I want **detection of recurring subscription patterns from transaction data**,
so that **subscription-heavy users can be identified and receive relevant education**.

## Acceptance Criteria

1. Recurring merchant detection identifies merchants with ≥3 transactions in 90 days
2. Cadence analysis determines if transactions are monthly or weekly recurring
3. Monthly recurring spend total calculated for each time window
4. Subscription share calculated as percentage of total spend
5. Results computed for both 30-day and 180-day windows
6. Detected subscriptions logged with merchant name, frequency, and amount
7. Edge cases handled: irregular timing, amount variations, cancelled subscriptions
8. Subscription metrics stored per user per time window
9. Unit tests verify detection accuracy with synthetic recurring patterns

## Tasks/Subtasks

### Core Subscription Detection Module
- [ ] Create `spendsense/features/subscription_detector.py` (AC: 1-5)
  - [ ] Implement `SubscriptionDetector` class
  - [ ] Implement `detect_recurring_merchants()` method
  - [ ] Implement `analyze_cadence()` method (monthly/weekly detection)
  - [ ] Implement `calculate_subscription_metrics()` method
  - [ ] Use TimeWindowCalculator for consistent date filtering

### Recurring Merchant Detection
- [ ] Identify merchants with ≥3 transactions in 90 days (AC: 1)
  - [ ] Group transactions by merchant_name
  - [ ] Count occurrences in 90-day lookback
  - [ ] Filter to merchants meeting threshold

### Cadence Analysis
- [ ] Determine transaction frequency (AC: 2)
  - [ ] Calculate time gaps between transactions
  - [ ] Identify monthly pattern (25-35 day gaps)
  - [ ] Identify weekly pattern (5-9 day gaps)
  - [ ] Handle irregular patterns gracefully

### Metrics Calculation
- [ ] Calculate subscription spend metrics (AC: 3, 4)
  - [ ] Sum monthly recurring charges
  - [ ] Calculate total spend in window
  - [ ] Compute subscription_share = recurring / total
  - [ ] Apply to both 30-day and 180-day windows (AC: 5)

### Edge Case Handling
- [ ] Handle irregular patterns (AC: 7)
  - [ ] Amount variations (±20% tolerance)
  - [ ] Timing irregularities (±7 day tolerance)
  - [ ] Recently cancelled subscriptions (no recent charges)
  - [ ] New subscriptions (< 3 transactions yet)

### Data Storage & Logging
- [ ] Store and log subscription data (AC: 6, 8)
  - [ ] Create SubscriptionMetrics data class
  - [ ] Log detected subscriptions with details
  - [ ] Store per-user, per-window metrics

### Testing
- [ ] Comprehensive unit tests (AC: 9)
  - [ ] Test with synthetic Netflix/Spotify patterns
  - [ ] Test monthly vs. weekly detection
  - [ ] Test edge cases (cancelled, irregular)
  - [ ] Test subscription share calculation
  - [ ] Test both 30 and 180-day windows

## Dev Notes

**Tech Stack:**
- TimeWindowCalculator from Story 2.1 for date filtering
- pandas for grouping and aggregation
- Pydantic for data validation

**Subscription Detection Algorithm:**
```python
1. Get transactions in extended window (reference_date - 90 days)
2. Group by merchant_name
3. For each merchant:
   - Count transactions
   - If count >= 3:
     - Calculate time gaps between transactions
     - Detect cadence (monthly: 25-35 days, weekly: 5-9 days)
     - Calculate average amount
     - Mark as subscription if cadence detected
4. Filter to current time window (30 or 180 days)
5. Calculate metrics
```

**Cadence Detection:**
- **Monthly**: median gap 25-35 days, std dev < 7 days
- **Weekly**: median gap 5-9 days, std dev < 3 days
- **Irregular**: doesn't match either pattern, but still recurring

**Subscription Share:**
```
subscription_share = recurring_spend / total_spend
```

**Data Structure:**
```python
@dataclass
class SubscriptionMetrics:
    user_id: str
    window_days: int
    subscription_count: int
    monthly_recurring_spend: float
    total_spend: float
    subscription_share: float
    detected_subscriptions: List[DetectedSubscription]

@dataclass
class DetectedSubscription:
    merchant_name: str
    cadence: str  # "monthly", "weekly", "irregular"
    avg_amount: float
    transaction_count: int
    last_charge_date: date
```

### Learnings from Previous Story

**From Story 2.1: Time Window Aggregation Framework**

- **TimeWindowCalculator available**: Use `get_transactions_in_window()` for consistent date filtering
- **TimeWindowResult structure**: Contains data, window bounds, is_complete flag
- **Edge case handling**: Framework handles insufficient data, returns empty DataFrames
- **Date arithmetic**: Use timedelta for consistency

[Source: docs/stories/2-1-time-window-aggregation-framework.md]

### References

- [Epic 2: Story 2.2](docs/prd/epic-2-behavioral-signal-detection-pipeline.md#Story-2.2)
- [Story 2.1: Time Windows](docs/stories/2-1-time-window-aggregation-framework.md)
- [Architecture: Features Module](docs/architecture.md#features-module)

## Dev Agent Record

### Context Reference

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-04: Story created for Epic 2 subscription pattern detection
