#!/usr/bin/env python3
"""
Generate sample audit log entries for testing Epic 6 - Story 6.5.

This script demonstrates how audit logs should be created throughout the system
and populates the database with realistic test data.

Usage:
    python scripts/generate_audit_logs.py --count 50
    python scripts/generate_audit_logs.py --clear  # Clear existing logs first
"""

import argparse
import json
import random
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import AuditLog, User


# Sample data for realistic log generation
EVENT_TYPES = [
    'recommendation_generated',
    'consent_changed',
    'eligibility_checked',
    'tone_validated',
    'operator_action',
    'persona_assigned',
    'persona_overridden',
    'login_attempt',
    'unauthorized_access',
]

# Will be populated from database
USERS = []
OPERATORS = ['op_admin_default', 'op_reviewer_001', 'op_viewer_001']
PERSONAS = ['debt_manager', 'budget_optimizer', 'savings_builder', 'unclassified']
CONTENT_TYPES = ['education', 'partner_offer']
OPERATOR_ACTIONS = ['approved', 'overridden', 'flagged']


def load_users_from_db():
    """Load all actual user IDs from database."""
    global USERS
    session = get_db_session()
    try:
        users = session.query(User.user_id).all()
        USERS = [user.user_id for user in users]
        print(f"Loaded {len(USERS)} users from database")
    finally:
        session.close()


def generate_event_data(event_type: str) -> dict:
    """Generate realistic event data based on event type."""

    if event_type == 'recommendation_generated':
        return {
            'content_type': random.choice(CONTENT_TYPES),
            'title': f'Sample Content {uuid.uuid4().hex[:8]}',
            'passed_guardrails': random.choice([True, True, True, False]),  # 75% pass
            'guardrail_results': {
                'eligibility': random.choice(['passed', 'passed', 'passed', 'failed']),
                'tone': random.choice(['passed', 'passed', 'passed', 'failed']),
            }
        }

    elif event_type == 'consent_changed':
        old_status = random.choice(['opted_in', 'opted_out'])
        new_status = 'opted_in' if old_status == 'opted_out' else 'opted_out'
        return {
            'old_status': old_status,
            'new_status': new_status,
            'consent_version': '1.0',
            'changed_via': random.choice(['web', 'api', 'operator_action'])
        }

    elif event_type == 'eligibility_checked':
        passed = random.choice([True, True, True, False])
        return {
            'check_result': 'passed' if passed else 'failed',
            'consent': random.choice(['opted_in', 'opted_out']),
            'persona': random.choice(PERSONAS),
            'failure_reason': None if passed else random.choice([
                'consent_opted_out',
                'no_persona_match',
                'insufficient_data'
            ])
        }

    elif event_type == 'tone_validated':
        passed = random.choice([True, True, True, False])
        return {
            'validation_result': 'passed' if passed else 'failed',
            'tone_score': random.uniform(0.7, 1.0) if passed else random.uniform(0.3, 0.7),
            'violations': [] if passed else [
                random.choice(['urgency_detected', 'fear_language', 'aggressive_tone'])
            ]
        }

    elif event_type == 'operator_action':
        action = random.choice(OPERATOR_ACTIONS)
        return {
            'action': action,
            'reason': f'Sample reason for {action} action',
            'recommendation_id': f'rec_{uuid.uuid4().hex[:8]}'
        }

    elif event_type == 'persona_assigned':
        return {
            'persona': random.choice(PERSONAS),
            'time_window': random.choice(['30d', '180d']),
            'confidence': random.uniform(0.7, 0.99),
            'qualifying_personas': random.sample(PERSONAS, k=random.randint(1, 3))
        }

    elif event_type == 'persona_overridden':
        return {
            'old_persona': random.choice(PERSONAS),
            'new_persona': random.choice(PERSONAS),
            'reason': 'Manual override by operator',
            'operator_id': random.choice(OPERATORS)
        }

    elif event_type == 'login_attempt':
        success = random.choice([True, True, True, False])
        return {
            'status': 'success' if success else 'failure',
            'username': random.choice(['admin', 'reviewer', 'viewer']),
            'failure_reason': None if success else random.choice([
                'invalid_password',
                'account_locked',
                'unknown_username'
            ])
        }

    elif event_type == 'unauthorized_access':
        return {
            'attempted_endpoint': random.choice([
                '/api/operator/review/approve',
                '/api/operator/personas/override',
                '/api/operator/audit/export'
            ]),
            'reason': 'insufficient_permissions',
            'required_role': random.choice(['admin', 'reviewer'])
        }

    return {}


