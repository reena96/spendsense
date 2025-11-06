"""
Comprehensive tests for recommendation review queue API (Story 6.4).

Tests cover:
- Review queue retrieval with filters (AC #1, #9)
- Recommendation detail view (AC #2, #4)
- Guardrail results display (AC #3)
- Approve action (AC #5, #8)
- Override action (AC #6, #8)
- Flag action (AC #7, #8)
- Batch approval (AC #10)
- Authentication and authorization (reviewer vs admin)
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from spendsense.api.main import app
from spendsense.auth.tokens import create_access_token
from spendsense.ingestion.database_writer import (
    FlaggedRecommendation,
    create_engine,
    sessionmaker
)
from pathlib import Path


# Test client
client = TestClient(app)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "processed" / "spendsense.db"


# ===== Fixtures =====

@pytest.fixture
def reviewer_token():
    """Generate reviewer role token."""
    return create_access_token(
        operator_id="test_reviewer",
        username="reviewer_user",
        role="reviewer"
    )


@pytest.fixture
def admin_token():
    """Generate admin role token."""
    return create_access_token(
        operator_id="test_admin",
        username="admin_user",
        role="admin"
    )


@pytest.fixture
def viewer_token():
    """Generate viewer role token (insufficient for review actions)."""
    return create_access_token(
        operator_id="test_viewer",
        username="viewer_user",
        role="viewer"
    )


@pytest.fixture
def reviewer_headers(reviewer_token):
    """Generate authorization headers with reviewer token."""
    return {"Authorization": f"Bearer {reviewer_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Generate authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def viewer_headers(viewer_token):
    """Generate authorization headers with viewer token."""
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture
def sample_flagged_rec():
    """Create a sample flagged recommendation for testing."""
    if not DB_PATH.exists():
        pytest.skip("Database not available")

    engine = create_engine(f"sqlite:///{str(DB_PATH)}")
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create test flagged recommendation
        rec_id = f"test_rec_{datetime.now().timestamp()}"
        flagged_rec = FlaggedRecommendation(
            recommendation_id=rec_id,
            user_id="user_MASKED_000",
            content_id="test_content_001",
            content_title="Test Recommendation",
            content_type="education",
            rationale="This is a test rationale for testing purposes.",
            flagged_at=datetime.now(),
            flagged_by="system",
            flag_reason="tone_fail",
            guardrail_status=json.dumps({
                "consent_status": "opted_in",
                "eligibility_passed": True,
                "eligibility_failures": [],
                "tone_passed": False,
                "tone_violations": ["test phrase"],
                "disclaimer_present": True
            }),
            decision_trace=json.dumps({
                "persona_id": "high_utilization",
                "persona_name": "High Credit Utilization",
                "matching_signals": {"credit_utilization": True},
                "ranking_score": None,
                "generation_reason": "Matched based on credit signals"
            }),
            review_status="pending"
        )

        session.add(flagged_rec)
        session.commit()

        yield rec_id

        # Cleanup
        session.query(FlaggedRecommendation).filter(
            FlaggedRecommendation.recommendation_id == rec_id
        ).delete()
        session.commit()

    finally:
        session.close()


# ===== Test Review Queue Endpoint =====

def test_get_review_queue_success(reviewer_headers):
    """Test fetching review queue returns items (AC #1)."""
    response = client.get(
        "/api/operator/review/queue",
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "has_more" in data


def test_get_review_queue_with_filters(reviewer_headers):
    """Test review queue with filters (AC #9)."""
    response = client.get(
        "/api/operator/review/queue?status=pending&flag_reason=tone_fail",
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)


def test_get_review_queue_with_persona_filter(reviewer_headers, sample_flagged_rec):
    """Test review queue with persona filter (AC #9)."""
    response = client.get(
        "/api/operator/review/queue?persona=high_utilization",
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    # Verify persona filter works (should include our test rec with high_utilization persona)
    if data["total"] > 0:
        assert all(item["decision_trace"]["persona_id"] == "high_utilization" for item in data["items"])


def test_get_review_queue_pagination(reviewer_headers):
    """Test review queue pagination."""
    response = client.get(
        "/api/operator/review/queue?page=1&page_size=10",
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_get_review_queue_requires_auth():
    """Test review queue requires authentication."""
    response = client.get("/api/operator/review/queue")
    assert response.status_code == 401


def test_get_review_queue_requires_reviewer_role(viewer_headers):
    """Test review queue requires at least reviewer role."""
    # Viewer role should have access (reviewer is minimum)
    response = client.get(
        "/api/operator/review/queue",
        headers=viewer_headers
    )
    # Viewer doesn't have reviewer role, should be forbidden
    assert response.status_code == 403


# ===== Test Recommendation Detail Endpoint =====

def test_get_recommendation_detail_success(reviewer_headers, sample_flagged_rec):
    """Test fetching recommendation detail (AC #2, #4)."""
    response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check complete structure (AC #2)
    assert "recommendation_id" in data
    assert "user_id" in data
    assert "content_title" in data
    assert "rationale" in data

    # Check guardrail results (AC #3)
    assert "guardrail_status" in data
    guardrails = data["guardrail_status"]
    assert "consent_status" in guardrails
    assert "eligibility_passed" in guardrails
    assert "tone_passed" in guardrails

    # Check decision trace (AC #4)
    assert "decision_trace" in data
    trace = data["decision_trace"]
    assert "persona_id" in trace
    assert "matching_signals" in trace


def test_get_recommendation_detail_not_found(reviewer_headers):
    """Test 404 when recommendation doesn't exist."""
    response = client.get(
        "/api/operator/review/nonexistent_rec",
        headers=reviewer_headers
    )

    assert response.status_code == 404


def test_get_recommendation_detail_requires_auth():
    """Test detail endpoint requires authentication."""
    response = client.get("/api/operator/review/test_rec")
    assert response.status_code == 401


# ===== Test Approve Action =====

def test_approve_recommendation_success(reviewer_headers, sample_flagged_rec):
    """Test approving recommendation (AC #5, #8)."""
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/approve",
        json={"notes": "Looks good, approving for delivery"},
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert data["recommendation_id"] == sample_flagged_rec
    assert data["action"] == "approved"
    assert data["status"] == "approved"
    assert "operator_id" in data
    assert "timestamp" in data


def test_approve_recommendation_updates_status(reviewer_headers, sample_flagged_rec):
    """Test approve updates review_status in database."""
    # Approve
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/approve",
        json={"notes": "Test approval"},
        headers=reviewer_headers
    )
    assert response.status_code == 200

    # Verify status updated
    detail_response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=reviewer_headers
    )
    assert detail_response.json()["review_status"] == "approved"


def test_approve_recommendation_not_found(reviewer_headers):
    """Test approve fails if recommendation doesn't exist."""
    response = client.post(
        "/api/operator/review/nonexistent_rec/approve",
        json={"notes": "Test"},
        headers=reviewer_headers
    )

    assert response.status_code == 404


def test_approve_recommendation_requires_auth():
    """Test approve requires authentication."""
    response = client.post(
        "/api/operator/review/test_rec/approve",
        json={"notes": "Test"}
    )
    assert response.status_code == 401


def test_approve_recommendation_requires_reviewer_role(viewer_headers):
    """Test approve requires at least reviewer role."""
    response = client.post(
        "/api/operator/review/test_rec/approve",
        json={"notes": "Test"},
        headers=viewer_headers
    )
    assert response.status_code == 403


# ===== Test Override Action =====

def test_override_recommendation_success(admin_headers, sample_flagged_rec):
    """Test overriding recommendation (AC #6, #8)."""
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/override",
        json={
            "justification": "This recommendation contains inappropriate language that violates our tone guidelines despite passing technical validation."
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check response
    assert data["recommendation_id"] == sample_flagged_rec
    assert data["action"] == "overridden"
    assert data["status"] == "overridden"
    assert "operator_id" in data


def test_override_recommendation_requires_admin(reviewer_headers, sample_flagged_rec):
    """Test override requires admin role (AC #6)."""
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/override",
        json={
            "justification": "Should fail because reviewer role insufficient"
        },
        headers=reviewer_headers
    )

    # Reviewer doesn't have admin role
    assert response.status_code == 403


def test_override_recommendation_requires_justification(admin_headers, sample_flagged_rec):
    """Test override requires justification (AC #6)."""
    # Missing justification field
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/override",
        json={},
        headers=admin_headers
    )

    assert response.status_code == 422  # Validation error


def test_override_recommendation_justification_too_short(admin_headers, sample_flagged_rec):
    """Test override justification must be at least 50 characters."""
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/override",
        json={"justification": "Too short"},  # Less than 50 chars
        headers=admin_headers
    )

    assert response.status_code == 422


def test_override_recommendation_not_found(admin_headers):
    """Test override fails if recommendation doesn't exist."""
    response = client.post(
        "/api/operator/review/nonexistent_rec/override",
        json={
            "justification": "This is a test justification that is definitely more than fifty characters long."
        },
        headers=admin_headers
    )

    assert response.status_code == 404


# ===== Test Flag Action =====

def test_flag_recommendation_success(reviewer_headers, sample_flagged_rec):
    """Test flagging recommendation for escalation (AC #7, #8)."""
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/flag",
        json={
            "flag_reason": "quality_concern",
            "notes": "Needs senior review for policy alignment"
        },
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check response
    assert data["recommendation_id"] == sample_flagged_rec
    assert data["action"] == "flagged"
    assert data["status"] == "escalated"


def test_flag_recommendation_updates_status(reviewer_headers, sample_flagged_rec):
    """Test flag updates review_status to escalated."""
    # Flag
    response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/flag",
        json={
            "flag_reason": "needs_review",
            "notes": "Test flag"
        },
        headers=reviewer_headers
    )
    assert response.status_code == 200

    # Verify status updated
    detail_response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=reviewer_headers
    )
    assert detail_response.json()["review_status"] == "escalated"


