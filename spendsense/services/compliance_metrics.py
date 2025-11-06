"""
Compliance metrics calculation service for Epic 6 Story 6.5.

Calculates comprehensive metrics from audit log for regulatory
compliance monitoring and reporting.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func

from spendsense.ingestion.database_writer import AuditLog, User


class ComplianceMetricsCalculator:
    """
    Service for calculating compliance metrics from audit log.

    Provides aggregated statistics for:
    - Consent opt-in/out rates
    - Eligibility check pass/fail reasons
    - Tone validation violations by category
    - Operator action distribution
    """

    def __init__(self, session: Session):
        """
        Initialize metrics calculator.

        Args:
            session: SQLAlchemy database session
        """
        self.session = session

    def calculate_consent_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate consent-related compliance metrics (AC #8).

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Dict with consent metrics:
                - total_users: Total users in system
                - opted_in_count: Users opted in
                - opted_out_count: Users opted out
                - opt_in_rate_pct: Percentage opted in
        """
        # Get current consent status from users table
        total_users = self.session.query(User).count()
        opted_in = self.session.query(User).filter(User.consent_status == "opted_in").count()
        opted_out = total_users - opted_in

        opt_in_rate = (opted_in / total_users * 100) if total_users > 0 else 0.0

        return {
            "total_users": total_users,
            "opted_in_count": opted_in,
            "opted_out_count": opted_out,
            "opt_in_rate_pct": round(opt_in_rate, 2)
        }

    def calculate_eligibility_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate eligibility check compliance metrics (AC #8).

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Dict with eligibility metrics:
                - total_checks: Total eligibility checks
                - passed: Number passed
                - failed: Number failed
                - pass_rate_pct: Percentage passed
                - failure_reasons: List of {"reason": str, "count": int}
        """
        # Get eligibility check events from audit log
        eligibility_entries = self.session.query(AuditLog).filter(
            AuditLog.event_type == "eligibility_checked",
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).all()

        total_checks = len(eligibility_entries)
        passed = 0
        failed = 0
        failure_reasons_counter = Counter()

        for entry in eligibility_entries:
            event_data = json.loads(entry.event_data)
            check_result = event_data.get("check_result", "unknown")

            if check_result == "passed":
                passed += 1
            else:
                failed += 1
                # Count failure reason (singular in our format)
                failure_reason = event_data.get("failure_reason")
                if failure_reason:
                    failure_reasons_counter[failure_reason] += 1

        pass_rate = (passed / total_checks * 100) if total_checks > 0 else 0.0

        # Convert failure reasons to list format
        failure_reasons = [
            {"reason": reason, "count": count}
            for reason, count in failure_reasons_counter.most_common()
        ]

        return {
            "total_checks": total_checks,
            "passed": passed,
            "failed": failed,
            "pass_rate_pct": round(pass_rate, 2),
            "failure_reasons": failure_reasons
        }

    def calculate_tone_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate tone validation compliance metrics (AC #8).

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Dict with tone metrics:
                - total_validations: Total tone validations
                - passed: Number passed
                - failed: Number failed
                - pass_rate_pct: Percentage passed
                - violations_by_category: List of {"category": str, "count": int}
        """
        # Get tone validation events from audit log
        tone_entries = self.session.query(AuditLog).filter(
            AuditLog.event_type == "tone_validated",
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).all()

        total_validations = len(tone_entries)
        passed = 0
        failed = 0
        violations_counter = Counter()

        for entry in tone_entries:
            event_data = json.loads(entry.event_data)
            validation_result = event_data.get("validation_result", "unknown")

            if validation_result == "passed":
                passed += 1
            else:
                failed += 1
                # Count each detected violation phrase
                for violation in event_data.get("violations", []):
                    violations_counter[violation] += 1

        pass_rate = (passed / total_validations * 100) if total_validations > 0 else 0.0

        # Convert violations to list format
        violations_by_category = [
            {"category": phrase, "count": count}
            for phrase, count in violations_counter.most_common(10)  # Top 10
        ]

        return {
            "total_validations": total_validations,
            "passed": passed,
            "failed": failed,
            "pass_rate_pct": round(pass_rate, 2),
            "violations_by_category": violations_by_category
        }

    def calculate_operator_metrics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate operator action compliance metrics (AC #8).

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            Dict with operator metrics:
                - total_actions: Total operator actions
                - approvals: Number of approvals
                - overrides: Number of overrides
                - flags: Number of flags
                - actions_by_operator: List of {"operator_id": str, "count": int}
        """
        # Get operator action events from audit log
        operator_entries = self.session.query(AuditLog).filter(
            AuditLog.event_type == "operator_action",
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).all()

        total_actions = len(operator_entries)
        approvals = 0
        overrides = 0
        flags = 0
        actions_by_operator_counter = Counter()

        for entry in operator_entries:
            event_data = json.loads(entry.event_data)
            action = event_data.get("action", "unknown")

            if action == "approved":
                approvals += 1
            elif action == "overridden":
                overrides += 1
            elif action == "flagged":
                flags += 1

            # Count actions by operator
            if entry.operator_id:
                actions_by_operator_counter[entry.operator_id] += 1

        # Convert operator actions to list format
        actions_by_operator = [
            {"operator_id": operator_id, "count": count}
            for operator_id, count in actions_by_operator_counter.most_common()
        ]

        return {
            "total_actions": total_actions,
            "approvals": approvals,
            "overrides": overrides,
            "flags": flags,
            "actions_by_operator": actions_by_operator
        }
