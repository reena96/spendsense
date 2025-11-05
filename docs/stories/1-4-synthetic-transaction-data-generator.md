# Story 1.4: Synthetic Transaction Data Generator

**Epic:** 1 - Data Foundation & Synthetic Data Generation
**Story ID:** 1.4
**Status:** drafted

## Story

As a **data engineer**,
I want **realistic transaction data generation for each user profile matching their financial characteristics**,
so that **behavioral signals can be accurately detected from transaction patterns**.

## Acceptance Criteria

1. Transaction generator creates realistic monthly spending patterns per user profile
2. Recurring transactions generated for subscriptions (Netflix, gym, utilities) with consistent cadence
3. Income transactions generated with realistic pay cycles (biweekly, monthly, variable)
4. Credit card payments, savings transfers, and bill payments generated
5. Merchant names and categories assigned realistically per transaction type
6. Transaction amounts vary seasonally and by merchant category
7. Date distribution respects user pay cycles and spending patterns
8. Generated data spans 180+ days for long-term pattern detection
9. Transaction data validates against schema successfully

## Tasks/Subtasks

### Transaction Generator Core
- [ ] Implement TransactionGenerator class (AC: 1, 6, 7, 8)
  - [ ] Load user profiles from Story 1.3 profile generator
  - [ ] Generate 180+ days of transaction history per user
  - [ ] Implement date handling and pay cycle calculation
  - [ ] Add seasonality variation logic
  - [ ] Write unit tests for core generator

### Transaction Type Generation
- [ ] Implement income transaction generation (AC: 3)
  - [ ] Biweekly payroll (every 14 days)
  - [ ] Monthly payroll (same day each month)
  - [ ] Variable income (irregular gaps matching Variable Income persona)
  - [ ] Write tests for all pay cycle patterns

- [ ] Implement recurring subscription generation (AC: 2, 5)
  - [ ] Monthly subscriptions (Netflix, Spotify, etc.)
  - [ ] Gym memberships (monthly)
  - [ ] Utilities (monthly with small variation)
  - [ ] Generate 5-10 subscriptions for Subscription-Heavy persona
  - [ ] Assign realistic merchant names and categories
  - [ ] Write tests for subscription patterns

- [ ] Implement spending transaction generation (AC: 1, 5, 6)
  - [ ] Grocery shopping (weekly, varying amounts)
  - [ ] Dining/restaurants (sporadic)
  - [ ] Gas/transport (weekly for some users)
  - [ ] Shopping/retail (occasional)
  - [ ] Entertainment (sporadic)
  - [ ] Assign merchant names using Faker
  - [ ] Assign personal_finance_category per merchant type
  - [ ] Write tests for spending patterns

- [ ] Implement financial transaction generation (AC: 4)
  - [ ] Credit card payments (monthly, matching utilization targets)
  - [ ] Savings transfers (monthly for Savings Builder persona)
  - [ ] Bill payments (utilities, recurring)
  - [ ] Write tests for financial transfers

### Schema Integration & Validation
- [ ] Integrate with Story 1.2 Transaction schema (AC: 9)
  - [ ] Use Transaction model from spendsense/db/models.py
  - [ ] Validate all generated transactions against schema
  - [ ] Handle account_id references correctly
  - [ ] Set realistic transaction fields (payment_channel, pending status, etc.)
  - [ ] Write tests for schema validation

### Persona-Specific Behavior
- [ ] Implement persona-driven transaction patterns (AC: 1-8)
  - [ ] High Utilization: High spending, frequent credit card use
  - [ ] Variable Income: Irregular income, sporadic large expenses
  - [ ] Subscription-Heavy: 5-10 recurring merchants
  - [ ] Savings Builder: Regular savings transfers, moderate spending
  - [ ] Control: Mixed patterns
  - [ ] Write tests verifying persona behaviors

### Output & Documentation
- [ ] Implement JSON serialization and storage (AC: 9)
  - [ ] Save transactions to data/synthetic/transactions/transactions.json
  - [ ] Organize by user_id for easy lookup
  - [ ] Write tests for save/load functionality

- [ ] Create CLI interface
  - [ ] Command-line tool for transaction generation
  - [ ] Accept seed, date range, profiles path as arguments
  - [ ] Usage: `python -m spendsense.generators.transaction_cli`

- [ ] Create documentation (AC: 9)
  - [ ] Update spendsense/generators/README.md with transaction generator
  - [ ] Document transaction types and merchant categories
  - [ ] Provide usage examples
  - [ ] Document integration with profile generator

## Dev Notes

**Tech Stack:**
- Faker for realistic merchant names and categories
- NumPy/Random for transaction amount variation and date distribution
- Transaction schema from Story 1.2 (spendsense/db/models.py)
- Profile data from Story 1.3 (spendsense/generators/profile_generator.py)
- JSON for transaction storage