def test_flag_recommendation_requires_auth():
    """Test flag requires authentication."""
    response = client.post(
        "/api/operator/review/test_rec/flag",
        json={"flag_reason": "test", "notes": "test"}
    )
    assert response.status_code == 401


# ===== Test Batch Approval =====

def test_batch_approve_success(reviewer_headers, sample_flagged_rec):
    """Test batch approval of multiple recommendations (AC #10)."""
    # Use actual recommendation ID for testing
    response = client.post(
        "/api/operator/review/batch-approve",
        json={"recommendation_ids": [sample_flagged_rec]},
        headers=reviewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "approved" in data
    assert "failed" in data
    assert "failed_ids" in data
    assert "timestamp" in data


def test_batch_approve_requires_auth():
    """Test batch approve requires authentication."""
    response = client.post(
        "/api/operator/review/batch-approve",
        json={"recommendation_ids": ["rec1", "rec2"]}
    )
    assert response.status_code == 401


def test_batch_approve_requires_reviewer_role(viewer_headers):
    """Test batch approve requires reviewer role."""
    response = client.post(
        "/api/operator/review/batch-approve",
        json={"recommendation_ids": ["rec1"]},
        headers=viewer_headers
    )
    assert response.status_code == 403


# ===== Integration Tests =====

def test_full_workflow_flag_to_approve(reviewer_headers, sample_flagged_rec):
    """Test complete workflow: view → approve → verify."""
    # Step 1: View recommendation
    detail_response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=reviewer_headers
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["review_status"] == "pending"

    # Step 2: Approve recommendation
    approve_response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/approve",
        json={"notes": "Integration test approval"},
        headers=reviewer_headers
    )
    assert approve_response.status_code == 200

    # Step 3: Verify status changed
    verify_response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=reviewer_headers
    )
    assert verify_response.json()["review_status"] == "approved"


def test_full_workflow_flag_to_override(admin_headers, sample_flagged_rec):
    """Test complete workflow: view → override → verify."""
    # Step 1: View recommendation
    detail_response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=admin_headers
    )
    assert detail_response.status_code == 200

    # Step 2: Override recommendation
    override_response = client.post(
        f"/api/operator/review/{sample_flagged_rec}/override",
        json={
            "justification": "This recommendation fails our quality standards and should be blocked from delivery for policy compliance reasons."
        },
        headers=admin_headers
    )
    assert override_response.status_code == 200

    # Step 3: Verify status changed
    verify_response = client.get(
        f"/api/operator/review/{sample_flagged_rec}",
        headers=admin_headers
    )
    assert verify_response.json()["review_status"] == "overridden"
