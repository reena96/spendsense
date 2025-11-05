"""
Command-line interface for data ingestion.

This module provides a CLI tool for ingesting CSV/JSON files, validating
against schemas, and storing in SQLite and Parquet formats.
"""

import argparse
import logging
from pathlib import Path
from typing import Optional

from spendsense.db.models import Account, Transaction, CreditCardLiability, StudentLoanLiability, MortgageLiability
from spendsense.ingestion.csv_reader import CSVReader
from spendsense.ingestion.json_reader import JSONReader
from spendsense.ingestion.database_writer import DatabaseWriter
from spendsense.ingestion.parquet_writer import ParquetWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)


def ingest_file(
    file_path: Path,
    file_format: str,
    data_type: str,
    db_writer: Optional[DatabaseWriter] = None,
    parquet_writer: Optional[ParquetWriter] = None,
    validate_only: bool = False,
    verbose: bool = False
):
    """
    Ingest a single file with validation and storage.

    Args:
        file_path: Path to file to ingest
        file_format: 'csv' or 'json'
        data_type: 'users', 'accounts', 'transactions', or 'liabilities'
        db_writer: DatabaseWriter instance for SQLite storage
        parquet_writer: ParquetWriter instance for Parquet export
        validate_only: If True, only validate without storing
        verbose: Enable verbose logging
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Select schema based on data type
    schema_map = {
        'accounts': Account,
        'transactions': Transaction,
        'liabilities': None,  # Multiple liability types
        'users': None  # UserProfile is not a Pydantic model
    }
    schema = schema_map.get(data_type)

    # Select reader based on format
    if file_format == 'csv':
        reader = CSVReader(schema=schema)
    elif file_format == 'json':
        reader = JSONReader(schema=schema)
    else:
        raise ValueError(f"Unsupported file format: {file_format}")

    logger.info(f"Ingesting {data_type} from {file_path} ({file_format} format)")

    # Ingest with validation
    result = reader.ingest(file_path)

    # Log summary
    summary = result.summary()
    logger.info(f"Ingestion complete: {summary['valid_records']} valid, {summary['invalid_records']} invalid")

    # Log errors if any
    if result.errors:
        logger.warning(f"Found {len(result.errors)} validation errors:")
        for error in result.errors[:10]:  # Show first 10 errors
            logger.warning(
                f"  Line {error['line_num']}: {error['record_id']} - {error['error']}"
            )
        if len(result.errors) > 10:
            logger.warning(f"  ... and {len(result.errors) - 10} more errors")

    if validate_only:
        logger.info("Validation-only mode: skipping storage")
        return result

    # Store valid data
    if result.valid_data:
        try:
            if db_writer:
                if data_type == 'users':
                    db_writer.write_users(result.valid_data)
                elif data_type == 'accounts':
                    db_writer.write_accounts(result.valid_data)
                elif data_type == 'transactions':
                    db_writer.write_transactions(result.valid_data)
                elif data_type == 'liabilities':
                    db_writer.write_liabilities(result.valid_data)

            if parquet_writer:
                if data_type == 'users':
                    parquet_writer.write_users(result.valid_data)
                elif data_type == 'accounts':
                    parquet_writer.write_accounts(result.valid_data)
                elif data_type == 'transactions':
                    parquet_writer.write_transactions(result.valid_data, partition_by_user=False)
                elif data_type == 'liabilities':
                    parquet_writer.write_liabilities(result.valid_data)

            logger.info(f"Successfully stored {len(result.valid_data)} {data_type} records")

        except Exception as e:
            logger.error(f"Failed to store data: {e}")
            raise

    return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest financial data files into SQLite and Parquet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all data types from JSON files
  python -m spendsense.ingestion.ingest_cli \\
    --profiles data/synthetic/users/profiles.json \\
    --transactions data/synthetic/transactions/transactions.json \\
    --liabilities data/synthetic/liabilities/liabilities.json \\
    --output-db data/processed/spendsense.db \\
    --output-parquet data/processed/parquet

  # Validate only (no storage)
  python -m spendsense.ingestion.ingest_cli \\
    --transactions data/synthetic/transactions/transactions.json \\
    --validate-only

  # Verbose mode for debugging
  python -m spendsense.ingestion.ingest_cli \\
    --profiles data/synthetic/users/profiles.json \\
    --output-db data/processed/spendsense.db \\
    --verbose
        """
    )

    # Input files
    parser.add_argument('--profiles', type=Path, help='Path to user profiles file (JSON)')
    parser.add_argument('--accounts', type=Path, help='Path to accounts file (CSV/JSON)')
    parser.add_argument('--transactions', type=Path, help='Path to transactions file (CSV/JSON)')
    parser.add_argument('--liabilities', type=Path, help='Path to liabilities file (CSV/JSON)')

    # Output paths
    parser.add_argument('--output-db', type=Path, help='Path to output SQLite database')
    parser.add_argument('--output-parquet', type=Path, help='Path to output Parquet directory')

    # Options
    parser.add_argument('--format', choices=['csv', 'json'], default='json',
                        help='Input file format (default: json)')
    parser.add_argument('--validate-only', action='store_true',
                        help='Only validate data without storing')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    # Validate arguments
    if not any([args.profiles, args.accounts, args.transactions, args.liabilities]):
        parser.error("At least one input file must be specified")

    if not args.validate_only and not args.output_db and not args.output_parquet:
        parser.error("At least one output destination (--output-db or --output-parquet) must be specified")

    # Initialize writers
    db_writer = None
    parquet_writer = None

    if not args.validate_only:
        if args.output_db:
            db_writer = DatabaseWriter(args.output_db)
            db_writer.create_tables()
            logger.info(f"Initialized SQLite database at {args.output_db}")

        if args.output_parquet:
            parquet_writer = ParquetWriter(args.output_parquet)
            logger.info(f"Initialized Parquet writer at {args.output_parquet}")

    # Ingest each file type
    total_valid = 0
    total_invalid = 0

    try:
        if args.profiles:
            result = ingest_file(
                args.profiles, args.format, 'users',
                db_writer, parquet_writer, args.validate_only, args.verbose
            )
            total_valid += result.valid_records
            total_invalid += result.invalid_records

        if args.accounts:
            result = ingest_file(
                args.accounts, args.format, 'accounts',
                db_writer, parquet_writer, args.validate_only, args.verbose
            )
            total_valid += result.valid_records
            total_invalid += result.invalid_records

        if args.transactions:
            result = ingest_file(
                args.transactions, args.format, 'transactions',
                db_writer, parquet_writer, args.validate_only, args.verbose
            )
            total_valid += result.valid_records
            total_invalid += result.invalid_records

        if args.liabilities:
            result = ingest_file(
                args.liabilities, args.format, 'liabilities',
                db_writer, parquet_writer, args.validate_only, args.verbose
            )
            total_valid += result.valid_records
            total_invalid += result.invalid_records

        # Final summary
        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info(f"Total valid records: {total_valid}")
        logger.info(f"Total invalid records: {total_invalid}")
        if args.output_db:
            logger.info(f"Database: {args.output_db}")
        if args.output_parquet:
            logger.info(f"Parquet files: {args.output_parquet}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise


if __name__ == '__main__':
    main()
