#!/usr/bin/env python3
"""
CLI tool for generating synthetic liability data.

Usage:
    python -m spendsense.generators.liability_cli \
        --profiles data/synthetic/users/profiles.json \
        --transactions data/synthetic/transactions/transactions.json \
        --output data/synthetic/liabilities/liabilities.json
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from spendsense.generators.liability_generator import generate_synthetic_liabilities


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic liability data for user profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate liabilities with default settings
  %(prog)s --profiles profiles.json --output liabilities.json

  # Include transaction history for consistency
  %(prog)s --profiles profiles.json --transactions transactions.json --output liabilities.json

  # Use custom seed and reference date
  %(prog)s --profiles profiles.json --output liabilities.json --seed 123 --reference-date 2025-01-01
        """
    )

    parser.add_argument(
        "--profiles",
        type=Path,
        required=True,
        help="Path to profiles JSON file (from ProfileGenerator)"
    )

    parser.add_argument(
        "--transactions",
        type=Path,
        help="Optional path to transactions JSON file (for consistency validation)"
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path to save generated liabilities JSON"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    parser.add_argument(
        "--reference-date",
        type=str,
        help="Reference date for liability calculations in YYYY-MM-DD format (default: today)"
    )

    args = parser.parse_args()

    # Validate input files
    if not args.profiles.exists():
        print(f"Error: Profiles file not found: {args.profiles}", file=sys.stderr)
        sys.exit(1)

    if args.transactions and not args.transactions.exists():
        print(f"Error: Transactions file not found: {args.transactions}", file=sys.stderr)
        sys.exit(1)

    # Parse reference date if provided
    reference_date = None
    if args.reference_date:
        try:
            reference_date = date.fromisoformat(args.reference_date)
        except ValueError:
            print(f"Error: Invalid date format: {args.reference_date}. Use YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)

    # Generate liabilities
    print(f"Generating liabilities from {args.profiles}")
    if args.transactions:
        print(f"Using transaction history from {args.transactions}")
    print(f"Seed: {args.seed}")
    print(f"Reference date: {reference_date or 'today'}")
    print()

    try:
        liabilities = generate_synthetic_liabilities(
            profiles_path=args.profiles,
            transactions_path=args.transactions,
            output_path=args.output,
            seed=args.seed,
            reference_date=reference_date
        )

        # Print summary statistics
        total_users = len(liabilities)
        total_credit_cards = sum(len(u["credit_cards"]) for u in liabilities.values())
        total_student_loans = sum(len(u["student_loans"]) for u in liabilities.values())
        total_mortgages = sum(len(u["mortgages"]) for u in liabilities.values())

        print()
        print("=" * 70)
        print("GENERATION SUMMARY")
        print("=" * 70)
        print(f"Total Users: {total_users}")
        print(f"Total Credit Cards: {total_credit_cards}")
        print(f"Total Student Loans: {total_student_loans}")
        print(f"Total Mortgages: {total_mortgages}")
        print(f"Total Liabilities: {total_credit_cards + total_student_loans + total_mortgages}")
        print()
        print(f"Output saved to: {args.output}")

    except Exception as e:
        print(f"Error generating liabilities: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
