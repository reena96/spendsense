"""
Command-line interface for synthetic transaction generation.
"""

import argparse
from pathlib import Path

from spendsense.generators.transaction_generator import generate_synthetic_transactions


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic transaction data for user profiles"
    )
    parser.add_argument(
        "--profiles-path",
        type=str,
        default="data/synthetic/users/profiles.json",
        help="Path to profiles JSON file (default: data/synthetic/users/profiles.json)"
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="data/synthetic/transactions/transactions.json",
        help="Path to output transactions JSON file (default: data/synthetic/transactions/transactions.json)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=180,
        help="Number of days of transaction history (default: 180)"
    )

    args = parser.parse_args()

    print(f"Generating transactions from profiles: {args.profiles_path}")
    print(f"Seed: {args.seed}")
    print(f"Days of history: {args.days}")
    print()

    generate_synthetic_transactions(
        profiles_path=Path(args.profiles_path),
        output_path=Path(args.output_path),
        seed=args.seed,
        days_of_history=args.days
    )

    print()
    print("✓ Transaction generation complete!")


if __name__ == "__main__":
    main()
