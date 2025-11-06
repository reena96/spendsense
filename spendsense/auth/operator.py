"""Operator model and authentication logic."""

from __future__ import annotations

import uuid
import bcrypt
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass

# Bcrypt rounds for password hashing (12 rounds = secure and performant)
BCRYPT_ROUNDS = 12


@dataclass
class Operator:
    """Operator user model."""

    operator_id: str
    username: str
    password_hash: str
    role: str  # 'viewer', 'reviewer', or 'admin'
    created_at: datetime
    last_login_at: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        """Validate role on initialization."""
        valid_roles = {'viewer', 'reviewer', 'admin'}
        if self.role not in valid_roles:
            raise ValueError(f"Invalid role: {self.role}. Must be one of {valid_roles}")


@dataclass
class OperatorSession:
    """Operator session model."""

    session_id: str
    operator_id: str
    token_hash: str
    expires_at: datetime
    created_at: datetime


@dataclass
class AuthAuditLog:
    """Authentication audit log entry."""

    log_id: str
    operator_id: Optional[str]
    event_type: str  # 'login_success', 'login_failure', 'logout', 'unauthorized_access'
    endpoint: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    details: Optional[str] = None  # JSON string with additional context


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # Encode password to bytes
    password_bytes = password.encode('utf-8')

    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    try:
        # Encode inputs to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Verify using bcrypt
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets security requirements.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, f"Password must contain at least one special character ({special_chars})"

    return True, ""


def create_operator(
    username: str,
    password: str,
    role: str,
    operator_id: Optional[str] = None,
) -> Operator:
    """
    Create a new operator with hashed password.

    Args:
        username: Unique username
        password: Plain text password
        role: Operator role ('viewer', 'reviewer', or 'admin')
        operator_id: Optional custom operator ID (generates UUID if not provided)

    Returns:
        Operator instance

    Raises:
        ValueError: If password doesn't meet security requirements
    """
    # Validate password strength
    is_valid, error_msg = validate_password_strength(password)
    if not is_valid:
        raise ValueError(error_msg)

    # Generate operator ID if not provided
    if operator_id is None:
        operator_id = f"op_{uuid.uuid4().hex[:16]}"

    # Hash password
    password_hash = hash_password(password)

    # Create operator
    return Operator(
        operator_id=operator_id,
        username=username,
        password_hash=password_hash,
        role=role,
        created_at=datetime.now(timezone.utc),
        is_active=True,
    )


# Database interaction functions (to be used with database connection)
def get_operator_by_username(db, username: str) -> Optional[Operator]:
    """
    Retrieve operator by username from database.

    Args:
        db: Database connection
        username: Username to look up

    Returns:
        Operator if found, None otherwise
    """
    cursor = db.cursor()
    cursor.execute(
        "SELECT operator_id, username, password_hash, role, created_at, last_login_at, is_active "
        "FROM operators WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()

    if row is None:
        return None

    return Operator(
        operator_id=row[0],
        username=row[1],
        password_hash=row[2],
        role=row[3],
        created_at=datetime.fromisoformat(row[4]),
        last_login_at=datetime.fromisoformat(row[5]) if row[5] else None,
        is_active=bool(row[6]),
    )


def get_operator_by_id(db, operator_id: str) -> Optional[Operator]:
    """
    Retrieve operator by ID from database.

    Args:
        db: Database connection
        operator_id: Operator ID to look up

    Returns:
        Operator if found, None otherwise
    """
    cursor = db.cursor()
    cursor.execute(
        "SELECT operator_id, username, password_hash, role, created_at, last_login_at, is_active "
        "FROM operators WHERE operator_id = ?",
        (operator_id,)
    )
    row = cursor.fetchone()

    if row is None:
        return None

    return Operator(
        operator_id=row[0],
        username=row[1],
        password_hash=row[2],
        role=row[3],
        created_at=datetime.fromisoformat(row[4]),
        last_login_at=datetime.fromisoformat(row[5]) if row[5] else None,
        is_active=bool(row[6]),
    )


def save_operator(db, operator: Operator) -> None:
    """
    Save operator to database (insert or update).

    Args:
        db: Database connection
        operator: Operator to save
    """
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO operators (operator_id, username, password_hash, role, created_at, last_login_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(operator_id) DO UPDATE SET
            username = excluded.username,
            password_hash = excluded.password_hash,
            role = excluded.role,
            last_login_at = excluded.last_login_at,
            is_active = excluded.is_active
        """,
        (
            operator.operator_id,
            operator.username,
            operator.password_hash,
            operator.role,
            operator.created_at.isoformat(),
            operator.last_login_at.isoformat() if operator.last_login_at else None,
            int(operator.is_active),
        )
    )
    db.commit()


def update_last_login(db, operator_id: str) -> None:
    """
    Update operator's last login timestamp.

    Args:
        db: Database connection
        operator_id: Operator ID to update
    """
    cursor = db.cursor()
    cursor.execute(
        "UPDATE operators SET last_login_at = ? WHERE operator_id = ?",
        (datetime.now(timezone.utc).isoformat(), operator_id)
    )
    db.commit()
