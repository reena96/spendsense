"""
Base data ingestor class with validation framework.

This module provides the abstract base class for data ingestion with built-in
schema validation using Pydantic models.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class IngestionResult:
    """Result of data ingestion operation with statistics and errors."""

    def __init__(self):
        self.total_records = 0
        self.valid_records = 0
        self.invalid_records = 0
        self.errors: List[Dict[str, Any]] = []
        self.valid_data: List[Dict[str, Any]] = []

    def add_valid(self, record: Dict[str, Any]):
        """Add a valid record to the result."""
        self.valid_records += 1
        self.total_records += 1
        self.valid_data.append(record)

    def add_invalid(self, record_id: Optional[str], line_num: Optional[int],
                    error: str, record_type: str):
        """Add an invalid record with error details."""
        self.invalid_records += 1
        self.total_records += 1
        self.errors.append({
            "record_id": record_id,
            "line_num": line_num,
            "error": error,
            "record_type": record_type
        })

    def summary(self) -> Dict[str, Any]:
        """Get summary statistics."""
        return {
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "error_count": len(self.errors)
        }


class DataIngestor(ABC):
    """
    Abstract base class for data ingestion with schema validation.

    This class provides common validation logic and enforces a consistent
    interface for reading different file formats.
    """

    def __init__(self, schema: Optional[Type[BaseModel]] = None):
        """
        Initialize the data ingestor.

        Args:
            schema: Pydantic model class for validation
        """
        self.schema = schema
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def read(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Read data from file.

        Args:
            file_path: Path to the file to read

        Returns:
            List of records as dictionaries

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        pass

    def validate_record(self, record: Dict[str, Any], record_id: Optional[str] = None) -> Optional[BaseModel]:
        """
        Validate a single record against the schema.

        Args:
            record: Record dictionary to validate
            record_id: Optional identifier for error logging

        Returns:
            Validated Pydantic model instance, or None if validation fails
        """
        if self.schema is None:
            # No schema validation
            return None

        try:
            # Convert string decimals to Decimal objects for financial fields
            record = self._convert_decimals(record)
            validated = self.schema(**record)
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error for record {record_id}: {e}")
            return None

    def _convert_decimals(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert string or float values to Decimal for financial fields.

        Args:
            record: Record dictionary

        Returns:
            Record with Decimal conversions applied
        """
        decimal_fields = {
            'amount', 'balance', 'current', 'available', 'limit',
            'annual_income', 'credit_limit', 'current_balance',
            'minimum_payment_amount', 'last_payment_amount',
            'last_statement_balance', 'interest_rate', 'initial_balance'
        }

        converted = record.copy()
        for key, value in record.items():
            if key in decimal_fields and value is not None:
                if isinstance(value, (int, float, str)):
                    try:
                        converted[key] = Decimal(str(value))
                    except (ValueError, TypeError):
                        pass  # Keep original value if conversion fails

            # Handle nested balances dict
            if key == 'balances' and isinstance(value, dict):
                converted_balances = {}
                for bal_key, bal_val in value.items():
                    if bal_key in decimal_fields and bal_val is not None:
                        try:
                            converted_balances[bal_key] = Decimal(str(bal_val))
                        except (ValueError, TypeError):
                            converted_balances[bal_key] = bal_val
                    else:
                        converted_balances[bal_key] = bal_val
                converted['balances'] = converted_balances

            # Handle APRs list
            if key == 'aprs' and isinstance(value, list):
                converted['aprs'] = [Decimal(str(apr)) for apr in value]

        return converted

    def ingest(self, file_path: Path) -> IngestionResult:
        """
        Ingest data from file with validation.

        Args:
            file_path: Path to the file to ingest

        Returns:
            IngestionResult with statistics and validated data

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read
        """
        result = IngestionResult()

        try:
            records = self.read(file_path)
            self.logger.info(f"Read {len(records)} records from {file_path}")

            for idx, record in enumerate(records):
                record_id = record.get('user_id') or record.get('account_id') or record.get('transaction_id') or f"record_{idx}"

                if self.schema:
                    validated = self.validate_record(record, record_id)
                    if validated:
                        # Store as dict (convert Pydantic model back to dict)
                        result.add_valid(record)
                    else:
                        # Validation failed - try to get specific error
                        try:
                            self.schema(**self._convert_decimals(record))
                        except ValidationError as e:
                            error_msg = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
                            result.add_invalid(
                                record_id=record_id,
                                line_num=idx + 1,
                                error=error_msg,
                                record_type=self.schema.__name__
                            )
                else:
                    # No validation - accept all records
                    result.add_valid(record)

        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            raise
        except IOError as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise

        return result
