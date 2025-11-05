"""
Unit tests for SpendSense validation functions.

Tests cover individual and batch validation for accounts, transactions,
and liabilities, plus chronological order validation.
"""

import pytest
import json
from pathlib import Path
from datetime import date

from spendsense.db.validators import (
    validate_account,
    validate_transaction,
    validate_liability,
    validate_accounts_batch,
    validate_transactions_batch,
    validate_liabilities_batch,
    validate_chronological_order,
    ValidationResult
)


# ===== Single Record Validation Tests =====

@pytest.mark.unit
class TestAccountValidation:
    """Tests for validate_account function."""

    def test_valid_account_passes(self):
        """Test that a valid account passes validation."""
        account_data = {
            "account_id": "acc_123",
            "type": "depository",
            "subtype": "checking",
            "balances": {
                "available": 1000.00,
                "current": 1200.00
            },
            "iso_currency_code": "USD"
        }
        result = validate_account(account_data)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_invalid_account_fails(self):
        """Test that an invalid account fails validation."""
        account_data = {
            "account_id": "acc_INVALID",
            "type": "depository",
            "subtype": "checking",
            "balances": {
                "available": -100.00,  # Negative balance
                "current": -50.00
            },
            "iso_currency_code": "USD"
        }
        result = validate_account(account_data)
        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("negative" in err.lower() for err in result.errors)

    def test_missing_required_field(self):
        """Test that missing required fields are caught."""
        account_data = {
            # Missing account_id
            "type": "depository",
            "subtype": "savings",
            "balances": {"current": 500.00},
            "iso_currency_code": "USD"
        }
        result = validate_account(account_data)
        assert result.is_valid is False
        assert any("account_id" in err for err in result.errors)


@pytest.mark.unit
class TestTransactionValidation:
    """Tests for validate_transaction function."""

    def test_valid_transaction_passes(self):
        """Test that a valid transaction passes validation."""
        txn_data = {
            "transaction_id": "txn_001",
            "account_id": "acc_123",
            "date": "2024-11-04",
            "amount": 45.67,
            "payment_channel": "in store",
            "personal_finance_category": "FOOD_AND_DRINK"
        }
        result = validate_transaction(txn_data)
        assert result.is_valid is True

    def test_invalid_category_fails(self):
        """Test that invalid category is caught."""
        txn_data = {
            "transaction_id": "txn_INVALID",
            "account_id": "acc_123",
            "date": "2024-11-04",
            "amount": 50.00,
            "payment_channel": "online",
            "personal_finance_category": "SHOPPING"  # Invalid
        }
        result = validate_transaction(txn_data)
        assert result.is_valid is False
        assert any("personal_finance_category" in err for err in result.errors)


@pytest.mark.unit
class TestLiabilityValidation:
    """Tests for validate_liability function."""

    def test_valid_credit_card_liability_passes(self):
        """Test that a valid credit card liability passes validation."""
        liability_data = {
            "account_id": "acc_CC_123",
            "aprs": [0.1999],
            "minimum_payment_amount": 75.00,
            "last_statement_balance": 2500.00
        }
        result = validate_liability(liability_data, liability_type="credit_card")
        assert result.is_valid is True

    def test_valid_mortgage_liability_passes(self):
        """Test that a valid mortgage liability passes validation."""
        liability_data = {
            "account_id": "acc_MORT_123",
            "interest_rate": 0.045
        }
        result = validate_liability(liability_data, liability_type="mortgage")
        assert result.is_valid is True

    def test_valid_student_loan_liability_passes(self):
        """Test that a valid student loan liability passes validation."""
        liability_data = {
            "account_id": "acc_SL_123",
            "interest_rate": 0.055
        }
        result = validate_liability(liability_data, liability_type="student_loan")
        assert result.is_valid is True

    def test_invalid_liability_type_raises_error(self):
        """Test that invalid liability type raises ValueError."""
        liability_data = {"account_id": "acc_123"}
        with pytest.raises(ValueError) as exc_info:
            validate_liability(liability_data, liability_type="invalid_type")
        assert "Invalid liability_type" in str(exc_info.value)

    def test_credit_card_apr_out_of_range_fails(self):
        """Test that APR out of range fails validation."""
        liability_data = {
            "account_id": "acc_CC_INVALID",
            "aprs": [1.50],  # 150% - too high
            "minimum_payment_amount": 50.00,
            "last_statement_balance": 1000.00
        }
        result = validate_liability(liability_data, liability_type="credit_card")
        assert result.is_valid is False


