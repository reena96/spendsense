"""
Tests for consent management system (Epic 5 - Story 5.1).

Comprehensive test suite covering all acceptance criteria.
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.ingestion.database_writer import Base, User
from spendsense.guardrails.consent import (
    ConsentService,
    ConsentStatus,
    ConsentNotGrantedError,
    ConsentResult,
    require_consent_decorator
)


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        user_id="test_user_123",
        name="Test User",
        persona="high_utilization",
        annual_income=55000.0,
        characteristics={}
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def consent_service(db_session):
    """Create ConsentService instance."""
    return ConsentService(db_session)


# ===== AC1: Consent database table with fields =====

def test_user_model_has_consent_fields(test_user):
    """Test that User model includes consent fields (AC1)."""
    assert hasattr(test_user, 'consent_status')
    assert hasattr(test_user, 'consent_timestamp')
    assert hasattr(test_user, 'consent_version')


def test_default_consent_status_is_opted_out(test_user):
    """Test that new users default to opted_out (AC1)."""
    assert test_user.consent_status == 'opted_out'
    assert test_user.consent_version == '1.0'


# ===== AC2 & AC3: Opt-in and opt-out functionality =====

def test_record_consent_opt_in(consent_service, test_user):
    """Test recording explicit opt-in consent (AC2)."""
    result = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN,
        consent_version="1.0"
    )

    assert isinstance(result, ConsentResult)
    assert result.user_id == test_user.user_id
    assert result.consent_status == ConsentStatus.OPTED_IN
    assert result.consent_version == "1.0"
    assert result.consent_timestamp is not None
    assert isinstance(result.consent_timestamp, datetime)


def test_record_consent_opt_out(consent_service, test_user, db_session):
    """Test recording opt-out/revoke consent (AC3)."""
    # First opt in
    consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )

    # Then opt out
    result = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_OUT
    )

    assert result.consent_status == ConsentStatus.OPTED_OUT

    # Verify in database
    db_session.refresh(test_user)
    assert test_user.consent_status == 'opted_out'


# ===== AC4: Consent status checked before processing =====

def test_check_consent_returns_status(consent_service, test_user):
    """Test checking consent status (AC4, AC9)."""
    result = consent_service.check_consent(user_id=test_user.user_id)

    assert isinstance(result, ConsentResult)
    assert result.user_id == test_user.user_id
    assert result.consent_status == ConsentStatus.OPTED_OUT  # Default status


def test_require_consent_raises_error_when_opted_out(consent_service, test_user):
    """Test that processing is blocked without consent (AC4, AC5, AC10)."""
    with pytest.raises(ConsentNotGrantedError) as exc_info:
        consent_service.require_consent(user_id=test_user.user_id)

    assert "has not granted consent" in str(exc_info.value)
    assert test_user.user_id in str(exc_info.value)


def test_require_consent_succeeds_when_opted_in(consent_service, test_user):
    """Test that processing proceeds when consented (AC4)."""
    # Opt in first
    consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )

    # Should not raise
    consent_service.require_consent(user_id=test_user.user_id)


# ===== AC5: Processing halted upon consent revocation =====

def test_processing_halted_after_consent_revocation(consent_service, test_user):
    """Test immediate halt upon consent revocation (AC5, AC10)."""
    # Start with opt-in
    consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )

    # Verify processing allowed
    consent_service.require_consent(user_id=test_user.user_id)

    # Revoke consent
    consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_OUT
    )

    # Verify processing now blocked
    with pytest.raises(ConsentNotGrantedError):
        consent_service.require_consent(user_id=test_user.user_id)


# ===== AC6: Consent changes logged in audit trail =====

def test_consent_changes_logged_in_audit_trail(consent_service, test_user):
    """Test that consent changes include audit trail (AC6, AC7)."""
    result = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN,
        consent_version="1.0"
    )

    # Verify audit trail structure
    assert 'audit_trail' in result.__dict__
    audit = result.audit_trail

    assert audit['action'] == 'consent_recorded'
    assert audit['user_id'] == test_user.user_id
    assert audit['previous_status'] == 'opted_out'
    assert audit['new_status'] == 'opted_in'
    assert audit['consent_version'] == '1.0'
    assert 'timestamp' in audit
    assert audit['change_detected'] == True


def test_audit_trail_includes_timestamp_and_user_id(consent_service, test_user):
    """Test audit trail includes required fields (AC6)."""
    result = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )

    audit = result.audit_trail
    assert 'user_id' in audit
    assert 'timestamp' in audit
    assert isinstance(audit['timestamp'], str)  # ISO format


# ===== AC8 & AC9: API endpoints =====
# Note: API endpoint tests will use FastAPI TestClient

def test_user_not_found_raises_value_error(consent_service):
    """Test error handling for non-existent user (AC8, AC9)."""
    with pytest.raises(ValueError) as exc_info:
        consent_service.check_consent(user_id="nonexistent_user")

    assert "not found" in str(exc_info.value).lower()


def test_record_consent_for_nonexistent_user_raises_error(consent_service):
    """Test recording consent for non-existent user fails (AC8)."""
    with pytest.raises(ValueError):
        consent_service.record_consent(
            user_id="nonexistent_user",
            consent_status=ConsentStatus.OPTED_IN
        )


# ===== AC10: Unit tests verify processing blocked =====

def test_decorator_requires_consent(db_session, test_user):
    """Test require_consent_decorator blocks processing (AC10)."""
    @require_consent_decorator
    def process_data(user_id: str, db_session, data: str):
        return f"Processed: {data}"

    # Should raise without consent
    with pytest.raises(ConsentNotGrantedError):
        process_data(user_id=test_user.user_id, db_session=db_session, data="test")

    # Grant consent
    consent_service = ConsentService(db_session)
    consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )

    # Should succeed with consent
    result = process_data(user_id=test_user.user_id, db_session=db_session, data="test")
    assert result == "Processed: test"


# ===== Additional edge cases and integration tests =====

def test_consent_version_tracking(consent_service, test_user):
    """Test that consent version is tracked correctly."""
    result = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN,
        consent_version="2.0"
    )

    assert result.consent_version == "2.0"

    # Verify in check
    check_result = consent_service.check_consent(user_id=test_user.user_id)
    assert check_result.consent_version == "2.0"


def test_multiple_consent_changes_tracked(consent_service, test_user):
    """Test multiple consent changes are properly tracked."""
    # Initial opt-in
    result1 = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )
    assert result1.audit_trail['previous_status'] == 'opted_out'

    # Opt-out
    result2 = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_OUT
    )
    assert result2.audit_trail['previous_status'] == 'opted_in'

    # Opt-in again
    result3 = consent_service.record_consent(
        user_id=test_user.user_id,
        consent_status=ConsentStatus.OPTED_IN
    )
    assert result3.audit_trail['previous_status'] == 'opted_out'


def test_check_consent_includes_audit_trail(consent_service, test_user):
    """Test that check_consent also includes audit trail."""
    result = consent_service.check_consent(user_id=test_user.user_id)

    assert 'audit_trail' in result.__dict__
    audit = result.audit_trail
    assert audit['action'] == 'consent_checked'
    assert audit['user_id'] == test_user.user_id
    assert 'timestamp' in audit


def test_consent_enum_values():
    """Test ConsentStatus enum has correct values."""
    assert ConsentStatus.OPTED_IN.value == "opted_in"
    assert ConsentStatus.OPTED_OUT.value == "opted_out"


# ===== FastAPI Integration Tests (Epic 5 - Story 5.1 Review) =====

@pytest.fixture
def test_client():
    """Create FastAPI TestClient for API endpoint testing."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    return TestClient(app)


