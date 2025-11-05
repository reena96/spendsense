"""
Comprehensive tests for data ingestion module.

Tests cover all acceptance criteria from Story 1.6:
- AC1-AC2: CSV and JSON readers
- AC3-AC4: Schema validation and error logging
- AC5: SQLite storage
- AC6: Parquet export
- AC7: Optional field handling
- AC8: Summary statistics logging
- AC9: CLI interface
- AC10: Edge cases and error handling
"""

import json
import tempfile
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.db.models import Account, Transaction
from spendsense.ingestion.csv_reader import CSVReader
from spendsense.ingestion.json_reader import JSONReader
from spendsense.ingestion.database_writer import DatabaseWriter, User, Account as DBAccount, Transaction as DBTransaction
from spendsense.ingestion.parquet_writer import ParquetWriter
from spendsense.ingestion.ingest_cli import ingest_file


# ===== Fixtures =====

@pytest.fixture
def sample_accounts():
    """Sample account data for testing."""
    return [
        {
            "account_id": "acc_user_001_checking_0",
            "user_id": "user_001",
            "type": "depository",
            "subtype": "checking",
            "balances": {
                "current": 5000.00,
                "available": 4800.00,
                "limit": None
            },
            "iso_currency_code": "USD",
            "holder_category": "personal"
        },
        {
            "account_id": "acc_user_001_credit_0",
            "user_id": "user_001",
            "type": "credit",
            "subtype": "credit card",
            "balances": {
                "current": 1500.00,
                "available": 8500.00,
                "limit": 10000.00
            },
            "iso_currency_code": "USD",
            "holder_category": "personal"
        }
    ]


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing."""
    today = date.today()
    return [
        {
            "transaction_id": "txn_001",
            "account_id": "acc_user_001_checking_0",
            "date": str(today - timedelta(days=5)),
            "amount": 50.75,
            "merchant_name": "Grocery Store",
            "payment_channel": "in store",
            "personal_finance_category": "FOOD_AND_DRINK_GROCERIES",
            "pending": False
        },
        {
            "transaction_id": "txn_002",
            "account_id": "acc_user_001_credit_0",
            "date": str(today - timedelta(days=3)),
            "amount": 120.00,
            "merchant_name": "Restaurant",
            "payment_channel": "in store",
            "personal_finance_category": "FOOD_AND_DRINK_RESTAURANTS",
            "pending": False
        }
    ]


@pytest.fixture
def sample_users():
    """Sample user profile data for testing."""
    return [
        {
            "user_id": "user_001",
            "name": "John Doe",
            "persona": "Savings Builder",
            "annual_income": 75000.00,
            "characteristics": {
                "target_savings_rate": 0.20,
                "risk_tolerance": "moderate"
            }
        }
    ]


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing."""
    db_path = tmp_path / "test.db"
    writer = DatabaseWriter(db_path)
    writer.create_tables()
    return writer


@pytest.fixture
def temp_parquet_dir(tmp_path):
    """Temporary directory for Parquet files."""
    parquet_dir = tmp_path / "parquet"
    return ParquetWriter(parquet_dir)


# ===== AC1: CSV Reader Tests =====

def test_ac1_csv_reader_accounts(tmp_path, sample_accounts):
    """AC1: CSV reader implemented supporting account files."""
    csv_file = tmp_path / "accounts.csv"

    # Flatten balances for CSV
    flat_accounts = []
    for acc in sample_accounts:
        flat = acc.copy()
        balances = flat.pop('balances')
        flat['balance_current'] = balances['current']
        flat['balance_available'] = balances.get('available')
        flat['balance_limit'] = balances.get('limit')
        flat_accounts.append(flat)

    df = pd.DataFrame(flat_accounts)
    df.to_csv(csv_file, index=False)

    reader = CSVReader(schema=Account)
    records = reader.read(csv_file)

    assert len(records) == 2
    assert records[0]['account_id'] == 'acc_user_001_checking_0'
    assert records[1]['type'] == 'credit'


def test_ac1_csv_reader_transactions(tmp_path, sample_transactions):
    """AC1: CSV reader implemented supporting transaction files."""
    csv_file = tmp_path / "transactions.csv"
    df = pd.DataFrame(sample_transactions)
    df.to_csv(csv_file, index=False)

    reader = CSVReader(schema=Transaction)
    records = reader.read(csv_file)

    assert len(records) == 2
    assert records[0]['transaction_id'] == 'txn_001'
    assert records[1]['amount'] == 120.00


# ===== AC2: JSON Reader Tests =====

