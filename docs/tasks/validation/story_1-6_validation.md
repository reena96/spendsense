# Story 1.6 Validation - Data Ingestion & Validation Pipeline

## Automated Checks ✅

- ✅ **Tests**: 24/24 passed in 0.63s
- ✅ **SQLite Database**: spendsense.db created (2.6MB)
- ✅ **Parquet Files**: 3 files created (386KB total)
  - users.parquet (11KB)
  - transactions.parquet (365KB)
  - liabilities.parquet (10KB)
- ✅ **CSV/JSON Readers**: Both formats validated
- ✅ **Schema Validation**: Pydantic models enforced
- ✅ **Error Handling**: Invalid records logged correctly

## Manual Steps 🔍

**IMPORTANT:** Activate virtual environment first:
```bash
source venv/bin/activate
```

### 1. Verify Database Contents

```bash
# Check SQLite database tables and counts
sqlite3 data/processed/spendsense.db <<EOF
.tables
SELECT COUNT(*) as user_count FROM users;
SELECT COUNT(*) as account_count FROM accounts;
SELECT COUNT(*) as transaction_count FROM transactions;
SELECT COUNT(*) as liability_count FROM liabilities;
.quit
EOF
```

Verify:
- [ ] All 4 tables exist (users, accounts, transactions, liabilities)
- [ ] 100 users loaded
- [ ] ~19,821 transactions loaded
- [ ] 100 liability records loaded
- [ ] No SQLite errors

### 2. Validate Parquet Files

```bash
# Read and verify Parquet files
python -c "
import pandas as pd

users = pd.read_parquet('data/processed/parquet/users.parquet')
print(f'Users in Parquet: {len(users)}')
print(users.head())

txns = pd.read_parquet('data/processed/parquet/transactions.parquet')
print(f'\nTransactions in Parquet: {len(txns)}')
print(txns.head())

liabs = pd.read_parquet('data/processed/parquet/liabilities.parquet')
print(f'\nLiabilities in Parquet: {len(liabs)}')
print(liabs.head())
"
```

Verify:
- [ ] Parquet files readable without errors
- [ ] Record counts match SQLite database
- [ ] Data types preserved correctly (Decimal → float)
- [ ] Column names match schema

### 3. Test CLI Tool

```bash
# Test ingestion with validate-only mode
python -m spendsense.ingestion.ingest_cli \
  --profiles data/synthetic/users/profiles.json \
  --transactions data/synthetic/transactions/transactions.json \
  --liabilities data/synthetic/liabilities/liabilities.json \
  --validate-only \
  --verbose
```

Verify:
- [ ] Validation runs without errors
- [ ] Summary shows: X total records, Y valid, Z invalid
- [ ] Verbose mode shows detailed processing info

### 4. Test Error Handling

```bash
# Create malformed test data
echo '{"user_001": {"invalid": "data"}}' > /tmp/bad_profiles.json

# Run ingestion - should log errors gracefully
python -m spendsense.ingestion.ingest_cli \
  --profiles /tmp/bad_profiles.json \
  --output-db /tmp/test.db \
  --verbose
```

Verify:
- [ ] Invalid records logged with specific error messages
- [ ] Process completes without crashes
- [ ] Summary shows invalid record count
- [ ] Error messages include field-level details

### 5. Verify Foreign Key Constraints

```bash
# Check database referential integrity
sqlite3 data/processed/spendsense.db <<EOF
PRAGMA foreign_keys = ON;
-- Try to insert invalid reference (should fail)
INSERT INTO accounts (account_id, user_id, type, subtype, balance)
VALUES ('test', 'nonexistent_user', 'depository', 'checking', 1000.00);
.quit
EOF
```

Verify:
- [ ] Foreign key constraint prevents invalid insert
- [ ] Error message: "FOREIGN KEY constraint failed"

**Done!** Story 1.6 ready for review.
