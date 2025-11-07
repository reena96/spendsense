#!/usr/bin/env python3
"""
Quick audit log viewer script.

Usage:
  python scripts/view_audit_log.py --event-type consent_changed
  python scripts/view_audit_log.py --user-id user_MASKED_000
  python scripts/view_audit_log.py --last 10
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.ingestion.database_writer import AuditLog

def view_audit_log(
    db_path: str = "data/processed/spendsense.db",
    event_type: str = None,
    user_id: str = None,
    operator_id: str = None,
    limit: int = 10
):
    """View audit log entries with optional filtering."""

    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Build query
    query = session.query(AuditLog)

    if event_type:
        query = query.filter(AuditLog.event_type == event_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if operator_id:
        query = query.filter(AuditLog.operator_id == operator_id)

    # Order by timestamp descending and limit
    entries = query.order_by(desc(AuditLog.timestamp)).limit(limit).all()

    if not entries:
        print("No audit log entries found matching your criteria.")
        return

    print(f"\n{'='*100}")
    print(f"Found {len(entries)} audit log entries (showing last {limit}):")
    print(f"{'='*100}\n")

    for entry in entries:
        print(f"📋 Log ID: {entry.log_id}")
        print(f"   Event Type: {entry.event_type}")
        print(f"   Timestamp: {entry.timestamp}")
        print(f"   User ID: {entry.user_id or 'N/A'}")
        print(f"   Operator ID: {entry.operator_id or 'N/A'}")
        print(f"   Recommendation ID: {entry.recommendation_id or 'N/A'}")

        # Parse and display event data
        try:
            event_data = json.loads(entry.event_data)
            print(f"   Event Data:")
            for key, value in event_data.items():
                print(f"      • {key}: {value}")
        except json.JSONDecodeError:
            print(f"   Event Data: {entry.event_data}")

        if entry.ip_address:
            print(f"   IP Address: {entry.ip_address}")

        print(f"{'-'*100}\n")

    session.close()


def main():
    parser = argparse.ArgumentParser(description="View SpendSense audit log")
    parser.add_argument("--db", default="data/processed/spendsense.db", help="Path to database")
    parser.add_argument("--event-type", help="Filter by event type")
    parser.add_argument("--user-id", help="Filter by user ID")
    parser.add_argument("--operator-id", help="Filter by operator ID")
    parser.add_argument("--last", type=int, default=10, help="Number of entries to show")

    args = parser.parse_args()

    view_audit_log(
        db_path=args.db,
        event_type=args.event_type,
        user_id=args.user_id,
        operator_id=args.operator_id,
        limit=args.last
    )


if __name__ == "__main__":
    main()
