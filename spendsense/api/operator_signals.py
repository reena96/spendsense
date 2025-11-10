"""
Operator Signal Dashboard API (Epic 6 - Story 6.2)

Provides operator endpoints for viewing user behavioral signals,
including subscription, savings, credit, and income metrics.
"""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, HTTPException, Query, Depends, Response
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData
from spendsense.features.behavioral_summary import BehavioralSummaryGenerator
from spendsense.ingestion.database_writer import User


# Router for operator signal endpoints
router = APIRouter(prefix="/api/operator", tags=["operator-signals"])

# Import database connection utility
from spendsense.db.connection import get_db_session, get_engine


# ===== Response Models =====

class UserSearchResult(BaseModel):
    """User search result item."""
    user_id: str
    name: str
    persona: str
    consent_status: str


class UserSearchResponse(BaseModel):
    """Response for user search endpoint."""
    total: int
    users: List[UserSearchResult]


class SignalMetrics(BaseModel):
    """Signal metrics for a specific category and time window."""
    time_window: str
    computed_at: str
    subscription: Dict[str, Any]
    savings: Dict[str, Any]
    credit: Dict[str, Any]
    income: Dict[str, Any]
    metadata: Dict[str, Any]


class SignalsResponse(BaseModel):
    """Response for user signals endpoint."""
    user_id: str
    data_30d: Optional[SignalMetrics]
    data_180d: Optional[SignalMetrics]


# ===== Utility Functions =====

def get_db_session_local():
    """Get database session using centralized connection utility."""
    try:
        return get_db_session()
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )


def convert_behavioral_summary_to_metrics(summary_dict: dict, time_window: str) -> Dict[str, Any]:
    """
    Convert BehavioralSummary dict to structured metrics for a specific time window.

    Args:
        summary_dict: Dict from BehavioralSummary.to_dict()
        time_window: '30d' or '180d'

    Returns:
        Structured metrics dict with subscription, savings, credit, income categories
    """
    # Extract the appropriate time window data
    subscriptions = summary_dict['subscriptions'][time_window]
    savings = summary_dict['savings'][time_window]
    credit = summary_dict['credit'][time_window]
    income = summary_dict['income'][time_window]

    # Build structured response
    return {
        "subscription": {
            "recurring_merchants": subscriptions.get('subscription_count', 0),
            "monthly_spend": subscriptions.get('monthly_recurring_spend', 0.0),
            "subscription_share_pct": subscriptions.get('subscription_share', 0.0) * 100,
            "total_spend": subscriptions.get('total_spend', 0.0),
            "detected_subscriptions": subscriptions.get('detected_subscriptions', [])
        },
        "savings": {
            "net_inflow": savings.get('net_inflow', 0.0),
            "growth_rate_pct": savings.get('savings_growth_rate', 0.0) * 100,
            "emergency_fund_months": savings.get('emergency_fund_months', 0.0),
            "total_balance": savings.get('total_savings_balance', 0.0),
            "avg_monthly_expenses": savings.get('avg_monthly_expenses', 0.0),
            "has_savings_accounts": savings.get('has_savings_accounts', False)
        },
        "credit": {
            "max_utilization_pct": credit.get('aggregate_utilization', 0.0) * 100,
            "has_interest_charges": credit.get('has_interest_charges', False),
            "minimum_payment_only": credit.get('minimum_payment_only_count', 0) > 0,
            "overdue_status": credit.get('overdue_count', 0) > 0,
            "num_cards": credit.get('num_credit_cards', 0),
            "high_utilization_count": credit.get('high_utilization_count', 0),
            "utilization_by_card": credit.get('per_card_details', [])
        },
        "income": {
            "payroll_count": income.get('num_income_transactions', 0),
            "median_pay_gap_days": income.get('median_pay_gap_days', 0.0),
            "cash_flow_buffer_months": income.get('cash_flow_buffer_months', 0.0),
            "total_income": income.get('total_income', 0.0),
            "payment_frequency": income.get('payment_frequency', 'unknown'),
            "has_regular_income": income.get('has_regular_income', False)
        }
    }


# ===== API Endpoints =====

