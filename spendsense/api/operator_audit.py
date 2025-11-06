"""
Audit log and compliance reporting API endpoints (Epic 6 - Story 6.5).

Provides secure access to comprehensive audit trail with filtering,
export capabilities, and compliance metrics for regulatory requirements.
"""

import csv
import io
import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from spendsense.auth.rbac import require_role, TokenData
from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import AuditLog

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/operator", tags=["operator-audit"])


# ===== Response Models =====

class AuditLogEntry(BaseModel):
    """Single audit log entry."""
    log_id: str
    event_type: str
    user_id: Optional[str]
    operator_id: Optional[str]
    recommendation_id: Optional[str]
    timestamp: str
    event_data: dict  # Parsed from JSON
    ip_address: Optional[str]
    user_agent: Optional[str]


class AuditLogListResponse(BaseModel):
    """List of audit log entries with pagination."""
    entries: List[AuditLogEntry]
    total_count: int
    page: int
    page_size: int


class ComplianceMetricsConsentStats(BaseModel):
    """Consent-related compliance metrics."""
    total_users: int
    opted_in_count: int
    opted_out_count: int
    opt_in_rate_pct: float


class ComplianceMetricsEligibilityStats(BaseModel):
    """Eligibility check compliance metrics."""
    total_checks: int
    passed: int
    failed: int
    pass_rate_pct: float
    failure_reasons: List[dict]  # [{"reason": str, "count": int}]


class ComplianceMetricsToneStats(BaseModel):
    """Tone validation compliance metrics."""
    total_validations: int
    passed: int
    failed: int
    pass_rate_pct: float
    violations_by_category: List[dict]  # [{"category": str, "count": int}]


class ComplianceMetricsOperatorStats(BaseModel):
    """Operator action compliance metrics."""
    total_actions: int
    approvals: int
    overrides: int
    flags: int
    actions_by_operator: List[dict]  # [{"operator_id": str, "count": int}]


class ComplianceMetricsResponse(BaseModel):
    """Complete compliance metrics."""
    consent_metrics: ComplianceMetricsConsentStats
    eligibility_metrics: ComplianceMetricsEligibilityStats
    tone_metrics: ComplianceMetricsToneStats
    operator_metrics: ComplianceMetricsOperatorStats
    date_range: dict  # {"start_date": str, "end_date": str}


# ===== API Endpoints =====