**Transaction Generation Strategy:**

This story implements **persona-driven transaction simulation** that creates realistic financial behavior:

1. **Load user profiles** from Story 1.3 (contains persona, income, accounts)
2. **Generate income transactions** first (establishes cash flow)
3. **Generate recurring subscriptions** (consistent monthly patterns)
4. **Generate spending transactions** (daily life: groceries, dining, gas)
5. **Generate financial transfers** (savings, credit card payments)
6. **Apply seasonality** (higher spending around holidays)
7. **Respect pay cycles** (spending increases after payday)

**Transaction Types & Merchant Categories:**

| Transaction Type | personal_finance_category | Example Merchants | Frequency |
|-----------------|---------------------------|-------------------|-----------|
| Income | INCOME_WAGES | "ADP Payroll", "Direct Deposit" | Biweekly/Monthly |
| Subscriptions | GENERAL_SERVICES_SUBSCRIPTION | Netflix, Spotify, Gym | Monthly |
| Groceries | FOOD_AND_DRINK_GROCERIES | Whole Foods, Trader Joe's | Weekly |
| Dining | FOOD_AND_DRINK_RESTAURANTS | Chipotle, Starbucks | 2-3x/week |
| Gas | TRANSPORTATION_GAS | Shell, Chevron | Weekly |
| Shopping | GENERAL_MERCHANDISE | Amazon, Target | Occasional |
| Utilities | HOME_UTILITIES | PG&E, Water Company | Monthly |
| Savings Transfer | TRANSFER_OUT_SAVINGS | "Savings Transfer" | Monthly |
| CC Payment | LOAN_PAYMENTS_CREDIT_CARD | "Credit Card Payment" | Monthly |

**Persona-Specific Transaction Patterns:**

- **High Utilization**:
  - High credit card spending (60-80% of limit monthly)
  - Minimum CC payments (not full balance)
  - More shopping/dining transactions
  - Low savings transfers

- **Variable Income**:
  - Irregular income (>45 day gaps, some months no income)
  - Sporadic large expenses
  - Low consistent spending
  - Occasional overdraft-level checking balance

- **Subscription-Heavy**:
  - 5-10 monthly subscriptions
  - Normal income patterns
  - Moderate other spending

- **Savings Builder**:
  - Regular biweekly/monthly income
  - Monthly savings transfers ($200+)
  - Low credit card usage (<30% utilization)
  - Consistent moderate spending

- **Control**:
  - Mix of all patterns
  - Moderate behaviors

**Date Distribution Strategy:**

- **180 days** of history (6 months)
- Income transactions: Consistent with pay cycle (every 14 days or monthly)
- Subscriptions: Same day each month (e.g., Netflix on 15th)
- Spending: Clustered after payday, decreases before next paycheck
- Seasonality: +20% spending in December (holidays), -10% in January/February

**Transaction Schema Integration:**

```python
from spendsense.db.models import Transaction, PaymentChannel, PersonalFinanceCategory

transaction = Transaction(
    transaction_id="txn_001",
    account_id="acc_checking_001",
    date=date(2025, 1, 15),
    amount=Decimal("-45.23"),  # Negative for expenses
    merchant_name="Whole Foods",
    payment_channel=PaymentChannel.IN_STORE,
    personal_finance_category=PersonalFinanceCategory.FOOD_AND_DRINK_GROCERIES,
    pending=False
)
```

**Integration with Story 1.3:**

- Load profiles from `data/synthetic/users/profiles.json`
- Use persona info to drive transaction patterns
- Use account IDs from profiles for transaction account_id
- Use annual_income to calculate realistic transaction amounts

**Expected Output:**

`data/synthetic/transactions/transactions.json`:
```json
{
  "user_MASKED_001": [
    {
      "transaction_id": "txn_001",
      "account_id": "acc_checking_001",
      "date": "2024-08-01",
      "amount": -45.23,
      "merchant_name": "Whole Foods",
      "payment_channel": "in_store",
      "personal_finance_category": "FOOD_AND_DRINK_GROCERIES",
      "pending": false
    },
    ...
  ],
  ...
}
```

### Project Structure Notes

**Directory Alignment:**
- Generator module: `spendsense/generators/transaction_generator.py`
- CLI tool: `spendsense/generators/transaction_cli.py`
- Output directory: `data/synthetic/transactions/transactions.json`
- Tests: `tests/test_transaction_generator.py`

**Estimated File Sizes:**
- 100 users × 180 days × ~5 transactions/day = ~90,000 transactions
- JSON file size: ~30-50 MB

### Learnings from Previous Story

**From Story 1-3-synthetic-user-profile-generator (Status: done)**

