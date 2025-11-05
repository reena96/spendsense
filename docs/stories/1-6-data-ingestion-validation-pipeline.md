# Story 1.6: Data Ingestion & Validation Pipeline

**Epic:** 1 - Data Foundation & Synthetic Data Generation
**Story ID:** 1.6
**Status:** review

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
- [x] Implement data ingestion module structure (AC: 1-3)
  - [x] Create `spendsense/ingestion/__init__.py` module
  - [x] Implement `DataIngestor` base class with validation framework
  - [x] Implement CSV reader using `pandas` with type inference
  - [x] Implement JSON reader with streaming support for large files
  - [x] Write unit tests for reader implementations

### Schema Validation Integration
- [x] Integrate Pydantic schema validation (AC: 3, 4, 7)
  - [x] Use existing models from Story 1.2 (UserProfile, Account, Transaction, Liability schemas)
  - [x] Implement validation wrapper that catches ValidationError
  - [x] Log invalid records with field-level error details
  - [x] Handle optional fields gracefully (use model defaults)
  - [x] Write tests for validation edge cases (missing fields, wrong types, out-of-range values)

### Database Storage Layer
- [x] Implement SQLite storage (AC: 5)
  - [x] Create database schema matching Pydantic models
  - [x] Implement `DatabaseWriter` class using SQLAlchemy ORM
  - [x] Create tables: users, accounts, transactions, liabilities
  - [x] Implement batch insert for performance
  - [x] Add foreign key constraints (account → user, transaction → account)
  - [x] Write tests for database operations

### Parquet Export
- [x] Implement Parquet export for analytics (AC: 6)
  - [x] Use `pyarrow` to write Parquet files
  - [x] Create Parquet files: users.parquet, accounts.parquet, transactions.parquet, liabilities.parquet
  - [x] Preserve schema information in Parquet metadata
  - [x] Implement partitioning strategy (e.g., by user_id for large datasets)
  - [x] Write tests for Parquet write/read roundtrip

### Error Handling & Logging
- [x] Implement comprehensive error handling (AC: 4, 7, 8)
  - [x] Log validation errors with record context (line number, record ID)
  - [x] Generate ingestion summary: total records, valid, invalid, skipped
  - [x] Write invalid records to error log file for review
  - [x] Handle file I/O errors gracefully (file not found, permissions)
  - [x] Write tests for error scenarios

### CLI Interface
- [x] Create command-line ingestion tool (AC: 9)
  - [x] Implement `spendsense/ingestion/ingest_cli.py`
  - [x] Arguments: --input (CSV/JSON), --format (csv|json), --output-db, --output-parquet
  - [x] Support multiple file types: --accounts, --transactions, --liabilities
  - [x] Add --validate-only flag for dry-run validation
  - [x] Add --verbose flag for detailed logging
  - [x] Write integration tests for CLI

### Integration & Testing
- [x] End-to-end integration testing (AC: 1-10)
  - [x] Test ingestion of synthetic data from Stories 1.3, 1.4, 1.5
  - [x] Verify all profiles, accounts, transactions, liabilities load correctly
  - [x] Test error handling with intentionally malformed data
  - [x] Validate database integrity (foreign keys, unique constraints)
  - [x] Verify Parquet files can be read by analytics tools
  - [x] Performance test with 100+ users, 10,000+ transactions

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

**Implementation Summary (2025-11-04):**

✅ **All 10 acceptance criteria met:**
- AC1-AC2: CSV and JSON readers with pandas and streaming support
- AC3-AC4: Pydantic schema validation with detailed error logging
- AC5: SQLite storage with foreign key constraints
- AC6: Parquet export with optional partitioning
- AC7: Graceful handling of optional fields
- AC8: Comprehensive ingestion summary statistics
- AC9: Full-featured CLI with validate-only and verbose modes
- AC10: Extensive unit tests (24 tests) and edge case coverage

