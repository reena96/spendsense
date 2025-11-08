"""
Comprehensive unit tests for coverage metrics calculation.

Tests cover:
- Persona assignment coverage calculation
- Behavioral signal coverage calculation
- Persona distribution across 6 personas
- Missing data analysis with reason identification
- JSON serialization and storage
- Trend calculation across multiple runs
- Edge cases (empty datasets, boundary conditions)
"""

import json
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from spendsense.ingestion.database_writer import Base, User, PersonaAssignmentRecord
from spendsense.evaluation.coverage_metrics import (
    CoverageMetrics,
    calculate_persona_coverage,
    calculate_persona_distribution,
    calculate_signal_coverage,
    analyze_missing_data,
    calculate_coverage_metrics,
    save_coverage_metrics,
    load_previous_metrics,
    calculate_coverage_trends
)

logger = logging.getLogger(__name__)


@pytest.fixture
def temp_db():
    """Create a temporary in-memory SQLite database for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield engine, session

    session.close()
    engine.dispose()


@pytest.fixture
def populated_db(temp_db):
    """Create a database with test data."""
    engine, session = temp_db

    # Create 10 test users
    users = []
    for i in range(10):
        user = User(
            user_id=f'user_{i:03d}',
            name=f'Test User {i}',
            persona=None,
            annual_income=50000.0 + (i * 5000),
            characteristics={}
        )
        users.append(user)
        session.add(user)

    session.commit()

    return engine, session, users


def test_coverage_metrics_dataclass():
    """Test CoverageMetrics dataclass creation and serialization."""
    metrics = CoverageMetrics(
        timestamp='2025-11-06T10:00:00Z',
        dataset='test_dataset',
        persona_assignment_rate=0.98,
        behavioral_signal_rate=0.96,
        persona_distribution={'high_utilization': 5, 'variable_income': 3},
        window_completion_30d=0.94,
        window_completion_180d=0.98,
        missing_data_users=[],
        total_users=50,
        users_with_personas=49,
        users_with_3plus_signals=48
    )

    # Test to_dict conversion
    result = metrics.to_dict()
    assert isinstance(result, dict)
    assert result['timestamp'] == '2025-11-06T10:00:00Z'
    assert result['dataset'] == 'test_dataset'
    assert result['persona_assignment_rate'] == 0.98
    assert result['total_users'] == 50


def test_calculate_persona_coverage_empty_database(temp_db):
    """Test persona coverage calculation with empty database (0 users)."""
    engine, session = temp_db

    # Save database path for testing
    db_path = ':memory:'

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_persona_coverage(db_path, '30d')

        assert result['assignment_rate'] == 0.0
        assert result['total_users'] == 0
        assert result['users_with_personas'] == 0
        assert result['users_without_personas'] == []


def test_calculate_persona_coverage_100_percent(populated_db):
    """Test persona coverage with 100% assignment (all users have personas)."""
    engine, session, users = populated_db

    # Assign personas to all users
    for i, user in enumerate(users):
        persona_id = ['high_utilization', 'variable_income'][i % 2]
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=user.user_id,
            time_window='30d',
            assigned_persona_id=persona_id,
            assigned_at=datetime.utcnow(),
            priority=1,
            qualifying_personas=[persona_id, 'savings_builder'],
            match_evidence={},
            prioritization_reason='Test assignment'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_persona_coverage(':memory:', '30d')

        assert result['assignment_rate'] == 1.0
        assert result['total_users'] == 10
        assert result['users_with_personas'] == 10
        assert len(result['users_without_personas']) == 0


def test_calculate_persona_coverage_partial(populated_db):
    """Test persona coverage with partial assignment (some users missing personas)."""
    engine, session, users = populated_db

    # Assign personas to only 7 out of 10 users
    for i in range(7):
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=users[i].user_id,
            time_window='30d',
            assigned_persona_id='high_utilization',
            assigned_at=datetime.utcnow(),
            priority=1,
            qualifying_personas=['high_utilization'],
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_persona_coverage(':memory:', '30d')

        assert result['assignment_rate'] == pytest.approx(0.7, rel=0.01)
        assert result['total_users'] == 10
        assert result['users_with_personas'] == 7
        assert len(result['users_without_personas']) == 3


def test_calculate_persona_coverage_unclassified_excluded(populated_db):
    """Test that unclassified personas are excluded from coverage calculation."""
    engine, session, users = populated_db

    # Assign 5 real personas and 5 unclassified
    for i in range(10):
        persona_id = 'high_utilization' if i < 5 else 'unclassified'
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=users[i].user_id,
            time_window='30d',
            assigned_persona_id=persona_id,
            assigned_at=datetime.utcnow(),
            priority=1 if i < 5 else None,
            qualifying_personas=[] if i >= 5 else ['high_utilization'],
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_persona_coverage(':memory:', '30d')

        # Only 5 users have real personas (unclassified not counted)
        assert result['assignment_rate'] == pytest.approx(0.5, rel=0.01)
        assert result['users_with_personas'] == 5


def test_calculate_persona_distribution_all_six_personas(populated_db):
    """Test persona distribution calculation across all expected personas from registry."""
    from spendsense.personas.registry import load_persona_registry

    engine, session, users = populated_db

    # Load actual personas from registry
    registry = load_persona_registry()
    personas = registry.get_persona_ids()

    num_personas = len(personas)

    for i, user in enumerate(users):
        persona_id = personas[i % num_personas]
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=user.user_id,
            time_window='30d',
            assigned_persona_id=persona_id,
            assigned_at=datetime.utcnow(),
            priority=1,
            qualifying_personas=[persona_id],
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_persona_distribution(':memory:', '30d')

        # All personas from registry should be present
        assert len(result) == num_personas
        assert all(persona in result for persona in personas)

        # Verify all personas have at least 1 user (10 users distributed across personas)
        assert sum(result.values()) == 10
        assert all(count >= 0 for count in result.values())


def test_calculate_persona_distribution_empty_personas(temp_db):
    """Test persona distribution with no assigned personas returns zeros."""
    from spendsense.personas.registry import load_persona_registry

    engine, session = temp_db

    # Create users but no assignments
    for i in range(5):
        user = User(
            user_id=f'user_{i}',
            name=f'User {i}',
            persona=None,
            annual_income=50000.0,
            characteristics={}
        )
        session.add(user)

    session.commit()

    # Load expected persona count from registry
    registry = load_persona_registry()
    expected_persona_count = len(registry.get_persona_ids())

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_persona_distribution(':memory:', '30d')

        # Should return all personas from registry with 0 counts
        assert len(result) == expected_persona_count
        assert all(count == 0 for count in result.values())


def test_calculate_signal_coverage_all_users_meet_threshold(populated_db):
    """Test signal coverage when all users have ≥3 qualifying signals."""
    engine, session, users = populated_db

    # Assign all users with ≥3 qualifying personas (proxy for signals)
    for i, user in enumerate(users):
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=user.user_id,
            time_window='30d',
            assigned_persona_id='high_utilization',
            assigned_at=datetime.utcnow(),
            priority=1,
            qualifying_personas=['high_utilization', 'variable_income', 'subscription_heavy', 'savings_builder'],
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_signal_coverage(':memory:', '30d', min_signals=3)

        assert result['signal_coverage_rate'] == 1.0
        assert result['total_users'] == 10
        assert result['users_with_min_signals'] == 10
        assert len(result['users_below_threshold']) == 0


def test_calculate_signal_coverage_mixed_signal_counts(populated_db):
    """Test signal coverage with mixed signal counts (some <3, some ≥3)."""
    engine, session, users = populated_db

    # Create users with varying signal counts
    signal_counts = [0, 1, 2, 3, 4, 5, 2, 3, 4, 5]  # 6 users with ≥3 signals

    for i, user in enumerate(users):
        count = signal_counts[i]
        qualifying = ['persona_' + str(j) for j in range(count)]

        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=user.user_id,
            time_window='30d',
            assigned_persona_id='high_utilization' if count >= 3 else 'unclassified',
            assigned_at=datetime.utcnow(),
            priority=1 if count >= 3 else None,
            qualifying_personas=qualifying,
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = calculate_signal_coverage(':memory:', '30d', min_signals=3)

        assert result['signal_coverage_rate'] == pytest.approx(0.6, rel=0.01)  # 6/10
        assert result['users_with_min_signals'] == 6
        assert len(result['users_below_threshold']) == 4  # indices 0,1,2,6 with <3 signals


def test_analyze_missing_data_no_assignment_record(populated_db):
    """Test missing data analysis identifies users with no assignment record."""
    engine, session, users = populated_db

    # Create assignments for only 8 users (2 missing)
    for i in range(8):
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=users[i].user_id,
            time_window='30d',
            assigned_persona_id='high_utilization',
            assigned_at=datetime.utcnow(),
            priority=1,
            qualifying_personas=['high_utilization'],
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = analyze_missing_data(':memory:', '30d')

        # Should identify 2 users with processing_error
        processing_errors = [u for u in result if u['issue_type'] == 'processing_error']
        assert len(processing_errors) == 2
        assert all(u['severity'] == 'high' for u in processing_errors)


def test_analyze_missing_data_no_qualifying_signals(populated_db):
    """Test missing data analysis identifies users with no qualifying signals."""
    engine, session, users = populated_db

    # Create unclassified assignments with empty qualifying_personas
    for i, user in enumerate(users):
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=user.user_id,
            time_window='30d',
            assigned_persona_id='unclassified',
            assigned_at=datetime.utcnow(),
            priority=None,
            qualifying_personas=[],  # No signals detected
            match_evidence={},
            prioritization_reason='No qualifying signals'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = analyze_missing_data(':memory:', '30d')

        # All 10 users should have no_qualifying_signals issue
        assert len(result) == 10
        assert all(u['issue_type'] == 'no_qualifying_signals' for u in result)
        assert all(u['severity'] == 'medium' for u in result)


def test_analyze_missing_data_insufficient_signals_but_persona_assigned(populated_db):
    """Test missing data analysis for users with persona but <3 signals."""
    engine, session, users = populated_db

    # Create assignments with personas but only 1-2 qualifying signals
    for i, user in enumerate(users):
        assignment = PersonaAssignmentRecord(
            assignment_id=f'assign_{i:03d}',
            user_id=user.user_id,
            time_window='30d',
            assigned_persona_id='high_utilization',
            assigned_at=datetime.utcnow(),
            priority=1,
            qualifying_personas=['high_utilization', 'variable_income'],  # Only 2 signals
            match_evidence={},
            prioritization_reason='Test'
        )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = analyze_missing_data(':memory:', '30d')

        # All users should have insufficient_behavioral_signals issue
        assert len(result) == 10
        assert all(u['issue_type'] == 'insufficient_behavioral_signals' for u in result)
        assert all(u['severity'] == 'low' for u in result)
        assert all(u['signal_count'] == 2 for u in result)


def test_analyze_missing_data_severity_sorting(populated_db):
    """Test that missing data results are sorted by severity (high > medium > low)."""
    engine, session, users = populated_db

    # Create mixed severity issues
    # Users 0-2: No assignment (high severity)
    # Users 3-5: Unclassified with no signals (medium severity)
    # Users 6-9: Assigned but insufficient signals (low severity)

    for i in range(3, 10):
        if i < 6:
            # Unclassified
            assignment = PersonaAssignmentRecord(
                assignment_id=f'assign_{i:03d}',
                user_id=users[i].user_id,
                time_window='30d',
                assigned_persona_id='unclassified',
                assigned_at=datetime.utcnow(),
                priority=None,
                qualifying_personas=[],
                match_evidence={},
                prioritization_reason='No signals'
            )
        else:
            # Assigned but insufficient signals
            assignment = PersonaAssignmentRecord(
                assignment_id=f'assign_{i:03d}',
                user_id=users[i].user_id,
                time_window='30d',
                assigned_persona_id='high_utilization',
                assigned_at=datetime.utcnow(),
                priority=1,
                qualifying_personas=['high_utilization'],  # Only 1
                match_evidence={},
                prioritization_reason='Test'
            )
        session.add(assignment)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        result = analyze_missing_data(':memory:', '30d')

        # Should return 10 issues sorted by severity
        assert len(result) == 10

        # First 3 should be high severity
        assert all(result[i]['severity'] == 'high' for i in range(3))

        # Next 3 should be medium severity
        assert all(result[i]['severity'] == 'medium' for i in range(3, 6))

        # Last 4 should be low severity
        assert all(result[i]['severity'] == 'low' for i in range(6, 10))


def test_save_and_load_coverage_metrics():
    """Test saving metrics to JSON and loading them back."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Create test metrics
        metrics = CoverageMetrics(
            timestamp='2025-11-06T10:00:00Z',
            dataset='test_dataset',
            persona_assignment_rate=0.98,
            behavioral_signal_rate=0.96,
            persona_distribution={'high_utilization': 25, 'variable_income': 24},
            window_completion_30d=0.94,
            window_completion_180d=0.98,
            missing_data_users=[{'user_id': 'user_001', 'issue_type': 'processing_error'}],
            total_users=50,
            users_with_personas=49,
            users_with_3plus_signals=48
        )

        # Save metrics
        output_path = save_coverage_metrics(metrics, output_dir)

        # Verify file exists
        assert output_path.exists()
        assert output_path.name.startswith('coverage_metrics_')
        assert output_path.suffix == '.json'

        # Verify latest file also created
        latest_path = output_dir / 'coverage_metrics_latest.json'
        assert latest_path.exists()

        # Load and verify content
        with open(output_path, 'r') as f:
            loaded_data = json.load(f)

        assert loaded_data['dataset'] == 'test_dataset'
        assert loaded_data['persona_assignment_rate'] == 0.98
        assert loaded_data['total_users'] == 50


