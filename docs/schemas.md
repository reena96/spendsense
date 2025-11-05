# SpendSense Data Schemas

**Version:** 1.0
**Last Updated:** November 4, 2025

This document defines the data schemas for SpendSense, matching Plaid's API structure for accounts, transactions, and liabilities. All schemas include validation rules to ensure data quality and consistency.

---

## Overview

SpendSense uses **Pydantic 2.5+** for schema definition and runtime validation. The schemas enforce:

- Type safety with Python type hints
- Field-level validation (non-negative balances, valid currency codes, etc.)
- Cross-field validation (account type/subtype consistency)
- Realistic value ranges for financial data

All schemas are defined in `spendsense/db/models.py`.

---

## Account Schema

Represents a financial account (checking, savings, credit card, loan, etc.) with balances and metadata.

### Fields

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `account_id` | string | Yes | Unique masked account identifier | Must be unique |
| `type` | enum | Yes | Account type category | Must be: `depository`, `credit`, or `loan` |
| `subtype` | enum | Yes | Specific account subtype | Must match account type (see table below) |
| `balances` | object | Yes | Account balance information | See AccountBalances schema |
| `iso_currency_code` | string | Yes | ISO 4217 currency code | Must be valid code (USD, EUR, GBP, CAD, AUD, JPY, CHF) |
| `holder_category` | enum | No (default: `personal`) | Account holder category | Must be: `personal` or `business` |

### Account Type and Subtype Combinations

| Account Type | Valid Subtypes |
|--------------|----------------|
| `depository` | `checking`, `savings`, `cd` (Certificate of Deposit), `money market` |
| `credit` | `credit card` |
| `loan` | `mortgage`, `student`, `personal` |

### AccountBalances Schema

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `available` | Decimal | No | Available balance | Must be ≥ 0 if present |
| `current` | Decimal | Yes | Current balance | Must be ≥ 0 |
| `limit` | Decimal | No | Credit limit (for credit accounts) | Must be ≥ 0 if present |

### Validation Rules

1. **Non-negative balances**: All balance fields must be ≥ 0
2. **Valid currency codes**: Must be one of the supported ISO 4217 codes
3. **Type/subtype consistency**: Subtype must be valid for the specified account type
4. **Required fields**: account_id, type, subtype, balances, iso_currency_code

### Example: Valid Account

```json
{
  "account_id": "acc_MASKED_1234567890",
  "type": "depository",
  "subtype": "checking",
  "balances": {
    "available": 2500.50,
    "current": 2800.75,
    "limit": null
  },
  "iso_currency_code": "USD",
  "holder_category": "personal"
}
```

### Example: Credit Card Account

```json
{
  "account_id": "acc_MASKED_CC98765",
  "type": "credit",
  "subtype": "credit card",
  "balances": {
    "available": 7500.00,
    "current": 2500.00,
    "limit": 10000.00
  },
  "iso_currency_code": "USD",
  "holder_category": "personal"
}
```

---

## Transaction Schema

Represents a financial transaction with merchant info, amount, and categorization following Plaid Transactions API structure.

### Fields

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `transaction_id` | string | Yes | Unique transaction identifier | Must be unique |
| `account_id` | string | Yes | Account this transaction belongs to | Must reference valid account |
| `date` | date | Yes | Transaction date (YYYY-MM-DD) | Must be valid date |
| `amount` | Decimal | Yes | Transaction amount | Positive = debit, Negative = credit |
| `merchant_name` | string | No | Merchant or payee name | Free text |
| `merchant_entity_id` | string | No | Unique merchant identifier | Optional merchant ID |
| `payment_channel` | enum | Yes | How payment was made | Must be: `online`, `in store`, or `other` |
| `personal_finance_category` | string | Yes | Transaction category | Must be valid Plaid category (see list below) |
| `pending` | boolean | No (default: false) | Whether transaction is pending | true or false |

### Valid Personal Finance Categories

Categories use UPPER_SNAKE_CASE format:

- `INCOME` - Salary, wages, freelance income
- `TRANSFER_IN` - Transfers into account
- `TRANSFER_OUT` - Transfers out of account
- `LOAN_PAYMENTS` - Loan, mortgage, credit card payments
- `BANK_FEES` - Bank charges, overdraft fees
- `ENTERTAINMENT` - Movies, concerts, streaming services
- `FOOD_AND_DRINK` - Restaurants, groceries, coffee shops
- `GENERAL_MERCHANDISE` - Retail purchases
- `HOME_IMPROVEMENT` - Hardware, furniture, home goods
- `MEDICAL` - Healthcare, pharmacy, insurance
- `PERSONAL_CARE` - Haircuts, spa, beauty products
- `GENERAL_SERVICES` - Professional services, subscriptions
- `GOVERNMENT_AND_NON_PROFIT` - Taxes, charity donations
- `TRANSPORTATION` - Gas, public transit, rideshare
- `TRAVEL` - Hotels, flights, vacation expenses
- `RENT_AND_UTILITIES` - Rent, electricity, water, internet

### Validation Rules

1. **Required fields**: transaction_id, account_id, date, amount, payment_channel, personal_finance_category
2. **Valid category**: Must be one of the supported Plaid categories
3. **Date format**: ISO 8601 date format (YYYY-MM-DD)
4. **Amount**: Can be positive (debit) or negative (credit)

### Example: Valid Transaction (Purchase)

```json
{
  "transaction_id": "txn_20241104_0001",
  "account_id": "acc_MASKED_1234567890",
  "date": "2024-11-04",
  "amount": 45.67,
  "merchant_name": "Whole Foods Market",
  "merchant_entity_id": "merchant_wholefoodsmarket",
  "payment_channel": "in store",
  "personal_finance_category": "FOOD_AND_DRINK",
  "pending": false
}
```

### Example: Valid Transaction (Income)

```json
{
  "transaction_id": "txn_20241101_PAYROLL",
  "account_id": "acc_MASKED_1234567890",
  "date": "2024-11-01",
  "amount": -3500.00,
  "merchant_name": "Acme Corp Payroll",
  "merchant_entity_id": null,
  "payment_channel": "other",
  "personal_finance_category": "INCOME",
  "pending": false
}
```

---

## Liability Schemas

### Credit Card Liability

Represents credit card debt and payment information following Plaid Liabilities API.

#### Fields

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `account_id` | string | Yes | Associated credit account ID | Must reference valid credit account |
| `aprs` | list[Decimal] | Yes | Annual Percentage Rates | Each APR must be 0-1.0 (0-100%) |
| `minimum_payment_amount` | Decimal | Yes | Minimum payment due | Must be ≥ 0 |
| `last_payment_amount` | Decimal | No | Last payment made | Must be ≥ 0 if present |
| `last_statement_balance` | Decimal | Yes | Balance on last statement | Must be ≥ 0 |
| `is_overdue` | boolean | No (default: false) | Whether account is overdue | true or false |
| `next_payment_due_date` | date | No | Next payment due date | Must be valid date if present |

#### Validation Rules

1. **APR range**: Must be between 0 and 1.0 (0% - 100%)
2. **Non-negative amounts**: All payment amounts and balances must be ≥ 0
3. **Realistic APRs**: Typically 15-30% (0.15-0.30) for credit cards
4. **Minimum payment**: Typically 2-3% of balance

#### Example

```json
{
  "account_id": "acc_MASKED_CC98765",
  "aprs": [0.1999, 0.2499],
  "minimum_payment_amount": 75.00,
  "last_payment_amount": 150.00,
  "last_statement_balance": 2500.00,
  "is_overdue": false,
  "next_payment_due_date": "2024-12-01"
}
```

### Mortgage Liability

Represents mortgage loan information following Plaid Liabilities API.

