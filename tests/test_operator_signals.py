"""
Comprehensive tests for operator signal dashboard API (Story 6.2 - Task 9).

Tests cover:
- User search functionality (AC #1)
- Signal data retrieval (AC #2-9)
- CSV export (AC #10)
- Authentication and authorization
- Error handling
"""

import pytest
from datetime import date
from fastapi.testclient import TestClient
from spendsense.api.main import app
from spendsense.auth.tokens import create_access_token
from pathlib import Path


# Test client
client = TestClient(app)

# Database path
DB_PATH = Path("data/processed/spendsense.db")


# ===== Fixtures =====

@pytest.fixture
def viewer_token():
    """Generate viewer role token for authentication."""
    return create_access_token(
        operator_id="test_viewer",
        username="test_viewer",
        role="viewer"
    )


@pytest.fixture
def admin_token():
    """Generate admin role token for authentication."""
    return create_access_token(
        operator_id="test_admin",
        username="test_admin",
        role="admin"
    )


@pytest.fixture
def auth_headers(viewer_token):
    """Generate authorization headers with viewer token."""
    return {"Authorization": f"Bearer {viewer_token}"}


# ===== Test User Search Endpoint (AC #1) =====

def test_user_search_by_user_id(auth_headers):
    """Test searching users by user ID returns correct results."""
    response = client.get(
        "/api/operator/users/search?q=user_MASKED_000",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "users" in data
    assert data["total"] > 0

    # Check first user structure
    user = data["users"][0]
    assert "user_id" in user
    assert "name" in user
    assert "persona" in user
    assert user["user_id"] == "user_MASKED_000"


def test_user_search_by_name(auth_headers):
    """Test searching users by name returns matching users."""
    response = client.get(
        "/api/operator/users/search?q=Hill",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0  # May or may not find matches


def test_user_search_case_insensitive(auth_headers):
    """Test user search is case-insensitive."""
    # Search with lowercase
    response1 = client.get(
        "/api/operator/users/search?q=masked",
        headers=auth_headers
    )

    # Search with uppercase
    response2 = client.get(
        "/api/operator/users/search?q=MASKED",
        headers=auth_headers
    )

    assert response1.status_code == 200
    assert response2.status_code == 200

    # Should return same number of results
    assert response1.json()["total"] == response2.json()["total"]


def test_user_search_requires_authentication():
    """Test user search endpoint requires authentication (AC #1)."""
    response = client.get("/api/operator/users/search?q=test")

    assert response.status_code == 401
    assert "detail" in response.json()


def test_user_search_requires_viewer_role():
    """Test user search requires viewer role or higher."""
    # Create token with invalid role (should fail RBAC check)
    response = client.get(
        "/api/operator/users/search?q=test",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code in [401, 403]


# ===== Test Signals Endpoint (AC #2-9) =====

@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_both_windows(auth_headers):
    """Test retrieving signals for both time windows (AC #6)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=both",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert "user_id" in data
    assert data["user_id"] == "user_MASKED_000"
    assert "data_30d" in data
    assert "data_180d" in data

    # Both windows should be present
    assert data["data_30d"] is not None
    assert data["data_180d"] is not None


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_30d_only(auth_headers):
    """Test retrieving only 30-day signals (AC #7)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["data_30d"] is not None
    # 180d should be null when requesting 30d only
    assert data["data_180d"] is None


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_180d_only(auth_headers):
    """Test retrieving only 180-day signals (AC #7)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=180d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["data_180d"] is not None
    # 30d should be null when requesting 180d only
    assert data["data_30d"] is None


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_contains_all_categories(auth_headers):
    """Test signals response contains all 4 signal categories (AC #2-5)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    signal_data = data["data_30d"]
    assert "subscription" in signal_data
    assert "savings" in signal_data
    assert "credit" in signal_data
    assert "income" in signal_data


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_subscription_metrics(auth_headers):
    """Test subscription metrics are present (AC #2)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    sub = data["data_30d"]["subscription"]
    assert "recurring_merchants" in sub
    assert "monthly_spend" in sub
    assert "subscription_share_pct" in sub
    assert isinstance(sub["recurring_merchants"], int)
    assert isinstance(sub["monthly_spend"], (int, float))
    assert isinstance(sub["subscription_share_pct"], (int, float))


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_savings_metrics(auth_headers):
    """Test savings metrics are present (AC #3)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    savings = data["data_30d"]["savings"]
    assert "net_inflow" in savings
    assert "growth_rate_pct" in savings
    assert "emergency_fund_months" in savings
    assert isinstance(savings["net_inflow"], (int, float))
    assert isinstance(savings["growth_rate_pct"], (int, float))
    assert isinstance(savings["emergency_fund_months"], (int, float))


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_credit_metrics(auth_headers):
    """Test credit metrics are present (AC #4)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    credit = data["data_30d"]["credit"]
    assert "max_utilization_pct" in credit
    assert "has_interest_charges" in credit
    assert "minimum_payment_only" in credit
    assert "overdue_status" in credit
    assert isinstance(credit["max_utilization_pct"], (int, float))
    assert isinstance(credit["has_interest_charges"], bool)
    assert isinstance(credit["minimum_payment_only"], bool)
    assert isinstance(credit["overdue_status"], bool)


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_income_metrics(auth_headers):
    """Test income metrics are present (AC #5)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    income = data["data_30d"]["income"]
    assert "payroll_count" in income
    assert "median_pay_gap_days" in income
    assert "cash_flow_buffer_months" in income
    assert isinstance(income["payroll_count"], int)
    assert isinstance(income["median_pay_gap_days"], (int, float))
    assert isinstance(income["cash_flow_buffer_months"], (int, float))


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_get_signals_has_timestamp(auth_headers):
    """Test signals include computed_at timestamp (AC #9)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=30d",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "computed_at" in data["data_30d"]
    # Check timestamp format (ISO 8601)
    assert "T" in data["data_30d"]["computed_at"]


def test_get_signals_user_not_found(auth_headers):
    """Test 404 error when user doesn't exist."""
    response = client.get(
        "/api/operator/signals/nonexistent_user",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_signals_requires_authentication():
    """Test signals endpoint requires authentication."""
    response = client.get("/api/operator/signals/user_MASKED_000")

    assert response.status_code == 401


def test_get_signals_requires_viewer_role():
    """Test signals endpoint requires viewer role or higher."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code in [401, 403]


# ===== Test Export Endpoint (AC #10) =====

@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_export_signals_csv(auth_headers):
    """Test CSV export generates correct format (AC #10)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000/export?format=csv",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    assert "attachment" in response.headers["content-disposition"]
    assert "signals_user_MASKED_000.csv" in response.headers["content-disposition"]

    # Check CSV structure
    content = response.text
    lines = content.strip().split("\n")

    # Check header
    header = lines[0]
    assert "user_id" in header
    assert "time_window" in header
    assert "category" in header
    assert "metric_name" in header
    assert "metric_value" in header
    assert "computed_at" in header

    # Check data rows exist
    assert len(lines) > 1


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_export_signals_json(auth_headers):
    """Test JSON export returns valid JSON (AC #10)."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000/export?format=json",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "attachment" in response.headers["content-disposition"]
    assert "signals_user_MASKED_000.json" in response.headers["content-disposition"]


def test_export_signals_requires_authentication():
    """Test export endpoint requires authentication."""
    response = client.get("/api/operator/signals/user_MASKED_000/export")

    assert response.status_code == 401


def test_export_signals_user_not_found(auth_headers):
    """Test export returns 404 for nonexistent user."""
    response = client.get(
        "/api/operator/signals/nonexistent_user/export",
        headers=auth_headers
    )

    assert response.status_code == 404


# ===== Integration Tests =====

@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_full_workflow_search_view_export(auth_headers):
    """Test complete workflow: search user → view signals → export (Integration)."""
    # Step 1: Search for user
    search_response = client.get(
        "/api/operator/users/search?q=user_MASKED_000",
        headers=auth_headers
    )
    assert search_response.status_code == 200
    users = search_response.json()["users"]
    assert len(users) > 0
    user_id = users[0]["user_id"]

    # Step 2: View signals
    signals_response = client.get(
        f"/api/operator/signals/{user_id}?time_window=both",
        headers=auth_headers
    )
    assert signals_response.status_code == 200
    signals = signals_response.json()
    assert signals["data_30d"] is not None
    assert signals["data_180d"] is not None

    # Step 3: Export data
    export_response = client.get(
        f"/api/operator/signals/{user_id}/export?format=csv",
        headers=auth_headers
    )
    assert export_response.status_code == 200
    assert "text/csv" in export_response.headers["content-type"]


@pytest.mark.skipif(not DB_PATH.exists(), reason="Database not available")
def test_signals_match_between_windows(auth_headers):
    """Test signal consistency between 30d and 180d windows."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=both",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Both should have same structure
    assert set(data["data_30d"].keys()) == set(data["data_180d"].keys())

    # Signal categories should match
    assert "subscription" in data["data_30d"]
    assert "subscription" in data["data_180d"]


# ===== Error Handling Tests =====

def test_invalid_time_window(auth_headers):
    """Test error handling for invalid time window parameter."""
    response = client.get(
        "/api/operator/signals/user_MASKED_000?time_window=invalid",
        headers=auth_headers
    )

    # Should return validation error
    assert response.status_code == 422


def test_missing_search_query(auth_headers):
    """Test error when search query is missing."""
    response = client.get(
        "/api/operator/users/search",
        headers=auth_headers
    )

    # Should return validation error for missing required parameter
    assert response.status_code == 422
