# Story 1.6: Data Ingestion & Validation Pipeline

**Epic:** 1 - Data Foundation & Synthetic Data Generation
**Story ID:** 1.6
**Status:** drafted

## Story

As a **developer**,
I want **data ingestion pipeline that loads CSV/JSON files and validates against schemas**,
so that **the system can safely process financial data with guaranteed quality**.

## Acceptance Criteria

1. CSV reader implemented supporting account, transaction, and liability files
2. JSON reader implemented supporting same data structures
3. Schema validation applied to all loaded data using Pydantic models
4. Invalid records logged with specific validation error messages
5. Valid records stored in SQLite database with appropriate schema
6. Valid records also stored in Parquet format for analytics
7. Ingestion process handles missing optional fields gracefully
8. Ingestion logs summary statistics (records processed/valid/invalid)
9. Ingestion can be run via command-line script with file paths as arguments
10. Unit tests cover validation edge cases and error handling

## Tasks/Subtasks

### Ingestion Module Core
- [ ] Implement data ingestion module structure (AC: 1-3)
  - [ ] Create `spendsense/ingestion/__init__.py` module
  - [ ] Implement `DataIngestor` base class with validation framework
  - [ ] Implement CSV reader using `pandas` with type inference
  - [ ] Implement JSON reader with streaming support for large files
  - [ ] Write unit tests for reader implementations

### Schema Validation Integration
- [ ] Integrate Pydantic schema validation (AC: 3, 4, 7)
  - [ ] Use existing models from Story 1.2 (UserProfile, Account, Transaction, Liability schemas)
  - [ ] Implement validation wrapper that catches ValidationError
  - [ ] Log invalid records with field-level error details
  - [ ] Handle optional fields gracefully (use model defaults)
  - [ ] Write tests for validation edge cases (missing fields, wrong types, out-of-range values)

### Database Storage Layer
- [ ] Implement SQLite storage (AC: 5)
  - [ ] Create database schema matching Pydantic models
  - [ ] Implement `DatabaseWriter` class using SQLAlchemy ORM
  - [ ] Create tables: users, accounts, transactions, liabilities
  - [ ] Implement batch insert for performance
  - [ ] Add foreign key constraints (account → user, transaction → account)
  - [ ] Write tests for database operations

### Parquet Export
- [ ] Implement Parquet export for analytics (AC: 6)
  - [ ] Use `pyarrow` to write Parquet files
  - [ ] Create Parquet files: users.parquet, accounts.parquet, transactions.parquet, liabilities.parquet
  - [ ] Preserve schema information in Parquet metadata
  - [ ] Implement partitioning strategy (e.g., by user_id for large datasets)
  - [ ] Write tests for Parquet write/read roundtrip

### Error Handling & Logging
- [ ] Implement comprehensive error handling (AC: 4, 7, 8)
  - [ ] Log validation errors with record context (line number, record ID)
  - [ ] Generate ingestion summary: total records, valid, invalid, skipped
  - [ ] Write invalid records to error log file for review
  - [ ] Handle file I/O errors gracefully (file not found, permissions)
  - [ ] Write tests for error scenarios

### CLI Interface
- [ ] Create command-line ingestion tool (AC: 9)
  - [ ] Implement `spendsense/ingestion/ingest_cli.py`
  - [ ] Arguments: --input (CSV/JSON), --format (csv|json), --output-db, --output-parquet
  - [ ] Support multiple file types: --accounts, --transactions, --liabilities
  - [ ] Add --validate-only flag for dry-run validation
  - [ ] Add --verbose flag for detailed logging
  - [ ] Write integration tests for CLI

### Integration & Testing
- [ ] End-to-end integration testing (AC: 1-10)
  - [ ] Test ingestion of synthetic data from Stories 1.3, 1.4, 1.5
  - [ ] Verify all profiles, accounts, transactions, liabilities load correctly
  - [ ] Test error handling with intentionally malformed data
  - [ ] Validate database integrity (foreign keys, unique constraints)
  - [ ] Verify Parquet files can be read by analytics tools
  - [ ] Performance test with 100+ users, 10,000+ transactions

## Dev Notes

**Tech Stack:**
- Pydantic models from Story 1.2 (`spendsense/db/models.py`)
- SQLAlchemy for database ORM
- SQLite for structured storage
- Pandas for CSV reading
- PyArrow for Parquet export
- JSON module for JSON reading
- Logging module for error tracking

**Data Flow:**
1. **Load**: CSV/JSON → Pandas DataFrame / Python dicts
2. **Validate**: Parse each record through Pydantic models
3. **Store**: Valid records → SQLite + Parquet, Invalid records → Error log
4. **Report**: Summary statistics to console and log file

