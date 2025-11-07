#!/usr/bin/env python3
"""
Launch the SpendSense Evaluation Metrics Dashboard

This script starts the Flask web server for the evaluation dashboard.

Usage:
    python scripts/run_dashboard.py
    python scripts/run_dashboard.py --port 8080
    python scripts/run_dashboard.py --host 0.0.0.0 --port 5000

Then open your browser to: http://localhost:5000
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from spendsense.evaluation.dashboard_server import run_dashboard


def main():
    parser = argparse.ArgumentParser(
        description='Launch SpendSense Evaluation Metrics Dashboard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on default port 5000
  python scripts/run_dashboard.py

  # Run on custom port
  python scripts/run_dashboard.py --port 8080

  # Allow external access
  python scripts/run_dashboard.py --host 0.0.0.0 --port 5000

  # Run in production mode (no debug)
  python scripts/run_dashboard.py --no-debug
        """
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0 for all interfaces)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run on (default: 5000)'
    )

    parser.add_argument(
        '--no-debug',
        action='store_true',
        help='Disable debug mode (for production)'
    )

    args = parser.parse_args()

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         SpendSense Evaluation Metrics Dashboard          ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Starting server...                                       ║
    ║                                                           ║
    ║  Make sure you have evaluation metrics generated:        ║
    ║    1. Run: python scripts/evaluate_coverage.py           ║
    ║    2. Run: python scripts/evaluate_explainability.py     ║
    ║    3. Run: python scripts/evaluate_performance.py        ║
    ║    4. Run: python scripts/evaluate_auditability.py       ║
    ║    5. Run: python scripts/evaluate_fairness.py           ║
    ║                                                           ║
    ║  Or run all at once with the evaluation orchestrator     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    run_dashboard(
        host=args.host,
        port=args.port,
        debug=not args.no_debug
    )


if __name__ == '__main__':
    main()