@router.get("/users/search", response_model=UserSearchResponse)
async def search_users(
    q: str = Query(..., min_length=1, description="Search query (user ID or name)"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results to return"),
    current_operator: TokenData = Depends(require_role("viewer"))
):
    """
    Search users by ID or name (AC #1).

    Requires viewer role or higher. Searches both user_id and name fields.

    Args:
        q: Search query string (matches user_id or name)
        limit: Maximum number of results (default 20, max 100)
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        UserSearchResponse with matching users

    Raises:
        HTTPException 401: Unauthorized (missing/invalid token)
        HTTPException 403: Forbidden (insufficient permissions)
        HTTPException 503: Database unavailable
    """
    session = get_db_session()

    try:
        # Search by user_id or name (case-insensitive partial match)
        query = session.query(User).filter(
            or_(
                User.user_id.ilike(f"%{q}%"),
                User.name.ilike(f"%{q}%")
            )
        ).limit(limit)

        users = query.all()

        results = [
            UserSearchResult(
                user_id=user.user_id,
                name=user.name,
                persona=user.persona,
                consent_status=user.consent_status
            )
            for user in users
        ]

        return UserSearchResponse(
            total=len(results),
            users=results
        )

    finally:
        session.close()


@router.get("/signals/{user_id}", response_model=SignalsResponse)
async def get_user_signals(
    user_id: str,
    time_window: Optional[str] = Query(
        default="both",
        regex="^(30d|180d|both)$",
        description="Time window: '30d', '180d', or 'both'"
    ),
    current_operator: TokenData = Depends(require_role("viewer"))
):
    """
    Get behavioral signals for a user (AC #2-9).

    Returns comprehensive signal data including subscription, savings, credit,
    and income metrics for requested time window(s).

    Args:
        user_id: User identifier
        time_window: Time window filter ('30d', '180d', or 'both')
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        SignalsResponse with signal data for requested window(s)

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

        # Generate behavioral summary
        generator = BehavioralSummaryGenerator(str(DB_PATH))
        summary = generator.generate_summary(
            user_id=user_id,
            reference_date=date.today()
        )

        # Convert to dict
        summary_dict = summary.to_dict()

        # Build response based on requested time window
        response_data = {
            "user_id": user_id,
            "data_30d": None,
            "data_180d": None
        }

        if time_window in ("30d", "both"):
            metrics_30d = convert_behavioral_summary_to_metrics(summary_dict, "30d")
            response_data["data_30d"] = SignalMetrics(
                time_window="30d",
                computed_at=summary_dict['generated_at'],
                subscription=metrics_30d["subscription"],
                savings=metrics_30d["savings"],
                credit=metrics_30d["credit"],
                income=metrics_30d["income"],
                metadata=summary_dict['metadata']
            )

        if time_window in ("180d", "both"):
            metrics_180d = convert_behavioral_summary_to_metrics(summary_dict, "180d")
            response_data["data_180d"] = SignalMetrics(
                time_window="180d",
                computed_at=summary_dict['generated_at'],
                subscription=metrics_180d["subscription"],
                savings=metrics_180d["savings"],
                credit=metrics_180d["credit"],
                income=metrics_180d["income"],
                metadata=summary_dict['metadata']
            )

        return SignalsResponse(**response_data)

    finally:
        session.close()


@router.get("/signals/{user_id}/export")
async def export_user_signals(
    user_id: str,
    format: str = Query(default="csv", regex="^(csv|json)$", description="Export format (csv or json)"),
    current_operator: TokenData = Depends(require_role("viewer"))
):
    """
    Export user signals as CSV or JSON (AC #10).

    Generates downloadable file with signal data for compliance and analysis.
    CSV format includes: user_id, time_window, metric_name, metric_value, computed_at

    Args:
        user_id: User identifier
        format: Export format ('csv' or 'json')
        current_operator: Authenticated operator (injected by FastAPI)

    Returns:
        CSV or JSON file download

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

        # Generate behavioral summary
        generator = BehavioralSummaryGenerator(str(DB_PATH))
        summary = generator.generate_summary(
            user_id=user_id,
            reference_date=date.today()
        )

        # Convert to dict
        summary_dict = summary.to_dict()
        computed_at = summary_dict['generated_at']

        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(['user_id', 'time_window', 'category', 'metric_name', 'metric_value', 'computed_at'])

            # Flatten all metrics into CSV rows
            for time_window in ['30d', '180d']:
                metrics = convert_behavioral_summary_to_metrics(summary_dict, time_window)

                # Subscription metrics
                for key, value in metrics['subscription'].items():
                    if key != 'detected_subscriptions':  # Skip complex nested data
                        writer.writerow([user_id, time_window, 'subscription', key, value, computed_at])

                # Savings metrics
                for key, value in metrics['savings'].items():
                    writer.writerow([user_id, time_window, 'savings', key, value, computed_at])

                # Credit metrics
                for key, value in metrics['credit'].items():
                    if key != 'utilization_by_card':  # Skip complex nested data
                        writer.writerow([user_id, time_window, 'credit', key, value, computed_at])

                # Income metrics
                for key, value in metrics['income'].items():
                    writer.writerow([user_id, time_window, 'income', key, value, computed_at])

            # Return CSV response
            csv_content = output.getvalue()
            return Response(
                content=csv_content,
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=signals_{user_id}.csv"
                }
            )

        else:  # JSON format
            # Return complete signal data as JSON
            return Response(
                content=summary_dict.__str__(),  # Convert dict to JSON string
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename=signals_{user_id}.json"
                }
            )

    finally:
        session.close()
