"""
Consent management system for SpendSense.

This module provides consent tracking with opt-in/opt-out capabilities and audit logging.
Ensures user data is only processed with explicit permission and consent changes are traceable.

Epic 5 - Story 5.1: Consent Management System
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
import logging
import structlog

from sqlalchemy.orm import Session

# Configure structured logging
logger = structlog.get_logger(__name__)


class ConsentStatus(str, Enum):
    """Consent status values."""
    OPTED_IN = "opted_in"
    OPTED_OUT = "opted_out"


class ConsentNotGrantedError(Exception):
    """Raised when attempting to process data without user consent."""
    pass


@dataclass
class ConsentResult:
    """
    Result of consent operation with audit trail.

    Similar to MatchingResult pattern from Story 4.3.
    """
    user_id: str
    consent_status: ConsentStatus
    consent_timestamp: Optional[datetime]
    consent_version: str
    audit_trail: dict


class ConsentService:
    """
    Service for managing user consent with audit logging.

    Uses dependency injection pattern following Story 4.3 RecommendationMatcher.
    """

    def __init__(self, db_session: Session):
        """
        Initialize consent service.

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def record_consent(
        self,
        user_id: str,
        consent_status: ConsentStatus,
        consent_version: str = "1.0"
    ) -> ConsentResult:
        """
        Record user consent change with audit logging.

        Args:
            user_id: User identifier
            consent_status: New consent status (opted_in or opted_out)
            consent_version: Version of consent terms (default: "1.0")

        Returns:
            ConsentResult with audit trail

        Raises:
            ValueError: If user not found
        """
        from spendsense.ingestion.database_writer import User

        # Fetch user
        user = self.db_session.query(User).filter(User.user_id == user_id).first()
        if not user:
            logger.error("user_not_found", user_id=user_id)
            raise ValueError(f"User {user_id} not found")

        # Store previous status for audit
        previous_status = user.consent_status
        timestamp = datetime.utcnow()

        # Update consent fields
        user.consent_status = consent_status.value
        user.consent_timestamp = timestamp
        user.consent_version = consent_version

        # Commit transaction
        self.db_session.commit()

        # Build audit trail
        audit_trail = {
            "action": "consent_recorded",
            "user_id": user_id,
            "previous_status": previous_status,
            "new_status": consent_status.value,
            "consent_version": consent_version,
            "timestamp": timestamp.isoformat(),
            "change_detected": previous_status != consent_status.value
        }

        # Structured logging for audit
        logger.info(
            "consent_change_recorded",
            user_id=user_id,
            previous_status=previous_status,
            new_status=consent_status.value,
            timestamp=timestamp.isoformat()
        )

        return ConsentResult(
            user_id=user_id,
            consent_status=ConsentStatus(consent_status.value),
            consent_timestamp=timestamp,
            consent_version=consent_version,
            audit_trail=audit_trail
        )

    def check_consent(self, user_id: str) -> ConsentResult:
        """
        Check user consent status.

        Args:
            user_id: User identifier

        Returns:
            ConsentResult with current status

        Raises:
            ValueError: If user not found
        """
        from spendsense.ingestion.database_writer import User

        # Fetch user
        user = self.db_session.query(User).filter(User.user_id == user_id).first()
        if not user:
            logger.error("user_not_found", user_id=user_id)
            raise ValueError(f"User {user_id} not found")

        # Build audit trail
        audit_trail = {
            "action": "consent_checked",
            "user_id": user_id,
            "consent_status": user.consent_status,
            "consent_version": user.consent_version or "1.0",
            "timestamp": datetime.utcnow().isoformat()
        }

        return ConsentResult(
            user_id=user_id,
            consent_status=ConsentStatus(user.consent_status),
            consent_timestamp=user.consent_timestamp,
            consent_version=user.consent_version or "1.0",
            audit_trail=audit_trail
        )

    def require_consent(self, user_id: str) -> None:
        """
        Verify user has opted in to data processing.

        Used as consent gate before processing operations.

        Args:
            user_id: User identifier

        Raises:
            ConsentNotGrantedError: If user has not opted in
            ValueError: If user not found
        """
        result = self.check_consent(user_id)

        if result.consent_status != ConsentStatus.OPTED_IN:
            logger.warning(
                "processing_blocked_no_consent",
                user_id=user_id,
                consent_status=result.consent_status.value
            )
            raise ConsentNotGrantedError(
                f"User {user_id} has not granted consent for data processing. "
                f"Current status: {result.consent_status.value}"
            )

        logger.debug("consent_verified", user_id=user_id)


def require_consent_decorator(func):
    """
    Decorator to require consent before function execution.

    Usage:
        @require_consent_decorator
        def process_user_data(user_id: str, db_session: Session, **kwargs):
            # Function body

    The decorated function must accept user_id and db_session as parameters.
    """
    def wrapper(*args, **kwargs):
        # Extract user_id and db_session from args/kwargs
        user_id = kwargs.get('user_id') or (args[0] if len(args) > 0 else None)
        db_session = kwargs.get('db_session') or (args[1] if len(args) > 1 else None)

        if not user_id or not db_session:
            raise ValueError("require_consent_decorator requires user_id and db_session parameters")

        # Check consent before proceeding
        consent_service = ConsentService(db_session)
        consent_service.require_consent(user_id)

        # Execute function
        return func(*args, **kwargs)

    return wrapper
