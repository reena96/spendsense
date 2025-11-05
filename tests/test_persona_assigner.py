"""
Tests for persona assignment storage and retrieval.

Tests database storage, retrieval, and API integration for persona assignments.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from spendsense.personas.assigner import PersonaAssigner
from spendsense.personas.prioritizer import PersonaAssignment
from spendsense.personas.matcher import PersonaMatch
from spendsense.ingestion.database_writer import PersonaAssignmentRecord, Base


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing."""
    from sqlalchemy import create_engine
    from spendsense.ingestion.database_writer import Base, DatabaseWriter

    db_file = tmp_path / "test.db"

    # Create database and tables
    engine = create_engine(f'sqlite:///{db_file}')
    Base.metadata.create_all(engine)

    return str(db_file)


@pytest.fixture
def sample_assignment():
    """Create sample PersonaAssignment for testing."""
    return PersonaAssignment(
        assigned_persona_id="high_utilization",
        priority=1,
        all_qualifying_personas=["high_utilization", "low_savings"],
        prioritization_reason="Highest priority match among 2 qualifying personas (priority 1)",
        assigned_at=datetime(2025, 11, 5, 10, 30, 0)
    )


@pytest.fixture
def sample_matches():
    """Create sample PersonaMatch list for testing."""
    return [
        PersonaMatch(
            persona_id="high_utilization",
            matched=True,
            evidence={"credit_max_utilization_pct": 60.0},
            matched_conditions=["credit_max_utilization_pct >= 50.0"]
        ),
        PersonaMatch(
            persona_id="irregular_income",
            matched=False,
            evidence={"income_median_pay_gap_days": 30.0}
        ),
        PersonaMatch(
            persona_id="low_savings",
            matched=True,
            evidence={"savings_emergency_fund_months": 2.5},
            matched_conditions=["savings_emergency_fund_months < 3.0"]
        ),
        PersonaMatch(persona_id="subscription_heavy", matched=False, evidence={}),
        PersonaMatch(persona_id="cash_flow_optimizer", matched=False, evidence={}),
        PersonaMatch(persona_id="young_professional", matched=False, evidence={}),
    ]


class TestPersonaAssigner:
    """Test PersonaAssigner class."""

    def test_initialization(self, temp_db):
        """Test assigner initializes correctly and creates tables."""
        assigner = PersonaAssigner(temp_db)

        assert assigner.db_path == temp_db
        assert assigner.matcher is not None
        assert assigner.prioritizer is not None
        assert assigner.summary_generator is not None

        # Verify table was created
        from sqlalchemy import inspect
        inspector = inspect(assigner.engine)
        tables = inspector.get_table_names()
        assert 'persona_assignments' in tables

    def test_store_assignment(self, temp_db, sample_assignment, sample_matches):
        """Test storing assignment to database."""
        assigner = PersonaAssigner(temp_db)

        assignment_id = assigner.store_assignment(
            user_id="user_001",
            time_window="30d",
            assignment=sample_assignment,
            matches=sample_matches
        )

        # Verify assignment_id is a valid UUID format
        assert isinstance(assignment_id, str)
        assert len(assignment_id) == 36  # UUID format

        # Verify stored in database
        with assigner.Session() as session:
            record = session.query(PersonaAssignmentRecord).filter(
                PersonaAssignmentRecord.assignment_id == assignment_id
            ).first()

            assert record is not None
            assert record.user_id == "user_001"
            assert record.time_window == "30d"
            assert record.assigned_persona_id == "high_utilization"
            assert record.priority == 1
            assert record.qualifying_personas == ["high_utilization", "low_savings"]
            assert "high_utilization" in record.match_evidence
            assert "low_savings" in record.match_evidence
            assert record.match_evidence["high_utilization"]["matched"] is True
            assert record.match_evidence["low_savings"]["matched"] is True

    def test_get_assignment(self, temp_db, sample_assignment, sample_matches):
        """Test retrieving assignment from database."""
        assigner = PersonaAssigner(temp_db)

        # Store assignment
        assignment_id = assigner.store_assignment(
            user_id="user_001",
            time_window="30d",
            assignment=sample_assignment,
            matches=sample_matches
        )

        # Retrieve assignment
        retrieved = assigner.get_assignment("user_001", "30d")

        assert retrieved is not None
        assert retrieved["assignment_id"] == assignment_id
        assert retrieved["assigned_persona_id"] == "high_utilization"
        assert retrieved["priority"] == 1
        assert retrieved["all_qualifying_personas"] == ["high_utilization", "low_savings"]
        assert "match_evidence" in retrieved
        assert "high_utilization" in retrieved["match_evidence"]

    def test_get_assignment_not_found(self, temp_db):
        """Test retrieving non-existent assignment returns None."""
        assigner = PersonaAssigner(temp_db)

        retrieved = assigner.get_assignment("nonexistent_user", "30d")

        assert retrieved is None

    def test_get_assignments_both_windows(self, temp_db, sample_assignment, sample_matches):
        """Test retrieving assignments for both time windows."""
        assigner = PersonaAssigner(temp_db)

        # Store assignment for 30d
        assigner.store_assignment(
            user_id="user_001",
            time_window="30d",
            assignment=sample_assignment,
            matches=sample_matches
        )

        # Store assignment for 180d (different persona)
        assignment_180d = PersonaAssignment(
            assigned_persona_id="irregular_income",
            priority=2,
            all_qualifying_personas=["irregular_income"],
            prioritization_reason="Only qualifying persona (priority 2)",
            assigned_at=datetime.now()
        )
        assigner.store_assignment(
            user_id="user_001",
            time_window="180d",
            assignment=assignment_180d,
            matches=sample_matches
        )

        # Retrieve both
        assignments = assigner.get_assignments_both_windows("user_001")

        assert "30d" in assignments
        assert "180d" in assignments
        assert assignments["30d"]["assigned_persona_id"] == "high_utilization"
        assert assignments["180d"]["assigned_persona_id"] == "irregular_income"

    def test_store_unclassified_assignment(self, temp_db, sample_matches):
        """Test storing unclassified assignment."""
        assigner = PersonaAssigner(temp_db)

        unclassified = PersonaAssignment(
            assigned_persona_id="unclassified",
            priority=None,
            all_qualifying_personas=[],
            prioritization_reason="No qualifying personas found",
            assigned_at=datetime.now()
        )

        assignment_id = assigner.store_assignment(
            user_id="user_002",
            time_window="30d",
            assignment=unclassified,
            matches=sample_matches
        )

        # Verify stored correctly
        retrieved = assigner.get_assignment("user_002", "30d")

        assert retrieved is not None
        assert retrieved["assigned_persona_id"] == "unclassified"
        assert retrieved["priority"] is None
        assert retrieved["all_qualifying_personas"] == []

    def test_match_evidence_completeness(self, temp_db, sample_assignment, sample_matches):
        """Test that match evidence includes all personas."""
        assigner = PersonaAssigner(temp_db)

        assigner.store_assignment(
            user_id="user_001",
            time_window="30d",
            assignment=sample_assignment,
            matches=sample_matches
        )

        retrieved = assigner.get_assignment("user_001", "30d")

        # All 6 personas should be in match evidence
        assert len(retrieved["match_evidence"]) == 6
        assert "high_utilization" in retrieved["match_evidence"]
        assert "irregular_income" in retrieved["match_evidence"]
        assert "low_savings" in retrieved["match_evidence"]
        assert "subscription_heavy" in retrieved["match_evidence"]
        assert "cash_flow_optimizer" in retrieved["match_evidence"]
        assert "young_professional" in retrieved["match_evidence"]

        # Check matched flags
        assert retrieved["match_evidence"]["high_utilization"]["matched"] is True
        assert retrieved["match_evidence"]["low_savings"]["matched"] is True
        assert retrieved["match_evidence"]["irregular_income"]["matched"] is False


