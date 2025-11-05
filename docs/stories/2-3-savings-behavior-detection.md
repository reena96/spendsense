# Story 2.3: Savings Behavior Detection

**Epic:** 2 - Behavioral Signal Detection Pipeline
**Story ID:** 2.3
**Status:** completed

## Story

As a **data scientist**,
I want **detection of savings patterns including account growth and emergency fund coverage**,
so that **savings builders can be identified and encouraged to optimize their strategy**.

## Acceptance Criteria

1. Net inflow calculated for savings-type accounts (savings, money market, HSA)
2. Savings growth rate calculated as percentage change over time window
3. Emergency fund coverage calculated as savings balance ÷ average monthly expenses
4. Monthly expense average computed from spending transactions
5. Results computed for both 30-day and 180-day windows
6. Savings metrics handle accounts with zero balance gracefully
7. All derived metrics logged for explainability and traceability
8. Savings metrics stored per user per time window
9. Unit tests verify calculations with various saving patterns

## Tasks/Subtasks

### Core Savings Detection Module
- [x] Create `spendsense/features/savings_detector.py` (AC: 1-5)
  - [x] Implement `SavingsDetector` class
  - [x] Implement `detect_savings_patterns()` method
  - [x] Use TimeWindowCalculator for data retrieval

### Savings Account Analysis
- [x] Calculate net inflow (AC: 1)
  - [x] Identify savings-type accounts (savings, money_market, cd, hsa)
  - [x] Sum deposits (positive transactions)
  - [x] Sum withdrawals (negative transactions)
  - [x] Calculate net = deposits - withdrawals

### Growth Rate Calculation
- [x] Calculate savings growth rate (AC: 2)
  - [x] Get starting balance (beginning of window)
  - [x] Get ending balance (end of window)
  - [x] Calculate: (ending - starting) / starting
  - [x] Handle zero starting balance

### Emergency Fund Analysis
- [x] Calculate emergency fund coverage (AC: 3, 4)
  - [x] Get total savings balance
  - [x] Calculate average monthly expenses from transactions
  - [x] Compute months of coverage = savings / monthly_expenses
  - [x] Handle zero expenses edge case

### Multi-Window Support
- [x] Apply to both windows (AC: 5)
  - [x] 30-day window metrics
  - [x] 180-day window metrics

### Edge Case Handling
- [x] Handle special cases (AC: 6)
  - [x] Zero savings balance
  - [x] No transactions in window
  - [x] Negative growth (withdrawals)
  - [x] New accounts

### Data Storage & Logging
- [x] Store and log metrics (AC: 7, 8)
  - [x] Create SavingsMetrics data class
  - [x] Log all calculations
  - [x] Store per-user, per-window

### Testing
- [x] Comprehensive tests (AC: 9)
  - [x] Test net inflow calculation
  - [x] Test growth rate with various patterns
  - [x] Test emergency fund calculation
  - [x] Test edge cases (zero balance, etc.)
  - [x] Test both windows

## Dev Notes

**Tech Stack:**
- TimeWindowCalculator from Story 2.1
- pandas for calculations
- Pydantic for validation

**Savings Account Types:**
- savings
- money_market
- cd (certificate of deposit)
- hsa (health savings account)

**Calculation Formulas:**
```python
net_inflow = sum(deposits) - sum(withdrawals)
growth_rate = (ending_balance - starting_balance) / starting_balance
emergency_fund_months = total_savings / avg_monthly_expenses
avg_monthly_expenses = abs(sum(debits)) / (window_days / 30)
```

**Data Structure:**
```python
@dataclass
class SavingsMetrics:
    user_id: str
    window_days: int
    reference_date: date
    net_inflow: float
    savings_growth_rate: float
    emergency_fund_months: float
    total_savings_balance: float
    avg_monthly_expenses: float
    has_savings_accounts: bool
```

### Learnings from Previous Stories

**From Story 2.1: Time Window Aggregation**
- Use TimeWindowCalculator for consistent date filtering
- TimeWindowResult provides data + metadata

**From Story 2.2: Subscription Detection**
- Pattern for detector class structure
- Metrics dataclass pattern
- Edge case handling approaches

### References

- [Epic 2: Story 2.3](docs/prd/epic-2-behavioral-signal-detection-pipeline.md#Story-2.3)
- [Story 2.1: Time Windows](docs/stories/2-1-time-window-aggregation-framework.md)
- [Architecture: Features Module](docs/architecture.md#features-module)

## Dev Agent Record

### Context Reference

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

**Implementation Summary:**
- Created `spendsense/features/savings_detector.py` with full SavingsDetector implementation
- Implemented all required metrics: net_inflow, savings_growth_rate, emergency_fund_months
- Added comprehensive test suite with 23 tests covering all acceptance criteria
- All tests passing (23/23)
- Follows established patterns from Stories 2.1 and 2.2

**Key Implementation Details:**
- Identifies savings accounts by subtype (savings, money_market, cd, hsa)
- Approximates starting balance by subtracting net inflow from current balance
- Handles edge cases: zero balance, no accounts, no transactions, future dates
- Returns SavingsMetrics dataclass with all required fields
- Updated `spendsense/features/__init__.py` to export new classes

**Testing:**
- 9 tests for acceptance criteria
- 11 tests for specific calculations (net inflow, growth rate, emergency fund)
- 3 tests for edge cases (no accounts, future dates, invalid windows)
- All tests pass consistently with synthetic data

### File List

**Implementation Files:**
- `spendsense/features/savings_detector.py` (320 lines)
- `spendsense/features/__init__.py` (updated)

**Test Files:**
- `tests/test_savings_detector.py` (450 lines, 23 tests)

## Change Log

- 2025-11-04: Story created for Epic 2 savings behavior detection
- 2025-11-04: Story completed - implementation and tests passing (23/23 tests)
