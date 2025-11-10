"""
Operator authentication endpoints (Epic 6 - Story 6.1).

Provides login, logout, and token refresh functionality for operator access.
"""

import uuid
import sqlite3
import structlog
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from collections import defaultdict

from fastapi import APIRouter, HTTPException, status, Request
from pydantic import BaseModel, Field

from spendsense.auth.operator import (
    get_operator_by_username,
    update_last_login,
    verify_password,
    create_operator,
    save_operator,
)
from spendsense.auth.tokens import (
    create_access_token,
    create_refresh_token,
    verify_token,
)

# Configure structured logging
logger = structlog.get_logger(__name__)

# Router for operator auth endpoints
router = APIRouter(prefix="/api/operator", tags=["operator-auth"])

# Rate limiting storage (in-memory for demo; use Redis in production)
login_attempts: Dict[str, list] = defaultdict(list)
RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_WINDOW_MINUTES = 15


# ===== Request/Response Models =====

class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(default="admin", min_length=1, max_length=100, description="Operator username")
    password: str = Field(default="AdminPass123!", min_length=12, description="Operator password (min 12 chars)")


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    operator_id: str
    role: str


class RefreshRequest(BaseModel):
    """Token refresh request model."""

    refresh_token: str = Field(default="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", description="Refresh token from login response")


class RefreshResponse(BaseModel):
    """Token refresh response model."""

    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Logout response model."""

    message: str


class CreateOperatorRequest(BaseModel):
    """Create operator request model (admin only)."""

    username: str = Field(default="test_viewer", min_length=3, max_length=100, description="Username (3-100 chars)")
    password: str = Field(default="ViewerPass123!", min_length=12, description="Password (min 12 chars, upper+lower+digit+special)")
    role: str = Field(default="viewer", pattern="^(viewer|reviewer|admin)$", description="Role: viewer, reviewer, or admin")


class CreateOperatorResponse(BaseModel):
    """Create operator response model."""

    operator_id: str
    username: str
    role: str
    message: str


# ===== Helper Functions =====

def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    # Get path relative to project root
    db_path = Path(__file__).parent.parent.parent / "data" / "processed" / "spendsense.db"
    if not db_path.exists():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database not found at {db_path}"
        )
    return sqlite3.connect(str(db_path))


def get_client_identifier(request: Request, username: str) -> str:
    """
    Get unique client identifier for rate limiting.

    Combines IP address and username for tracking login attempts.
    """
    client_ip = request.client.host if request.client else "unknown"
    return f"{client_ip}:{username}"


def check_rate_limit(client_id: str) -> bool:
    """
    Check if client has exceeded rate limit.

    Returns:
        True if client is within rate limit, False if exceeded
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)

    # Remove old attempts
    login_attempts[client_id] = [
        attempt for attempt in login_attempts[client_id]
        if attempt > cutoff
    ]

    # Check if limit exceeded
    if len(login_attempts[client_id]) >= RATE_LIMIT_ATTEMPTS:
        return False

    return True


def record_login_attempt(client_id: str) -> None:
    """Record a failed login attempt for rate limiting."""
    login_attempts[client_id].append(datetime.now(timezone.utc))


