# Epic 2: Behavioral Signal Detection Pipeline

**Goal:** Implement comprehensive feature engineering modules that analyze user financial data to detect subscription patterns, savings behaviors, credit utilization, and income stability. All signals computed over both 30-day and 180-day time windows with standardized aggregation logic and complete audit logging.

## Story 2.1: Time Window Aggregation Framework

As a **data scientist**,
I want **standardized time window calculation framework supporting 30-day and 180-day analysis periods**,
so that **all behavioral signals can be computed consistently across different time horizons**.

### Acceptance Criteria

1. Time window utility function created accepting reference date and window size (30/180 days)
2. Function returns filtered dataset for specified window
3. Function handles edge cases (insufficient historical data)
4. Window calculations use consistent date arithmetic across all modules
5. Default fallback values defined for users with insufficient data
6. Window framework documented with usage examples
7. Unit tests verify correct date filtering and edge case handling

## Story 2.2: Subscription Pattern Detection

As a **data scientist**,
I want **detection of recurring subscription patterns from transaction data**,
so that **subscription-heavy users can be identified and receive relevant education**.

### Acceptance Criteria

1. Recurring merchant detection identifies merchants with ≥3 transactions in 90 days
2. Cadence analysis determines if transactions are monthly or weekly recurring
3. Monthly recurring spend total calculated for each time window
4. Subscription share calculated as percentage of total spend
5. Results computed for both 30-day and 180-day windows
6. Detected subscriptions logged with merchant name, frequency, and amount
7. Edge cases handled: irregular timing, amount variations, cancelled subscriptions
8. Subscription metrics stored per user per time window
9. Unit tests verify detection accuracy with synthetic recurring patterns

## Story 2.3: Savings Behavior Detection

As a **data scientist**,
I want **detection of savings patterns including account growth and emergency fund coverage**,
so that **savings builders can be identified and encouraged to optimize their strategy**.

### Acceptance Criteria

1. Net inflow calculated for savings-type accounts (savings, money market, HSA)
2. Savings growth rate calculated as percentage change over time window
3. Emergency fund coverage calculated as savings balance ÷ average monthly expenses
4. Monthly expense average computed from spending transactions
5. Results computed for both 30-day and 180-day windows
6. Savings metrics handle accounts with zero balance gracefully
7. All derived metrics logged for explainability and traceability
8. Savings metrics stored per user per time window
9. Unit tests verify calculations with various saving patterns

## Story 2.4: Credit Utilization & Debt Signal Detection

As a **data scientist**,
I want **detection of credit card utilization levels and debt stress indicators**,
so that **high-utilization users can receive debt paydown education and resources**.

### Acceptance Criteria

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

## Story 2.5: Income Stability Detection

As a **data scientist**,
I want **detection of income patterns including pay frequency and cash-flow buffer**,
so that **variable income users can receive budgeting strategies appropriate for their situation**.

### Acceptance Criteria

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

## Story 2.6: Behavioral Summary Aggregation

As a **data scientist**,
I want **aggregated behavioral summaries per user combining all detected signals**,
so that **persona classification has complete feature set available for decision logic**.

### Acceptance Criteria

1. User behavioral summary created combining subscription, savings, credit, and income signals
2. Summary includes all metrics computed for both time windows
3. Summary includes metadata: calculation timestamp, data completeness flags
4. Missing data indicators added where signals could not be computed
5. Summary stored in structured format (JSON) for recommendation engine access
6. Summary accessible via API endpoint GET /profile/{user_id}
7. Fallback defaults applied consistently for incomplete data
8. Summary generation logged for audit trail
9. Unit tests verify summary completeness and data structure

---
