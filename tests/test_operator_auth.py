"""
Unit and integration tests for operator authentication (Epic 6 - Story 6.1).

Tests cover:
- Operator creation and password hashing (AC #1, #7)
- Login success and failure (AC #1, #8)
- Token generation and validation (AC #3)
- RBAC enforcement (AC #2, #4)
- Audit logging (AC #5, #6)
- Epic 5 consent endpoint protection (AC #4)
"""

import pytest
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path

from spendsense.auth.operator import (
    create_operator,
    verify_password,
    validate_password_strength,
    hash_password,
)
from spendsense.auth.tokens import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from spendsense.auth.rbac import check_permission, OperatorRole


# ===== Unit Tests - Password Security (AC #7) =====

def test_password_strength_validation_min_length():
    """Test password must be at least 12 characters."""
    is_valid, error = validate_password_strength("Short1!")
    assert not is_valid
    assert "at least 12 characters" in error


def test_password_strength_validation_complexity():
    """Test password must meet complexity requirements."""
    # Missing uppercase
    is_valid, error = validate_password_strength("lowercase123!")
    assert not is_valid
    assert "uppercase" in error

    # Missing lowercase
    is_valid, error = validate_password_strength("UPPERCASE123!")
    assert not is_valid
    assert "lowercase" in error

    # Missing digit
    is_valid, error = validate_password_strength("NoDigitsHere!")
    assert not is_valid
    assert "digit" in error

    # Missing special char
    is_valid, error = validate_password_strength("NoSpecial123")
    assert not is_valid
    assert "special character" in error


def test_password_strength_validation_valid():
    """Test valid password passes all checks."""
    is_valid, error = validate_password_strength("ValidPass123!")
    assert is_valid
    assert error == ""


def test_password_hashing():
    """Test password is hashed, not stored in plaintext."""
    password = "SecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 50  # bcrypt hashes are long
    assert hashed.startswith("$2b$")  # bcrypt format


def test_password_verification():
    """Test password verification works correctly."""
    password = "TestPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword123!", hashed)


# ===== Unit Tests - Operator Creation (AC #1, #2) =====

def test_create_operator_success():
    """Test creating an operator with valid data."""
    operator = create_operator(
        username="test_operator",
        password="TestPassword123!",
        role="admin"
    )

    assert operator.operator_id.startswith("op_")
    assert operator.username == "test_operator"
    assert operator.role == "admin"
    assert operator.password_hash != "TestPassword123!"
    assert operator.is_active is True
    assert verify_password("TestPassword123!", operator.password_hash)


def test_create_operator_invalid_password():
    """Test operator creation fails with weak password."""
    with pytest.raises(ValueError) as exc_info:
        create_operator(
            username="test_operator",
            password="weak",
            role="admin"
        )
    assert "at least 12 characters" in str(exc_info.value)


def test_create_operator_invalid_role():
    """Test operator creation fails with invalid role."""
    with pytest.raises(ValueError) as exc_info:
        operator = create_operator(
            username="test_operator",
            password="ValidPass123!",
            role="invalid_role"
        )
        # Validation happens in __post_init__


# ===== Unit Tests - JWT Tokens (AC #3) =====

def test_create_access_token():
    """Test access token generation."""
    token = create_access_token("op_123", "testuser", "admin")

    assert isinstance(token, str)
    assert len(token) > 50

    # Verify token contents
    token_data = verify_token(token, expected_type="access")
    assert token_data is not None
    assert token_data.operator_id == "op_123"
    assert token_data.username == "testuser"
    assert token_data.role == "admin"
    assert token_data.token_type == "access"


def test_create_refresh_token():
    """Test refresh token generation."""
    token = create_refresh_token("op_456", "refreshuser", "reviewer")

    assert isinstance(token, str)
    assert len(token) > 50

    # Verify token contents
    token_data = verify_token(token, expected_type="refresh")
    assert token_data is not None
    assert token_data.operator_id == "op_456"
    assert token_data.username == "refreshuser"
    assert token_data.role == "reviewer"
    assert token_data.token_type == "refresh"


def test_verify_token_invalid():
    """Test token verification rejects invalid tokens."""
    assert verify_token("invalid_token") is None
    assert verify_token("") is None


def test_verify_token_wrong_type():
    """Test token verification rejects wrong token type."""
    access_token = create_access_token("op_789", "user", "viewer")
    # Try to verify as refresh token
    assert verify_token(access_token, expected_type="refresh") is None


# ===== Unit Tests - RBAC (AC #2, #4) =====