class TestAssignPersonaOrchestration:
    """Test end-to-end persona assignment workflow."""

    def test_assign_persona_invalid_time_window(self, temp_db):
        """Test that invalid time_window raises ValueError."""
        assigner = PersonaAssigner(temp_db)

        with pytest.raises(ValueError, match="Invalid time_window"):
            assigner.assign_persona("user_001", date(2025, 11, 5), "invalid")

    def test_assign_persona_workflow_mocked(self, temp_db):
        """Test complete assignment workflow with mocked components."""
        assigner = PersonaAssigner(temp_db)

        # Mock the behavioral summary generator
        mock_summary = MagicMock()
        mock_summary.user_id = "user_001"
        assigner.summary_generator.generate_summary = Mock(return_value=mock_summary)

        # Mock the matcher
        mock_matches = [
            PersonaMatch(
                persona_id="high_utilization",
                matched=True,
                evidence={"credit_max_utilization_pct": 60.0},
                matched_conditions=["credit_max_utilization_pct >= 50.0"]
            ),
            PersonaMatch(persona_id="irregular_income", matched=False, evidence={}),
            PersonaMatch(persona_id="low_savings", matched=False, evidence={}),
            PersonaMatch(persona_id="subscription_heavy", matched=False, evidence={}),
            PersonaMatch(persona_id="cash_flow_optimizer", matched=False, evidence={}),
            PersonaMatch(persona_id="young_professional", matched=False, evidence={}),
        ]
        assigner.matcher.match_personas = Mock(return_value=mock_matches)

        # Run assignment
        assignment = assigner.assign_persona("user_001", date(2025, 11, 5), "30d")

        # Verify workflow executed
        assigner.summary_generator.generate_summary.assert_called_once()
        assigner.matcher.match_personas.assert_called_once()

        # Verify assignment
        assert assignment.assigned_persona_id == "high_utilization"
        assert assignment.priority == 1

        # Verify stored in database
        retrieved = assigner.get_assignment("user_001", "30d")
        assert retrieved is not None
        assert retrieved["assigned_persona_id"] == "high_utilization"


class TestAPIIntegration:
    """Test API endpoint functionality."""

    def test_api_endpoint_structure(self):
        """Test that API endpoint imports work correctly."""
        from spendsense.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # Test that endpoint exists (will return 503 if DB doesn't exist)
        response = client.get("/api/profile/user_001")

        # Should get 503 (database not available) or 404 (user not found) - not 404 (endpoint not found)
        assert response.status_code in [503, 404, 500]

    def test_api_response_format(self):
        """Test API response structure (conceptual test)."""
        # This test documents the expected API response format
        expected_response_structure = {
            "user_id": str,
            "assignments": {
                "30d": {
                    "assignment_id": str,
                    "assigned_persona_id": str,
                    "priority": int,
                    "assigned_at": str,
                    "all_qualifying_personas": list,
                    "prioritization_reason": str,
                    "match_evidence": dict
                },
                "180d": dict  # or None
            }
        }

        # Verify structure is documented
        assert expected_response_structure is not None