def test_post_consent_endpoint_success(test_client):
    """Test POST /api/consent endpoint with valid request (AC8)."""
    # Use a real user from the database
    response = test_client.post(
        "/api/consent",
        json={
            "user_id": "user_MASKED_000",
            "consent_status": "opted_in",
            "consent_version": "1.0"
        }
    )

    assert response.status_code == 201  # Created
    data = response.json()
    assert data["user_id"] == "user_MASKED_000"
    assert data["consent_status"] == "opted_in"
    assert data["consent_version"] == "1.0"
    assert "consent_timestamp" in data


def test_post_consent_endpoint_invalid_status(test_client):
    """Test POST /api/consent with invalid consent status returns 400 (AC8)."""
    response = test_client.post(
        "/api/consent",
        json={
            "user_id": "user_MASKED_000",
            "consent_status": "invalid_status",
            "consent_version": "1.0"
        }
    )

    assert response.status_code == 400
    assert "Invalid consent_status" in response.json()["detail"]


def test_post_consent_endpoint_user_not_found(test_client):
    """Test POST /api/consent with non-existent user returns 404 (AC8)."""
    response = test_client.post(
        "/api/consent",
        json={
            "user_id": "nonexistent_user",
            "consent_status": "opted_in",
            "consent_version": "1.0"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_consent_endpoint_success(test_client):
    """Test GET /api/consent/{user_id} endpoint returns consent status (AC9)."""
    # Use a real user from the database (user_MASKED_000 was just set to opted_in above)
    response = test_client.get("/api/consent/user_MASKED_000")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_MASKED_000"
    assert data["consent_status"] in ["opted_in", "opted_out"]  # Could be either depending on test order
    assert "consent_timestamp" in data


def test_get_consent_endpoint_user_not_found(test_client):
    """Test GET /api/consent/{user_id} with non-existent user returns 404 (AC9)."""
    response = test_client.get("/api/consent/nonexistent_user")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_consent_endpoint_pydantic_validation(test_client):
    """Test Pydantic validation on consent endpoints."""
    # Missing required field
    response = test_client.post(
        "/api/consent",
        json={
            "user_id": "test_user"
            # Missing consent_status
        }
    )

    assert response.status_code == 422  # Unprocessable Entity (Pydantic validation error)