def log_auth_event(
    db: sqlite3.Connection,
    event_type: str,
    operator_id: Optional[str] = None,
    endpoint: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log authentication event to audit log.

    Args:
        db: Database connection
        event_type: Type of event (login_success, login_failure, logout, unauthorized_access)
        operator_id: Operator ID (if authenticated)
        endpoint: API endpoint
        ip_address: Client IP address
        user_agent: Client user agent
        details: Additional event details (stored as JSON)
    """
    import json

    log_id = f"log_{uuid.uuid4().hex[:16]}"
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO auth_audit_log (log_id, operator_id, event_type, endpoint, ip_address, user_agent, timestamp, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            log_id,
            operator_id,
            event_type,
            endpoint,
            ip_address,
            user_agent,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(details) if details else None,
        )
    )
    db.commit()

    # Also log to structlog
    logger.info(
        "auth_event",
        event_type=event_type,
        operator_id=operator_id,
        endpoint=endpoint,
        ip_address=ip_address,
    )


# ===== Endpoints =====

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: Request, login_data: LoginRequest):
    """
    Operator login endpoint (AC: #1, #3, #7, #8).

    Authenticates operator with username/password and returns JWT tokens.
    Enforces rate limiting (max 5 attempts per 15 minutes).

    Args:
        request: FastAPI request for client info
        login_data: Login credentials

    Returns:
        LoginResponse with access and refresh tokens

    Raises:
        HTTPException 401: Invalid credentials or inactive account
        HTTPException 429: Too many login attempts
        HTTPException 500: Database error
    """
    db = None
    try:
        db = get_db_connection()

        # Extract client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        client_id = get_client_identifier(request, login_data.username)

        # Check rate limiting (AC: #8)
        if not check_rate_limit(client_id):
            # Log failed attempt
            log_auth_event(
                db,
                event_type="login_failure",
                endpoint="/api/operator/login",
                ip_address=client_ip,
                user_agent=user_agent,
                details={"username": login_data.username, "reason": "rate_limit_exceeded"}
            )

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later.",
                headers={"Retry-After": str(RATE_LIMIT_WINDOW_MINUTES * 60)}
            )

        # Retrieve operator
        operator = get_operator_by_username(db, login_data.username)

        if operator is None:
            # Record failed attempt for rate limiting
            record_login_attempt(client_id)

            # Log failed attempt
            log_auth_event(
                db,
                event_type="login_failure",
                endpoint="/api/operator/login",
                ip_address=client_ip,
                user_agent=user_agent,
                details={"username": login_data.username, "reason": "user_not_found"}
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Verify password
        if not verify_password(login_data.password, operator.password_hash):
            # Record failed attempt for rate limiting
            record_login_attempt(client_id)

            # Log failed attempt
            log_auth_event(
                db,
                event_type="login_failure",
                operator_id=operator.operator_id,
                endpoint="/api/operator/login",
                ip_address=client_ip,
                user_agent=user_agent,
                details={"username": login_data.username, "reason": "invalid_password"}
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Check if operator is active
        if not operator.is_active:
            # Log failed attempt
            log_auth_event(
                db,
                event_type="login_failure",
                operator_id=operator.operator_id,
                endpoint="/api/operator/login",
                ip_address=client_ip,
                user_agent=user_agent,
                details={"username": login_data.username, "reason": "account_inactive"}
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive. Please contact administrator."
            )

        # Generate tokens (AC: #3)
        access_token = create_access_token(operator.operator_id, operator.username, operator.role)
        refresh_token = create_refresh_token(operator.operator_id, operator.username, operator.role)

        # Update last login timestamp
        update_last_login(db, operator.operator_id)

        # Clear rate limit for successful login
        if client_id in login_attempts:
            del login_attempts[client_id]

        # Log successful login (AC: #6)
        log_auth_event(
            db,
            event_type="login_success",
            operator_id=operator.operator_id,
            endpoint="/api/operator/login",
            ip_address=client_ip,
            user_agent=user_agent,
            details={"username": login_data.username}
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            operator_id=operator.operator_id,
            role=operator.role
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("login_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during login"
        )
    finally:
        if db:
            db.close()


@router.post("/refresh", response_model=RefreshResponse, status_code=status.HTTP_200_OK)
async def refresh_token_endpoint(refresh_data: RefreshRequest):
    """
    Refresh access token using refresh token (AC: #3).

    Args:
        refresh_data: Refresh token

    Returns:
        RefreshResponse with new access token

    Raises:
        HTTPException 401: Invalid or expired refresh token
    """
    # Verify refresh token
    token_data = verify_token(refresh_data.refresh_token, expected_type="refresh")

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Generate new access token
    access_token = create_access_token(
        token_data.operator_id,
        token_data.username,
        token_data.role
    )

    return RefreshResponse(access_token=access_token)


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(request: Request):
    """
    Operator logout endpoint (AC: #1).

    Logs the logout event. In a production system with session storage,
    this would invalidate the session token.

    Args:
        request: FastAPI request for client info

    Returns:
        LogoutResponse with success message
    """
    # In production, would invalidate session in database/cache
    # For now, just log the event

    db = None
    try:
        db = get_db_connection()

        # Extract client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Try to extract operator ID from Authorization header
        auth_header = request.headers.get("authorization")
        operator_id = None
        if auth_header:
            try:
                token = auth_header.split()[1] if len(auth_header.split()) == 2 else None
                if token:
                    token_data = verify_token(token, expected_type="access")
                    if token_data:
                        operator_id = token_data.operator_id
            except Exception:
                pass

        # Log logout event (AC: #6)
        log_auth_event(
            db,
            event_type="logout",
            operator_id=operator_id,
            endpoint="/api/operator/logout",
            ip_address=client_ip,
            user_agent=user_agent
        )

        return LogoutResponse(message="Logged out successfully")

    except Exception as e:
        logger.error("logout_error", error=str(e), exc_info=True)
        # Don't fail logout on error - return success anyway
        return LogoutResponse(message="Logged out successfully")
    finally:
        if db:
            db.close()


@router.post("/create", response_model=CreateOperatorResponse, status_code=status.HTTP_201_CREATED)
async def create_operator_endpoint(request: Request, operator_data: CreateOperatorRequest):
    """
    Create new operator account (admin only - would need RBAC in production).

    This endpoint would normally require @require_role("admin") decorator,
    but for initial setup, it's open to create the first admin.

    Args:
        request: FastAPI request
        operator_data: New operator details

    Returns:
        CreateOperatorResponse with operator details

    Raises:
        HTTPException 400: Username already exists or invalid data
        HTTPException 500: Database error
    """
    db = None
    try:
        db = get_db_connection()

        # Check if username already exists
        existing = get_operator_by_username(db, operator_data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username '{operator_data.username}' already exists"
            )

        # Create operator
        operator = create_operator(
            username=operator_data.username,
            password=operator_data.password,
            role=operator_data.role
        )

        # Save to database
        save_operator(db, operator)

        # Log event
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        log_auth_event(
            db,
            event_type="operator_created",
            operator_id=operator.operator_id,
            endpoint="/api/operator/create",
            ip_address=client_ip,
            user_agent=user_agent,
            details={"username": operator.username, "role": operator.role}
        )

        return CreateOperatorResponse(
            operator_id=operator.operator_id,
            username=operator.username,
            role=operator.role,
            message=f"Operator '{operator.username}' created successfully"
        )

    except ValueError as e:
        # Password validation or other value errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("create_operator_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred creating operator"
        )
    finally:
        if db:
            db.close()