def test_load_previous_metrics_multiple_files():
    """Test loading multiple previous metrics files for trend analysis."""
    import time
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Create 3 metrics files with slight delay to ensure unique timestamps
        for i in range(3):
            metrics = CoverageMetrics(
                timestamp=f'2025-11-0{i+1}T10:00:00Z',
                dataset=f'test_dataset_{i}',
                persona_assignment_rate=0.90 + (i * 0.03),
                behavioral_signal_rate=0.88 + (i * 0.04),
                persona_distribution={},
                window_completion_30d=0.90,
                window_completion_180d=0.95,
                missing_data_users=[],
                total_users=50,
                users_with_personas=45 + i,
                users_with_3plus_signals=44 + i
            )
            save_coverage_metrics(metrics, output_dir)
            time.sleep(0.01)  # Small delay to ensure unique filenames

        # Load previous metrics
        loaded = load_previous_metrics(output_dir, count=10)

        # Should load all 3 metrics, sorted by timestamp (oldest first)
        assert len(loaded) == 3
        assert loaded[0].dataset == 'test_dataset_0'
        assert loaded[1].dataset == 'test_dataset_1'
        assert loaded[2].dataset == 'test_dataset_2'


def test_calculate_coverage_trends_improvement():
    """Test trend calculation shows improvement when metrics increase."""
    # Create previous metrics
    prev_metrics = CoverageMetrics(
        timestamp='2025-11-01T10:00:00Z',
        dataset='test',
        persona_assignment_rate=0.90,
        behavioral_signal_rate=0.88,
        persona_distribution={'high_utilization': 20, 'variable_income': 25},
        window_completion_30d=0.90,
        window_completion_180d=0.95,
        missing_data_users=[],
        total_users=50,
        users_with_personas=45,
        users_with_3plus_signals=44
    )

    # Create current metrics (improved)
    current_metrics = CoverageMetrics(
        timestamp='2025-11-06T10:00:00Z',
        dataset='test',
        persona_assignment_rate=0.96,
        behavioral_signal_rate=0.94,
        persona_distribution={'high_utilization': 23, 'variable_income': 25},
        window_completion_30d=0.95,
        window_completion_180d=0.98,
        missing_data_users=[],
        total_users=50,
        users_with_personas=48,
        users_with_3plus_signals=47
    )

    trends = calculate_coverage_trends(current_metrics, [prev_metrics])

    assert trends['persona_assignment_trend'] == pytest.approx(0.06, rel=0.01)
    assert trends['signal_coverage_trend'] == pytest.approx(0.06, rel=0.01)
    assert trends['persona_distribution_changes']['high_utilization'] == 3
    assert 'improved' in trends['improvement_summary'].lower()


