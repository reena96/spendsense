"""Authentication and authorization module for operator access."""

from .operator import (
    Operator,
    OperatorSession,
    AuthAuditLog,
    create_operator,
    verify_password,
    get_operator_by_username,
    get_operator_by_id,
)
from .tokens import (
    create_access_token,
    create_refresh_token,
    verify_token,
    TokenData,
)
from .rbac import (
    require_role,
    OperatorRole,
    check_permission,
)

__all__ = [
    "Operator",
    "OperatorSession",
    "AuthAuditLog",
    "create_operator",
    "verify_password",
    "get_operator_by_username",
    "get_operator_by_id",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "TokenData",
    "require_role",
    "OperatorRole",
    "check_permission",
]
