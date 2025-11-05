"""
Data ingestion module for SpendSense.

This module provides data ingestion capabilities for loading CSV and JSON files,
validating against Pydantic schemas, and storing in SQLite and Parquet formats.
"""

from spendsense.ingestion.data_ingestor import DataIngestor
from spendsense.ingestion.csv_reader import CSVReader
from spendsense.ingestion.json_reader import JSONReader
from spendsense.ingestion.database_writer import DatabaseWriter
from spendsense.ingestion.parquet_writer import ParquetWriter

__all__ = [
    "DataIngestor",
    "CSVReader",
    "JSONReader",
    "DatabaseWriter",
    "ParquetWriter",
]
