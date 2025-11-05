# Story 2.4: Credit Utilization & Debt Signal Detection

**Epic:** 2 - Behavioral Signal Detection Pipeline
**Story ID:** 2.4
**Status:** completed

## Story

As a **data scientist**,
I want **detection of credit card utilization levels and debt stress indicators**,
so that **high-utilization users can receive debt paydown education and resources**.

## Acceptance Criteria

1. Credit utilization calculated as balance ÷ limit for each credit card
2. Utilization flags set for ≥30%, ≥50%, ≥80% thresholds
3. Minimum-payment-only behavior detected from payment history
4. Interest charges presence identified from liability data
5. Overdue status flagged from is_overdue field
6. Aggregate utilization calculated across all cards
7. Results computed for both 30-day and 180-day windows
8. All credit signals logged with specific card identifiers
9. Credit metrics stored per user per time window
10. Unit tests verify detection across various credit scenarios

## Tasks/Subtasks

### Core Credit Detection Module
- [ ] Create `spendsense/features/credit_detector.py` (AC: 1-6)
  - [ ] Implement `CreditDetector` class
  - [ ] Implement `detect_credit_patterns()` method
  - [ ] Use TimeWindowCalculator for data retrieval

### Utilization Calculation
- [ ] Calculate per-card utilization (AC: 1)
  - [ ] Get credit card accounts from liabilities
  - [ ] Calculate: balance / limit for each card
  - [ ] Handle cards with no limit (skip)
  - [ ] Handle zero limit edge case

### Utilization Thresholds
- [ ] Set utilization flags (AC: 2)
  - [ ] Flag ≥30% utilization (moderate)
  - [ ] Flag ≥50% utilization (high)
  - [ ] Flag ≥80% utilization (very high)
  - [ ] Calculate aggregate utilization across all cards

### Payment Behavior Analysis
- [ ] Detect minimum-payment-only behavior (AC: 3)
  - [ ] Compare last_payment_amount to minimum_payment_amount
  - [ ] Identify users paying only minimum
  - [ ] Track payment patterns

### Interest and Overdue Detection
- [ ] Identify debt stress indicators (AC: 4, 5)
  - [ ] Check for APR > 0 (interest charges)
  - [ ] Flag is_overdue status
  - [ ] Count overdue accounts

### Aggregate Metrics
- [ ] Calculate aggregate utilization (AC: 6)
  - [ ] Sum all balances across cards
  - [ ] Sum all limits across cards
  - [ ] Calculate: total_balance / total_limit

### Multi-Window Support
- [ ] Apply to both windows (AC: 7)
  - [ ] 30-day window metrics
  - [ ] 180-day window metrics

### Data Storage & Logging
- [ ] Store and log metrics (AC: 8, 9)
  - [ ] Create CreditMetrics data class
  - [ ] Create PerCardUtilization data class
  - [ ] Log all calculations with card IDs
  - [ ] Store per-user, per-window

### Testing
- [ ] Comprehensive tests (AC: 10)
  - [ ] Test per-card utilization calculation
  - [ ] Test utilization thresholds
  - [ ] Test aggregate utilization
  - [ ] Test minimum-payment detection
  - [ ] Test overdue flagging
  - [ ] Test edge cases (no cards, no limit, etc.)
  - [ ] Test both windows

## Dev Notes

**Tech Stack:**
- TimeWindowCalculator from Story 2.1
- pandas for calculations
- Pydantic for validation

**Credit Card Identification:**
- liability_type: 'credit'
- From liabilities table joined with accounts

**Calculation Formulas:**
```python
utilization = balance / limit  # Per card
aggregate_utilization = sum(balances) / sum(limits)  # All cards
minimum_payment_only = last_payment <= minimum_payment * 1.05  # 5% tolerance
```

**Data Structure:**
```python
@dataclass
class PerCardUtilization:
    account_id: str
    balance: float
    limit: float
    utilization: float
    utilization_tier: str  # 'low', 'moderate', 'high', 'very_high'
    is_overdue: bool
    has_interest_charges: bool

@dataclass
class CreditMetrics:
    user_id: str
    window_days: int
    reference_date: date
    num_credit_cards: int
    aggregate_utilization: float
    high_utilization_count: int  # Cards ≥50%
    very_high_utilization_count: int  # Cards ≥80%
    minimum_payment_only_count: int
    overdue_count: int
    has_interest_charges: bool
    per_card_details: List[PerCardUtilization]
```

### Learnings from Previous Stories

**From Story 2.1: Time Window Aggregation**
- Use TimeWindowCalculator for consistent data access
- get_liabilities_snapshot() provides liability data

**From Stories 2.2-2.3: Detector Pattern**
- Detector class with detect_* method
- Metrics dataclass pattern
- Edge case handling approaches
- Multiple window support

### References

- [Epic 2: Story 2.4](docs/prd/epic-2-behavioral-signal-detection-pipeline.md#Story-2.4)
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

- 2025-11-04: Story created for Epic 2 credit utilization detection
