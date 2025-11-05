"""
Parquet file writer for analytics storage.

This module provides Parquet export capabilities using PyArrow with
schema preservation and optional partitioning.
"""

import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

logger = logging.getLogger(__name__)


class ParquetWriter:
    """
    Parquet file writer for efficient analytics storage.

    Provides columnar storage with compression and schema preservation.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize the Parquet writer.

        Args:
            output_dir: Directory to write Parquet files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)

    def _convert_to_serializable(self, value: Any) -> Any:
        """Convert non-serializable types to Parquet-compatible types."""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (dict, list)):
            # Store complex types as JSON strings
            return json.dumps(value)
        return value

    def _prepare_dataframe(self, records: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert records to pandas DataFrame with type conversions.

        Args:
            records: List of record dictionaries

        Returns:
            pandas DataFrame ready for Parquet export
        """
        if not records:
            return pd.DataFrame()

        # Convert records with type handling
        converted_records = []
        for record in records:
            converted = {}
            for key, value in record.items():
                converted[key] = self._convert_to_serializable(value)
            converted_records.append(converted)

        df = pd.DataFrame(converted_records)

        # Convert date columns to datetime
        date_columns = ['date', 'next_payment_due_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        return df

    def write_users(self, users: List[Dict[str, Any]]) -> Path:
        """
        Write user records to Parquet file.

        Args:
            users: List of user dictionaries

        Returns:
            Path to created Parquet file
        """
        output_path = self.output_dir / "users.parquet"

        try:
            df = self._prepare_dataframe(users)

            if df.empty:
                self.logger.warning("No users to write to Parquet")
                return output_path

            # Write to Parquet with compression
            df.to_parquet(
                output_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )

            self.logger.info(f"Wrote {len(users)} users to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to write users Parquet: {e}")
            raise

    def write_accounts(self, accounts: List[Dict[str, Any]]) -> Path:
        """
        Write account records to Parquet file.

        Args:
            accounts: List of account dictionaries

        Returns:
            Path to created Parquet file
        """
        output_path = self.output_dir / "accounts.parquet"

        try:
            # Flatten balances dict if present
            flattened = []
            for account in accounts:
                flat = account.copy()
                if 'balances' in flat and isinstance(flat['balances'], dict):
                    balances = flat.pop('balances')
                    flat['balance_current'] = balances.get('current')
                    flat['balance_available'] = balances.get('available')
                    flat['balance_limit'] = balances.get('limit')
                flattened.append(flat)

            df = self._prepare_dataframe(flattened)

            if df.empty:
                self.logger.warning("No accounts to write to Parquet")
                return output_path

            df.to_parquet(
                output_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )

            self.logger.info(f"Wrote {len(accounts)} accounts to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to write accounts Parquet: {e}")
            raise

    def write_transactions(self, transactions: List[Dict[str, Any]], partition_by_user: bool = False) -> Path:
        """
        Write transaction records to Parquet file with optional partitioning.

        Args:
            transactions: List of transaction dictionaries
            partition_by_user: If True, partition by user_id (requires user_id in data)

        Returns:
            Path to created Parquet file or directory
        """
        output_path = self.output_dir / "transactions.parquet"

        try:
            df = self._prepare_dataframe(transactions)

            if df.empty:
                self.logger.warning("No transactions to write to Parquet")
                return output_path

            if partition_by_user and 'account_id' in df.columns:
                # Extract user_id from account_id (assumes format: acc_{user_id}_...)
                df['user_id'] = df['account_id'].str.extract(r'acc_([^_]+_[^_]+)')[0]

                # Write partitioned dataset
                table = pa.Table.from_pandas(df)
                pq.write_to_dataset(
                    table,
                    root_path=str(self.output_dir / "transactions"),
                    partition_cols=['user_id'],
                    compression='snappy'
                )
                output_path = self.output_dir / "transactions"
                self.logger.info(f"Wrote {len(transactions)} transactions to partitioned dataset at {output_path}")

            else:
                # Write single file
                df.to_parquet(
                    output_path,
                    engine='pyarrow',
                    compression='snappy',
                    index=False
                )
                self.logger.info(f"Wrote {len(transactions)} transactions to {output_path}")

            return output_path

        except Exception as e:
            self.logger.error(f"Failed to write transactions Parquet: {e}")
            raise

    def write_liabilities(self, liabilities: List[Dict[str, Any]]) -> Path:
        """
        Write liability records to Parquet file.

        Args:
            liabilities: List of liability dictionaries

        Returns:
            Path to created Parquet file
        """
        output_path = self.output_dir / "liabilities.parquet"

        try:
            df = self._prepare_dataframe(liabilities)

            if df.empty:
                self.logger.warning("No liabilities to write to Parquet")
                return output_path

            df.to_parquet(
                output_path,
                engine='pyarrow',
                compression='snappy',
                index=False
            )

            self.logger.info(f"Wrote {len(liabilities)} liabilities to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Failed to write liabilities Parquet: {e}")
            raise

    def read_parquet(self, file_path: Path) -> pd.DataFrame:
        """
        Read Parquet file back to DataFrame (for verification).

        Args:
            file_path: Path to Parquet file

        Returns:
            pandas DataFrame
        """
        try:
            df = pd.read_parquet(file_path, engine='pyarrow')
            self.logger.info(f"Read {len(df)} records from {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Failed to read Parquet file {file_path}: {e}")
            raise