def test_rbac_permission_hierarchy():
    """Test role hierarchy: viewer < reviewer < admin."""
    # Viewer can access viewer-required endpoints
    assert check_permission("viewer", "viewer") is True

    # Viewer cannot access reviewer or admin endpoints
    assert check_permission("viewer", "reviewer") is False
    assert check_permission("viewer", "admin") is False

    # Reviewer can access viewer and reviewer endpoints
    assert check_permission("reviewer", "viewer") is True
    assert check_permission("reviewer", "reviewer") is True

    # Reviewer cannot access admin endpoints
    assert check_permission("reviewer", "admin") is False

    # Admin can access all endpoints
    assert check_permission("admin", "viewer") is True
    assert check_permission("admin", "reviewer") is True
    assert check_permission("admin", "admin") is True


def test_rbac_invalid_roles():
    """Test RBAC handles invalid roles gracefully."""
    assert check_permission("invalid", "viewer") is False
    assert check_permission("viewer", "invalid") is False


# ===== Unit Tests - Rate Limiting (AC #8) =====

def test_rate_limiting_allows_within_limit():
    """Test rate limiting allows requests within the 5 attempts limit."""
    from spendsense.api.operator_auth import (
        check_rate_limit,
        record_login_attempt,
        login_attempts,
        RATE_LIMIT_ATTEMPTS
    )

    # Use unique client_id for this test
    client_id = "test_rate_limit_allow:testuser"

    # Clear any existing attempts
    if client_id in login_attempts:
        del login_attempts[client_id]

    # First 5 attempts should be allowed
    for i in range(RATE_LIMIT_ATTEMPTS):
        assert check_rate_limit(client_id) is True, f"Attempt {i+1} should be allowed"
        record_login_attempt(client_id)

    # Verify we have exactly 5 attempts recorded
    assert len(login_attempts[client_id]) == RATE_LIMIT_ATTEMPTS


def test_rate_limiting_blocks_after_limit():
    """Test rate limiting blocks requests after exceeding 5 attempts (AC #8)."""
    from spendsense.api.operator_auth import (
        check_rate_limit,
        record_login_attempt,
        login_attempts,
        RATE_LIMIT_ATTEMPTS
    )

    # Use unique client_id for this test
    client_id = "test_rate_limit_block:testuser"

    # Clear any existing attempts
    if client_id in login_attempts:
        del login_attempts[client_id]

    # Record 5 failed attempts (at the limit)
    for i in range(RATE_LIMIT_ATTEMPTS):
        record_login_attempt(client_id)

    # 6th attempt should be blocked
    assert check_rate_limit(client_id) is False, "6th attempt should be blocked"

    # 7th attempt should also be blocked
    assert check_rate_limit(client_id) is False, "7th attempt should be blocked"


def test_rate_limiting_clears_old_attempts():
    """Test rate limiting clears attempts older than 15 minutes."""
    from spendsense.api.operator_auth import (
        check_rate_limit,
        login_attempts,
        RATE_LIMIT_WINDOW_MINUTES
    )
    from datetime import datetime, timezone, timedelta

    # Use unique client_id for this test
    client_id = "test_rate_limit_clear:testuser"

    # Clear any existing attempts
    if client_id in login_attempts:
        del login_attempts[client_id]

    now = datetime.now(timezone.utc)

    # Add 3 old attempts (older than 15 minutes)
    old_time = now - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES + 1)
    login_attempts[client_id] = [old_time] * 3

    # Add 2 recent attempts (within 15 minutes)
    recent_time = now - timedelta(minutes=5)
    login_attempts[client_id].extend([recent_time, recent_time])

    # Should have 5 total attempts now
    assert len(login_attempts[client_id]) == 5

    # Check rate limit - this should clean up old attempts
    result = check_rate_limit(client_id)

    # Should be allowed because only 2 recent attempts remain after cleanup
    assert result is True
    assert len(login_attempts[client_id]) == 2, "Should have only 2 recent attempts after cleanup"


# ===== Integration Tests - Login Flow (AC #1, #8) =====