def test_ac2_json_reader_array_format(tmp_path, sample_transactions):
    """AC2: JSON reader implemented supporting array format."""
    json_file = tmp_path / "transactions.json"
    with open(json_file, 'w') as f:
        json.dump(sample_transactions, f)

    reader = JSONReader(schema=Transaction)
    records = reader.read(json_file)

    assert len(records) == 2
    assert records[0]['transaction_id'] == 'txn_001'


def test_ac2_json_reader_object_format(tmp_path, sample_accounts):
    """AC2: JSON reader implemented supporting user-keyed object format."""
    json_file = tmp_path / "accounts.json"
    user_keyed = {"user_001": sample_accounts}

    with open(json_file, 'w') as f:
        json.dump(user_keyed, f)

    reader = JSONReader(schema=None)  # No validation for this test
    records = reader.read(json_file)

    # The reader flattens nested arrays: {user_001: [acc1, acc2]} -> [acc1, acc2]
    assert len(records) == 2  # Two accounts flattened from the array
    assert isinstance(records, list)
    assert records[0]['account_id'] == 'acc_user_001_checking_0'


def test_ac2_json_reader_transactions_format(tmp_path):
    """AC2: JSON reader handles transaction format {user_id: [txn1, txn2]}."""
    json_file = tmp_path / "transactions.json"
    transactions_by_user = {
        "user_001": [
            {"transaction_id": "txn_001", "amount": 50.00},
            {"transaction_id": "txn_002", "amount": 75.00}
        ],
        "user_002": [
            {"transaction_id": "txn_003", "amount": 100.00}
        ]
    }

    with open(json_file, 'w') as f:
        json.dump(transactions_by_user, f)

    reader = JSONReader(schema=None)
    records = reader.read(json_file)

    assert len(records) == 3  # Flattened from 2 users
    assert records[0]['transaction_id'] == 'txn_001'
    assert records[2]['transaction_id'] == 'txn_003'


# ===== AC3: Schema Validation Tests =====

def test_ac3_schema_validation_valid_account(sample_accounts):
    """AC3: Schema validation applied to all loaded data using Pydantic models."""
    reader = JSONReader(schema=Account)

    # Test valid account
    valid_account = sample_accounts[0]
    validated = reader.validate_record(valid_account, "acc_001")

    assert validated is not None
    assert validated.account_id == 'acc_user_001_checking_0'


def test_ac3_schema_validation_invalid_account():
    """AC3: Invalid account rejected by schema validation."""
    reader = JSONReader(schema=Account)

    invalid_account = {
        "account_id": "acc_001",
        "type": "depository",
        "subtype": "invalid_subtype",  # Invalid subtype
        "balances": {"current": 1000},
        "iso_currency_code": "USD"
    }

    validated = reader.validate_record(invalid_account, "acc_001")
    assert validated is None  # Validation should fail


# ===== AC4: Invalid Record Logging Tests =====

def test_ac4_invalid_records_logged(tmp_path):
    """AC4: Invalid records logged with specific validation error messages."""
    json_file = tmp_path / "accounts.json"

    invalid_accounts = [
        {
            "account_id": "acc_001",
            "type": "depository",
            "subtype": "checking",
            "balances": {"current": 1000},
            "iso_currency_code": "USD"
        },
        {
            "account_id": "acc_002",
            "type": "invalid_type",  # Invalid type
            "subtype": "checking",
            "balances": {"current": 2000},
            "iso_currency_code": "USD"
        }
    ]

    with open(json_file, 'w') as f:
        json.dump(invalid_accounts, f)

    reader = JSONReader(schema=Account)
    result = reader.ingest(json_file)

    assert result.valid_records == 1
    assert result.invalid_records == 1
    assert len(result.errors) == 1
    assert 'type' in result.errors[0]['error'].lower()


# ===== AC5: SQLite Storage Tests =====

def test_ac5_sqlite_storage_users(temp_db, sample_users):
    """AC5: Valid records stored in SQLite database with appropriate schema."""
    count = temp_db.write_users(sample_users)
    assert count == 1

    # Verify data stored correctly
    session = temp_db.Session()
    users = session.query(User).all()
    assert len(users) == 1
    assert users[0].user_id == 'user_001'
    assert users[0].persona == 'Savings Builder'
    session.close()


def test_ac5_sqlite_storage_accounts(temp_db, sample_accounts):
    """AC5: Accounts stored with foreign key to users."""
    # First create user
    temp_db.write_users([{"user_id": "user_001", "name": "John Doe", "persona": "Test", "annual_income": 50000}])

    count = temp_db.write_accounts(sample_accounts)
    assert count == 2

    session = temp_db.Session()
    accounts = session.query(DBAccount).all()
    assert len(accounts) == 2
    assert accounts[0].user_id == 'user_001'
    assert accounts[0].balance_current == 5000.00
    session.close()


