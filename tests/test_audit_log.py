"""
Tests for audit log functionality (Epic 6 - Story 6.5).

Covers audit log creation, API endpoints, compliance metrics,
export functionality, and RBAC enforcement.
"""

import json
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.api.main import app
from spendsense.ingestion.database_writer import Base, AuditLog, User, Operator, OperatorSession
from spendsense.services.audit_service import AuditService
from spendsense.services.compliance_metrics import ComplianceMetricsCalculator


# Test fixtures
@pytest.fixture
def test_db():
    """Create in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create test users
    test_user = User(
        user_id="test_user_001",
        name="Test User",
        persona="low_savings",
        annual_income=50000,
        characteristics={},
        consent_status="opted_in"
    )
    session.add(test_user)

    # Create test operator
    test_operator = Operator(
        operator_id="op_admin_001",
        username="admin",
        password_hash="hashed",
        role="admin",
        created_at=datetime.utcnow(),
        is_active=True
    )
    session.add(test_operator)
    session.commit()

    yield session
    session.close()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


# ===== Audit Service Tests =====

def test_log_consent_changed(test_db):
    """Test AC#2: Audit log displays all consent changes with timestamps."""
    log_id = AuditService.log_consent_changed(
        user_id="test_user_001",
        old_status="opted_out",
        new_status="opted_in",
        consent_version="1.0",
        session=test_db
    )

    # Verify log created
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    assert log is not None
    assert log.event_type == "consent_changed"
    assert log.user_id == "test_user_001"
    assert log.timestamp is not None

    # Verify event data
    event_data = json.loads(log.event_data)
    assert event_data["old_status"] == "opted_out"
    assert event_data["new_status"] == "opted_in"
    assert event_data["consent_version"] == "1.0"


def test_log_eligibility_checked(test_db):
    """Test AC#3: Audit log displays all eligibility check results."""
    log_id = AuditService.log_eligibility_checked(
        user_id="test_user_001",
        recommendation_id="rec_123",
        passed=False,
        failure_reasons=["income_below_threshold", "age_below_18"],
        thresholds={"age": 18, "income": 20000},
        user_values={"age": 17, "income": 15000},
        session=test_db
    )

    # Verify log created
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    assert log is not None
    assert log.event_type == "eligibility_checked"
    assert log.recommendation_id == "rec_123"

    # Verify event data
    event_data = json.loads(log.event_data)
    assert event_data["passed"] is False
    assert "income_below_threshold" in event_data["failure_reasons"]
    assert event_data["thresholds"]["age"] == 18


def test_log_tone_validated(test_db):
    """Test AC#4: Audit log displays all tone validation results."""
    log_id = AuditService.log_tone_validated(
        user_id="test_user_001",
        recommendation_id="rec_456",
        passed=False,
        detected_violations=["irresponsible", "bad with money"],
        severity="critical",
        original_text="You're irresponsible with money...",
        session=test_db
    )

    # Verify log created
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    assert log is not None
    assert log.event_type == "tone_validated"

    # Verify event data
    event_data = json.loads(log.event_data)
    assert event_data["passed"] is False
    assert "irresponsible" in event_data["detected_violations"]
    assert event_data["severity"] == "critical"


def test_log_operator_action(test_db):
    """Test AC#5: Audit log displays all operator actions."""
    log_id = AuditService.log_operator_action(
        operator_id="op_admin_001",
        action="overridden",
        recommendation_id="rec_789",
        user_id="test_user_001",
        justification="Content not appropriate",
        review_time_seconds=120,
        session=test_db
    )

    # Verify log created
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    assert log is not None
    assert log.event_type == "operator_action"
    assert log.operator_id == "op_admin_001"

    # Verify event data
    event_data = json.loads(log.event_data)
    assert event_data["action"] == "overridden"
    assert event_data["justification"] == "Content not appropriate"
    assert event_data["review_time_seconds"] == 120