# ===== Batch Validation Tests =====

@pytest.mark.unit
class TestBatchValidation:
    """Tests for batch validation functions."""

    def test_validate_accounts_batch_all_valid(self):
        """Test batch validation with all valid accounts."""
        accounts = [
            {
                "account_id": f"acc_{i}",
                "type": "depository",
                "subtype": "checking",
                "balances": {"current": 1000.00},
                "iso_currency_code": "USD"
            }
            for i in range(5)
        ]
        valid, invalid = validate_accounts_batch(accounts)
        assert len(valid) == 5
        assert len(invalid) == 0

    def test_validate_accounts_batch_mixed_validity(self):
        """Test batch validation with mix of valid and invalid accounts."""
        accounts = [
            {  # Valid
                "account_id": "acc_1",
                "type": "depository",
                "subtype": "checking",
                "balances": {"current": 1000.00},
                "iso_currency_code": "USD"
            },
            {  # Invalid - negative balance
                "account_id": "acc_2",
                "type": "depository",
                "subtype": "savings",
                "balances": {"current": -500.00},
                "iso_currency_code": "USD"
            },
            {  # Valid
                "account_id": "acc_3",
                "type": "credit",
                "subtype": "credit card",
                "balances": {"current": 2000.00, "limit": 5000.00},
                "iso_currency_code": "USD"
            }
        ]
        valid, invalid = validate_accounts_batch(accounts)
        assert len(valid) == 2
        assert len(invalid) == 1
        assert invalid[0][0] == 1  # Index of invalid account

    def test_validate_transactions_batch(self):
        """Test batch validation for transactions."""
        transactions = [
            {
                "transaction_id": "txn_1",
                "account_id": "acc_123",
                "date": "2024-11-04",
                "amount": 50.00,
                "payment_channel": "online",
                "personal_finance_category": "FOOD_AND_DRINK"
            },
            {  # Invalid - bad category
                "transaction_id": "txn_2",
                "account_id": "acc_123",
                "date": "2024-11-04",
                "amount": 30.00,
                "payment_channel": "online",
                "personal_finance_category": "INVALID_CAT"
            }
        ]
        valid, invalid = validate_transactions_batch(transactions)
        assert len(valid) == 1
        assert len(invalid) == 1

    def test_validate_liabilities_batch(self):
        """Test batch validation for liabilities."""
        liabilities = [
            ({
                "account_id": "acc_CC_1",
                "aprs": [0.1999],
                "minimum_payment_amount": 75.00,
                "last_statement_balance": 2500.00
            }, "credit_card"),
            ({
                "account_id": "acc_MORT_1",
                "interest_rate": 0.045
            }, "mortgage"),
            ({  # Invalid - rate too high
                "account_id": "acc_SL_INVALID",
                "interest_rate": 0.10
            }, "student_loan")
        ]
        valid, invalid = validate_liabilities_batch(liabilities)
        assert len(valid) == 2
        assert len(invalid) == 1


# ===== Chronological Order Validation Tests =====

@pytest.mark.unit
class TestChronologicalOrderValidation:
    """Tests for validate_chronological_order function."""

    def test_chronological_transactions_pass(self):
        """Test that transactions in chronological order pass."""
        transactions = [
            {"date": "2024-11-01", "amount": 100.00},
            {"date": "2024-11-02", "amount": 50.00},
            {"date": "2024-11-04", "amount": 75.00}
        ]
        result = validate_chronological_order(transactions)
        assert result.is_valid is True

    def test_non_chronological_transactions_fail(self):
        """Test that transactions not in chronological order fail."""
        transactions = [
            {"date": "2024-11-04", "amount": 100.00},
            {"date": "2024-11-02", "amount": 50.00},  # Out of order
            {"date": "2024-11-05", "amount": 75.00}
        ]
        result = validate_chronological_order(transactions)
        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_same_date_transactions_pass(self):
        """Test that multiple transactions on same date pass."""
        transactions = [
            {"date": "2024-11-04", "amount": 100.00},
            {"date": "2024-11-04", "amount": 50.00},
            {"date": "2024-11-04", "amount": 75.00}
        ]
        result = validate_chronological_order(transactions)
        assert result.is_valid is True

    def test_empty_transaction_list_passes(self):
        """Test that empty list passes validation."""
        result = validate_chronological_order([])
        assert result.is_valid is True

    def test_single_transaction_passes(self):
        """Test that single transaction passes validation."""
        result = validate_chronological_order([{"date": "2024-11-04"}])
        assert result.is_valid is True

    def test_missing_date_field_fails(self):
        """Test that missing date field fails validation."""
        transactions = [
            {"amount": 100.00},  # Missing date
            {"date": "2024-11-04", "amount": 50.00}
        ]
        result = validate_chronological_order(transactions)
        assert result.is_valid is False