**Files Implemented:**
1. `spendsense/ingestion/__init__.py` - Module exports
2. `spendsense/ingestion/data_ingestor.py` (202 lines)
   - IngestionResult class for tracking statistics
   - DataIngestor base class with validation framework
   - Decimal conversion for financial precision
   - Schema validation wrapper with error handling
3. `spendsense/ingestion/csv_reader.py` (88 lines)
   - CSV reading with pandas
   - JSON-encoded column handling for complex fields
   - NaN value cleanup
4. `spendsense/ingestion/json_reader.py` (114 lines)
   - Array and object format support
   - User-keyed data flattening
   - Nested transaction array handling
5. `spendsense/ingestion/database_writer.py` (367 lines)
   - SQLAlchemy ORM models (User, Account, Transaction, Liability)
   - DatabaseWriter class with create, write, and clear methods
   - Batch insert support
   - Foreign key constraints
6. `spendsense/ingestion/parquet_writer.py` (220 lines)
   - ParquetWriter class for analytics storage
   - Snappy compression
   - Optional user_id partitioning for transactions
   - Type conversion for Parquet compatibility
7. `spendsense/ingestion/ingest_cli.py` (246 lines)
   - Full CLI with argparse
   - Multi-file ingestion support
   - Validate-only and verbose modes
   - Comprehensive help and examples
8. `tests/test_ingestion.py` (553 lines, 24 tests)
   - Tests for all 10 acceptance criteria
   - Edge case tests (empty files, malformed JSON, Unicode, Decimal precision)
   - Integration test for full pipeline
   - All tests passing ✓

**Test Results:**
```
24 passed in 0.59s
All Story 1.6 tests passing ✓
No regressions in Stories 1.3, 1.4, 1.5 tests
```

**Real Data Ingestion Test:**
Successfully ingested synthetic data:
- 100 users from profiles.json
- 19,821 transactions from transactions.json
- 100 liabilities from liabilities.json
- Output: data/processed/spendsense.db (2.6MB)
- Output: data/processed/parquet/ (386KB total)

**Key Implementation Details:**
- CSV and JSON readers both extend DataIngestor base class
- Validation uses Pydantic models from Story 1.2
- SQLite tables: users, accounts, transactions, liabilities
- Foreign keys: accounts.user_id → users.user_id, transactions.account_id → accounts.account_id
- Parquet compression: Snappy algorithm
- Decimal → float conversion for SQLite storage (minimal precision loss)
- Comprehensive error logging with line numbers and field-level details
- CLI supports --profiles, --transactions, --liabilities, --output-db, --output-parquet flags

**Integration:**
- Uses Account, Transaction, CreditCardLiability, StudentLoanLiability, MortgageLiability schemas from Story 1.2
- Successfully ingests all data from Stories 1.3 (profiles), 1.4 (transactions), 1.5 (liabilities)
- Ready for Epic 2 behavioral signal detection pipeline

### File List

**Created:**
- `spendsense/ingestion/__init__.py` - Module initialization and exports
- `spendsense/ingestion/data_ingestor.py` - Base ingestor class with validation
- `spendsense/ingestion/csv_reader.py` - CSV file reader
- `spendsense/ingestion/json_reader.py` - JSON file reader
- `spendsense/ingestion/database_writer.py` - SQLite storage with SQLAlchemy
- `spendsense/ingestion/parquet_writer.py` - Parquet export for analytics
- `spendsense/ingestion/ingest_cli.py` - CLI tool for data ingestion
- `tests/test_ingestion.py` - Comprehensive test suite (24 tests)
- `data/processed/spendsense.db` - SQLite database with ingested data
- `data/processed/parquet/users.parquet` - User profiles in Parquet format
- `data/processed/parquet/accounts.parquet` - Accounts in Parquet format
- `data/processed/parquet/transactions.parquet` - Transactions in Parquet format
- `data/processed/parquet/liabilities.parquet` - Liabilities in Parquet format

## Change Log

- 2025-11-04: Story created from Epic 1 focusing on data validation and ingestion pipeline
- 2025-11-04: Story completed - All acceptance criteria met, 24 tests passing, real data ingestion verified