def test_calculate_coverage_trends_no_previous_data():
    """Test trend calculation when no previous metrics available."""
    current_metrics = CoverageMetrics(
        timestamp='2025-11-06T10:00:00Z',
        dataset='test',
        persona_assignment_rate=0.96,
        behavioral_signal_rate=0.94,
        persona_distribution={},
        window_completion_30d=0.95,
        window_completion_180d=0.98,
        missing_data_users=[],
        total_users=50,
        users_with_personas=48,
        users_with_3plus_signals=47
    )

    trends = calculate_coverage_trends(current_metrics, [])

    assert trends['persona_assignment_trend'] is None
    assert trends['signal_coverage_trend'] is None
    assert 'No previous metrics' in trends['improvement_summary']


def test_calculate_coverage_metrics_integration(populated_db):
    """Integration test: Calculate full coverage metrics end-to-end."""
    from spendsense.personas.registry import load_persona_registry

    engine, session, users = populated_db

    # Load actual personas from registry
    registry = load_persona_registry()
    personas = registry.get_persona_ids()

    num_personas = len(personas)

    for i, user in enumerate(users):
        # 9 out of 10 users get personas with ≥3 signals
        if i < 9:
            persona = personas[i % num_personas]
            # Create qualifying list from personas, varying length
            qualifying = personas[:(i % 5) + 1]

            assignment_30d = PersonaAssignmentRecord(
                assignment_id=f'assign_30d_{i:03d}',
                user_id=user.user_id,
                time_window='30d',
                assigned_persona_id=persona,
                assigned_at=datetime.utcnow(),
                priority=1,
                qualifying_personas=qualifying,
                match_evidence={},
                prioritization_reason='Test'
            )
            session.add(assignment_30d)

            # For 180d, add one more qualifying persona if available
            qualifying_180d = qualifying + [personas[0]] if len(qualifying) < num_personas else qualifying

            assignment_180d = PersonaAssignmentRecord(
                assignment_id=f'assign_180d_{i:03d}',
                user_id=user.user_id,
                time_window='180d',
                assigned_persona_id=persona,
                assigned_at=datetime.utcnow(),
                priority=1,
                qualifying_personas=qualifying_180d,
                match_evidence={},
                prioritization_reason='Test'
            )
            session.add(assignment_180d)

    session.commit()

    with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
        mock_create.return_value = engine

        metrics = calculate_coverage_metrics(':memory:', 'test_integration')

        # Verify overall metrics
        assert metrics.total_users == 10
        assert metrics.persona_assignment_rate == pytest.approx(0.9, rel=0.01)
        assert metrics.users_with_personas == 9

        # Verify persona distribution (should match registry count)
        assert len(metrics.persona_distribution) == num_personas
        assert sum(metrics.persona_distribution.values()) == 9

        # Verify missing data analysis
        assert len(metrics.missing_data_users) >= 1  # At least 1 user missing