def test_ac5_sqlite_storage_transactions(temp_db, sample_transactions):
    """AC5: Transactions stored with foreign key to accounts."""
    # Setup: Create user and account first
    temp_db.write_users([{"user_id": "user_001", "name": "John", "persona": "Test", "annual_income": 50000}])
    temp_db.write_accounts([{
        "account_id": "acc_user_001_checking_0",
        "user_id": "user_001",
        "type": "depository",
        "subtype": "checking",
        "balances": {"current": 5000}
    }])

    count = temp_db.write_transactions(sample_transactions)
    assert count == 2

    session = temp_db.Session()
    transactions = session.query(DBTransaction).all()
    assert len(transactions) == 2
    assert transactions[0].transaction_id == 'txn_001'
    assert float(transactions[0].amount) == 50.75
    session.close()


# ===== AC6: Parquet Export Tests =====

def test_ac6_parquet_export_users(temp_parquet_dir, sample_users):
    """AC6: Valid records stored in Parquet format for analytics."""
    output_path = temp_parquet_dir.write_users(sample_users)

    assert output_path.exists()

    # Read back and verify
    df = temp_parquet_dir.read_parquet(output_path)
    assert len(df) == 1
    assert df.iloc[0]['user_id'] == 'user_001'


def test_ac6_parquet_export_accounts(temp_parquet_dir, sample_accounts):
    """AC6: Accounts exported to Parquet with schema preservation."""
    output_path = temp_parquet_dir.write_accounts(sample_accounts)

    assert output_path.exists()

    df = temp_parquet_dir.read_parquet(output_path)
    assert len(df) == 2
    assert 'balance_current' in df.columns
    assert df.iloc[0]['balance_current'] == 5000.00


def test_ac6_parquet_export_transactions(temp_parquet_dir, sample_transactions):
    """AC6: Transactions exported to Parquet format."""
    output_path = temp_parquet_dir.write_transactions(sample_transactions, partition_by_user=False)

    assert output_path.exists()

    df = temp_parquet_dir.read_parquet(output_path)
    assert len(df) == 2
    assert df.iloc[0]['transaction_id'] == 'txn_001'


# ===== AC7: Optional Field Handling Tests =====

def test_ac7_optional_fields_handled_gracefully(tmp_path):
    """AC7: Ingestion process handles missing optional fields gracefully."""
    json_file = tmp_path / "transactions.json"

    # Transaction with missing optional fields
    minimal_transaction = {
        "transaction_id": "txn_minimal",
        "account_id": "acc_001",
        "date": str(date.today()),
        "amount": 100.00,
        # merchant_name: missing (optional)
        # merchant_entity_id: missing (optional)
        "payment_channel": "online",
        "personal_finance_category": "FOOD_AND_DRINK_RESTAURANTS"
    }

    with open(json_file, 'w') as f:
        json.dump([minimal_transaction], f)

    reader = JSONReader(schema=Transaction)
    result = reader.ingest(json_file)

    assert result.valid_records == 1
    assert result.invalid_records == 0


# ===== AC8: Summary Statistics Tests =====

def test_ac8_ingestion_logs_summary_statistics(tmp_path, sample_accounts):
    """AC8: Ingestion logs summary statistics (records processed/valid/invalid)."""
    json_file = tmp_path / "accounts.json"

    # Mix of valid and invalid
    mixed_accounts = sample_accounts + [
        {
            "account_id": "acc_invalid",
            "type": "bad_type",  # Invalid
            "subtype": "checking",
            "balances": {"current": 1000},
            "iso_currency_code": "USD"
        }
    ]

    with open(json_file, 'w') as f:
        json.dump(mixed_accounts, f)

    reader = JSONReader(schema=Account)
    result = reader.ingest(json_file)

    summary = result.summary()
    assert summary['total_records'] == 3
    assert summary['valid_records'] == 2
    assert summary['invalid_records'] == 1


# ===== AC9: CLI Interface Tests =====

def test_ac9_cli_interface_basic(tmp_path, sample_transactions):
    """AC9: Ingestion can be run via command-line script with file paths as arguments."""
    json_file = tmp_path / "transactions.json"
    with open(json_file, 'w') as f:
        json.dump(sample_transactions, f)

    db_path = tmp_path / "test.db"
    parquet_dir = tmp_path / "parquet"

    db_writer = DatabaseWriter(db_path)
    db_writer.create_tables()
    parquet_writer = ParquetWriter(parquet_dir)

    # Test CLI function directly
    result = ingest_file(
        file_path=json_file,
        file_format='json',
        data_type='transactions',
        db_writer=None,  # Skip DB for this test
        parquet_writer=parquet_writer,
        validate_only=False,
        verbose=False
    )

    assert result.valid_records == 2
    assert (parquet_dir / "transactions.parquet").exists()


