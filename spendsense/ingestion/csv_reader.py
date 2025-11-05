"""
CSV file reader for data ingestion.

This module provides CSV reading capabilities with type inference using pandas.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

import pandas as pd
from pydantic import BaseModel

from spendsense.ingestion.data_ingestor import DataIngestor

logger = logging.getLogger(__name__)


class CSVReader(DataIngestor):
    """
    CSV file reader with pandas-based parsing.

    Supports automatic type inference and handles missing optional fields.
    """

    def __init__(self, schema: Optional[Type[BaseModel]] = None):
        """
        Initialize the CSV reader.

        Args:
            schema: Pydantic model class for validation
        """
        super().__init__(schema)

    def read(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Read CSV file and return records as dictionaries.

        Args:
            file_path: Path to CSV file

        Returns:
            List of records as dictionaries

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file can't be read or parsed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            # Read CSV with pandas
            df = pd.read_csv(file_path)

            # Handle JSON-encoded columns (e.g., balances, characteristics)
            for col in df.columns:
                if col in ['balances', 'characteristics', 'accounts', 'aprs']:
                    try:
                        df[col] = df[col].apply(lambda x: json.loads(x) if pd.notna(x) and isinstance(x, str) else x)
                    except (json.JSONDecodeError, TypeError):
                        pass  # Keep as-is if not JSON

            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')

            # Clean up NaN values (replace with None)
            cleaned_records = []
            for record in records:
                cleaned = {k: (None if pd.isna(v) else v) for k, v in record.items()}
                cleaned_records.append(cleaned)

            logger.info(f"Successfully read {len(cleaned_records)} records from {file_path}")
            return cleaned_records

        except pd.errors.EmptyDataError:
            logger.warning(f"CSV file is empty: {file_path}")
            return []
        except pd.errors.ParserError as e:
            logger.error(f"Failed to parse CSV file {file_path}: {e}")
            raise IOError(f"CSV parsing error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error reading CSV {file_path}: {e}")
            raise IOError(f"Error reading CSV: {e}")
