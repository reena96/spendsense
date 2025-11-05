"""
JSON file reader for data ingestion.

This module provides JSON reading capabilities with streaming support for large files.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel

from spendsense.ingestion.data_ingestor import DataIngestor

logger = logging.getLogger(__name__)


class JSONReader(DataIngestor):
    """
    JSON file reader with streaming support for large files.

    Handles both array-based JSON (list of records) and object-based JSON
    (dictionary with user_id keys mapping to records).
    """

    def __init__(self, schema: Optional[Type[BaseModel]] = None):
        """
        Initialize the JSON reader.

        Args:
            schema: Pydantic model class for validation
        """
        super().__init__(schema)

    def read(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Read JSON file and return records as dictionaries.

        Supports two JSON structures:
        1. Array format: [{"record1": ...}, {"record2": ...}]
        2. Object format: {"user_001": {...}, "user_002": {...}}

        Args:
            file_path: Path to JSON file

        Returns:
            List of records as dictionaries

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read or parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, list):
                # Array format: direct list of records
                records = data
                logger.info(f"Read array-format JSON with {len(records)} records from {file_path}")

            elif isinstance(data, dict):
                # Object format: check if it's user_id keyed data
                # Detect structure: transactions have user_id keys with array values
                # vs profiles/accounts have user_id keys with object values

                first_key = next(iter(data.keys()), None)
                if first_key and isinstance(data[first_key], list):
                    # Transactions format: {user_id: [txn1, txn2, ...]}
                    records = []
                    for user_id, user_records in data.items():
                        if isinstance(user_records, list):
                            records.extend(user_records)
                        else:
                            # Single record for this user
                            record = user_records.copy() if isinstance(user_records, dict) else user_records
                            if isinstance(record, dict) and 'user_id' not in record:
                                record['user_id'] = user_id
                            records.append(record)
                    logger.info(f"Read object-format JSON (nested arrays) with {len(records)} total records from {file_path}")

                elif first_key and isinstance(data[first_key], dict):
                    # Profiles/liabilities format: {user_id: {profile data}}
                    records = []
                    for user_id, record in data.items():
                        # Ensure user_id is in the record
                        if isinstance(record, dict):
                            record_copy = record.copy()
                            if 'user_id' not in record_copy:
                                record_copy['user_id'] = user_id
                            records.append(record_copy)
                        else:
                            records.append(record)
                    logger.info(f"Read object-format JSON (user-keyed) with {len(records)} records from {file_path}")

                else:
                    # Empty dict or unknown structure
                    records = []
                    logger.warning(f"JSON file has unknown or empty structure: {file_path}")

            else:
                raise IOError(f"Unexpected JSON structure (not array or object): {type(data)}")

            return records

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            raise IOError(f"JSON parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading JSON {file_path}: {e}")
            raise IOError(f"Error reading JSON: {e}")
