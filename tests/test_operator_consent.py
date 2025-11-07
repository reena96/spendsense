"""
Tests for Operator Consent Management API (Epic 6 - Story 6.6).

Tests batch consent operations, consent history, and user filtering.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.ingestion.database_writer import User, Account, AuditLog, Base
from spendsense.auth.operator import Operator


@pytest.fixture
def test_db(tmp_path):
    """Create test database with sample users."""
    db_path = tmp_path / "test_consent.db"
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test users
    users = [
        User(
            user_id="user_001",
            name="Alice Test",
            persona="young_professional",
            annual_income=60000,
            characteristics={},
            consent_status="opted_in",
            consent_timestamp=datetime.utcnow() - timedelta(days=30),
            consent_version="1.0"
        ),
        User(
            user_id="user_002",
            name="Bob Test",
            persona="debt_manager",
            annual_income=50000,
            characteristics={},
            consent_status="opted_out",
            consent_timestamp=datetime.utcnow() - timedelta(days=5),
            consent_version="1.0"
        ),
        User(
            user_id="user_003",
            name="Carol Test",
            persona="budget_builder",
            annual_income=45000,
            characteristics={},
            consent_status="opted_in",
            consent_timestamp=datetime.utcnow() - timedelta(days=60),
            consent_version="1.0"
        ),
    ]

    for user in users:
        session.add(user)

    # Create test operator
    operator = Operator(
        operator_id="test_admin",
        email="admin@test.com",
        name="Test Admin",
        role="admin",
        password_hash="hashed_password"
    )
    session.add(operator)

    # Create some consent change audit logs
    audit_logs = [
        AuditLog(
            event_type="consent_changed",
            user_id="user_001",
            operator_id="test_admin",
            timestamp=datetime.utcnow() - timedelta(days=30),
            event_data={
                "old_status": None,
                "new_status": "opted_in",
                "reason": "Initial consent"
            }
        ),
        AuditLog(
            event_type="consent_changed",
            user_id="user_002",
            operator_id="test_admin",
            timestamp=datetime.utcnow() - timedelta(days=10),
            event_data={
                "old_status": "opted_in",
                "new_status": "opted_out",
                "reason": "User requested opt-out"
            }
        ),
    ]

    for log in audit_logs:
        session.add(log)

    session.commit()
    session.close()

    return db_path


def test_batch_consent_change_success(test_db, monkeypatch):
    """Test batch consent change succeeds for valid users."""
    from spendsense.api.operator_consent import batch_consent_change, BatchConsentRequest
    from spendsense.auth.tokens import TokenData

    # Mock get_db_path
    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    # Mock operator token
    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="admin"
    )

    # Test batch change
    request = BatchConsentRequest(
        user_ids=["user_001", "user_002"],
        consent_status="opted_out",
        reason="Testing batch consent change for compliance audit",
        consent_version="1.0"
    )

    # Use pytest's async test support
    import asyncio
    result = asyncio.run(batch_consent_change(request, token))

    assert result.success_count == 2
    assert result.failure_count == 0
    assert len(result.failed_users) == 0
    assert "2 succeeded" in result.message


def test_batch_consent_change_partial_failure(test_db, monkeypatch):
    """Test batch consent change handles invalid users gracefully."""
    from spendsense.api.operator_consent import batch_consent_change, BatchConsentRequest
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="admin"
    )

    request = BatchConsentRequest(
        user_ids=["user_001", "invalid_user", "user_002"],
        consent_status="opted_in",
        reason="Testing batch operation with invalid user included",
        consent_version="1.0"
    )

    import asyncio
    result = asyncio.run(batch_consent_change(request, token))

    assert result.success_count == 2
    assert result.failure_count == 1
    assert len(result.failed_users) == 1
    assert result.failed_users[0]["user_id"] == "invalid_user"


def test_batch_consent_invalid_status(test_db, monkeypatch):
    """Test batch consent rejects invalid consent status."""
    from spendsense.api.operator_consent import batch_consent_change, BatchConsentRequest
    from spendsense.auth.tokens import TokenData
    from fastapi import HTTPException

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="admin"
    )

    request = BatchConsentRequest(
        user_ids=["user_001"],
        consent_status="invalid_status",
        reason="Testing invalid consent status validation",
        consent_version="1.0"
    )

    import asyncio
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(batch_consent_change(request, token))

    assert exc_info.value.status_code == 400
    assert "Invalid consent_status" in str(exc_info.value.detail)


def test_get_users_with_consent_filter_all(test_db, monkeypatch):
    """Test get users returns all users when no filters applied."""
    from spendsense.api.operator_consent import get_users_with_consent_filter
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    result = asyncio.run(get_users_with_consent_filter(
        consent_status=None,
        changed_since=None,
        limit=50,
        offset=0,
        current_operator=token
    ))

    assert result.total == 3
    assert len(result.users) == 3


def test_get_users_with_consent_filter_opted_in(test_db, monkeypatch):
    """Test get users filters by opted_in status."""
    from spendsense.api.operator_consent import get_users_with_consent_filter
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    result = asyncio.run(get_users_with_consent_filter(
        consent_status="opted_in",
        changed_since=None,
        limit=50,
        offset=0,
        current_operator=token
    ))

    assert result.total == 2
    assert len(result.users) == 2
    assert all(user.consent_status == "opted_in" for user in result.users)


def test_get_users_with_consent_filter_opted_out(test_db, monkeypatch):
    """Test get users filters by opted_out status."""
    from spendsense.api.operator_consent import get_users_with_consent_filter
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    result = asyncio.run(get_users_with_consent_filter(
        consent_status="opted_out",
        changed_since=None,
        limit=50,
        offset=0,
        current_operator=token
    ))

    assert result.total == 1
    assert len(result.users) == 1
    assert result.users[0].consent_status == "opted_out"


def test_get_users_with_changed_since_filter(test_db, monkeypatch):
    """Test get users filters by recent changes."""
    from spendsense.api.operator_consent import get_users_with_consent_filter
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    # Filter for changes in last 10 days
    cutoff_date = (datetime.utcnow() - timedelta(days=10)).isoformat()

    import asyncio
    result = asyncio.run(get_users_with_consent_filter(
        consent_status=None,
        changed_since=cutoff_date,
        limit=50,
        offset=0,
        current_operator=token
    ))

    # Should only return user_002 (changed 5 days ago)
    assert result.total == 1
    assert len(result.users) == 1
    assert result.users[0].user_id == "user_002"


def test_get_users_pagination(test_db, monkeypatch):
    """Test get users pagination works correctly."""
    from spendsense.api.operator_consent import get_users_with_consent_filter
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    # Get first page (limit 2)
    result_page1 = asyncio.run(get_users_with_consent_filter(
        consent_status=None,
        changed_since=None,
        limit=2,
        offset=0,
        current_operator=token
    ))

    # Get second page
    result_page2 = asyncio.run(get_users_with_consent_filter(
        consent_status=None,
        changed_since=None,
        limit=2,
        offset=2,
        current_operator=token
    ))

    assert result_page1.total == 3
    assert len(result_page1.users) == 2
    assert len(result_page2.users) == 1


def test_get_consent_history(test_db, monkeypatch):
    """Test get consent history returns change timeline."""
    from spendsense.api.operator_consent import get_consent_history
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    result = asyncio.run(get_consent_history(
        user_id="user_001",
        current_operator=token
    ))

    assert result.user_id == "user_001"
    assert result.total_changes == 1
    assert len(result.history) == 1
    assert result.history[0].new_status == "opted_in"
    assert result.history[0].changed_by == "test_admin"
    assert result.history[0].reason == "Initial consent"


def test_get_consent_history_user_not_found(test_db, monkeypatch):
    """Test get consent history returns 404 for invalid user."""
    from spendsense.api.operator_consent import get_consent_history
    from spendsense.auth.tokens import TokenData
    from fastapi import HTTPException

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_consent_history(
            user_id="invalid_user",
            current_operator=token
        ))

    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail).lower()


def test_get_consent_history_no_changes(test_db, monkeypatch):
    """Test get consent history handles users with no history."""
    from spendsense.api.operator_consent import get_consent_history
    from spendsense.auth.tokens import TokenData

    monkeypatch.setattr("spendsense.api.operator_consent.get_db_path", lambda: test_db)

    token = TokenData(
        operator_id="test_admin",
        email="admin@test.com",
        role="reviewer"
    )

    import asyncio
    result = asyncio.run(get_consent_history(
        user_id="user_003",  # No audit log entries
        current_operator=token
    ))

    assert result.user_id == "user_003"
    assert result.total_changes == 0
    assert len(result.history) == 0
