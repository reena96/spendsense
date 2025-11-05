# Story 1.5: Synthetic Liability Data Generator

**Epic:** 1 - Data Foundation & Synthetic Data Generation
**Story ID:** 1.5
**Status:** done

## Story

As a **data engineer**,
I want **realistic liability data generation including credit cards and loans matching user profiles**,
so that **credit utilization and debt signals can be accurately calculated**.

## Acceptance Criteria

1. Credit card data generated with realistic limits ($500-$25,000 range)
2. Credit card balances set based on user profile utilization targets
3. APR rates assigned realistically (15%-30% range)
4. Minimum payment amounts calculated correctly (typically 2-3% of balance)
5. Overdue status and payment history generated based on profile
6. Student loan and mortgage data generated for applicable profiles
7. Interest rates match realistic market conditions
8. All liability data validates against schema
9. Liability data consistent with transaction history

## Tasks/Subtasks

### Liability Generator Core
- [ ] Implement LiabilityGenerator class (AC: 1-9)
  - [ ] Load user profiles from Story 1.3 profile generator
  - [ ] Load transaction data from Story 1.4 for consistency validation
  - [ ] Initialize with seed for reproducibility
  - [ ] Write unit tests for core generator

### Credit Card Liability Generation
- [ ] Implement credit card liability generation (AC: 1-5)
  - [ ] Generate credit limits based on income levels ($500-$25,000 range)
  - [ ] Calculate current balances using target_credit_utilization from profiles
  - [ ] Assign realistic APR rates (15%-30% with income-based variation)
  - [ ] Calculate minimum payment amounts (2-3% of balance, $25 minimum)
  - [ ] Set overdue status based on persona behavioral patterns
  - [ ] Generate last_payment_amount from transaction history
  - [ ] Set next_payment_due_date relative to current date
  - [ ] Calculate last_statement_balance
  - [ ] Write tests for all credit card fields

### Loan Liability Generation
- [ ] Implement student loan generation (AC: 6, 7, 8)
  - [ ] Generate student loans for profiles with student debt
  - [ ] Assign realistic interest rates (3%-8% based on loan type)
  - [ ] Set next_payment_due_date
  - [ ] Write tests for student loan generation

- [ ] Implement mortgage generation (AC: 6, 7, 8)
  - [ ] Generate mortgages for high-income profiles
  - [ ] Assign realistic interest rates (2%-12% based on market)
  - [ ] Set next_payment_due_date
  - [ ] Write tests for mortgage generation

### Schema Integration & Validation
- [ ] Integrate with Story 1.2 Liability schemas (AC: 8)
  - [ ] Use CreditCardLiability model from spendsense/db/models.py
  - [ ] Use StudentLoanLiability model
  - [ ] Use MortgageLiability model
  - [ ] Validate all generated liabilities against schemas
  - [ ] Write tests for schema validation

### Consistency with Transaction Data
- [ ] Ensure liability-transaction consistency (AC: 9)
  - [ ] Verify credit card payments in transactions match liability amounts
  - [ ] Validate balances are consistent with spending patterns
  - [ ] Check loan payment transactions exist for active loans
  - [ ] Write tests for data consistency

### Persona-Specific Behavior
- [ ] Implement persona-driven liability patterns (AC: 2, 5, 6)
  - [ ] High Utilization: High balances (60-80% utilization), occasional overdue
  - [ ] Variable Income: Moderate utilization, higher overdue risk
  - [ ] Subscription-Heavy: Moderate credit usage
  - [ ] Savings Builder: Low utilization (<30%), always current
  - [ ] Control: Mixed patterns
  - [ ] Write tests verifying persona behaviors

### Output & Documentation
- [ ] Implement JSON serialization and storage (AC: 8)
  - [ ] Save liabilities to data/synthetic/liabilities/liabilities.json
  - [ ] Organize by user_id for easy lookup
  - [ ] Write tests for save/load functionality

- [ ] Create CLI interface
  - [ ] Command-line tool for liability generation
  - [ ] Accept seed, profiles path, transactions path as arguments
  - [ ] Usage: `python -m spendsense.generators.liability_cli`

- [ ] Create documentation
  - [ ] Document liability generation logic
  - [ ] Provide usage examples
  - [ ] Document integration with profile and transaction generators

## Dev Notes

**Tech Stack:**
- CreditCardLiability, StudentLoanLiability, MortgageLiability from Story 1.2 (spendsense/db/models.py)
- Profile data from Story 1.3 (spendsense/generators/profile_generator.py)
- Transaction data from Story 1.4 for consistency validation
- Decimal for all financial calculations
- JSON for liability storage

**Liability Generation Strategy:**

This story implements **persona-driven liability simulation** that creates realistic debt obligations:

1. **Load user profiles** from Story 1.3 (contains persona, income, accounts, target_credit_utilization)
2. **Load transaction history** from Story 1.4 (for consistency validation)
3. **Generate credit card liabilities** for users with credit accounts
4. **Generate loan liabilities** (student/mortgage) based on profile characteristics
5. **Validate consistency** with transaction payment history
6. **Ensure schema compliance** with all liability models

**Credit Card Liability Fields:**

| Field | Calculation Logic | Example |
|-------|------------------|---------|
| account_id | From profile credit card accounts | "acc_user_001_credit_0" |
| credit_limit | $500-$25K based on income ($income * 0.3 to 0.5) | $15,000 |
| current_balance | limit * target_utilization | $9,000 (60%) |
| aprs | 15%-30% (higher for lower income) | [0.1999] (19.99%) |
| minimum_payment_amount | max(balance * 0.02, $25) | $180 |
| last_payment_amount | From transaction history CC payments | $200 |
| last_statement_balance | Previous month's balance | $8,500 |
| is_overdue | Based on persona (High Util: 10% chance) | false |
| next_payment_due_date | Current date + 15-25 days | 2025-11-20 |

**Student Loan Liability Fields:**

| Field | Logic | Example |
|-------|-------|---------|
| account_id | From profile loan accounts | "acc_user_001_student_0" |
| interest_rate | 3%-8% realistic range | 0.065 (6.5%) |
| next_payment_due_date | Current date + 1 month | 2025-12-04 |

**Mortgage Liability Fields:**

| Field | Logic | Example |
|-------|-------|---------|
| account_id | From profile mortgage accounts | "acc_user_001_mortgage_0" |
| interest_rate | 2%-12% realistic range | 0.045 (4.5%) |
| next_payment_due_date | Current date + 1 month | 2025-12-01 |

**Persona-Specific Patterns:**

- **High Utilization**:
  - Credit limit: Income * 0.4
  - Balance: 60-80% of limit
  - Overdue probability: 10%
  - Minimum payments only

- **Variable Income**:
  - Credit limit: Income * 0.35
  - Balance: 40-60% of limit
  - Overdue probability: 15%
  - Irregular payment amounts

- **Savings Builder**:
  - Credit limit: Income * 0.3
  - Balance: 10-30% of limit
  - Overdue probability: 0%
  - Regular full payments

- **Subscription-Heavy**:
  - Credit limit: Income * 0.35
  - Balance: 30-50% of limit
  - Overdue probability: 5%

- **Control**:
  - Credit limit: Income * 0.35
  - Balance: 20-40% of limit
  - Overdue probability: 2%

**Integration with Previous Stories:**

From Story 1.3 (Profiles):
- Use `target_credit_utilization` characteristic for balance calculation
- Use `annual_income` for credit limit calculation
- Use persona for overdue risk patterns
- Use account list to identify which accounts need liabilities

From Story 1.4 (Transactions):
- Extract credit card payment amounts for `last_payment_amount`
- Validate that payment transactions exist for all liabilities
- Ensure balances are consistent with spending + payments

**Expected Output:**

`data/synthetic/liabilities/liabilities.json`:
```json
{
  "user_MASKED_001": {
    "credit_cards": [
      {
        "account_id": "acc_user_MASKED_001_credit_0",
        "aprs": [0.1999],
        "minimum_payment_amount": 180.0,
        "last_payment_amount": 200.0,
        "last_statement_balance": 8500.0,
        "is_overdue": false,
        "next_payment_due_date": "2025-11-20"
      }
    ],
    "student_loans": [
      {
        "account_id": "acc_user_MASKED_001_student_0",
        "interest_rate": 0.065,
        "next_payment_due_date": "2025-12-04"
      }
    ],
    "mortgages": []
  },
  ...
}
```

### Project Structure Notes

**Directory Alignment:**
- Generator module: `spendsense/generators/liability_generator.py`
- CLI tool: `spendsense/generators/liability_cli.py`
- Output directory: `data/synthetic/liabilities/liabilities.json`
- Tests: `tests/test_liability_generator.py`

**File Organization:**
- Liability generator follows same pattern as Story 1.3 (profiles) and Story 1.4 (transactions)
- CLI follows same argparse pattern
- JSON output follows same structure (dict keyed by user_id)

### Learnings from Previous Story

**From Story 1-4-synthetic-transaction-data-generator (Status: done)**