def test_log_persona_overridden(test_db):
    """Test AC#5: Audit log displays persona overrides."""
    log_id = AuditService.log_persona_overridden(
        operator_id="op_admin_001",
        user_id="test_user_001",
        old_persona="low_savings",
        new_persona="high_utilization",
        justification="Manual override based on review",
        session=test_db
    )

    # Verify log created
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    assert log is not None
    assert log.event_type == "persona_overridden"

    # Verify event data
    event_data = json.loads(log.event_data)
    assert event_data["old_persona"] == "low_savings"
    assert event_data["new_persona"] == "high_utilization"


def test_log_recommendation_generated(test_db):
    """Test AC#1: Audit log displays all recommendation decisions with full trace."""
    log_id = AuditService.log_recommendation_generated(
        user_id="test_user_001",
        recommendation_id="rec_set_001",
        persona_id="low_savings",
        content_ids=["edu_001", "edu_002", "offer_003"],
        guardrail_results={
            "eligibility_passed": 2,
            "eligibility_failed": 1,
            "tone_passed": 3,
            "tone_failed": 0
        },
        session=test_db
    )

    # Verify log created
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    assert log is not None
    assert log.event_type == "recommendation_generated"

    # Verify event data
    event_data = json.loads(log.event_data)
    assert event_data["persona_id"] == "low_savings"
    assert len(event_data["content_ids"]) == 3
    assert event_data["guardrail_results"]["eligibility_passed"] == 2


def test_invalid_event_type(test_db):
    """Test that invalid event types raise ValueError."""
    with pytest.raises(ValueError, match="Invalid event_type"):
        AuditService.log_event(
            event_type="invalid_type",
            event_data={"test": "data"},
            session=test_db
        )


# ===== Compliance Metrics Tests =====

def test_calculate_consent_metrics(test_db):
    """Test AC#8: Consent metrics calculation."""
    # Add consent change logs
    for i in range(5):
        AuditService.log_consent_changed(
            user_id=f"user_{i}",
            old_status="opted_out",
            new_status="opted_in",
            consent_version="1.0",
            session=test_db
        )

    calculator = ComplianceMetricsCalculator(test_db)
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()

    metrics = calculator.calculate_consent_metrics(start_date, end_date)

    assert metrics["total_users"] >= 1  # At least test user
    assert metrics["opted_in_count"] >= 1
    assert 0 <= metrics["opt_in_rate_pct"] <= 100


def test_calculate_eligibility_metrics(test_db):
    """Test AC#8: Eligibility metrics calculation."""
    # Add eligibility logs
    AuditService.log_eligibility_checked(
        user_id="test_user_001",
        recommendation_id="rec_1",
        passed=True,
        failure_reasons=[],
        thresholds={},
        user_values={},
        session=test_db
    )

    AuditService.log_eligibility_checked(
        user_id="test_user_001",
        recommendation_id="rec_2",
        passed=False,
        failure_reasons=["income_below_threshold"],
        thresholds={"income": 20000},
        user_values={"income": 15000},
        session=test_db
    )

    calculator = ComplianceMetricsCalculator(test_db)
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()

    metrics = calculator.calculate_eligibility_metrics(start_date, end_date)

    assert metrics["total_checks"] == 2
    assert metrics["passed"] == 1
    assert metrics["failed"] == 1
    assert metrics["pass_rate_pct"] == 50.0
    assert len(metrics["failure_reasons"]) == 1
    assert metrics["failure_reasons"][0]["reason"] == "income_below_threshold"


def test_calculate_tone_metrics(test_db):
    """Test AC#8: Tone metrics calculation."""
    # Add tone validation logs
    AuditService.log_tone_validated(
        user_id="test_user_001",
        recommendation_id="rec_1",
        passed=True,
        detected_violations=[],
        severity="none",
        original_text="Good text",
        session=test_db
    )

    AuditService.log_tone_validated(
        user_id="test_user_001",
        recommendation_id="rec_2",
        passed=False,
        detected_violations=["irresponsible"],
        severity="critical",
        original_text="Bad text",
        session=test_db
    )

    calculator = ComplianceMetricsCalculator(test_db)
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()

    metrics = calculator.calculate_tone_metrics(start_date, end_date)

    assert metrics["total_validations"] == 2
    assert metrics["passed"] == 1
    assert metrics["failed"] == 1
    assert metrics["pass_rate_pct"] == 50.0
    assert len(metrics["violations_by_category"]) == 1


