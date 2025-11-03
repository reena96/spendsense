# Epic 1: Data Foundation & Synthetic Data Generation

**Goal:** Establish foundational project infrastructure with version control, dependency management, and testing framework. Build a synthetic data generator producing realistic Plaid-style financial data for 50-100 users with diverse behavioral patterns. Implement data ingestion and validation pipeline ensuring schema compliance and data quality.

## Story 1.1: Project Setup & Infrastructure

As a **developer**,
I want **project scaffolding with repository structure, dependency management, and basic CI/CD configuration**,
so that **the team has a solid foundation for collaborative development with automated testing**.

### Acceptance Criteria

1. Repository initialized with `.gitignore` for Python/Node.js
2. README.md created with project overview and setup instructions
3. Directory structure created matching technical architecture (`ingest/`, `features/`, `personas/`, `recommend/`, `guardrails/`, `ui/`, `eval/`, `docs/`)
4. Dependency file created (`requirements.txt` or `package.json`) with core libraries
5. One-command setup script created and documented in README
6. Basic test framework configured (pytest/jest) with example test
7. Configuration file system established using YAML/JSON
8. Logging framework configured with structured output
9. All setup executes successfully on clean environment

## Story 1.2: Synthetic Data Schema Definition

As a **data engineer**,
I want **comprehensive data schemas matching Plaid's structure for accounts, transactions, and liabilities**,
so that **synthetic data generation and validation can enforce realistic constraints**.

### Acceptance Criteria

1. Account schema defined with fields: account_id, type/subtype, balances (available/current/limit), iso_currency_code, holder_category
2. Transaction schema defined with fields: account_id, date, amount, merchant_name/entity_id, payment_channel, personal_finance_category, pending status
3. Liability schema defined for credit cards: APRs, minimum_payment_amount, last_payment_amount, is_overdue, next_payment_due_date, last_statement_balance
4. Liability schema defined for mortgages/student loans: interest_rate, next_payment_due_date
5. Schema validation rules documented: non-negative balances, chronological order, valid currency codes
6. Schema documentation created in `docs/schemas.md` with examples
7. Schema validation functions implemented and tested
8. Example valid and invalid data created for testing

## Story 1.3: Synthetic User Profile Generator

As a **data engineer**,
I want **generation of 50-100 diverse synthetic user profiles with realistic financial characteristics**,
so that **the system can be tested across varied financial behaviors and demographics**.

### Acceptance Criteria

1. User profile generator creates 50-100 unique users with fake names and masked IDs
2. Profiles include diverse income levels (e.g., $20K-$200K annual range)
3. Profiles include varied credit behaviors (low/medium/high utilization, overdue/current)
4. Profiles include different saving patterns (active savers, minimal savers, no savings)
5. Profiles include varied debt levels (no debt, moderate debt, high debt)
6. Generation uses fixed seed for reproducibility
7. Profile distribution validated for realistic statistical spread
8. Generated profiles stored in JSON format
9. Profile generator documented with usage examples

## Story 1.4: Synthetic Transaction Data Generator

As a **data engineer**,
I want **realistic transaction data generation for each user profile matching their financial characteristics**,
so that **behavioral signals can be accurately detected from transaction patterns**.

### Acceptance Criteria

1. Transaction generator creates realistic monthly spending patterns per user profile
2. Recurring transactions generated for subscriptions (Netflix, gym, utilities) with consistent cadence
3. Income transactions generated with realistic pay cycles (biweekly, monthly, variable)
4. Credit card payments, savings transfers, and bill payments generated
5. Merchant names and categories assigned realistically per transaction type
6. Transaction amounts vary seasonally and by merchant category
7. Date distribution respects user pay cycles and spending patterns
8. Generated data spans 180+ days for long-term pattern detection
9. Transaction data validates against schema successfully

## Story 1.5: Synthetic Liability Data Generator

As a **data engineer**,
I want **realistic liability data generation including credit cards and loans matching user profiles**,
so that **credit utilization and debt signals can be accurately calculated**.

### Acceptance Criteria

1. Credit card data generated with realistic limits ($500-$25,000 range)
2. Credit card balances set based on user profile utilization targets
3. APR rates assigned realistically (15%-30% range)
4. Minimum payment amounts calculated correctly (typically 2-3% of balance)
5. Overdue status and payment history generated based on profile
6. Student loan and mortgage data generated for applicable profiles
7. Interest rates match realistic market conditions
8. All liability data validates against schema
9. Liability data consistent with transaction history

## Story 1.6: Data Ingestion & Validation Pipeline

As a **developer**,
I want **data ingestion pipeline that loads CSV/JSON files and validates against schemas**,
so that **the system can safely process financial data with guaranteed quality**.

### Acceptance Criteria

1. CSV reader implemented supporting account, transaction, and liability files
2. JSON reader implemented supporting same data structures
3. Schema validation applied to all loaded data
4. Invalid records logged with specific validation error messages
5. Valid records stored in SQLite database with appropriate schema
6. Valid records also stored in Parquet format for analytics
7. Ingestion process handles missing optional fields gracefully
8. Ingestion logs summary statistics (records processed/valid/invalid)
9. Ingestion can be run via command-line script with file paths as arguments
10. Unit tests cover validation edge cases and error handling

---
