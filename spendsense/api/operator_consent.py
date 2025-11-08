"""
Operator Consent Management API (Epic 6 - Story 6.6).

Provides batch consent operations, consent history, and user filtering
for compliance officers and administrators.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData
from spendsense.guardrails.consent import ConsentService, ConsentStatus
from spendsense.config.database import get_db_path
from spendsense.ingestion.database_writer import User, AuditLog

router = APIRouter(prefix="/api/operator/consent", tags=["Operator Consent"])


# Request/Response Models
class BatchConsentRequest(BaseModel):
    """Request model for batch consent operations."""
    user_ids: List[str] = Field(..., description="List of user IDs to update", min_items=1, max_items=1000)
    consent_status: str = Field(..., description="Consent status: 'opted_in' or 'opted_out'")
    reason: str = Field(..., description="Reason for bulk consent change", min_length=20)
    consent_version: str = Field(default="1.0", description="Consent version")


class BatchConsentResponse(BaseModel):
    """Response model for batch consent operations."""
    success_count: int
    failure_count: int
    failed_users: List[dict]
    message: str


class ConsentUserInfo(BaseModel):
    """User information with consent status."""
    user_id: str
    name: str
    consent_status: str
    consent_timestamp: Optional[str]
    consent_version: str


class ConsentUserListResponse(BaseModel):
    """Response model for user list with consent filters."""
    total: int
    users: List[ConsentUserInfo]
    filters_applied: dict


class ConsentHistoryEntry(BaseModel):
    """Single consent change history entry."""
    timestamp: str
    old_status: Optional[str]
    new_status: str
    changed_by: str  # operator_id or 'user'
    reason: Optional[str]
    operator_name: Optional[str]


class ConsentHistoryResponse(BaseModel):
    """Response model for consent change history."""
    user_id: str
    history: List[ConsentHistoryEntry]
    total_changes: int


@router.post("/batch", response_model=BatchConsentResponse)
async def batch_consent_change(
    request: BatchConsentRequest,
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Perform bulk consent changes (admin only).

    Updates consent status for multiple users at once. All changes are
    logged individually in the audit trail.

    **Requires admin role.**

    Args:
        request: Batch consent request with user IDs, status, and reason
        current_operator: Operator info from JWT token

    Returns:
        BatchConsentResponse with success/failure counts

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 403: Forbidden (admin only)
        HTTPException 400: Invalid consent status or empty user list
    """
    # Validate consent status
    if request.consent_status not in ['opted_in', 'opted_out']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status: {request.consent_status}"
        )

    db_path = get_db_path()
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not found")

    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)

    success_count = 0
    failure_count = 0
    failed_users = []

    with Session() as session:
        consent_service = ConsentService(session)

        for user_id in request.user_ids:
            try:
                # Record consent for this user
                consent_status_enum = ConsentStatus(request.consent_status)
                consent_service.record_consent(
                    user_id=user_id,
                    consent_status=consent_status_enum,
                    consent_version=request.consent_version
                )

                # Log to audit trail
                audit_entry = AuditLog(
                    event_type="consent_changed_batch",
                    user_id=user_id,
                    operator_id=current_operator.operator_id,
                    timestamp=datetime.utcnow(),
                    event_data={
                        "new_status": request.consent_status,
                        "reason": request.reason,
                        "consent_version": request.consent_version,
                        "batch_operation": True
                    }
                )
                session.add(audit_entry)
                success_count += 1

            except Exception as e:
                failure_count += 1
                failed_users.append({
                    "user_id": user_id,
                    "error": str(e)
                })

        session.commit()

    return BatchConsentResponse(
        success_count=success_count,
        failure_count=failure_count,
        failed_users=failed_users,
        message=f"Batch consent update: {success_count} succeeded, {failure_count} failed"
    )


@router.get("/users", response_model=ConsentUserListResponse)
async def get_users_with_consent_filter(
    consent_status: Optional[str] = Query(None, description="Filter by: 'opted_in', 'opted_out', or None for all"),
    changed_since: Optional[str] = Query(None, description="Filter by changes since date (ISO format)"),
    limit: int = Query(50, ge=1, le=500, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Get users with consent status filters.

    Supports filtering by consent status and recent changes.
    **Requires reviewer or admin role.**

    Args:
        consent_status: Filter by consent status (optional)
        changed_since: ISO date string to filter recent changes
        limit: Results per page
        offset: Pagination offset
        current_operator: Operator info from JWT token

    Returns:
        ConsentUserListResponse with filtered user list

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 403: Forbidden
        HTTPException 400: Invalid filter parameters
    """
    # Validate consent_status if provided
    if consent_status and consent_status not in ['opted_in', 'opted_out']:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid consent_status filter: {consent_status}"
        )

    db_path = get_db_path()
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not found")

    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Build query
        query = session.query(User)

        # Apply consent status filter
        if consent_status:
            query = query.filter(User.consent_status == consent_status)

        # Apply changed_since filter
        if changed_since:
            try:
                cutoff_date = datetime.fromisoformat(changed_since)
                query = query.filter(User.consent_timestamp >= cutoff_date)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format: {changed_since}. Use ISO format (YYYY-MM-DD)"
                )

        # Get total count
        total = query.count()

        # Apply pagination
        users = query.order_by(User.user_id).offset(offset).limit(limit).all()

        # Build response
        user_list = [
            ConsentUserInfo(
                user_id=user.user_id,
                name=user.name,
                consent_status=user.consent_status,
                consent_timestamp=user.consent_timestamp.isoformat() if user.consent_timestamp else None,
                consent_version=user.consent_version or "1.0"
            )
            for user in users
        ]

        return ConsentUserListResponse(
            total=total,
            users=user_list,
            filters_applied={
                "consent_status": consent_status,
                "changed_since": changed_since,
                "limit": limit,
                "offset": offset
            }
        )


@router.get("/{user_id}/history", response_model=ConsentHistoryResponse)
async def get_consent_history(
    user_id: str,
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Get consent change history for a user.

    Returns timeline of all consent changes from audit log.
    **Requires reviewer or admin role.**

    Args:
        user_id: User identifier
        current_operator: Operator info from JWT token

    Returns:
        ConsentHistoryResponse with change history timeline

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 403: Forbidden
        HTTPException 404: User not found
    """
    db_path = get_db_path()
    if not db_path.exists():
        raise HTTPException(status_code=500, detail="Database not found")

    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Verify user exists
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User not found: {user_id}")

        # Get consent changes from audit log
        consent_logs = session.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.event_type.in_(['consent_changed', 'consent_changed_batch'])
        ).order_by(AuditLog.timestamp.desc()).all()

        # Build history
        history = []
        for log in consent_logs:
            # Parse event_data if it's a JSON string
            if isinstance(log.event_data, str):
                try:
                    event_data = json.loads(log.event_data)
                except (json.JSONDecodeError, TypeError):
                    event_data = {}
            else:
                event_data = log.event_data or {}

            # Get operator name if available
            operator_name = None
            if log.operator_id:
                from spendsense.auth.operator import Operator
                operator = session.query(Operator).filter(
                    Operator.operator_id == log.operator_id
                ).first()
                if operator:
                    operator_name = operator.name

            history.append(ConsentHistoryEntry(
                timestamp=log.timestamp.isoformat(),
                old_status=event_data.get('old_status'),
                new_status=event_data.get('new_status', 'unknown'),
                changed_by=log.operator_id or 'user',
                reason=event_data.get('reason'),
                operator_name=operator_name
            ))

        return ConsentHistoryResponse(
            user_id=user_id,
            history=history,
            total_changes=len(history)
        )
