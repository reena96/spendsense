"""
Command-line interface for synthetic user profile generation.

Usage:
    python -m spendsense.generators.cli [OPTIONS]

Examples:
    # Generate 100 profiles with default seed (42)
    python -m spendsense.generators.cli

    # Generate 75 profiles with custom seed
    python -m spendsense.generators.cli --num-users 75 --seed 999

    # Generate and save to custom path
    python -m spendsense.generators.cli --output custom/path/profiles.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from spendsense.generators.profile_generator import generate_synthetic_profiles


def main():
    """CLI entry point for profile generation."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic user profiles for SpendSense testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--num-users",
        type=int,
        default=100,
        help="Number of user profiles to generate (50-100, default: 100)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("data/synthetic/users/profiles.json"),
        help="Output path for profiles JSON (default: data/synthetic/users/profiles.json)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed validation information"
    )

    args = parser.parse_args()

    # Validate num_users
    if not 50 <= args.num_users <= 100:
        print(f"Error: num-users must be between 50 and 100, got {args.num_users}", file=sys.stderr)
        sys.exit(1)

    # Generate profiles
    print(f"Generating {args.num_users} user profiles with seed {args.seed}...")

    try:
        profiles, validation = generate_synthetic_profiles(
            num_users=args.num_users,
            seed=args.seed,
            output_path=args.output
        )
    except ValueError as e:
        print(f"Error: Profile validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Report results
    print(f"\u2713 Generated {len(profiles)} profiles")
    print(f"\u2713 Saved to: {args.output}")
    print()
    print("Persona Distribution:")
    for persona, count in validation["persona_distribution"].items():
        percentage = validation["persona_percentages"][persona]
        print(f"  {persona:20s}: {count:3d} ({percentage:5.1f}%)")

    print()
    min_income, max_income = validation["income_range"]
    print(f"Income Range: ${min_income:,.0f} - ${max_income:,.0f}")

    if args.verbose:
        print("\nValidation Status:")
        if validation["valid"]:
            print("  \u2713 All validation checks passed")
        else:
            print("  \u2717 Validation errors:")
            for error in validation["errors"]:
                print(f"    - {error}")

    print("\nProfiles ready for use in testing!")


if __name__ == "__main__":
    main()