@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test_auth.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create operators table
    cursor.execute("""
        CREATE TABLE operators (
            operator_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('viewer', 'reviewer', 'admin')),
            created_at TIMESTAMP NOT NULL,
            last_login_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)

    # Create auth_audit_log table
    cursor.execute("""
        CREATE TABLE auth_audit_log (
            log_id TEXT PRIMARY KEY,
            operator_id TEXT,
            event_type TEXT NOT NULL,
            endpoint TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP NOT NULL,
            details TEXT
        )
    """)

    conn.commit()
    yield conn
    conn.close()


def test_integration_operator_login_flow(test_db):
    """Test complete login flow: create operator, save, retrieve, verify password."""
    from spendsense.auth.operator import save_operator, get_operator_by_username

    # Create and save operator
    operator = create_operator(
        username="integration_test",
        password="IntegrationTest123!",
        role="reviewer"
    )
    save_operator(test_db, operator)

    # Retrieve operator
    retrieved = get_operator_by_username(test_db, "integration_test")

    assert retrieved is not None
    assert retrieved.username == "integration_test"
    assert retrieved.role == "reviewer"
    assert verify_password("IntegrationTest123!", retrieved.password_hash)


def test_integration_audit_logging(test_db):
    """Test audit logging stores authentication events (AC #5, #6)."""
    import uuid
    import json

    log_id = f"log_{uuid.uuid4().hex[:16]}"
    cursor = test_db.cursor()

    # Log a login success event
    cursor.execute(
        """
        INSERT INTO auth_audit_log (log_id, operator_id, event_type, endpoint, ip_address, user_agent, timestamp, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            log_id,
            "op_test123",
            "login_success",
            "/api/operator/login",
            "192.168.1.1",
            "Mozilla/5.0",
            datetime.now(timezone.utc).isoformat(),
            json.dumps({"username": "testuser"})
        )
    )
    test_db.commit()

    # Retrieve and verify
    cursor.execute("SELECT * FROM auth_audit_log WHERE log_id = ?", (log_id,))
    row = cursor.fetchone()

    assert row is not None
    assert row[1] == "op_test123"  # operator_id
    assert row[2] == "login_success"  # event_type
    assert row[3] == "/api/operator/login"  # endpoint


# ===== Integration Tests - Epic 5 Consent Endpoint Protection (AC #4) =====

def test_consent_endpoint_requires_admin():
    """Test POST /api/consent requires admin role (AC #4 - Epic 5 integration)."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    from spendsense.auth.tokens import create_access_token

    client = TestClient(app)

    # Create viewer token (should be blocked)
    viewer_token = create_access_token("op_viewer", "viewer_user", "viewer")

    # Attempt to record consent with viewer token
    response = client.post(
        "/api/consent",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"user_id": "user_MASKED_000", "consent_status": "opted_in"}
    )

    # Should be forbidden (403)
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]
    assert "admin" in response.json()["detail"]


def test_consent_endpoint_allows_admin():
    """Test POST /api/consent allows admin role (AC #4 - Epic 5 integration)."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    from spendsense.auth.tokens import create_access_token

    client = TestClient(app)

    # Create admin token (should work)
    admin_token = create_access_token("op_admin", "admin_user", "admin")

    # Attempt to record consent with admin token
    response = client.post(
        "/api/consent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"user_id": "user_MASKED_000", "consent_status": "opted_in"}
    )

    # Should succeed (201) or fail with 404 if user doesn't exist (not auth error)
    assert response.status_code in [201, 404], f"Expected 201 or 404, got {response.status_code}: {response.json()}"
    if response.status_code == 404:
        # User not found is acceptable - the auth worked
        assert "not found" in response.json()["detail"].lower()


def test_consent_get_requires_reviewer():
    """Test GET /api/consent requires reviewer role (AC #4 - Epic 5 integration)."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    from spendsense.auth.tokens import create_access_token

    client = TestClient(app)

    # Create viewer token (should be blocked)
    viewer_token = create_access_token("op_viewer", "viewer_user", "viewer")

    # Attempt to get consent with viewer token
    response = client.get(
        "/api/consent/user_MASKED_000",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )

    # Should be forbidden (403)
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]
    assert "reviewer" in response.json()["detail"]


def test_consent_get_allows_reviewer():
    """Test GET /api/consent allows reviewer role (AC #4 - Epic 5 integration)."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    from spendsense.auth.tokens import create_access_token

    client = TestClient(app)

    # Create reviewer token (should work)
    reviewer_token = create_access_token("op_reviewer", "reviewer_user", "reviewer")

    # Attempt to get consent with reviewer token
    response = client.get(
        "/api/consent/user_MASKED_000",
        headers={"Authorization": f"Bearer {reviewer_token}"}
    )

    # Should succeed (200) or fail with 404 if user doesn't exist (not auth error)
    assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.json()}"
    if response.status_code == 404:
        # User not found is acceptable - the auth worked
        assert "not found" in response.json()["detail"].lower()


def test_consent_endpoint_requires_token():
    """Test consent endpoints reject requests without authentication token."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app

    client = TestClient(app)

    # Test POST without token
    response = client.post(
        "/api/consent",
        json={"user_id": "user_MASKED_000", "consent_status": "opted_in"}
    )
    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()

    # Test GET without token
    response = client.get("/api/consent/user_MASKED_000")
    assert response.status_code == 401
    assert "authorization" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