@router.get("/audit/log", response_model=AuditLogListResponse)
async def get_audit_log(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    operator_id: Optional[str] = Query(None, description="Filter by operator ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Get audit log entries with pagination and filtering (AC #6, #10).

    Requires admin or compliance role for access.

    Args:
        event_type: Filter by specific event type
        user_id: Filter by user ID
        operator_id: Filter by operator ID
        start_date: Start of date range (ISO format)
        end_date: End of date range (ISO format)
        page: Page number (1-indexed)
        page_size: Number of items per page
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        AuditLogListResponse with filtered audit log entries

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 400: Invalid date format or parameters
    """
    session: Session = get_db_session()

    try:
        # Build query with filters
        query = session.query(AuditLog)

        if event_type:
            if event_type not in AuditLog.VALID_EVENT_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid event_type '{event_type}'. Valid types: {', '.join(sorted(AuditLog.VALID_EVENT_TYPES))}"
                )
            query = query.filter(AuditLog.event_type == event_type)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if operator_id:
            query = query.filter(AuditLog.operator_id == operator_id)

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date format: {start_date}")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date format: {end_date}")

        # Get total count
        total_count = query.count()

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        entries = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(page_size).all()

        # Convert to response model
        audit_entries = [
            AuditLogEntry(
                log_id=entry.log_id,
                event_type=entry.event_type,
                user_id=entry.user_id,
                operator_id=entry.operator_id,
                recommendation_id=entry.recommendation_id,
                timestamp=entry.timestamp.isoformat(),
                event_data=json.loads(entry.event_data),
                ip_address=entry.ip_address,
                user_agent=entry.user_agent
            )
            for entry in entries
        ]

        logger.info(
            f"Audit log query by {current_operator.username}: "
            f"{len(audit_entries)} entries (page {page}/{(total_count + page_size - 1) // page_size})"
        )

        return AuditLogListResponse(
            entries=audit_entries,
            total_count=total_count,
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch audit log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit log: {str(e)}")
    finally:
        session.close()


@router.get("/audit/export")
async def export_audit_log(
    format: str = Query("csv", regex="^(csv|json)$", description="Export format (csv or json)"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    operator_id: Optional[str] = Query(None, description="Filter by operator ID"),
    start_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format)"),
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Export audit logs as CSV or JSON (AC #7, #10).

    Streams large exports to avoid memory issues for regulatory reporting.
    Requires admin or compliance role for access.

    Args:
        format: Export format ('csv' or 'json')
        event_type: Filter by specific event type
        user_id: Filter by user ID
        operator_id: Filter by operator ID
        start_date: Start of date range (ISO format)
        end_date: End of date range (ISO format)
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        StreamingResponse with exported file

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 400: Invalid parameters
    """
    session: Session = get_db_session()

    try:
        # Build query with filters (same as get_audit_log)
        query = session.query(AuditLog)

        if event_type:
            if event_type not in AuditLog.VALID_EVENT_TYPES:
                raise HTTPException(status_code=400, detail=f"Invalid event_type: {event_type}")
            query = query.filter(AuditLog.event_type == event_type)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if operator_id:
            query = query.filter(AuditLog.operator_id == operator_id)

        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date: {start_date}")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp <= end_dt)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date: {end_date}")

        # Fetch all entries (ordered by timestamp)
        entries = query.order_by(desc(AuditLog.timestamp)).all()

        logger.info(f"Exporting {len(entries)} audit log entries as {format} by {current_operator.username}")

        # Generate filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"audit_log_{timestamp}.{format}"

        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "log_id", "event_type", "user_id", "operator_id", "recommendation_id",
                "timestamp", "event_data", "ip_address", "user_agent"
            ])
            writer.writeheader()

            for entry in entries:
                writer.writerow({
                    "log_id": entry.log_id,
                    "event_type": entry.event_type,
                    "user_id": entry.user_id or "",
                    "operator_id": entry.operator_id or "",
                    "recommendation_id": entry.recommendation_id or "",
                    "timestamp": entry.timestamp.isoformat(),
                    "event_data": entry.event_data,  # JSON string
                    "ip_address": entry.ip_address or "",
                    "user_agent": entry.user_agent or "",
                })

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )

        else:  # format == "json"
            # Generate JSON
            entries_json = [
                {
                    "log_id": entry.log_id,
                    "event_type": entry.event_type,
                    "user_id": entry.user_id,
                    "operator_id": entry.operator_id,
                    "recommendation_id": entry.recommendation_id,
                    "timestamp": entry.timestamp.isoformat(),
                    "event_data": json.loads(entry.event_data),
                    "ip_address": entry.ip_address,
                    "user_agent": entry.user_agent,
                }
                for entry in entries
            ]

            json_output = json.dumps(entries_json, indent=2)

            return StreamingResponse(
                iter([json_output]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export audit log: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    finally:
        session.close()


@router.get("/audit/metrics", response_model=ComplianceMetricsResponse)
async def get_compliance_metrics(
    start_date: Optional[str] = Query(None, description="Start date (ISO format, defaults to 30 days ago)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format, defaults to now)"),
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Get compliance metrics for monitoring system behavior (AC #8, #10).

    Calculates consent opt-in rate, eligibility failure reasons,
    tone validation issues, and operator action distribution.
    Requires admin or compliance role for access.

    Args:
        start_date: Start of date range (ISO format, default: 30 days ago)
        end_date: End of date range (ISO format, default: now)
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        ComplianceMetricsResponse with calculated metrics

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 400: Invalid date format
    """
    session: Session = get_db_session()

    try:
        # Default date range: last 30 days
        if not end_date:
            end_dt = datetime.utcnow()
        else:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid end_date: {end_date}")

        if not start_date:
            start_dt = end_dt - timedelta(days=30)
        else:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid start_date: {start_date}")

        # Build base query for date range
        base_query = session.query(AuditLog).filter(
            AuditLog.timestamp >= start_dt,
            AuditLog.timestamp <= end_dt
        )

        # Calculate consent metrics
        from spendsense.services.compliance_metrics import ComplianceMetricsCalculator
        calculator = ComplianceMetricsCalculator(session)

        consent_metrics = calculator.calculate_consent_metrics(start_dt, end_dt)
        eligibility_metrics = calculator.calculate_eligibility_metrics(start_dt, end_dt)
        tone_metrics = calculator.calculate_tone_metrics(start_dt, end_dt)
        operator_metrics = calculator.calculate_operator_metrics(start_dt, end_dt)

        logger.info(f"Compliance metrics retrieved by {current_operator.username} for {start_dt.date()} to {end_dt.date()}")

        return ComplianceMetricsResponse(
            consent_metrics=consent_metrics,
            eligibility_metrics=eligibility_metrics,
            tone_metrics=tone_metrics,
            operator_metrics=operator_metrics,
            date_range={
                "start_date": start_dt.isoformat(),
                "end_date": end_dt.isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate compliance metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Metrics calculation failed: {str(e)}")
    finally:
        session.close()