#### Fields

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `account_id` | string | Yes | Associated loan account ID | Must reference valid loan account |
| `interest_rate` | Decimal | Yes | Interest rate (as decimal) | Must be 0.02-0.12 (2-12%) |
| `next_payment_due_date` | date | No | Next payment due date | Must be valid date if present |

#### Validation Rules

1. **Interest rate range**: Must be between 2% and 12% (0.02-0.12)
2. **Realistic rates**: Typical mortgage rates are 3-7% depending on market conditions

#### Example

```json
{
  "account_id": "acc_MASKED_MORT5678",
  "interest_rate": 0.0450,
  "next_payment_due_date": "2024-12-01"
}
```

### Student Loan Liability

Represents student loan information following Plaid Liabilities API.

#### Fields

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `account_id` | string | Yes | Associated loan account ID | Must reference valid loan account |
| `interest_rate` | Decimal | Yes | Interest rate (as decimal) | Must be 0.03-0.08 (3-8%) |
| `next_payment_due_date` | date | No | Next payment due date | Must be valid date if present |

#### Validation Rules

1. **Interest rate range**: Must be between 3% and 8% (0.03-0.08)
2. **Realistic rates**: Federal student loans typically 4-6%, private loans may be higher

#### Example

```json
{
  "account_id": "acc_MASKED_SL9012",
  "interest_rate": 0.0550,
  "next_payment_due_date": "2024-12-15"
}
```

---

## Validation Functions

The `spendsense/db/validators.py` module provides validation utilities:

### Single Record Validation

```python
from spendsense.db.validators import validate_account, validate_transaction, validate_liability

# Validate an account
result = validate_account(account_data)
if result.is_valid:
    print("Account is valid")
else:
    print(f"Errors: {result.errors}")

# Validate a transaction
result = validate_transaction(transaction_data)

# Validate a liability
result = validate_liability(liability_data, liability_type="credit_card")
```

### Batch Validation

```python
from spendsense.db.validators import (
    validate_accounts_batch,
    validate_transactions_batch,
    validate_liabilities_batch
)

# Validate multiple accounts
valid_accounts, invalid_accounts = validate_accounts_batch(accounts_list)
print(f"Valid: {len(valid_accounts)}, Invalid: {len(invalid_accounts)}")

# Check invalid records
for idx, errors in invalid_accounts:
    print(f"Account {idx} errors: {errors}")
```

### Chronological Order Validation

```python
from spendsense.db.validators import validate_chronological_order

# Verify transactions are in chronological order
result = validate_chronological_order(transactions, date_field="date")
if not result.is_valid:
    print(f"Chronological order violation: {result.errors}")
```

---

## Common Validation Errors

### Non-negative Balance Violation

```json
{
  "error": "Balance cannot be negative",
  "field": "balances.current",
  "value": -100.50
}
```

### Invalid Currency Code

```json
{
  "error": "Invalid currency code: XYZ. Must be one of {'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'CHF'}",
  "field": "iso_currency_code",
  "value": "XYZ"
}
```

### Type/Subtype Mismatch

```json
{
  "error": "Invalid subtype 'checking' for account type 'credit'. Valid subtypes: {'credit card'}",
  "field": "subtype",
  "value": "checking"
}
```

### Invalid Category

```json
{
  "error": "Invalid personal_finance_category: SHOPPING",
  "field": "personal_finance_category",
  "value": "SHOPPING"
}
```

---

## Schema Evolution

When modifying schemas:

1. **Maintain backward compatibility** - Add new optional fields rather than removing fields
2. **Update validation rules** - Ensure new rules don't break existing valid data
3. **Version schemas** - Consider schema versioning for major changes
4. **Update tests** - Add tests for new fields and validation rules
5. **Update documentation** - Keep this document synchronized with code changes

---

## References

- [Plaid API Documentation](https://plaid.com/docs/api/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [ISO 4217 Currency Codes](https://www.iso.org/iso-4217-currency-codes.html)
- SpendSense Architecture: `docs/architecture.md`
- SpendSense PRD: `docs/prd.md`
