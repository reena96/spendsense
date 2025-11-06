"""
Audit logging service for Epic 6 Story 6.5.

Provides centralized audit trail creation for all system decisions
and operator actions with consistent structure and validation.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from sqlalchemy.orm import Session
from spendsense.ingestion.database_writer import AuditLog
from spendsense.config.database import get_db_session


class AuditService:
    """
    Centralized audit logging service.

    Handles creation, validation, and storage of audit log entries
    for compliance and regulatory requirements.
    """

    @staticmethod
    def log_event(
        event_type: str,
        event_data: Dict[str, Any],
        user_id: Optional[str] = None,
        operator_id: Optional[str] = None,
        recommendation_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session: Optional[Session] = None
    ) -> str:
        """
        Log an audit event to the database.

        Args:
            event_type: Type of event (must be in VALID_EVENT_TYPES)
            event_data: Event-specific data as dictionary (will be JSON serialized)
            user_id: User ID (nullable for operator-only events)
            operator_id: Operator ID (nullable for system events)
            recommendation_id: Recommendation ID (nullable)
            ip_address: IP address of requester
            user_agent: User agent string
            session: Optional SQLAlchemy session (creates new if not provided)

        Returns:
            log_id: Generated audit log ID

        Raises:
            ValueError: If event_type is invalid
        """
        # Validate event type
        if event_type not in AuditLog.VALID_EVENT_TYPES:
            raise ValueError(
                f"Invalid event_type '{event_type}'. "
                f"Must be one of: {', '.join(sorted(AuditLog.VALID_EVENT_TYPES))}"
            )

        # Generate log ID
        log_id = f"audit_{uuid.uuid4().hex[:12]}"

        # Serialize event data to JSON
        event_data_json = json.dumps(event_data, default=str)

        # Create audit log entry
        audit_entry = AuditLog(
            log_id=log_id,
            event_type=event_type,
            user_id=user_id,
            operator_id=operator_id,
            recommendation_id=recommendation_id,
            timestamp=datetime.utcnow(),
            event_data=event_data_json,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Use provided session or create new one
        close_session = False
        if session is None:
            session = get_db_session()
            close_session = True

        try:
            session.add(audit_entry)
            session.commit()
            return log_id
        except Exception as e:
            session.rollback()
            raise RuntimeError(f"Failed to log audit event: {e}") from e
        finally:
            if close_session:
                session.close()

    @staticmethod
    def log_recommendation_generated(
        user_id: str,
        recommendation_id: str,
        persona_id: str,
        content_ids: list,
        guardrail_results: Dict[str, Any],
        session: Optional[Session] = None
    ) -> str:
        """
        Log a recommendation generation event.

        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            persona_id: Assigned persona ID
            content_ids: List of recommended content IDs
            guardrail_results: Guardrail check results (consent, eligibility, tone)
            session: Optional SQLAlchemy session

        Returns:
            log_id: Generated audit log ID
        """
        event_data = {
            "persona_id": persona_id,
            "content_ids": content_ids,
            "guardrail_results": guardrail_results,
            "recommendation_count": len(content_ids)
        }

        return AuditService.log_event(
            event_type="recommendation_generated",
            event_data=event_data,
            user_id=user_id,
            recommendation_id=recommendation_id,
            session=session
        )

    @staticmethod
    def log_consent_changed(
        user_id: str,
        old_status: str,
        new_status: str,
        consent_version: str,
        changed_by: Optional[str] = None,
        session: Optional[Session] = None
    ) -> str:
        """
        Log a consent status change event.

        Args:
            user_id: User ID
            old_status: Previous consent status
            new_status: New consent status
            consent_version: Consent policy version
            changed_by: Operator ID if changed by operator, else None (user-initiated)
            session: Optional SQLAlchemy session

        Returns:
            log_id: Generated audit log ID
        """
        event_data = {
            "old_status": old_status,
            "new_status": new_status,
            "consent_version": consent_version,
            "changed_by": changed_by or "user"
        }

        return AuditService.log_event(
            event_type="consent_changed",
            event_data=event_data,
            user_id=user_id,
            operator_id=changed_by,
            session=session
        )

    @staticmethod
    def log_eligibility_checked(
        user_id: str,
        recommendation_id: str,
        passed: bool,
        failure_reasons: list,
        thresholds: Dict[str, Any],
        user_values: Dict[str, Any],
        session: Optional[Session] = None
    ) -> str:
        """
        Log an eligibility check event.

        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            passed: Whether eligibility check passed
            failure_reasons: List of failure reasons (empty if passed)
            thresholds: Eligibility thresholds checked
            user_values: User's actual values
            session: Optional SQLAlchemy session

        Returns:
            log_id: Generated audit log ID
        """
        event_data = {
            "passed": passed,
            "failure_reasons": failure_reasons,
            "thresholds": thresholds,
            "user_values": user_values
        }

        return AuditService.log_event(
            event_type="eligibility_checked",
            event_data=event_data,
            user_id=user_id,
            recommendation_id=recommendation_id,
            session=session
        )

    @staticmethod
    def log_tone_validated(
        user_id: str,
        recommendation_id: str,
        passed: bool,
        detected_violations: list,
        severity: str,
        original_text: str,
        session: Optional[Session] = None
    ) -> str:
        """
        Log a tone validation event.

        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            passed: Whether tone validation passed
            detected_violations: List of detected phrase violations
            severity: Severity level (warning/critical)
            original_text: Original text that was validated
            session: Optional SQLAlchemy session

        Returns:
            log_id: Generated audit log ID
        """
        event_data = {
            "passed": passed,
            "detected_violations": detected_violations,
            "severity": severity,
            "original_text": original_text
        }

        return AuditService.log_event(
            event_type="tone_validated",
            event_data=event_data,
            user_id=user_id,
            recommendation_id=recommendation_id,
            session=session
        )

    @staticmethod
    def log_operator_action(
        operator_id: str,
        action: str,
        recommendation_id: str,
        user_id: str,
        justification: Optional[str] = None,
        review_time_seconds: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session: Optional[Session] = None
    ) -> str:
        """
        Log an operator action event (approve, override, flag).

        Args:
            operator_id: Operator ID
            action: Action taken (approved/overridden/flagged)
            recommendation_id: Recommendation ID
            user_id: User ID
            justification: Justification text (required for override)
            review_time_seconds: Time spent reviewing
            ip_address: IP address
            user_agent: User agent string
            session: Optional SQLAlchemy session

        Returns:
            log_id: Generated audit log ID
        """
        event_data = {
            "action": action,
            "justification": justification,
            "review_time_seconds": review_time_seconds
        }

        return AuditService.log_event(
            event_type="operator_action",
            event_data=event_data,
            user_id=user_id,
            operator_id=operator_id,
            recommendation_id=recommendation_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session=session
        )

    @staticmethod
    def log_persona_overridden(
        operator_id: str,
        user_id: str,
        old_persona: str,
        new_persona: str,
        justification: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session: Optional[Session] = None
    ) -> str:
        """
        Log a persona override event.

        Args:
            operator_id: Operator ID
            user_id: User ID
            old_persona: Previous persona ID
            new_persona: New persona ID
            justification: Justification for override
            ip_address: IP address
            user_agent: User agent string
            session: Optional SQLAlchemy session

        Returns:
            log_id: Generated audit log ID
        """
        event_data = {
            "old_persona": old_persona,
            "new_persona": new_persona,
            "justification": justification
        }

        return AuditService.log_event(
            event_type="persona_overridden",
            event_data=event_data,
            user_id=user_id,
            operator_id=operator_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session=session
        )
