"""
Operator Persona Assignment Review API (Epic 6 - Story 6.3)

Provides operator endpoints for reviewing persona assignments with complete
decision traces, including qualifying personas, match evidence, and prioritization logic.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData
from spendsense.ingestion.database_writer import User, PersonaAssignmentRecord, Operator, AuthAuditLog


# Router for operator persona endpoints
router = APIRouter(prefix="/api/operator", tags=["operator-personas"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "spendsense.db"


# ===== Persona Definitions Registry =====
# These definitions come from Epic 3 persona registry
# In production, these would be loaded from a database table

PERSONA_DEFINITIONS = {
    "high_utilization": {
        "persona_id": "high_utilization",
        "display_name": "High Credit Utilization",
        "description": "Users with credit card utilization above 70%, indicating potential debt stress",
        "educational_focus": "Debt reduction strategies, credit score management, balance transfer options",
        "priority_rank": 1,
        "criteria": {
            "credit_max_utilization_pct": {
                "threshold": 70.0,
                "operator": ">",
                "description": "Credit utilization above 70%"
            }
        },
        "icon": "credit-card-alert",
        "color": "red"
    },
    "low_savings": {
        "persona_id": "low_savings",
        "display_name": "Low Savings / Emergency Fund",
        "description": "Users with insufficient emergency fund coverage (<3 months expenses)",
        "educational_focus": "Emergency fund building, automated savings, expense reduction",
        "priority_rank": 2,
        "criteria": {
            "savings_emergency_fund_months": {
                "threshold": 3.0,
                "operator": "<",
                "description": "Emergency fund below 3 months"
            }
        },
        "icon": "piggy-bank",
        "color": "orange"
    },
    "subscription_heavy": {
        "persona_id": "subscription_heavy",
        "display_name": "Subscription-Heavy Spender",
        "description": "Users spending >25% of income on recurring subscriptions",
        "educational_focus": "Subscription audit, cost optimization, alternatives",
        "priority_rank": 3,
        "criteria": {
            "subscription_share_pct": {
                "threshold": 25.0,
                "operator": ">",
                "description": "Subscription spend above 25%"
            }
        },
        "icon": "repeat",
        "color": "blue"
    },
    "variable_income": {
        "persona_id": "variable_income",
        "display_name": "Irregular Income",
        "description": "Users with irregular or variable income patterns",
        "educational_focus": "Cash flow management, income smoothing, budgeting flexibility",
        "priority_rank": 4,
        "criteria": {
            "income_has_regular_income": {
                "threshold": False,
                "operator": "==",
                "description": "Irregular income pattern detected"
            }
        },
        "icon": "trending-up",
        "color": "purple"
    },
    "cash_flow_optimizer": {
        "persona_id": "cash_flow_optimizer",
        "display_name": "Cash Flow Optimizer",
        "description": "Users with low cash flow buffer (<1 month)",
        "educational_focus": "Cash flow optimization, timing strategies, buffer building",
        "priority_rank": 5,
        "criteria": {
            "income_cash_flow_buffer_months": {
                "threshold": 1.0,
                "operator": "<",
                "description": "Cash flow buffer below 1 month"
            }
        },
        "icon": "dollar-sign",
        "color": "green"
    },
    "young_professional": {
        "persona_id": "young_professional",
        "display_name": "Young Professional",
        "description": "Users with stable income but developing financial habits",
        "educational_focus": "Financial foundations, investment basics, goal setting",
        "priority_rank": 6,
        "criteria": {
            "income_has_regular_income": {
                "threshold": True,
                "operator": "==",
                "description": "Regular income pattern"
            },
            "savings_emergency_fund_months": {
                "threshold": 3.0,
                "operator": ">=",
                "description": "Adequate emergency fund"
            }
        },
        "icon": "user",
        "color": "teal"
    }
}


# ===== Response Models =====

class PersonaDefinition(BaseModel):
    """Persona definition from registry."""
    persona_id: str
    display_name: str
    description: str
    educational_focus: str
    priority_rank: int
    criteria: Dict[str, Any]
    icon: str
    color: str


class QualifyingPersona(BaseModel):
    """A persona that matched criteria for this user."""
    persona_id: str
    persona_name: str
    priority_rank: int
    match_evidence: Dict[str, Any]


class PersonaAssignment(BaseModel):
    """Persona assignment for a specific time window."""
    assignment_id: str
    time_window: str
    assigned_persona_id: str
    assigned_persona_name: str
    assigned_at: str
    priority_rank: Optional[int]
    qualifying_personas: List[QualifyingPersona]
    prioritization_reason: str
    confidence_level: Optional[float] = None
    is_override: bool = False


class PersonaChangeHistoryItem(BaseModel):
    """A persona change event."""
    changed_at: str
    time_window: str
    previous_persona: str
    previous_persona_name: str
    new_persona: str
    new_persona_name: str
    reason: str
    is_override: bool


class PersonaAssignmentsResponse(BaseModel):
    """Complete persona assignments for a user."""
    user_id: str
    user_name: str
    assignments: Dict[str, PersonaAssignment]  # "30d" and "180d"
    change_history: List[PersonaChangeHistoryItem]


class PersonaOverrideRequest(BaseModel):
    """Request to manually override a persona assignment."""
    new_persona_id: str = Field(..., description="New persona to assign")
    justification: str = Field(..., min_length=20, description="Reason for override (min 20 chars)")
    time_window: str = Field(default="30d", pattern="^(30d|180d)$", description="Time window to override")


class PersonaOverrideResponse(BaseModel):
    """Response after successful override."""
    assignment_id: str
    user_id: str
    old_persona: str
    new_persona: str
    operator_id: str
    justification: str
    assigned_at: str


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


def get_persona_name(persona_id: str) -> str:
    """Get display name for a persona ID."""
    return PERSONA_DEFINITIONS.get(persona_id, {}).get("display_name", persona_id)


# ===== API Endpoints =====

@router.get("/personas/definitions", response_model=List[PersonaDefinition])
async def get_persona_definitions(
    current_operator: TokenData = Depends(require_role("viewer"))
):
    """
    Get all persona definitions from registry (AC #5).

    Returns complete persona definitions including criteria, educational focus,
    and priority rankings.

    Args:
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        List of PersonaDefinition objects

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
    """
    definitions = [PersonaDefinition(**data) for data in PERSONA_DEFINITIONS.values()]
    # Sort by priority rank
    definitions.sort(key=lambda x: x.priority_rank)
    return definitions


@router.get("/personas/{user_id}", response_model=PersonaAssignmentsResponse)
async def get_persona_assignments(
    user_id: str,
    current_operator: TokenData = Depends(require_role("viewer"))
):
    """
    Get persona assignments for a user (AC #1, #2, #3, #4, #7).

    Returns assignments for both 30-day and 180-day windows with complete
    decision traces including qualifying personas, match evidence, and
    prioritization reasoning.

    Args:
        user_id: User identifier
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        PersonaAssignmentsResponse with assignments and change history

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 404: User not found or no assignments
        HTTPException 503: Database unavailable
    """
    session = get_db_session()

    try:
        # Verify user exists
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Get assignments for both time windows
        assignments_30d = session.query(PersonaAssignmentRecord).filter(
            PersonaAssignmentRecord.user_id == user_id,
            PersonaAssignmentRecord.time_window == "30d"
        ).order_by(desc(PersonaAssignmentRecord.assigned_at)).first()

        assignments_180d = session.query(PersonaAssignmentRecord).filter(
            PersonaAssignmentRecord.user_id == user_id,
            PersonaAssignmentRecord.time_window == "180d"
        ).order_by(desc(PersonaAssignmentRecord.assigned_at)).first()

        if not assignments_30d and not assignments_180d:
            raise HTTPException(
                status_code=404,
                detail=f"No persona assignments found for user {user_id}"
            )

        # Build response
        response_assignments = {}

        for window, assignment in [("30d", assignments_30d), ("180d", assignments_180d)]:
            if assignment:
                # Parse qualifying personas from JSON
                qualifying_list = []
                for persona_id in assignment.qualifying_personas:
                    evidence = assignment.match_evidence.get(persona_id, {})
                    qualifying_list.append(QualifyingPersona(
                        persona_id=persona_id,
                        persona_name=get_persona_name(persona_id),
                        priority_rank=PERSONA_DEFINITIONS.get(persona_id, {}).get("priority_rank", 99),
                        match_evidence=evidence
                    ))

                # Sort by priority
                qualifying_list.sort(key=lambda x: x.priority_rank)

                response_assignments[window] = PersonaAssignment(
                    assignment_id=assignment.assignment_id,
                    time_window=assignment.time_window,
                    assigned_persona_id=assignment.assigned_persona_id,
                    assigned_persona_name=get_persona_name(assignment.assigned_persona_id),
                    assigned_at=assignment.assigned_at.isoformat(),
                    priority_rank=assignment.priority,
                    qualifying_personas=qualifying_list,
                    prioritization_reason=assignment.prioritization_reason,
                    confidence_level=None,  # Not implemented yet
                    is_override=False  # Would check audit log in production
                )

        # Get change history (simplified - queries last 10 assignments per window)
        change_history = []
        for window in ["30d", "180d"]:
            history_records = session.query(PersonaAssignmentRecord).filter(
                PersonaAssignmentRecord.user_id == user_id,
                PersonaAssignmentRecord.time_window == window
            ).order_by(desc(PersonaAssignmentRecord.assigned_at)).limit(10).all()

            # Compare consecutive assignments to detect changes
            for i in range(len(history_records) - 1):
                current = history_records[i]
                previous = history_records[i + 1]

                if current.assigned_persona_id != previous.assigned_persona_id:
                    change_history.append(PersonaChangeHistoryItem(
                        changed_at=current.assigned_at.isoformat(),
                        time_window=window,
                        previous_persona=previous.assigned_persona_id,
                        previous_persona_name=get_persona_name(previous.assigned_persona_id),
                        new_persona=current.assigned_persona_id,
                        new_persona_name=get_persona_name(current.assigned_persona_id),
                        reason=current.prioritization_reason,
                        is_override=False  # Would check audit log
                    ))

        # Sort history by date
        change_history.sort(key=lambda x: x.changed_at, reverse=True)

        return PersonaAssignmentsResponse(
            user_id=user_id,
            user_name=user.name,
            assignments=response_assignments,
            change_history=change_history[:5]  # Return last 5 changes
        )

    finally:
        session.close()


@router.post("/personas/{user_id}/override", response_model=PersonaOverrideResponse)
async def override_persona_assignment(
    user_id: str,
    override_request: PersonaOverrideRequest = Body(...),
    current_operator: TokenData = Depends(require_role("admin"))
):
    """
    Manually override persona assignment (AC #9, #10).

    Allows admin operators to manually assign a different persona to a user
    with required justification. All overrides are logged in audit trail.

    Args:
        user_id: User identifier
        override_request: Override details (new persona, justification, time window)
        current_operator: Authenticated admin operator (injected by FastAPI)

    Returns:
        PersonaOverrideResponse with override details

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions - admin required)
        HTTPException 404: User not found
        HTTPException 400: Invalid persona ID or missing justification
        HTTPException 503: Database unavailable
    """
    session = get_db_session()

    try:
        # Verify user exists
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        # Verify new persona exists
        if override_request.new_persona_id not in PERSONA_DEFINITIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid persona ID: {override_request.new_persona_id}"
            )

        # Get current assignment
        current_assignment = session.query(PersonaAssignmentRecord).filter(
            PersonaAssignmentRecord.user_id == user_id,
            PersonaAssignmentRecord.time_window == override_request.time_window
        ).order_by(desc(PersonaAssignmentRecord.assigned_at)).first()

        old_persona = current_assignment.assigned_persona_id if current_assignment else "unclassified"

        # Create new assignment record with override
        new_assignment_id = f"assign_override_{user_id}_{override_request.time_window}_{datetime.now().timestamp()}"

        new_assignment = PersonaAssignmentRecord(
            assignment_id=new_assignment_id,
            user_id=user_id,
            time_window=override_request.time_window,
            assigned_persona_id=override_request.new_persona_id,
            assigned_at=datetime.now(),
            priority=PERSONA_DEFINITIONS[override_request.new_persona_id]["priority_rank"],
            qualifying_personas=[override_request.new_persona_id],  # Only the overridden persona
            match_evidence={override_request.new_persona_id: {"override": True}},
            prioritization_reason=f"Manual override by {current_operator.username}: {override_request.justification}"
        )

        session.add(new_assignment)

        # Log to audit trail
        audit_entry = AuthAuditLog(
            log_id=f"audit_override_{datetime.now().timestamp()}",
            event_type="persona_override",
            operator_id=current_operator.operator_id,
            endpoint=f"/api/operator/personas/{user_id}/override",
            timestamp=datetime.now(),
            details=json.dumps({
                "user_id": user_id,
                "old_persona": old_persona,
                "new_persona": override_request.new_persona_id,
                "time_window": override_request.time_window,
                "justification": override_request.justification,
                "operator_username": current_operator.username
            })
        )

        session.add(audit_entry)
        session.commit()

        # Epic 6 Story 6.5: Log to audit_log table for compliance reporting
        try:
            from spendsense.services.audit_service import AuditService
            AuditService.log_persona_overridden(
                operator_id=current_operator.operator_id,
                user_id=user_id,
                old_persona=old_persona,
                new_persona=override_request.new_persona_id,
                justification=override_request.justification,
                session=session
            )
        except Exception as e:
            # Log but don't fail persona override if audit logging fails
            logger.warning(f"audit_log_failed: {e}", extra={"user_id": user_id})

        return PersonaOverrideResponse(
            assignment_id=new_assignment_id,
            user_id=user_id,
            old_persona=old_persona,
            new_persona=override_request.new_persona_id,
            operator_id=current_operator.operator_id,
            justification=override_request.justification,
            assigned_at=new_assignment.assigned_at.isoformat()
        )

    except Exception as e:
        session.rollback()
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=f"Override failed: {str(e)}")

    finally:
        session.close()


@router.get("/personas/{user_id}/history", response_model=List[PersonaChangeHistoryItem])
async def get_persona_change_history(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50, description="Maximum history items to return"),
    current_operator: TokenData = Depends(require_role("viewer"))
):
    """
    Get persona change history for a user (AC #8).

    Returns timeline of persona changes with reasons for each change.

    Args:
        user_id: User identifier
        limit: Maximum number of history items (default 10, max 50)
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        List of PersonaChangeHistoryItem objects

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 404: User not found
        HTTPException 503: Database unavailable
    """
    session = get_db_session()

    try:
        # Verify user exists
        user = session.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} not found"
            )

        change_history = []

        # Get assignment history for both windows
        for window in ["30d", "180d"]:
            history_records = session.query(PersonaAssignmentRecord).filter(
                PersonaAssignmentRecord.user_id == user_id,
                PersonaAssignmentRecord.time_window == window
            ).order_by(desc(PersonaAssignmentRecord.assigned_at)).limit(limit).all()

            # Detect changes between consecutive assignments
            for i in range(len(history_records) - 1):
                current = history_records[i]
                previous = history_records[i + 1]

                if current.assigned_persona_id != previous.assigned_persona_id:
                    change_history.append(PersonaChangeHistoryItem(
                        changed_at=current.assigned_at.isoformat(),
                        time_window=window,
                        previous_persona=previous.assigned_persona_id,
                        previous_persona_name=get_persona_name(previous.assigned_persona_id),
                        new_persona=current.assigned_persona_id,
                        new_persona_name=get_persona_name(current.assigned_persona_id),
                        reason=current.prioritization_reason,
                        is_override="override" in current.prioritization_reason.lower()
                    ))

        # Sort by date descending
        change_history.sort(key=lambda x: x.changed_at, reverse=True)

        return change_history[:limit]

    finally:
        session.close()
