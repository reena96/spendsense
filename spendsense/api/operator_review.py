"""
Operator Review Queue API (Epic 6 - Story 6.4)

Provides operator endpoints for reviewing flagged recommendations with
approve/override/flag capabilities. Integrates with Epic 5 guardrail pipeline.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, desc, or_, and_
from sqlalchemy.orm import sessionmaker

from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData
from spendsense.config.database import get_db_path
from spendsense.ingestion.database_writer import (
    FlaggedRecommendation,
    User,
    Operator,
    AuthAuditLog
)


# Router for operator review endpoints
router = APIRouter(prefix="/api/operator", tags=["operator-review"])

# Database path (centralized configuration)
DB_PATH = get_db_path()


# ===== Response Models =====

class GuardrailStatusModel(BaseModel):
    """Guardrail check results."""
    consent_status: str
    eligibility_passed: bool
    eligibility_failures: List[str]
    tone_passed: bool
    tone_violations: List[str]
    disclaimer_present: bool


class DecisionTraceModel(BaseModel):
    """Decision trace showing why recommendation was generated."""
    persona_id: str
    persona_name: str
    matching_signals: Dict[str, Any]
    ranking_score: Optional[float] = None
    generation_reason: str


class ReviewQueueItem(BaseModel):
    """Single item in review queue."""
    recommendation_id: str
    user_id: str
    user_name: str
    content_id: str
    content_title: str
    content_type: str
    rationale: str
    flagged_at: str
    flagged_by: Optional[str]
    flag_reason: str
    review_status: str
    guardrail_status: GuardrailStatusModel
    decision_trace: DecisionTraceModel


class ReviewQueueResponse(BaseModel):
    """Review queue with pagination."""
    items: List[ReviewQueueItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class RecommendationDetail(BaseModel):
    """Full recommendation details for review."""
    recommendation_id: str
    user_id: str
    user_name: str
    content_id: str
    content_title: str
    content_type: str
    rationale: str
    flagged_at: str
    flagged_by: Optional[str]
    flag_reason: str
    guardrail_status: GuardrailStatusModel
    decision_trace: DecisionTraceModel
    review_status: str
    reviewed_at: Optional[str]
    reviewed_by: Optional[str]
    review_notes: Optional[str]


class ApproveRequest(BaseModel):
    """Request to approve a recommendation."""
    notes: Optional[str] = Field(None, description="Optional approval notes")


class OverrideRequest(BaseModel):
    """Request to override/block a recommendation."""
    justification: str = Field(..., min_length=50, description="Override justification (min 50 chars)")


class FlagRequest(BaseModel):
    """Request to flag recommendation for escalation."""
    flag_reason: str = Field(..., description="Reason for flagging")
    notes: Optional[str] = Field(None, description="Additional notes")


class BatchApproveRequest(BaseModel):
    """Request to batch approve multiple recommendations."""
    recommendation_ids: List[str] = Field(..., min_items=1, description="List of recommendation IDs to approve")


class ActionResponse(BaseModel):
    """Response after action taken."""
    recommendation_id: str
    action: str
    status: str
    operator_id: str
    timestamp: str


class BatchApproveResponse(BaseModel):
    """Response after batch approval."""
    approved: int
    failed: int
    failed_ids: List[str]
    timestamp: str


# ===== Utility Functions =====

def get_db_session():
    """Get database session."""
    if not DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Database not available. Please run data ingestion first."
        )

    engine = create_engine(f"sqlite:///{str(DB_PATH)}")
    Session = sessionmaker(bind=engine)
    return Session()


def parse_guardrail_status(json_data: str | Dict[str, Any]) -> GuardrailStatusModel:
    """
    Parse guardrail status from JSON string or dict.

    Args:
        json_data: JSON string or dictionary containing guardrail status

    Returns:
        GuardrailStatusModel with parsed data
    """
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    return GuardrailStatusModel(**json_data)


def parse_decision_trace(json_data: str | Dict[str, Any]) -> DecisionTraceModel:
    """
    Parse decision trace from JSON string or dict.

    Args:
        json_data: JSON string or dictionary containing decision trace

    Returns:
        DecisionTraceModel with parsed data
    """
    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    return DecisionTraceModel(**json_data)


# ===== API Endpoints =====

@router.get("/review/queue", response_model=ReviewQueueResponse)
async def get_review_queue(
    status: Optional[str] = Query(None, description="Filter by status (pending/approved/overridden/escalated)"),
    persona: Optional[str] = Query(None, description="Filter by persona type"),
    flag_reason: Optional[str] = Query(None, description="Filter by flag reason"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Get review queue with filters and pagination (AC #1, #9).

    Returns list of flagged recommendations requiring operator review.

    Args:
        status: Filter by review status
        persona: Filter by persona type
        flag_reason: Filter by flag reason (eligibility_fail, tone_fail, manual_flag)
        content_type: Filter by content type (education, partner_offer)
        page: Page number (1-indexed)
        page_size: Items per page (max 100)
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        ReviewQueueResponse with items and pagination info

    Raises:
        HTTPException 401: Unauthorized
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 503: Database unavailable
    """
    session = get_db_session()

    try:
        # Build query with filters
        query = session.query(FlaggedRecommendation)

        if status:
            query = query.filter(FlaggedRecommendation.review_status == status)

        if flag_reason:
            query = query.filter(FlaggedRecommendation.flag_reason == flag_reason)

        if content_type:
            query = query.filter(FlaggedRecommendation.content_type == content_type)

        if persona:
            # Filter by persona_id in decision_trace JSON field
            # SQLite JSON extraction: json_extract(column, '$.key')
            from sqlalchemy import func, text
            query = query.filter(
                func.json_extract(FlaggedRecommendation.decision_trace, '$.persona_id') == persona
            )

        # Count total before pagination
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        items_query = query.order_by(desc(FlaggedRecommendation.flagged_at)).limit(page_size).offset(offset)

        # Fetch items
        items = []
        for rec in items_query.all():
            # Get user name
            user = session.query(User).filter(User.user_id == rec.user_id).first()
            user_name = user.name if user else "Unknown"

            # Parse JSON fields
            guardrail_status = parse_guardrail_status(rec.guardrail_status)
            decision_trace = parse_decision_trace(rec.decision_trace)

            items.append(ReviewQueueItem(
                recommendation_id=rec.recommendation_id,
                user_id=rec.user_id,
                user_name=user_name,
                content_id=rec.content_id,
                content_title=rec.content_title,
                content_type=rec.content_type,
                rationale=rec.rationale,
                flagged_at=rec.flagged_at.isoformat(),
                flagged_by=rec.flagged_by,
                flag_reason=rec.flag_reason,
                review_status=rec.review_status,
                guardrail_status=guardrail_status,
                decision_trace=decision_trace
            ))

        has_more = (offset + page_size) < total

        return ReviewQueueResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            has_more=has_more
        )

    finally:
        session.close()


