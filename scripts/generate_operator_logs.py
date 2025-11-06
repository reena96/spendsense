#!/usr/bin/env python3
"""
Generate operator action audit logs for ALL users.

Ensures every user has multiple operator interactions (approvals, overrides, flags)
so that filtering by operator_id returns results for all users.
"""

import json
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import AuditLog, User

OPERATORS = ['op_admin_default', 'op_reviewer_001', 'op_viewer_001']
OPERATOR_ACTIONS = ['approved', 'overridden', 'flagged']


def generate_operator_logs_for_user(user_id: str, base_time: datetime, num_logs: int = 3):
    """Generate operator action logs for a specific user."""
    logs = []

    for i in range(num_logs):
        action = random.choice(OPERATOR_ACTIONS)
        operator = random.choice(OPERATORS)

        event_data = {
            'action': action,
            'reason': f'Operator {action} recommendation after review',
            'recommendation_id': f'rec_{uuid.uuid4().hex[:8]}'
        }

        log = AuditLog(
            log_id=f'log_{uuid.uuid4().hex}',
            event_type='operator_action',
            user_id=user_id,
            operator_id=operator,
            recommendation_id=event_data['recommendation_id'],
            timestamp=base_time + timedelta(hours=i*8, minutes=random.randint(0, 480)),
            event_data=json.dumps(event_data),
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0 (Operator Dashboard)'
        )
        logs.append(log)

    return logs


def main():
    session = get_db_session()

    try:
        # Get all users
        users = session.query(User.user_id).all()
        user_ids = [u.user_id for u in users]

        print(f"Found {len(user_ids)} users")
        print(f"Generating 3 operator action logs per user...")

        base_time = datetime.now() - timedelta(days=25)
        all_logs = []

        for user_id in user_ids:
            logs = generate_operator_logs_for_user(user_id, base_time, num_logs=3)
            all_logs.extend(logs)
            for log in logs:
                session.add(log)

        session.commit()

        print(f"✓ Successfully generated {len(all_logs)} operator action logs")
        print(f"✓ Every user now has 3 operator interactions")
        print(f"\nOperator distribution:")

        operator_counts = {}
        for log in all_logs:
            operator_counts[log.operator_id] = operator_counts.get(log.operator_id, 0) + 1

        for operator, count in sorted(operator_counts.items()):
            print(f"  {operator}: {count} actions")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
