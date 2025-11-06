"""Role-based access control (RBAC) for operator endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from fastapi import Header, HTTPException, status, Depends

from .tokens import verify_token, TokenData


class OperatorRole(str, Enum):
    """Operator role enumeration."""

    VIEWER = "viewer"
    REVIEWER = "reviewer"
    ADMIN = "admin"


# Role hierarchy: viewer < reviewer < admin
ROLE_HIERARCHY = {
    OperatorRole.VIEWER: 0,
    OperatorRole.REVIEWER: 1,
    OperatorRole.ADMIN: 2,
}


def check_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user role has permission for required role.

    Args:
        user_role: User's current role
        required_role: Required role for the operation

    Returns:
        True if user has sufficient permissions, False otherwise
    """
    try:
        user_level = ROLE_HIERARCHY[OperatorRole(user_role)]
        required_level = ROLE_HIERARCHY[OperatorRole(required_role)]
        return user_level >= required_level
    except (ValueError, KeyError):
        return False


def get_current_operator(authorization: Optional[str] = Header(None)):
    """
    Extract and verify operator from Authorization header.

    Args:
        authorization: Authorization header value (Bearer token)

    Returns:
        TokenData with operator information

    Raises:
        HTTPException: If token is missing or invalid
    """
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from "Bearer <token>" format
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    token_data = verify_token(token, expected_type="access")

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def require_role(required_role: str):
    """
    FastAPI dependency to require a specific role for an endpoint.

    This function returns a dependency callable that FastAPI can use with Depends().

    Usage:
        @app.post("/api/operator/data")
        async def create_data(
            data: DataModel,
            current_operator: TokenData = Depends(require_role("admin"))
        ):
            # current_operator contains operator info (operator_id, username, role)
            ...

    Args:
        required_role: Minimum required role ('viewer', 'reviewer', or 'admin')

    Returns:
        Dependency function that validates role and returns TokenData
    """
    async def role_checker(authorization: Optional[str] = Header(None)) -> TokenData:
        """
        Dependency that extracts and validates operator token with role check.

        Args:
            authorization: Authorization header value (Bearer token)

        Returns:
            TokenData with operator information

        Raises:
            HTTPException 401: Missing or invalid token
            HTTPException 403: Insufficient permissions
        """
        # Get current operator from token
        token_data = get_current_operator(authorization)

        # Check if operator has sufficient permissions
        if not check_permission(token_data.role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role} or higher",
            )

        return token_data

    return role_checker