@router.get("/review/{recommendation_id}", response_model=RecommendationDetail)
async def get_recommendation_detail(
    recommendation_id: str,
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Get full recommendation details for review (AC #2, #4).

    Returns complete information including guardrail results and decision trace.

    Args:
        recommendation_id: Recommendation identifier
        current_operator: Authenticated operator

    Returns:
        RecommendationDetail with complete information

    Raises:
        HTTPException 404: Recommendation not found
    """
    session = get_db_session()

    try:
        rec = session.query(FlaggedRecommendation).filter(
            FlaggedRecommendation.recommendation_id == recommendation_id
        ).first()

        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation {recommendation_id} not found"
            )

        # Get user name
        user = session.query(User).filter(User.user_id == rec.user_id).first()
        user_name = user.name if user else "Unknown"

        # Parse JSON fields
        guardrail_status = parse_guardrail_status(rec.guardrail_status)
        decision_trace = parse_decision_trace(rec.decision_trace)

        return RecommendationDetail(
            recommendation_id=rec.recommendation_id,
            user_id=rec.user_id,
            user_name=user_name,
            content_id=rec.content_id,
            content_title=rec.content_title,
            content_type=rec.content_type,
            rationale=rec.rationale,
            flagged_at=rec.flagged_at.isoformat(),
            flagged_by=rec.flagged_by,
            flag_reason=rec.flag_reason,
            guardrail_status=guardrail_status,
            decision_trace=decision_trace,
            review_status=rec.review_status,
            reviewed_at=rec.reviewed_at.isoformat() if rec.reviewed_at else None,
            reviewed_by=rec.reviewed_by,
            review_notes=rec.review_notes
        )

    finally:
        session.close()


@router.post("/review/{recommendation_id}/approve", response_model=ActionResponse)
async def approve_recommendation(
    recommendation_id: str,
    request: ApproveRequest = Body(...),
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Approve recommendation for delivery (AC #5, #8).

    Marks recommendation as approved and logs action in audit trail.

    Args:
        recommendation_id: Recommendation identifier
        request: Approval request with optional notes
        current_operator: Authenticated operator (reviewer or admin)

    Returns:
        ActionResponse with approval details

    Raises:
        HTTPException 404: Recommendation not found
    """
    session = get_db_session()

    try:
        rec = session.query(FlaggedRecommendation).filter(
            FlaggedRecommendation.recommendation_id == recommendation_id
        ).first()

        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation {recommendation_id} not found"
            )

        # Update recommendation status
        rec.review_status = "approved"
        rec.reviewed_at = datetime.now()
        rec.reviewed_by = current_operator.operator_id
        rec.review_notes = request.notes

        # Log to audit trail
        audit_entry = AuthAuditLog(
            log_id=f"audit_approve_{datetime.now().timestamp()}",
            event_type="recommendation_approved",
            operator_id=current_operator.operator_id,
            endpoint=f"/api/operator/review/{recommendation_id}/approve",
            timestamp=datetime.now(),
            details=json.dumps({
                "recommendation_id": recommendation_id,
                "user_id": rec.user_id,
                "content_id": rec.content_id,
                "notes": request.notes,
                "operator_username": current_operator.username
            })
        )

        session.add(audit_entry)
        session.commit()

        # Epic 6 Story 6.5: Log to audit_log table for compliance reporting
        try:
            from spendsense.services.audit_service import AuditService
            AuditService.log_operator_action(
                operator_id=current_operator.operator_id,
                action="approved",
                recommendation_id=recommendation_id,
                user_id=rec.user_id,
                justification=request.notes,
                session=session
            )
        except Exception as e:
            # Log but don't fail approval if audit logging fails
            logger.warning(f"audit_log_failed: {e}", extra={"recommendation_id": recommendation_id})

        return ActionResponse(
            recommendation_id=recommendation_id,
            action="approved",
            status="approved",
            operator_id=current_operator.operator_id,
            timestamp=rec.reviewed_at.isoformat()
        )

    except Exception as e:
        session.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Approval failed: {str(e)}")

    finally:
        session.close()


@router.post("/review/{recommendation_id}/override", response_model=ActionResponse)
async def override_recommendation(
    recommendation_id: str,
    request: OverrideRequest = Body(...),
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Override/block recommendation (AC #6, #8).

    Blocks delivery and requires justification. Admin only.

    Args:
        recommendation_id: Recommendation identifier
        request: Override request with justification
        current_operator: Authenticated admin operator

    Returns:
        ActionResponse with override details

    Raises:
        HTTPException 404: Recommendation not found
        HTTPException 403: Forbidden (admin required)
    """
    session = get_db_session()

    try:
        rec = session.query(FlaggedRecommendation).filter(
            FlaggedRecommendation.recommendation_id == recommendation_id
        ).first()

        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation {recommendation_id} not found"
            )

        # Update recommendation status
        rec.review_status = "overridden"
        rec.reviewed_at = datetime.now()
        rec.reviewed_by = current_operator.operator_id
        rec.review_notes = request.justification

        # Log to audit trail
        audit_entry = AuthAuditLog(
            log_id=f"audit_override_{datetime.now().timestamp()}",
            event_type="recommendation_overridden",
            operator_id=current_operator.operator_id,
            endpoint=f"/api/operator/review/{recommendation_id}/override",
            timestamp=datetime.now(),
            details=json.dumps({
                "recommendation_id": recommendation_id,
                "user_id": rec.user_id,
                "content_id": rec.content_id,
                "justification": request.justification,
                "operator_username": current_operator.username
            })
        )

        session.add(audit_entry)
        session.commit()

        # Epic 6 Story 6.5: Log to audit_log table for compliance reporting
        try:
            from spendsense.services.audit_service import AuditService
            AuditService.log_operator_action(
                operator_id=current_operator.operator_id,
                action="overridden",
                recommendation_id=recommendation_id,
                user_id=rec.user_id,
                justification=request.justification,
                session=session
            )
        except Exception as e:
            # Log but don't fail override if audit logging fails
            logger.warning(f"audit_log_failed: {e}", extra={"recommendation_id": recommendation_id})

        return ActionResponse(
            recommendation_id=recommendation_id,
            action="overridden",
            status="overridden",
            operator_id=current_operator.operator_id,
            timestamp=rec.reviewed_at.isoformat()
        )

    except Exception as e:
        session.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Override failed: {str(e)}")

    finally:
        session.close()


@router.post("/review/{recommendation_id}/flag", response_model=ActionResponse)
async def flag_recommendation(
    recommendation_id: str,
    request: FlagRequest = Body(...),
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Flag recommendation for escalation (AC #7, #8).

    Adds to escalation watch list for further review.

    Args:
        recommendation_id: Recommendation identifier
        request: Flag request with reason and notes
        current_operator: Authenticated operator (reviewer or admin)

    Returns:
        ActionResponse with flag details

    Raises:
        HTTPException 404: Recommendation not found
    """
    session = get_db_session()

    try:
        rec = session.query(FlaggedRecommendation).filter(
            FlaggedRecommendation.recommendation_id == recommendation_id
        ).first()

        if not rec:
            raise HTTPException(
                status_code=404,
                detail=f"Recommendation {recommendation_id} not found"
            )

        # Update recommendation status
        rec.review_status = "escalated"
        rec.reviewed_at = datetime.now()
        rec.reviewed_by = current_operator.operator_id
        rec.review_notes = f"[{request.flag_reason}] {request.notes or ''}"

        # Log to audit trail
        audit_entry = AuthAuditLog(
            log_id=f"audit_flag_{datetime.now().timestamp()}",
            event_type="recommendation_flagged",
            operator_id=current_operator.operator_id,
            endpoint=f"/api/operator/review/{recommendation_id}/flag",
            timestamp=datetime.now(),
            details=json.dumps({
                "recommendation_id": recommendation_id,
                "user_id": rec.user_id,
                "content_id": rec.content_id,
                "flag_reason": request.flag_reason,
                "notes": request.notes,
                "operator_username": current_operator.username
            })
        )

        session.add(audit_entry)
        session.commit()

        # Epic 6 Story 6.5: Log to audit_log table for compliance reporting
        try:
            from spendsense.services.audit_service import AuditService
            AuditService.log_operator_action(
                operator_id=current_operator.operator_id,
                action="flagged",
                recommendation_id=recommendation_id,
                user_id=rec.user_id,
                justification=f"{request.flag_reason}: {request.notes or ''}",
                session=session
            )
        except Exception as e:
            # Log but don't fail flagging if audit logging fails
            logger.warning(f"audit_log_failed: {e}", extra={"recommendation_id": recommendation_id})

        return ActionResponse(
            recommendation_id=recommendation_id,
            action="flagged",
            status="escalated",
            operator_id=current_operator.operator_id,
            timestamp=rec.reviewed_at.isoformat()
        )

    except Exception as e:
        session.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Flag operation failed: {str(e)}")

    finally:
        session.close()


@router.post("/review/batch-approve", response_model=BatchApproveResponse)
async def batch_approve_recommendations(
    request: BatchApproveRequest = Body(...),
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    """
    Batch approve multiple recommendations (AC #10).

    Approves multiple recommendations in a single operation for efficiency.

    Args:
        request: Batch approve request with list of recommendation IDs
        current_operator: Authenticated operator (reviewer or admin)

    Returns:
        BatchApproveResponse with success/failure counts

    Raises:
        HTTPException 400: No recommendations provided
    """
    session = get_db_session()

    try:
        approved = 0
        failed = 0
        failed_ids = []

        for rec_id in request.recommendation_ids:
            try:
                rec = session.query(FlaggedRecommendation).filter(
                    FlaggedRecommendation.recommendation_id == rec_id
                ).first()

                if not rec:
                    failed += 1
                    failed_ids.append(rec_id)
                    continue

                # Update recommendation status
                rec.review_status = "approved"
                rec.reviewed_at = datetime.now()
                rec.reviewed_by = current_operator.operator_id
                rec.review_notes = "Batch approved"

                approved += 1

            except Exception as e:
                failed += 1
                failed_ids.append(rec_id)
                continue

        # Log batch operation to audit trail
        audit_entry = AuthAuditLog(
            log_id=f"audit_batch_{datetime.now().timestamp()}",
            event_type="batch_approval",
            operator_id=current_operator.operator_id,
            endpoint="/api/operator/review/batch-approve",
            timestamp=datetime.now(),
            details=json.dumps({
                "approved_count": approved,
                "failed_count": failed,
                "failed_ids": failed_ids,
                "operator_username": current_operator.username
            })
        )

        session.add(audit_entry)
        session.commit()

        return BatchApproveResponse(
            approved=approved,
            failed=failed,
            failed_ids=failed_ids,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Batch approval failed: {str(e)}")

    finally:
        session.close()
