# Story 2.5: Income Stability Detection

**Epic:** 2 - Behavioral Signal Detection Pipeline
**Story ID:** 2.5
**Status:** completed

## Story

As a **data scientist**,
I want **detection of income patterns including pay frequency and cash-flow buffer**,
so that **variable income users can receive budgeting strategies appropriate for their situation**.

## Acceptance Criteria

1. Payroll ACH transactions detected from transaction category and amount patterns
2. Payment frequency calculated from time gaps between payroll transactions
3. Median pay gap calculated to identify regular vs. irregular income
4. Cash-flow buffer calculated in months of expenses coverage
5. Income variability metric calculated from payment amount standard deviation
6. Results computed for both 30-day and 180-day windows
7. Edge cases handled: first job, job changes, missing income data
8. All income metrics logged with detected payroll dates
9. Income metrics stored per user per time window
10. Unit tests verify detection with biweekly, monthly, and irregular patterns

## Tasks/Subtasks

### Core Income Detection Module
- [ ] Create `spendsense/features/income_detector.py` (AC: 1-5)
  - [ ] Implement `IncomeDetector` class
  - [ ] Implement `detect_income_patterns()` method
  - [ ] Use TimeWindowCalculator for data retrieval

### Payroll Detection
- [ ] Detect payroll transactions (AC: 1)
  - [ ] Filter for positive (credit) transactions
  - [ ] Look for INCOME category transactions
  - [ ] Identify recurring large deposits
  - [ ] Filter out non-payroll transfers

### Payment Frequency Calculation
- [ ] Calculate pay frequency (AC: 2, 3)
  - [ ] Calculate time gaps between payroll transactions
  - [ ] Compute median gap (identify regular income)
  - [ ] Classify: weekly (7 days), biweekly (14 days), monthly (30 days)
  - [ ] Handle irregular income (high variance in gaps)

### Cash Flow Buffer
- [ ] Calculate cash flow buffer (AC: 4)
  - [ ] Get current liquid account balances
  - [ ] Calculate average monthly expenses
  - [ ] Compute: liquid_balance / monthly_expenses (in months)

### Income Variability
- [ ] Calculate income variability (AC: 5)
  - [ ] Get all payroll transaction amounts
  - [ ] Calculate standard deviation
  - [ ] Calculate coefficient of variation (std / mean)
  - [ ] Higher CV = more variable income

### Multi-Window Support
- [ ] Apply to both windows (AC: 6)
  - [ ] 30-day window metrics
  - [ ] 180-day window metrics

### Edge Case Handling
- [ ] Handle special cases (AC: 7)
  - [ ] No income transactions found
  - [ ] Only 1-2 income transactions (insufficient data)
  - [ ] Job change (sudden pattern shift)
  - [ ] First job (no history)

### Data Storage & Logging
- [ ] Store and log metrics (AC: 8, 9)
  - [ ] Create IncomeMetrics data class
  - [ ] Log detected payroll dates
  - [ ] Store per-user, per-window

### Testing
- [ ] Comprehensive tests (AC: 10)
  - [ ] Test payroll detection
  - [ ] Test biweekly pattern (14-day gaps)
  - [ ] Test monthly pattern (30-day gaps)
  - [ ] Test irregular pattern (variable gaps)
  - [ ] Test cash flow buffer calculation
  - [ ] Test income variability
  - [ ] Test edge cases (no income, etc.)
  - [ ] Test both windows

## Dev Notes

**Tech Stack:**
- TimeWindowCalculator from Story 2.1
- pandas for calculations
- numpy for statistics
- Pydantic for validation

**Income Detection Strategy:**
- Look for positive transactions with INCOME category
- Filter by minimum amount threshold (e.g., $500+)
- Require ≥2 transactions to establish pattern

**Frequency Classification:**
```python
# Based on median gap between payments
weekly: 5-9 days
biweekly: 12-16 days
semi_monthly: 13-17 days
monthly: 28-32 days
irregular: anything else or high variance
```

**Data Structure:**
```python
@dataclass
class IncomeMetrics:
    user_id: str
    window_days: int
    reference_date: date
    num_income_transactions: int
    total_income: float
    avg_income_per_payment: float
    payment_frequency: str  # 'weekly', 'biweekly', 'monthly', 'irregular'
    median_pay_gap_days: float
    income_variability_cv: float  # Coefficient of variation
    cash_flow_buffer_months: float
    has_regular_income: bool
    payroll_dates: List[date]
```

### Learnings from Previous Stories

**From Story 2.1: Time Window Aggregation**
- Use TimeWindowCalculator for transaction retrieval
- get_transactions_in_window() provides transaction data

**From Stories 2.2-2.4: Detector Pattern**
- Detector class structure
- Metrics dataclass pattern
- Edge case handling
- Multiple window support

### References

- [Epic 2: Story 2.5](docs/prd/epic-2-behavioral-signal-detection-pipeline.md#Story-2.5)
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

- 2025-11-04: Story created for Epic 2 income stability detection