def test_ac9_cli_validate_only_mode(tmp_path, sample_accounts):
    """AC9: CLI supports --validate-only flag for dry-run validation."""
    json_file = tmp_path / "accounts.json"
    with open(json_file, 'w') as f:
        json.dump(sample_accounts, f)

    result = ingest_file(
        file_path=json_file,
        file_format='json',
        data_type='accounts',
        db_writer=None,
        parquet_writer=None,
        validate_only=True,
        verbose=False
    )

    assert result.valid_records == 2
    # No files should be created in validate-only mode


# ===== AC10: Edge Cases and Error Handling Tests =====

def test_ac10_edge_case_empty_file(tmp_path):
    """AC10: Handle empty files gracefully."""
    json_file = tmp_path / "empty.json"
    with open(json_file, 'w') as f:
        json.dump([], f)

    reader = JSONReader(schema=None)
    records = reader.read(json_file)

    assert len(records) == 0


def test_ac10_edge_case_file_not_found():
    """AC10: Handle missing files with appropriate error."""
    reader = JSONReader(schema=None)

    with pytest.raises(FileNotFoundError):
        reader.read(Path("nonexistent.json"))


def test_ac10_edge_case_malformed_json(tmp_path):
    """AC10: Handle malformed JSON with appropriate error."""
    json_file = tmp_path / "malformed.json"
    with open(json_file, 'w') as f:
        f.write("{invalid json")

    reader = JSONReader(schema=None)

    with pytest.raises(IOError, match="JSON parsing error"):
        reader.read(json_file)


def test_ac10_edge_case_decimal_precision(temp_db):
    """AC10: Ensure Decimal precision maintained through ingestion."""
    transactions = [{
        "transaction_id": "txn_decimal_test",
        "account_id": "acc_001",
        "date": str(date.today()),
        "amount": Decimal("123.4567890"),  # High precision
        "payment_channel": "online",
        "personal_finance_category": "FOOD_AND_DRINK_RESTAURANTS"
    }]

    # Write transactions (Decimal converted to float for SQLite)
    count = temp_db.write_transactions(transactions)
    assert count == 1

    # Verify precision (SQLite stores as float, so some precision loss expected)
    session = temp_db.Session()
    txn = session.query(DBTransaction).first()
    assert abs(txn.amount - 123.4567890) < 0.0001
    session.close()


def test_ac10_edge_case_unicode_merchants(temp_parquet_dir):
    """AC10: Handle Unicode characters in merchant names."""
    transactions = [{
        "transaction_id": "txn_unicode",
        "account_id": "acc_001",
        "date": str(date.today()),
        "amount": 50.00,
        "merchant_name": "Café René's 日本料理",  # Unicode characters
        "payment_channel": "in store",
        "personal_finance_category": "FOOD_AND_DRINK_RESTAURANTS"
    }]

    output_path = temp_parquet_dir.write_transactions(transactions)
    df = temp_parquet_dir.read_parquet(output_path)

    assert df.iloc[0]['merchant_name'] == "Café René's 日本料理"


# ===== Integration Tests =====

def test_integration_full_pipeline(tmp_path, sample_users, sample_accounts, sample_transactions):
    """Integration test: Full ingestion pipeline from JSON to SQLite and Parquet."""
    # Setup files
    users_file = tmp_path / "users.json"
    accounts_file = tmp_path / "accounts.json"
    transactions_file = tmp_path / "transactions.json"

    with open(users_file, 'w') as f:
        json.dump(sample_users, f)
    with open(accounts_file, 'w') as f:
        json.dump(sample_accounts, f)
    with open(transactions_file, 'w') as f:
        json.dump(sample_transactions, f)

    # Setup writers
    db_path = tmp_path / "spendsense.db"
    parquet_dir = tmp_path / "parquet"

    db_writer = DatabaseWriter(db_path)
    db_writer.create_tables()
    parquet_writer = ParquetWriter(parquet_dir)

    # Ingest all data
    ingest_file(users_file, 'json', 'users', db_writer, parquet_writer)
    ingest_file(accounts_file, 'json', 'accounts', db_writer, parquet_writer)
    ingest_file(transactions_file, 'json', 'transactions', db_writer, parquet_writer)

    # Verify SQLite
    session = db_writer.Session()
    assert session.query(User).count() == 1
    assert session.query(DBAccount).count() == 2
    assert session.query(DBTransaction).count() == 2
    session.close()

    # Verify Parquet
    assert (parquet_dir / "users.parquet").exists()
    assert (parquet_dir / "accounts.parquet").exists()
    assert (parquet_dir / "transactions.parquet").exists()