**Database Schema:**
- `users` table: user_id (PK), persona, annual_income, characteristics (JSON)
- `accounts` table: account_id (PK), user_id (FK), type, subtype, balance
- `transactions` table: transaction_id (PK), account_id (FK), date, amount, merchant, category
- `liabilities` table: liability_id (PK), account_id (FK), type, details (JSON for type-specific fields)

**Parquet Organization:**
```
data/processed/
├── users.parquet
├── accounts.parquet
├── transactions.parquet (partitioned by user_id)
└── liabilities.parquet
```

**Error Log Format:**
```
2025-11-04 12:34:56 | ERROR | transaction | Line 123 | transaction_id=txn_001 | amount: Input should be a valid decimal
2025-11-04 12:34:57 | ERROR | account | Line 456 | account_id=acc_002 | type: Invalid enum value 'checking_account'
```

**Integration with Previous Stories:**
- Story 1.2: Use all Pydantic models (UserProfile, Account, Transaction, CreditCardLiability, StudentLoanLiability, MortgageLiability)
- Story 1.3: Ingest profiles from `data/synthetic/users/profiles.json`
- Story 1.4: Ingest transactions from `data/synthetic/transactions/transactions.json`
- Story 1.5: Ingest liabilities from `data/synthetic/liabilities/liabilities.json`

### Project Structure Notes

**File Alignment:**
```
spendsense/
├── ingestion/
│   ├── __init__.py          # DataIngestor base class, readers, validators
│   ├── csv_reader.py        # CSV ingestion logic
│   ├── json_reader.py       # JSON ingestion logic
│   ├── database_writer.py   # SQLite storage
│   ├── parquet_writer.py    # Parquet export
│   └── ingest_cli.py        # CLI tool
├── db/
│   └── models.py            # Existing Pydantic models (Story 1.2)
tests/
└── test_ingestion.py        # Comprehensive ingestion tests

data/
├── synthetic/               # Source data from generators
│   ├── users/profiles.json
│   ├── transactions/transactions.json
│   └── liabilities/liabilities.json
└── processed/               # Ingested data
    ├── spendsense.db        # SQLite database
    └── parquet/             # Parquet files
```

**Dependencies to Add:**
- `pandas` - CSV reading and data manipulation
- `pyarrow` - Parquet file format
- `sqlalchemy` - Database ORM

### Learnings from Previous Story

**From Story 1-5-synthetic-liability-data-generator (Status: done)**

- **Generator Pattern Established**: All generators follow consistent structure:
  - Core generator class with `generate()` method
  - CLI tool in `generators/{name}_cli.py`
  - Comprehensive tests in `tests/test_{name}_generator.py`
  - Export to `__init__.py` for easy importing

- **Files Available for Reuse**:
  - `spendsense/generators/liability_generator.py` - Generates liabilities at `data/synthetic/liabilities/liabilities.json`
  - `spendsense/generators/transaction_generator.py` - Generates transactions at `data/synthetic/transactions/transactions.json`
  - `spendsense/generators/profile_generator.py` - Generates profiles at `data/synthetic/users/profiles.json`

- **Data Format**: All generators output JSON with structure:
  ```json
  {
    "user_001": { /* user data */ },
    "user_002": { /* user data */ }
  }
  ```

- **Schema Models Available** (from Story 1.2):
  - `UserProfile` - User profile validation
  - `Account` - Account validation
  - `Transaction` - Transaction validation with PersonalFinanceCategory enum
  - `CreditCardLiability`, `StudentLoanLiability`, `MortgageLiability` - Liability validation

- **Testing Pattern**:
  - Use pytest fixtures for sample data
  - Test all acceptance criteria explicitly
  - Include edge case tests
  - Use `tmp_path` fixture for file operations
  - Target: 15-20+ tests for comprehensive coverage

- **Decimal Precision**: All financial calculations must use `Decimal` type, not float
  - Convert on read: `Decimal(str(value))`
  - Maintain precision through calculations
  - Convert to float only for JSON serialization if needed

- **Key Technical Details**:
  - Payment channel uses "in store" with space (not underscore) per Plaid spec
  - PersonalFinanceCategory enum has 80+ values
  - Seed-based reproducibility critical for testing

[Source: docs/stories/1-5-synthetic-liability-data-generator.md#Dev-Agent-Record]

### References

- [Epic 1: Story 1.6](docs/prd/epic-1-data-foundation-synthetic-data-generation.md#Story-1.6)
- [Story 1.2: Schema Definitions](docs/stories/1-2-synthetic-data-schema-definition.md)
- [Story 1.3: Profile Generator](docs/stories/1-3-synthetic-user-profile-generator.md)
- [Story 1.4: Transaction Generator](docs/stories/1-4-synthetic-transaction-data-generator.md)
- [Story 1.5: Liability Generator](docs/stories/1-5-synthetic-liability-data-generator.md)
- [PRD: FR1 - Data Ingestion Requirements](docs/prd.md#functional-requirements)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-04: Story created from Epic 1 focusing on data validation and ingestion pipeline