# ===== Example File Validation Tests =====

@pytest.mark.unit
class TestExampleFileValidation:
    """Tests using example JSON files."""

    def test_valid_accounts_example_file(self):
        """Test that example_valid_accounts.json passes validation."""
        file_path = Path("data/synthetic/example_valid_accounts.json")
        if not file_path.exists():
            pytest.skip("Example file not found")

        with open(file_path) as f:
            accounts = json.load(f)

        valid, invalid = validate_accounts_batch(accounts)
        assert len(valid) == len(accounts)
        assert len(invalid) == 0

    def test_valid_transactions_example_file(self):
        """Test that example_valid_transactions.json passes validation."""
        file_path = Path("data/synthetic/example_valid_transactions.json")
        if not file_path.exists():
            pytest.skip("Example file not found")

        with open(file_path) as f:
            transactions = json.load(f)

        valid, invalid = validate_transactions_batch(transactions)
        assert len(valid) == len(transactions)
        assert len(invalid) == 0

    def test_valid_liabilities_example_file(self):
        """Test that example_valid_liabilities.json passes validation."""
        file_path = Path("data/synthetic/example_valid_liabilities.json")
        if not file_path.exists():
            pytest.skip("Example file not found")

        with open(file_path) as f:
            liabilities_data = json.load(f)

        liabilities = [(item["data"], item["liability_type"]) for item in liabilities_data]
        valid, invalid = validate_liabilities_batch(liabilities)
        assert len(valid) == len(liabilities)
        assert len(invalid) == 0

    def test_invalid_accounts_example_file(self):
        """Test that example_invalid_accounts.json fails validation."""
        file_path = Path("data/synthetic/example_invalid_accounts.json")
        if not file_path.exists():
            pytest.skip("Example file not found")

        with open(file_path) as f:
            accounts = json.load(f)

        valid, invalid = validate_accounts_batch(accounts)
        # All examples should be invalid
        assert len(invalid) > 0

    def test_invalid_transactions_example_file(self):
        """Test that example_invalid_transactions.json fails validation."""
        file_path = Path("data/synthetic/example_invalid_transactions.json")
        if not file_path.exists():
            pytest.skip("Example file not found")

        with open(file_path) as f:
            transactions = json.load(f)

        valid, invalid = validate_transactions_batch(transactions)
        # All examples should be invalid
        assert len(invalid) > 0

    def test_invalid_liabilities_example_file(self):
        """Test that example_invalid_liabilities.json fails validation."""
        file_path = Path("data/synthetic/example_invalid_liabilities.json")
        if not file_path.exists():
            pytest.skip("Example file not found")

        with open(file_path) as f:
            liabilities_data = json.load(f)

        liabilities = [(item["data"], item["liability_type"]) for item in liabilities_data]
        valid, invalid = validate_liabilities_batch(liabilities)
        # All examples should be invalid
        assert len(invalid) > 0


# ===== Integration Tests =====

@pytest.mark.integration
class TestValidationIntegration:
    """Integration tests for validation workflows."""

    def test_end_to_end_validation_workflow(self):
        """Test complete validation workflow with example data."""
        # Load valid examples
        accounts_file = Path("data/synthetic/example_valid_accounts.json")
        transactions_file = Path("data/synthetic/example_valid_transactions.json")

        if not (accounts_file.exists() and transactions_file.exists()):
            pytest.skip("Example files not found")

        with open(accounts_file) as f:
            accounts = json.load(f)
        with open(transactions_file) as f:
            transactions = json.load(f)

        # Validate accounts
        valid_accounts, invalid_accounts = validate_accounts_batch(accounts)
        assert len(invalid_accounts) == 0, f"Found invalid accounts: {invalid_accounts}"

        # Validate transactions
        valid_transactions, invalid_transactions = validate_transactions_batch(transactions)
        assert len(invalid_transactions) == 0, f"Found invalid transactions: {invalid_transactions}"

        # Validate chronological order
        result = validate_chronological_order(transactions)
        assert result.is_valid is True, f"Transactions not in chronological order: {result.errors}"

        print(f"✅ Validated {len(valid_accounts)} accounts and {len(valid_transactions)} transactions")