def generate_audit_log(base_time: datetime, offset_minutes: int) -> AuditLog:
    """Generate a single audit log entry."""

    event_type = random.choice(EVENT_TYPES)

    # Determine user_id and operator_id based on event type
    user_id = None
    operator_id = None
    recommendation_id = None

    if event_type in ['recommendation_generated', 'eligibility_checked', 'tone_validated',
                      'consent_changed', 'persona_assigned', 'persona_overridden']:
        user_id = random.choice(USERS)

    if event_type in ['operator_action', 'persona_overridden']:
        operator_id = random.choice(OPERATORS)

    if event_type == 'login_attempt':
        operator_id = random.choice(OPERATORS)

    if event_type == 'unauthorized_access':
        operator_id = random.choice(OPERATORS)

    if event_type in ['recommendation_generated', 'eligibility_checked', 'tone_validated', 'operator_action']:
        recommendation_id = f'rec_{uuid.uuid4().hex[:8]}'

    # Generate event data
    event_data = generate_event_data(event_type)

    # Create audit log entry
    return AuditLog(
        log_id=f'log_{uuid.uuid4().hex}',
        event_type=event_type,
        user_id=user_id,
        operator_id=operator_id,
        recommendation_id=recommendation_id,
        timestamp=base_time + timedelta(minutes=offset_minutes),
        event_data=json.dumps(event_data),
        ip_address='127.0.0.1',
        user_agent='Mozilla/5.0 (Test Generator)'
    )


def main():
    parser = argparse.ArgumentParser(description='Generate audit log entries')
    parser.add_argument('--count', type=int, default=50,
                       help='Number of audit log entries to generate (default: 50)')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing audit logs before generating new ones')
    parser.add_argument('--days', type=int, default=7,
                       help='Spread logs over this many days (default: 7)')

    args = parser.parse_args()

    # Load actual users from database
    load_users_from_db()

    if not USERS:
        print("Error: No users found in database. Please ensure users table is populated.", file=sys.stderr)
        return

    session = get_db_session()

    try:
        # Clear existing logs if requested
        if args.clear:
            count = session.query(AuditLog).count()
            session.query(AuditLog).delete()
            session.commit()
            print(f"Cleared {count} existing audit log entries")

        # Generate new logs
        print(f"Generating {args.count} audit log entries over {args.days} days...")

        base_time = datetime.now() - timedelta(days=args.days)
        minutes_per_entry = (args.days * 24 * 60) // args.count

        logs = []
        for i in range(args.count):
            log = generate_audit_log(base_time, i * minutes_per_entry)
            logs.append(log)
            session.add(log)

        session.commit()

        print(f"✓ Successfully generated {args.count} audit log entries")

        # Print summary statistics
        print("\nEvent type distribution:")
        for event_type in EVENT_TYPES:
            count = sum(1 for log in logs if log.event_type == event_type)
            percentage = (count / args.count) * 100
            print(f"  {event_type:25s} {count:3d} ({percentage:5.1f}%)")

        print(f"\nTime range: {logs[0].timestamp.isoformat()} to {logs[-1].timestamp.isoformat()}")
        print(f"\nYou can now view these logs in the Audit Log page at http://localhost:3000/audit")

    except Exception as e:
        session.rollback()
        print(f"Error generating audit logs: {e}", file=sys.stderr)
        raise
    finally:
        session.close()


if __name__ == '__main__':
    main()
