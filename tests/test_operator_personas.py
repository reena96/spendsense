"""
Comprehensive tests for operator persona assignment API (Story 6.3 - Task 10).

Tests cover:
- Persona assignment retrieval (AC #1-7)
- Qualifying personas and match evidence (AC #3)
- Prioritization logic (AC #4)
- Persona change history (AC #8)
- Manual override capability (AC #9, #10)
- Authentication and authorization
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from spendsense.api.main import app
from spendsense.auth.tokens import create_access_token


# Test client
client = TestClient(app)


# ===== Fixtures =====

@pytest.fixture
def viewer_token():
    """Generate viewer role token."""
    return create_access_token(
        operator_id="test_viewer",
        username="test_viewer",
        role="viewer"
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
def viewer_headers(viewer_token):
    """Generate authorization headers with viewer token."""
    return {"Authorization": f"Bearer {viewer_token}"}


@pytest.fixture
def admin_headers(admin_token):
    """Generate authorization headers with admin token."""
    return {"Authorization": f"Bearer {admin_token}"}


# ===== Test Persona Definitions Endpoint =====

def test_get_persona_definitions(viewer_headers):
    """Test fetching persona definitions returns all 6 personas (AC #5)."""
    response = client.get(
        "/api/operator/personas/definitions",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return 6 personas
    assert len(data) == 6

    # Check structure of first persona
    first_persona = data[0]
    assert "persona_id" in first_persona
    assert "display_name" in first_persona
    assert "description" in first_persona
    assert "educational_focus" in first_persona
    assert "priority_rank" in first_persona
    assert "criteria" in first_persona

    # Personas should be sorted by priority rank
    ranks = [p["priority_rank"] for p in data]
    assert ranks == sorted(ranks)


def test_persona_definitions_requires_auth():
    """Test persona definitions endpoint requires authentication."""
    response = client.get("/api/operator/personas/definitions")
    assert response.status_code == 401


# ===== Test Get Persona Assignments Endpoint =====

def test_get_persona_assignments_success(viewer_headers):
    """Test fetching persona assignments returns complete data (AC #1, #2)."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "user_id" in data
    assert "user_name" in data
    assert "assignments" in data
    assert "change_history" in data

    # Should have assignments for time windows
    assignments = data["assignments"]
    assert "30d" in assignments or "180d" in assignments


def test_persona_assignment_has_qualifying_personas(viewer_headers):
    """Test assignment includes qualifying personas with match evidence (AC #3)."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Get an assignment
    assignment = data["assignments"].get("30d") or data["assignments"].get("180d")
    assert assignment is not None

    # Check qualifying personas
    assert "qualifying_personas" in assignment
    assert len(assignment["qualifying_personas"]) > 0

    # Check each qualifying persona has required fields
    for qp in assignment["qualifying_personas"]:
        assert "persona_id" in qp
        assert "persona_name" in qp
        assert "priority_rank" in qp
        assert "match_evidence" in qp


def test_persona_assignment_has_prioritization_reason(viewer_headers):
    """Test assignment includes prioritization logic explanation (AC #4)."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    assignment = data["assignments"].get("30d") or data["assignments"].get("180d")
    assert assignment is not None

    # Check prioritization reason exists
    assert "prioritization_reason" in assignment
    assert len(assignment["prioritization_reason"]) > 0


def test_persona_assignment_has_timestamp(viewer_headers):
    """Test assignment includes timestamp (AC #7)."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    assignment = data["assignments"].get("30d") or data["assignments"].get("180d")
    assert assignment is not None

    # Check timestamp exists and is valid ISO format
    assert "assigned_at" in assignment
    # Should be parseable as datetime
    datetime.fromisoformat(assignment["assigned_at"].replace("Z", "+00:00"))


def test_get_persona_assignments_user_not_found(viewer_headers):
    """Test 404 when user doesn't exist."""
    response = client.get(
        "/api/operator/personas/nonexistent_user",
        headers=viewer_headers
    )

    assert response.status_code == 404


def test_get_persona_assignments_requires_auth():
    """Test assignments endpoint requires authentication."""
    response = client.get("/api/operator/personas/user_MASKED_000")
    assert response.status_code == 401


# ===== Test Persona Change History Endpoint =====

def test_get_persona_history_success(viewer_headers):
    """Test fetching persona change history (AC #8)."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000/history",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return array of history items
    assert isinstance(data, list)

    # If history exists, check structure
    if len(data) > 0:
        item = data[0]
        assert "changed_at" in item
        assert "time_window" in item
        assert "previous_persona" in item
        assert "new_persona" in item
        assert "reason" in item
        assert "is_override" in item


def test_get_persona_history_with_limit(viewer_headers):
    """Test history endpoint respects limit parameter."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000/history?limit=3",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return at most 3 items
    assert len(data) <= 3


def test_get_persona_history_requires_auth():
    """Test history endpoint requires authentication."""
    response = client.get("/api/operator/personas/user_MASKED_000/history")
    assert response.status_code == 401


# ===== Test Persona Override Endpoint =====

def test_override_persona_success(admin_headers):
    """Test manual persona override by admin (AC #9, #10)."""
    override_data = {
        "new_persona_id": "subscription_heavy",
        "justification": "User has very high subscription spending that wasn't properly detected",
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/user_MASKED_000/override",
        json=override_data,
        headers=admin_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check response structure
    assert "assignment_id" in data
    assert "user_id" in data
    assert data["user_id"] == "user_MASKED_000"
    assert "old_persona" in data
    assert "new_persona" in data
    assert data["new_persona"] == "subscription_heavy"
    assert "operator_id" in data
    assert "justification" in data
    assert data["justification"] == override_data["justification"]


def test_override_persona_requires_admin(viewer_headers):
    """Test override requires admin role (AC #9)."""
    override_data = {
        "new_persona_id": "subscription_heavy",
        "justification": "Testing with viewer role - should fail",
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/user_MASKED_000/override",
        json=override_data,
        headers=viewer_headers
    )

    # Should be forbidden (viewer doesn't have admin role)
    assert response.status_code == 403


def test_override_persona_requires_justification(admin_headers):
    """Test override requires justification (AC #10)."""
    # Try with missing justification
    override_data = {
        "new_persona_id": "subscription_heavy",
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/user_MASKED_000/override",
        json=override_data,
        headers=admin_headers
    )

    # Should fail validation (missing required field)
    assert response.status_code == 422


def test_override_persona_justification_too_short(admin_headers):
    """Test override justification must be at least 20 characters (AC #10)."""
    override_data = {
        "new_persona_id": "subscription_heavy",
        "justification": "Too short",  # Less than 20 chars
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/user_MASKED_000/override",
        json=override_data,
        headers=admin_headers
    )

    # Should fail validation (justification too short)
    assert response.status_code == 422


def test_override_persona_invalid_persona_id(admin_headers):
    """Test override fails with invalid persona ID."""
    override_data = {
        "new_persona_id": "nonexistent_persona",
        "justification": "This should fail because persona doesn't exist",
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/user_MASKED_000/override",
        json=override_data,
        headers=admin_headers
    )

    # Should fail with 400 bad request
    assert response.status_code == 400


def test_override_persona_user_not_found(admin_headers):
    """Test override fails if user doesn't exist."""
    override_data = {
        "new_persona_id": "subscription_heavy",
        "justification": "Testing with nonexistent user - should fail",
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/nonexistent_user/override",
        json=override_data,
        headers=admin_headers
    )

    # Should fail with 404
    assert response.status_code == 404


def test_override_persona_requires_auth():
    """Test override endpoint requires authentication."""
    override_data = {
        "new_persona_id": "subscription_heavy",
        "justification": "No auth token provided - should fail",
        "time_window": "30d"
    }

    response = client.post(
        "/api/operator/personas/user_MASKED_000/override",
        json=override_data
    )

    assert response.status_code == 401


# ===== Integration Tests =====

def test_full_workflow_view_and_override(viewer_headers, admin_headers):
    """Test complete workflow: view assignment → override (admin) → verify change."""
    # Step 1: View current assignment
    response1 = client.get(
        "/api/operator/personas/user_MASKED_001",
        headers=viewer_headers
    )
    assert response1.status_code == 200
    original_data = response1.json()
    original_persona = original_data["assignments"].get("30d", {}).get("assigned_persona_id")

    # Step 2: Override persona (as admin)
    new_persona = "cash_flow_optimizer"  # Choose different persona
    if original_persona == new_persona:
        new_persona = "low_savings"

    override_response = client.post(
        "/api/operator/personas/user_MASKED_001/override",
        json={
            "new_persona_id": new_persona,
            "justification": "Testing complete workflow - override for testing purposes",
            "time_window": "30d"
        },
        headers=admin_headers
    )
    assert override_response.status_code == 200

    # Step 3: Verify assignment changed
    response2 = client.get(
        "/api/operator/personas/user_MASKED_001",
        headers=viewer_headers
    )
    assert response2.status_code == 200
    updated_data = response2.json()
    updated_persona = updated_data["assignments"]["30d"]["assigned_persona_id"]

    assert updated_persona == new_persona


def test_qualifying_personas_sorted_by_priority(viewer_headers):
    """Test qualifying personas are sorted by priority rank."""
    response = client.get(
        "/api/operator/personas/user_MASKED_000",
        headers=viewer_headers
    )

    assert response.status_code == 200
    data = response.json()

    assignment = data["assignments"].get("30d") or data["assignments"].get("180d")
    if assignment and len(assignment["qualifying_personas"]) > 1:
        ranks = [qp["priority_rank"] for qp in assignment["qualifying_personas"]]
        # Should be sorted ascending
        assert ranks == sorted(ranks)
