"""
Validation utilities for SpendSense data schemas.

This module provides validation functions for accounts, transactions, and liabilities.
Functions validate individual records and batches, returning detailed error information.
"""

from typing import Union
from pydantic import ValidationError
from spendsense.db.models import (
    Account,
    Transaction,
    CreditCardLiability,
    MortgageLiability,
    StudentLoanLiability
)


class ValidationResult:
    """Result of a validation operation."""

    def __init__(self, is_valid: bool, errors: list[str] | None = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def __repr__(self) -> str:
        if self.is_valid:
            return "ValidationResult(valid=True)"
        return f"ValidationResult(valid=False, errors={self.errors})"


def validate_account(data: dict) -> ValidationResult:
    """
    Validate account data against Account schema.

    Args:
        data: Dictionary containing account data

    Returns:
        ValidationResult with is_valid flag and error messages

    Example:
        >>> result = validate_account({"account_id": "acc_123", ...})
        >>> if result.is_valid:
        >>>     print("Valid account")
        >>> else:
        >>>     print(f"Errors: {result.errors}")
    """
    try:
        Account(**data)
        return ValidationResult(is_valid=True)
    except ValidationError as e:
        errors = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" if err['loc'] else err['msg'] for err in e.errors()]
        return ValidationResult(is_valid=False, errors=errors)


def validate_transaction(data: dict) -> ValidationResult:
    """
    Validate transaction data against Transaction schema.

    Args:
        data: Dictionary containing transaction data

    Returns:
        ValidationResult with is_valid flag and error messages

    Example:
        >>> result = validate_transaction({"transaction_id": "txn_123", ...})
        >>> if not result.is_valid:
        >>>     for error in result.errors:
        >>>         print(f"Validation error: {error}")
    """
    try:
        Transaction(**data)
        return ValidationResult(is_valid=True)
    except ValidationError as e:
        errors = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" if err['loc'] else err['msg'] for err in e.errors()]
        return ValidationResult(is_valid=False, errors=errors)


def validate_liability(
    data: dict,
    liability_type: str = "credit_card"
) -> ValidationResult:
    """
    Validate liability data against appropriate schema.

    Args:
        data: Dictionary containing liability data
        liability_type: Type of liability ("credit_card", "mortgage", or "student_loan")

    Returns:
        ValidationResult with is_valid flag and error messages

    Raises:
        ValueError: If liability_type is not recognized

    Example:
        >>> result = validate_liability(
        >>>     {"account_id": "acc_123", "aprs": [0.1999], ...},
        >>>     liability_type="credit_card"
        >>> )
    """
    liability_models = {
        "credit_card": CreditCardLiability,
        "mortgage": MortgageLiability,
        "student_loan": StudentLoanLiability
    }

    model_class = liability_models.get(liability_type)
    if model_class is None:
        raise ValueError(
            f"Invalid liability_type: {liability_type}. "
            f"Must be one of {list(liability_models.keys())}"
        )

    try:
        model_class(**data)
        return ValidationResult(is_valid=True)
    except ValidationError as e:
        errors = [f"{'.'.join(str(x) for x in err['loc'])}: {err['msg']}" if err['loc'] else err['msg'] for err in e.errors()]
        return ValidationResult(is_valid=False, errors=errors)


def validate_accounts_batch(accounts: list[dict]) -> tuple[list[dict], list[tuple[int, list[str]]]]:
    """
    Validate a batch of account records.

    Args:
        accounts: List of account dictionaries

    Returns:
        Tuple of (valid_accounts, invalid_accounts_with_errors)
        where invalid_accounts_with_errors is list of (index, errors)

    Example:
        >>> valid, invalid = validate_accounts_batch([account1, account2, ...])
        >>> print(f"Valid: {len(valid)}, Invalid: {len(invalid)}")
        >>> for idx, errors in invalid:
        >>>     print(f"Account {idx} errors: {errors}")
    """
    valid_accounts = []
    invalid_accounts = []

    for idx, account_data in enumerate(accounts):
        result = validate_account(account_data)
        if result.is_valid:
            valid_accounts.append(account_data)
        else:
            invalid_accounts.append((idx, result.errors))

    return valid_accounts, invalid_accounts


def validate_transactions_batch(transactions: list[dict]) -> tuple[list[dict], list[tuple[int, list[str]]]]:
    """
    Validate a batch of transaction records.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Tuple of (valid_transactions, invalid_transactions_with_errors)
        where invalid_transactions_with_errors is list of (index, errors)

    Example:
        >>> valid, invalid = validate_transactions_batch([txn1, txn2, ...])
        >>> if invalid:
        >>>     print(f"Found {len(invalid)} invalid transactions")
    """
    valid_transactions = []
    invalid_transactions = []

    for idx, transaction_data in enumerate(transactions):
        result = validate_transaction(transaction_data)
        if result.is_valid:
            valid_transactions.append(transaction_data)
        else:
            invalid_transactions.append((idx, result.errors))

    return valid_transactions, invalid_transactions


def validate_liabilities_batch(
    liabilities: list[tuple[dict, str]]
) -> tuple[list[dict], list[tuple[int, list[str]]]]:
    """
    Validate a batch of liability records.

    Args:
        liabilities: List of (liability_dict, liability_type) tuples

    Returns:
        Tuple of (valid_liabilities, invalid_liabilities_with_errors)
        where invalid_liabilities_with_errors is list of (index, errors)

    Example:
        >>> liabilities = [
        >>>     ({"account_id": "acc_1", "aprs": [0.20], ...}, "credit_card"),
        >>>     ({"account_id": "acc_2", "interest_rate": 0.045}, "mortgage")
        >>> ]
        >>> valid, invalid = validate_liabilities_batch(liabilities)
    """
    valid_liabilities = []
    invalid_liabilities = []

    for idx, (liability_data, liability_type) in enumerate(liabilities):
        result = validate_liability(liability_data, liability_type)
        if result.is_valid:
            valid_liabilities.append(liability_data)
        else:
            invalid_liabilities.append((idx, result.errors))

    return valid_liabilities, invalid_liabilities


def validate_chronological_order(transactions: list[dict], date_field: str = "date") -> ValidationResult:
    """
    Validate that transactions are in chronological order.

    Args:
        transactions: List of transaction dictionaries
        date_field: Name of the date field to check

    Returns:
        ValidationResult indicating if order is chronological

    Example:
        >>> transactions = [
        >>>     {"date": "2024-01-01", ...},
        >>>     {"date": "2024-01-15", ...}
        >>> ]
        >>> result = validate_chronological_order(transactions)
    """
    if len(transactions) <= 1:
        return ValidationResult(is_valid=True)

    from datetime import datetime

    prev_date = None
    for idx, txn in enumerate(transactions):
        if date_field not in txn:
            return ValidationResult(
                is_valid=False,
                errors=[f"Transaction {idx} missing '{date_field}' field"]
            )

        current_date = txn[date_field]
        # Handle both string and date objects
        if isinstance(current_date, str):
            try:
                current_date = datetime.fromisoformat(current_date).date()
            except ValueError:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Transaction {idx} has invalid date format: {current_date}"]
                )

        if prev_date and current_date < prev_date:
            return ValidationResult(
                is_valid=False,
                errors=[f"Transactions not in chronological order at index {idx}: {prev_date} > {current_date}"]
            )

        prev_date = current_date

    return ValidationResult(is_valid=True)