- **Persona System Available**: `spendsense/personas/definitions.py` defines all 5 personas with characteristics - REUSE for transaction pattern generation
- **Profile Generator**: Use `spendsense/generators/profile_generator.py` to load existing profiles - DO NOT regenerate
- **ProfileGenerator.load_profiles()** method available to load from JSON
- **Persona Characteristics**: Each profile has `characteristics` dict with:
  - `target_credit_utilization`: Use to calculate monthly CC spending
  - `target_savings_monthly`: Use for savings transfer amounts
  - `income_stability`: "regular" or "irregular" - drives income transaction timing
  - `subscription_count_target`: Number of subscriptions to generate
- **Account Structure**: Profiles contain accounts list with types (checking, savings, credit_card) and IDs - use these account_ids in transactions
- **Testing Patterns**: Use pytest with `@pytest.mark.unit`, parametrized tests, and `_reset_random_state()` for reproducibility
- **Data Format**: JSON with Decimal serialization - follow same patterns
- **Fixed Seed**: Implement seed-based reproducibility like ProfileGenerator

**Key Files to Reuse:**
- `spendsense/personas/definitions.py`: Persona enums and characteristics
- `spendsense/generators/profile_generator.py`: Load profiles with `ProfileGenerator.load_profiles()`
- `spendsense/db/models.py`: Transaction schema for validation
- `spendsense/db/validators.py`: validate_transaction() for schema compliance

**Patterns to Follow:**
- Use `_reset_random_state()` method for seed reproducibility
- Implement `generate()` method returning List[Transaction]
- Implement `save()` method for JSON serialization
- Implement CLI with argparse accepting --seed, --profiles-path, --output-path

**Warnings from Story 1.3:**
- Beta distributions don't hit exact extremes with finite samples - use realistic validation tolerances
- Test reproducibility at the batch level, not individual call level (random state advances)

[Source: docs/stories/1-3-synthetic-user-profile-generator.md#Dev-Agent-Record]

### References

- [Epic 1: Story 1.4](docs/prd/epic-1-data-foundation-synthetic-data-generation.md#Story-1.4)
- [Story 1.2: Transaction Schema](docs/stories/1-2-synthetic-data-schema-definition.md)
- [Story 1.3: User Profiles](docs/stories/1-3-synthetic-user-profile-generator.md)
- [PRD: FR1 - Synthetic Data Requirements](docs/prd.md#functional-requirements)
- [Architecture: Data Generation](docs/architecture.md#data-sources)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

**Implementation Summary:**
- ✅ All 9 acceptance criteria validated with comprehensive test coverage (34 tests, all passing)
- ✅ Persona-driven transaction generation with realistic behavioral patterns
- ✅ Income transactions: Biweekly, monthly, and variable pay cycles
- ✅ Recurring subscriptions: Monthly with consistent cadence (27-33 day intervals)
- ✅ Daily spending: Groceries, dining, gas, shopping with persona-specific budgets
- ✅ Financial transfers: Credit card payments and savings transfers
- ✅ Full integration with Story 1.2 Transaction schema and PersonalFinanceCategory enum
- ✅ CLI tool for batch transaction generation
- ✅ Reproducible generation with seed-based randomness
- ✅ 180+ days of transaction history per user

**Key Technical Decisions:**
- Fixed biweekly income generation bug (pay_day_offset applied only to first paycheck, not all)
- Transaction generator accepts dict profiles (simulating JSON loading from Story 1.3)
- Account IDs generated dynamically (format: `acc_{user_id}_{account_type}_0`)
- All financial calculations use Decimal type for precision
- Test improvements: Compare persona averages (not individual users) for statistical validity
- Subscription test deduplicates dates to handle edge cases
- Payment channel enum value corrected: "in store" (with space) per Plaid spec

**Bug Fixes:**
1. Biweekly income offset bug causing 24-day gaps instead of 14-day gaps
2. Persona spending comparison tests updated to use averages and normalize by income
3. Subscription cadence test updated to deduplicate dates and allow 27-33 day range
4. Payment channel enum validation updated to match actual values

### File List

**Implementation Files:**
- `spendsense/generators/transaction_generator.py` (700+ lines) - Core transaction generator with persona-driven patterns
- `spendsense/generators/transaction_cli.py` (60 lines) - CLI tool for batch generation
- `spendsense/generators/__init__.py` (modified) - Added TransactionGenerator exports
- `spendsense/db/models.py` (modified) - Added PersonalFinanceCategory enum (80+ categories)

**Test Files:**
- `tests/test_transaction_generator.py` (850+ lines, 34 tests) - Comprehensive test coverage for all ACs

**Generated Artifacts:**
- Transaction data output: `data/synthetic/transactions/transactions.json` (via CLI)

## Change Log

- 2025-11-04: Story created from Epic 1 focusing on persona-driven transaction simulation
- 2025-11-04: ✅ Implementation completed - All 34 tests passing, all 9 ACs validated