- **TransactionGenerator Pattern**: `spendsense/generators/transaction_generator.py` - follow same class structure for LiabilityGenerator
- **Account ID Format**: Use `acc_{user_id}_{account_type}_0` pattern established in Story 1.4
- **Decimal Precision**: All financial calculations MUST use Decimal type (not float)
- **CLI Pattern**: Use argparse with --seed, --profiles-path, --transactions-path, --output-path
- **Testing Pattern**: Write comprehensive tests (30+ tests), use averages for persona comparisons
- **Reproducibility**: Implement seed-based randomness with `_reset_random_state()` method
- **JSON Serialization**: Convert Pydantic models to dicts for JSON output
- **Profile Loading**: Profiles are loaded as dicts from JSON (not Pydantic objects)

**Technical Decisions to Apply:**
- Use `Decimal(str(value))` for all calculations involving currency
- Test persona behaviors by comparing averages, not individual users
- Validate against Pydantic schemas before returning data
- Store paths and load on-demand for efficiency

**Files to Reuse:**
- `spendsense/db/models.py`: CreditCardLiability, StudentLoanLiability, MortgageLiability models
- `spendsense/generators/profile_generator.py`: Pattern for loading profiles
- `spendsense/generators/transaction_generator.py`: Pattern for CLI and JSON serialization
- `tests/test_transaction_generator.py`: Testing patterns and fixtures

**Warnings:**
- Payment channel enum uses "in store" with space (not "in_store")
- Use realistic tolerances for validation (not exact values)
- Deduplicate edge cases in tests

[Source: docs/stories/1-4-synthetic-transaction-data-generator.md#Dev-Agent-Record]

### References

- [Epic 1: Story 1.5](docs/prd/epic-1-data-foundation-synthetic-data-generation.md#Story-1.5)
- [Story 1.2: Liability Schemas](docs/stories/1-2-synthetic-data-schema-definition.md)
- [Story 1.3: User Profiles](docs/stories/1-3-synthetic-user-profile-generator.md)
- [Story 1.4: Transaction Generator](docs/stories/1-4-synthetic-transaction-data-generator.md)
- [PRD: FR1 - Synthetic Data Requirements](docs/prd.md#functional-requirements)
- [Architecture: Data Generation](docs/architecture.md#data-sources)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

**Implementation Summary (2025-11-04):**

✅ **All 9 acceptance criteria met:**
- AC1-AC9: All credit card, student loan, and mortgage liability generation working correctly
- All 15 tests passing with comprehensive coverage
- Full schema validation and persona-specific behaviors implemented

**Files Implemented:**
1. `spendsense/generators/liability_generator.py` (371 lines)
   - LiabilityGenerator class with full functionality
   - Credit card liability generation with realistic APRs, limits, and balances
   - Student loan and mortgage generation
   - Persona-specific overdue probabilities
   - Consistency with transaction history for last payment amounts
   - Seed-based reproducibility

2. `spendsense/generators/liability_cli.py` (118 lines)
   - Command-line interface for generating liabilities
   - Arguments: --profiles, --transactions, --output, --seed, --reference-date
   - Summary statistics output

3. `tests/test_liability_generator.py` (533 lines, 15 tests)
   - TestAcceptanceCriteria: 9 tests covering all ACs
   - TestLiabilityGenerator: 4 functional tests
   - TestEdgeCases: 2 edge case tests
   - All tests passing ✓

4. `spendsense/generators/__init__.py` (updated)
   - Added LiabilityGenerator and generate_synthetic_liabilities exports

**Test Results:**
```
15 passed in 0.11s
```

**Key Implementation Details:**
- Credit limits: $500-$25K range based on 30-50% of annual income
- APRs: 15-30% (income-based: lower income = higher APR)
- Minimum payments: 2-3% of balance with $25 minimum
- Overdue probabilities: High Utilization (10%), Variable Income (15%), Savings Builder (0%)
- Student loan rates: 3-8%
- Mortgage rates: 2-12%
- All Decimal calculations for financial precision
- Full Pydantic schema validation

**Generated Output:**
- Location: `data/synthetic/liabilities/liabilities.json`
- Format: Dict keyed by user_id containing credit_cards, student_loans, mortgages arrays
- CLI tested successfully: 100 users, 108 credit cards generated

**Integration:**
- Loads profiles from Story 1.3
- Uses transaction history from Story 1.4 for payment consistency
- Validates against CreditCardLiability, StudentLoanLiability, MortgageLiability schemas from Story 1.2

### File List

- `spendsense/generators/liability_generator.py` - Core liability generator class
- `spendsense/generators/liability_cli.py` - CLI tool for liability generation
- `tests/test_liability_generator.py` - Comprehensive test suite (15 tests)
- `spendsense/generators/__init__.py` - Updated exports
- `data/synthetic/liabilities/liabilities.json` - Generated output

## Change Log

- 2025-11-04: Story created from Epic 1 focusing on persona-driven liability simulation