def test_calculate_operator_metrics(test_db):
    """Test AC#8: Operator action metrics calculation."""
    # Add operator action logs
    for action in ["approved", "overridden", "flagged"]:
        AuditService.log_operator_action(
            operator_id="op_admin_001",
            action=action,
            recommendation_id=f"rec_{action}",
            user_id="test_user_001",
            justification=f"{action} action",
            session=test_db
        )

    calculator = ComplianceMetricsCalculator(test_db)
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()

    metrics = calculator.calculate_operator_metrics(start_date, end_date)

    assert metrics["total_actions"] == 3
    assert metrics["approvals"] == 1
    assert metrics["overrides"] == 1
    assert metrics["flags"] == 1
    assert len(metrics["actions_by_operator"]) == 1
    assert metrics["actions_by_operator"][0]["operator_id"] == "op_admin_001"
    assert metrics["actions_by_operator"][0]["count"] == 3


# ===== API Tests (RBAC enforcement) =====

def test_audit_log_requires_admin_role(client):
    """Test AC#10: Audit log access restricted to admin and compliance roles."""
    # Without authentication
    response = client.get("/api/operator/audit/log")
    assert response.status_code == 401  # Unauthorized


def test_audit_export_requires_admin_role(client):
    """Test AC#10: Export functionality requires admin role."""
    # Without authentication
    response = client.get("/api/operator/audit/export?format=csv")
    assert response.status_code == 401  # Unauthorized


def test_audit_metrics_requires_admin_role(client):
    """Test AC#10: Metrics access requires admin role."""
    # Without authentication
    response = client.get("/api/operator/audit/metrics")
    assert response.status_code == 401  # Unauthorized


# ===== Filtering and Pagination Tests =====

def test_audit_log_filtering_by_event_type(test_db):
    """Test AC#6: Filter capabilities by event type."""
    # Create logs of different types
    AuditService.log_consent_changed(
        user_id="test_user_001",
        old_status="opted_out",
        new_status="opted_in",
        consent_version="1.0",
        session=test_db
    )

    AuditService.log_operator_action(
        operator_id="op_admin_001",
        action="approved",
        recommendation_id="rec_1",
        user_id="test_user_001",
        session=test_db
    )

    # Query by event type
    consent_logs = test_db.query(AuditLog).filter(
        AuditLog.event_type == "consent_changed"
    ).all()

    operator_logs = test_db.query(AuditLog).filter(
        AuditLog.event_type == "operator_action"
    ).all()

    assert len(consent_logs) == 1
    assert len(operator_logs) == 1


def test_audit_log_filtering_by_user_id(test_db):
    """Test AC#6: Filter capabilities by user ID."""
    # Create logs for different users
    AuditService.log_consent_changed(
        user_id="user_A",
        old_status="opted_out",
        new_status="opted_in",
        consent_version="1.0",
        session=test_db
    )

    AuditService.log_consent_changed(
        user_id="user_B",
        old_status="opted_out",
        new_status="opted_in",
        consent_version="1.0",
        session=test_db
    )

    # Query by user_id
    user_a_logs = test_db.query(AuditLog).filter(
        AuditLog.user_id == "user_A"
    ).all()

    assert len(user_a_logs) == 1
    assert user_a_logs[0].user_id == "user_A"


def test_audit_log_filtering_by_date_range(test_db):
    """Test AC#6: Filter capabilities by date range."""
    # Create log in the past
    old_timestamp = datetime.utcnow() - timedelta(days=10)
    log_id = AuditService.log_consent_changed(
        user_id="test_user_001",
        old_status="opted_out",
        new_status="opted_in",
        consent_version="1.0",
        session=test_db
    )

    # Update timestamp to simulate old log
    log = test_db.query(AuditLog).filter(AuditLog.log_id == log_id).first()
    log.timestamp = old_timestamp
    test_db.commit()

    # Query with date range
    start_date = datetime.utcnow() - timedelta(days=15)
    end_date = datetime.utcnow() - timedelta(days=5)

    logs_in_range = test_db.query(AuditLog).filter(
        AuditLog.timestamp >= start_date,
        AuditLog.timestamp <= end_date
    ).all()

    assert len(logs_in_range) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