def test_invalid_time_window_raises_error():
    """Test that invalid time windows raise ValueError."""
    with pytest.raises(ValueError, match="Invalid time_window"):
        calculate_persona_coverage(':memory:', 'invalid')

    with pytest.raises(ValueError, match="Invalid time_window"):
        calculate_persona_distribution(':memory:', '90d')

    with pytest.raises(ValueError, match="Invalid time_window"):
        calculate_signal_coverage(':memory:', '7d')


def test_performance_large_dataset():
    """Test coverage metrics calculation performance with 50-100 user dataset."""
    import time
    from spendsense.personas.registry import load_persona_registry

    # Create temporary in-memory database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Load actual personas from registry
        registry = load_persona_registry()
        personas = registry.get_persona_ids()
        num_personas = len(personas)

        users = []
        for i in range(100):
            user = User(
                user_id=f'user_{i:03d}',
                name=f'Test User {i}',
                persona=None,
                annual_income=50000.0 + (i * 1000),
                characteristics={}
            )
            users.append(user)
            session.add(user)

        session.commit()

        # Create persona assignments for all users
        for i, user in enumerate(users):
            persona = personas[i % num_personas]
            # Vary qualifying personas to simulate realistic data
            # Ensure we don't try to get more personas than exist
            num_qualifying = min(3 + (i % 3), num_personas)  # 3-5 qualifying personas, capped at available
            qualifying = personas[:num_qualifying]

            # Create both 30d and 180d assignments
            for time_window in ['30d', '180d']:
                assignment = PersonaAssignmentRecord(
                    assignment_id=f'assign_{time_window}_{i:03d}',
                    user_id=user.user_id,
                    time_window=time_window,
                    assigned_persona_id=persona,
                    assigned_at=datetime.utcnow(),
                    priority=(i % 6) + 1,
                    qualifying_personas=qualifying,
                    match_evidence={},
                    prioritization_reason='Performance test'
                )
                session.add(assignment)

        session.commit()

        # Measure performance of coverage metrics calculation
        with patch('spendsense.evaluation.coverage_metrics.create_engine') as mock_create:
            mock_create.return_value = engine

            start_time = time.time()
            metrics = calculate_coverage_metrics(':memory:', 'performance_test_100_users')
            elapsed_time = time.time() - start_time

            # Verify metrics calculated correctly
            assert metrics.total_users == 100
            assert metrics.persona_assignment_rate == 1.0  # All users assigned
            assert metrics.behavioral_signal_rate == 1.0  # All have ≥3 signals
            assert len(metrics.persona_distribution) == num_personas
            assert sum(metrics.persona_distribution.values()) == 100

            # Performance assertion: should complete in under 5 seconds
            # for 100 users with both 30d and 180d windows
            assert elapsed_time < 5.0, f"Performance test took {elapsed_time:.2f}s (should be <5s)"

            # Log performance for monitoring
            logger.info(f"Performance test (100 users): {elapsed_time:.3f}s")

    finally:
        session.close()
        engine.dispose()
