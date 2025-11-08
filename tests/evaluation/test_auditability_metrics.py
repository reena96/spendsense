"""
Unit tests for auditability and compliance metrics.

Epic 7 - Story 7.4: Auditability & Compliance Metrics

Tests cover:
- Decision trace verification (complete and incomplete)
- Consent compliance checking (opted-in and opted-out users)
- Guardrail compliance for eligibility and tone
- Disclaimer presence detection
- Audit log completeness analysis
- Compliance failure categorization
- Edge cases (100% compliant, 0% compliant, mixed scenarios)
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from spendsense.evaluation.auditability_metrics import (
    AuditabilityEvaluator,
    AuditabilityMetrics,
    ComplianceFailure,
    ComplianceSeverity,
    ComplianceStatus,
    DecisionTraceAnalysis,
    GuardrailComplianceReport,
    AuditLogAnalysis,
    RecommendationAgeStats,
    generate_compliance_report
)
from spendsense.ingestion.database_writer import AuditLog, User


class TestDecisionTraceVerification:
    """Tests for decision trace completeness verification (AC #1)."""

    def test_complete_decision_traces_100_percent(self):
        """Test with all recommendations having complete decision traces."""
        # Create mock database session
        mock_session = Mock()

        # Mock recommendation_generated events
        rec_event = Mock(spec=AuditLog)
        rec_event.recommendation_id = "rec_001"
        rec_event.user_id = "user_001"
        rec_event.event_type = "recommendation_generated"
        rec_event.timestamp = datetime.utcnow()

        # Mock user with consent
        mock_user = Mock(spec=User)
        mock_user.user_id = "user_001"
        mock_user.consent_status = "opted_in"

        # Mock all required events for batched queries
        consent_event = Mock(spec=AuditLog)
        consent_event.user_id = "user_001"
        consent_event.event_type = "consent_changed"
        consent_event.recommendation_id = None

        persona_event = Mock(spec=AuditLog)
        persona_event.user_id = "user_001"
        persona_event.event_type = "persona_assigned"
        persona_event.recommendation_id = None

        eligibility_event = Mock(spec=AuditLog)
        eligibility_event.recommendation_id = "rec_001"
        eligibility_event.user_id = "user_001"
        eligibility_event.event_type = "eligibility_checked"

        tone_event = Mock(spec=AuditLog)
        tone_event.recommendation_id = "rec_001"
        tone_event.user_id = "user_001"
        tone_event.event_type = "tone_validated"

        # Setup mock to handle different query patterns
        def mock_query_handler(*args):
            query_mock = Mock()

            def filter_handler(*filter_args):
                filter_mock = Mock()

                # First call returns rec_events
                if not hasattr(mock_query_handler, 'call_count'):
                    mock_query_handler.call_count = 0
                mock_query_handler.call_count += 1

                if mock_query_handler.call_count == 1:
                    # First query: recommendation_generated events
                    filter_mock.all.return_value = [rec_event]
                elif mock_query_handler.call_count == 2:
                    # Second query: users batch query
                    filter_mock.all.return_value = [mock_user]
                elif mock_query_handler.call_count == 3:
                    # Third query: audit events batch query
                    filter_mock.all.return_value = [consent_event, persona_event, eligibility_event, tone_event]
                else:
                    filter_mock.all.return_value = []

                return filter_mock

            query_mock.filter = filter_handler
            return query_mock

        mock_session.query = mock_query_handler

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        analysis = evaluator.verify_decision_traces()

        assert analysis.total_recommendations == 1
        assert analysis.complete_traces == 1
        assert analysis.incomplete_traces == 0
        assert analysis.completeness_rate == 100.0
        assert len(analysis.incomplete_recommendation_ids) == 0

    def test_no_recommendations_returns_100_percent(self):
        """Test that no recommendations equals 100% compliance."""
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        analysis = evaluator.verify_decision_traces()

        assert analysis.total_recommendations == 0
        assert analysis.complete_traces == 0
        assert analysis.incomplete_traces == 0
        assert analysis.completeness_rate == 100.0


class TestConsentCompliance:
    """Tests for consent compliance verification (AC #2) - CRITICAL."""

    def test_all_users_opted_in_100_percent(self):
        """Test 100% consent compliance with all opted-in users."""
        mock_session = Mock()

        # Mock recommendation event
        rec_event = Mock(spec=AuditLog)
        rec_event.recommendation_id = "rec_001"
        rec_event.user_id = "user_001"
        rec_event.event_type = "recommendation_generated"
        rec_event.timestamp = datetime.utcnow()

        mock_session.query.return_value.filter.return_value.all.return_value = [rec_event]

        # Mock opted-in user
        mock_user = Mock(spec=User)
        mock_user.user_id = "user_001"
        mock_user.consent_status = "opted_in"
        mock_user.consent_timestamp = datetime.utcnow() - timedelta(days=1)

        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_consent_compliance()

        assert report.compliance_rate == 100.0
        assert report.status == ComplianceStatus.PASS
        assert report.passed == 1
        assert report.failed == 0
        assert len(report.failures) == 0

    def test_consent_violation_opted_out_user(self):
        """Test CRITICAL violation when recommendation generated for opted-out user."""
        mock_session = Mock()

        # Mock recommendation event
        rec_event = Mock(spec=AuditLog)
        rec_event.recommendation_id = "rec_002"
        rec_event.user_id = "user_002"
        rec_event.event_type = "recommendation_generated"
        rec_event.timestamp = datetime.utcnow()

        mock_session.query.return_value.filter.return_value.all.return_value = [rec_event]

        # Mock opted-out user (CRITICAL VIOLATION)
        mock_user = Mock(spec=User)
        mock_user.user_id = "user_002"
        mock_user.consent_status = "opted_out"
        mock_user.consent_timestamp = None

        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_consent_compliance()

        assert report.compliance_rate == 0.0
        assert report.status == ComplianceStatus.FAIL
        assert report.passed == 0
        assert report.failed == 1
        assert len(report.failures) == 1
        assert report.failures[0].severity == ComplianceSeverity.CRITICAL
        assert report.failures[0].failure_type == "consent_violation"

    def test_consent_violation_before_timestamp(self):
        """Test violation when recommendation generated before consent timestamp."""
        mock_session = Mock()

        consent_time = datetime.utcnow()
        rec_time = consent_time - timedelta(hours=1)  # Before consent

        # Mock recommendation event BEFORE consent
        rec_event = Mock(spec=AuditLog)
        rec_event.recommendation_id = "rec_003"
        rec_event.user_id = "user_003"
        rec_event.event_type = "recommendation_generated"
        rec_event.timestamp = rec_time

        mock_session.query.return_value.filter.return_value.all.return_value = [rec_event]

        # Mock user with consent AFTER recommendation
        mock_user = Mock(spec=User)
        mock_user.user_id = "user_003"
        mock_user.consent_status = "opted_in"
        mock_user.consent_timestamp = consent_time  # After recommendation

        mock_session.query.return_value.filter.return_value.first.return_value = mock_user

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_consent_compliance()

        assert report.compliance_rate == 0.0
        assert report.status == ComplianceStatus.FAIL
        assert len(report.failures) == 1
        assert report.failures[0].severity == ComplianceSeverity.CRITICAL


class TestGuardrailCompliance:
    """Tests for eligibility and tone guardrail compliance (AC #3, #4)."""

    def test_eligibility_compliance_all_passed(self):
        """Test 100% eligibility compliance."""
        mock_session = Mock()

        # Mock eligibility_checked event that passed
        elig_event = Mock(spec=AuditLog)
        elig_event.recommendation_id = "rec_001"
        elig_event.user_id = "user_001"
        elig_event.event_type = "eligibility_checked"
        elig_event.timestamp = datetime.utcnow()
        elig_event.event_data = json.dumps({"passed": True, "failure_reasons": []})

        mock_session.query.return_value.filter.return_value.all.return_value = [elig_event]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_guardrail_compliance('eligibility')

        assert report.compliance_rate == 100.0
        assert report.status == ComplianceStatus.PASS
        assert report.passed == 1
        assert report.failed == 0
        assert len(report.failures) == 0

    def test_eligibility_violation(self):
        """Test eligibility failure flagged as HIGH severity."""
        mock_session = Mock()

        # Mock eligibility_checked event that failed
        elig_event = Mock(spec=AuditLog)
        elig_event.recommendation_id = "rec_002"
        elig_event.user_id = "user_002"
        elig_event.event_type = "eligibility_checked"
        elig_event.timestamp = datetime.utcnow()
        elig_event.event_data = json.dumps({
            "passed": False,
            "failure_reasons": ["User already has savings account", "Income below threshold"]
        })

        mock_session.query.return_value.filter.return_value.all.return_value = [elig_event]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_guardrail_compliance('eligibility')

        assert report.compliance_rate == 0.0
        assert report.status == ComplianceStatus.FAIL
        assert report.passed == 0
        assert report.failed == 1
        assert len(report.failures) == 1
        assert report.failures[0].severity == ComplianceSeverity.HIGH
        assert "User already has savings account" in report.failures[0].details

    def test_tone_compliance_all_passed(self):
        """Test 100% tone compliance."""
        mock_session = Mock()

        # Mock tone_validated event that passed
        tone_event = Mock(spec=AuditLog)
        tone_event.recommendation_id = "rec_001"
        tone_event.user_id = "user_001"
        tone_event.event_type = "tone_validated"
        tone_event.timestamp = datetime.utcnow()
        tone_event.event_data = json.dumps({"passed": True, "detected_violations": []})

        mock_session.query.return_value.filter.return_value.all.return_value = [tone_event]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_guardrail_compliance('tone')

        assert report.compliance_rate == 100.0
        assert report.status == ComplianceStatus.PASS

    def test_tone_violation(self):
        """Test tone failure flagged as MEDIUM severity."""
        mock_session = Mock()

        # Mock tone_validated event that failed
        tone_event = Mock(spec=AuditLog)
        tone_event.recommendation_id = "rec_003"
        tone_event.user_id = "user_003"
        tone_event.event_type = "tone_validated"
        tone_event.timestamp = datetime.utcnow()
        tone_event.event_data = json.dumps({
            "passed": False,
            "detected_violations": ["Shaming language detected", "Negative tone"]
        })

        mock_session.query.return_value.filter.return_value.all.return_value = [tone_event]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_guardrail_compliance('tone')

        assert report.compliance_rate == 0.0
        assert report.status == ComplianceStatus.FAIL
        assert len(report.failures) == 1
        assert report.failures[0].severity == ComplianceSeverity.MEDIUM


class TestDisclaimerPresence:
    """Tests for disclaimer presence verification (AC #5)."""

    def test_all_recommendations_have_disclaimer(self):
        """Test 100% disclaimer presence."""
        mock_session = Mock()

        # Mock recommendation with disclaimer
        rec_event = Mock(spec=AuditLog)
        rec_event.recommendation_id = "rec_001"
        rec_event.user_id = "user_001"
        rec_event.event_type = "recommendation_generated"
        rec_event.timestamp = datetime.utcnow()
        rec_event.event_data = json.dumps({
            "guardrail_results": {"disclaimer_present": True}
        })

        mock_session.query.return_value.filter.return_value.all.return_value = [rec_event]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_disclaimer_presence()

        assert report.compliance_rate == 100.0
        assert report.status == ComplianceStatus.PASS
        assert report.passed == 1
        assert report.failed == 0

    def test_missing_disclaimer_flagged(self):
        """Test missing disclaimer flagged as HIGH severity."""
        mock_session = Mock()

        # Mock recommendation without disclaimer
        rec_event = Mock(spec=AuditLog)
        rec_event.recommendation_id = "rec_002"
        rec_event.user_id = "user_002"
        rec_event.event_type = "recommendation_generated"
        rec_event.timestamp = datetime.utcnow()
        rec_event.event_data = json.dumps({
            "guardrail_results": {"disclaimer_present": False}
        })

        mock_session.query.return_value.filter.return_value.all.return_value = [rec_event]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        report = evaluator.check_disclaimer_presence()

        assert report.compliance_rate == 0.0
        assert report.status == ComplianceStatus.FAIL
        assert len(report.failures) == 1
        assert report.failures[0].severity == ComplianceSeverity.HIGH
        assert report.failures[0].failure_type == "missing_disclaimer"


class TestAuditLogCompleteness:
    """Tests for audit log completeness analysis (AC #6)."""

    def test_all_required_event_types_present(self):
        """Test audit log with all required event types."""
        mock_session = Mock()

        # Mock total event count with timestamps
        mock_events = [Mock(timestamp=datetime.utcnow() - timedelta(days=i)) for i in range(100)]
        mock_session.query.return_value.all.return_value = mock_events

        # Mock all required event types present
        required_types = [
            'consent_changed',
            'persona_assigned',
            'recommendation_generated',
            'eligibility_checked',
            'tone_validated',
            'operator_action'
        ]
        mock_session.query.return_value.distinct.return_value.all.return_value = [
            (event_type,) for event_type in required_types
        ]

        # Mock event counts
        mock_session.query.return_value.filter.return_value.count.return_value = 10

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        analysis = evaluator.analyze_audit_log_completeness()

        assert analysis.completeness_score == 100.0
        assert len(analysis.missing_event_types) == 0
        assert set(analysis.present_event_types) == set(required_types)

    def test_missing_event_types_detected(self):
        """Test detection of missing required event types."""
        mock_session = Mock()

        # Mock events with timestamps
        mock_events = [Mock(timestamp=datetime.utcnow() - timedelta(days=i)) for i in range(50)]
        mock_session.query.return_value.all.return_value = mock_events

        # Mock only some event types present
        present_types = ['consent_changed', 'recommendation_generated']
        mock_session.query.return_value.distinct.return_value.all.return_value = [
            (event_type,) for event_type in present_types
        ]

        mock_session.query.return_value.filter.return_value.count.return_value = 5

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        analysis = evaluator.analyze_audit_log_completeness()

        assert analysis.completeness_score < 100.0
        assert len(analysis.missing_event_types) > 0
        assert 'persona_assigned' in analysis.missing_event_types
        assert 'eligibility_checked' in analysis.missing_event_types


class TestRecommendationAgeTracking:
    """Tests for recommendation age tracking (AC #9)."""

    def test_recommendation_age_calculation(self):
        """Test recommendation age statistics."""
        mock_session = Mock()

        # Mock recent recommendation (1 day old)
        recent_time = datetime.utcnow() - timedelta(days=1)
        rec1 = Mock(spec=AuditLog)
        rec1.recommendation_id = "rec_001"
        rec1.user_id = "user_001"
        rec1.event_type = "recommendation_generated"
        rec1.timestamp = recent_time

        # Mock old recommendation (35 days old - stale)
        stale_time = datetime.utcnow() - timedelta(days=35)
        rec2 = Mock(spec=AuditLog)
        rec2.recommendation_id = "rec_002"
        rec2.user_id = "user_002"
        rec2.event_type = "recommendation_generated"
        rec2.timestamp = stale_time

        mock_session.query.return_value.filter.return_value.all.return_value = [rec1, rec2]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        stats = evaluator.track_recommendation_ages()

        assert stats.total_recommendations == 2
        assert stats.average_age_hours > 0
        assert len(stats.stale_recommendations) == 1  # rec_002 is >30 days
        assert stats.stale_recommendations[0]["recommendation_id"] == "rec_002"

    def test_no_stale_recommendations(self):
        """Test when all recommendations are fresh (<30 days)."""
        mock_session = Mock()

        # Mock recent recommendation
        recent_time = datetime.utcnow() - timedelta(days=5)
        rec = Mock(spec=AuditLog)
        rec.recommendation_id = "rec_001"
        rec.user_id = "user_001"
        rec.event_type = "recommendation_generated"
        rec.timestamp = recent_time

        mock_session.query.return_value.filter.return_value.all.return_value = [rec]

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        stats = evaluator.track_recommendation_ages()

        assert stats.total_recommendations == 1
        assert len(stats.stale_recommendations) == 0


class TestDataRetentionCompliance:
    """Tests for data retention compliance (AC #10)."""

    def test_compliant_data_retention(self):
        """Test compliant data retention status."""
        mock_session = Mock()

        # Mock audit log with valid events
        mock_session.query.return_value.scalar.return_value = datetime.utcnow() - timedelta(days=30)
        mock_session.query.return_value.order_by.return_value.all.return_value = [
            Mock(timestamp=datetime.utcnow() - timedelta(days=i)) for i in range(30)
        ]

        # Mock all events have required fields
        mock_session.query.return_value.count.return_value = 30
        mock_session.query.return_value.filter.return_value.count.return_value = 30

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        status = evaluator.verify_data_retention()

        assert "COMPLIANT" in status

    def test_data_retention_with_gaps(self):
        """Test data retention with gaps in audit log."""
        mock_session = Mock()

        mock_session.query.return_value.scalar.return_value = datetime.utcnow() - timedelta(days=60)

        # Mock events with large gap
        events = [
            Mock(timestamp=datetime.utcnow() - timedelta(days=60)),
            Mock(timestamp=datetime.utcnow() - timedelta(days=10))  # 50-day gap
        ]
        mock_session.query.return_value.order_by.return_value.all.return_value = events

        mock_session.query.return_value.count.return_value = 2
        mock_session.query.return_value.filter.return_value.count.return_value = 2

        evaluator = AuditabilityEvaluator(db_session=mock_session)
        status = evaluator.verify_data_retention()

        assert "WARNING" in status or "gap" in status.lower()


class TestComplianceReportGeneration:
    """Tests for compliance report generation (AC #8)."""

    def test_generate_compliance_report_structure(self):
        """Test compliance report has correct structure."""
        # Create sample metrics
        metrics = AuditabilityMetrics(
            decision_trace_completeness=100.0,
            consent_compliance_rate=100.0,
            eligibility_compliance_rate=95.0,
            tone_compliance_rate=98.0,
            disclaimer_presence_rate=100.0,
            audit_log_completeness=100.0,
            compliance_failures=[],
            recommendation_ages=RecommendationAgeStats(
                total_recommendations=10,
                average_age_hours=48.0,
                oldest_recommendation_id="rec_001",
                oldest_age_hours=120.0,
                stale_recommendations=[],
                age_distribution={"0-24h": 5, "1-7d": 5, "7-30d": 0, ">30d": 0}
            ),
            data_retention_status="COMPLIANT",
            timestamp=datetime.utcnow(),
            overall_compliance_score=98.5,
            critical_issues_count=0
        )

        report = generate_compliance_report(metrics)

        assert "overall_compliance_score" in report
        assert "guardrail_status" in report
        assert "consent_compliance" in report["guardrail_status"]
        assert "eligibility_compliance" in report["guardrail_status"]
        assert "tone_compliance" in report["guardrail_status"]
        assert "disclaimer_presence" in report["guardrail_status"]
        assert "violations_by_severity" in report
        assert "recommendations_for_remediation" in report

    def test_compliance_report_with_critical_violations(self):
        """Test report generation with critical consent violations."""
        failure = ComplianceFailure(
            recommendation_id="rec_001",
            user_id="user_001",
            failure_type="consent_violation",
            severity=ComplianceSeverity.CRITICAL,
            details="User opted out",
            timestamp=datetime.utcnow().isoformat()
        )

        metrics = AuditabilityMetrics(
            decision_trace_completeness=100.0,
            consent_compliance_rate=0.0,  # CRITICAL FAILURE
            eligibility_compliance_rate=100.0,
            tone_compliance_rate=100.0,
            disclaimer_presence_rate=100.0,
            audit_log_completeness=100.0,
            compliance_failures=[failure],
            recommendation_ages=RecommendationAgeStats(
                total_recommendations=1,
                average_age_hours=24.0,
                oldest_recommendation_id="rec_001",
                oldest_age_hours=24.0,
                stale_recommendations=[],
                age_distribution={"0-24h": 1, "1-7d": 0, "7-30d": 0, ">30d": 0}
            ),
            data_retention_status="COMPLIANT",
            timestamp=datetime.utcnow(),
            overall_compliance_score=30.0,  # Low due to consent failure
            critical_issues_count=1
        )

        report = generate_compliance_report(metrics)

        assert report["overall_status"] == "FAIL"
        assert report["critical_issues_count"] == 1
        assert report["violations_by_severity"]["CRITICAL"] == 1
        assert any("consent" in rec.lower() for rec in report["recommendations_for_remediation"])


class TestEdgeCases:
    """Tests for edge cases."""


# ===== INTEGRATION TESTS WITH REAL DATABASE =====

@pytest.fixture
def test_db_with_audit_data():
    """
    Create test SQLite database with sample audit data.

    Creates an in-memory SQLite database populated with:
    - Test users with consent_status
    - Test audit log events (consent, persona, eligibility, tone, recommendations)
    - Test recommendations

    Yields:
        SQLAlchemy Session connected to test database
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from spendsense.ingestion.database_writer import Base, User, AuditLog

    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Insert test users with consent
        user1 = User(
            user_id="test_user_001",
            name="Test User 1",
            persona="young_professional",
            annual_income=75000.0,
            characteristics={"age": 28, "location": "urban"},
            consent_status="opted_in",
            consent_timestamp=datetime.utcnow() - timedelta(days=10),
            consent_version="1.0"
        )
        user2 = User(
            user_id="test_user_002",
            name="Test User 2",
            persona="budget_conscious",
            annual_income=45000.0,
            characteristics={"age": 35, "location": "suburban"},
            consent_status="opted_in",
            consent_timestamp=datetime.utcnow() - timedelta(days=20),
            consent_version="1.0"
        )
        session.add(user1)
        session.add(user2)
        session.commit()

        # Insert audit log events for complete decision trace
        base_time = datetime.utcnow() - timedelta(days=1)

        # User 1: Complete trace with passing guardrails
        events_user1 = [
            # Consent event
            AuditLog(
                log_id="evt_consent_001",
                user_id="test_user_001",
                event_type="consent_changed",
                timestamp=base_time - timedelta(days=10),
                event_data=json.dumps({
                    "new_status": "opted_in",
                    "consent_version": "1.0"
                }),
                recommendation_id=None
            ),
            # Persona assignment
            AuditLog(
                log_id="evt_persona_001",
                user_id="test_user_001",
                event_type="persona_assigned",
                timestamp=base_time - timedelta(hours=2),
                event_data=json.dumps({
                    "persona": "young_professional",
                    "confidence": 0.95
                }),
                recommendation_id=None
            ),
            # Eligibility check - PASSING
            AuditLog(
                log_id="evt_elig_001",
                user_id="test_user_001",
                event_type="eligibility_checked",
                timestamp=base_time - timedelta(hours=1),
                event_data=json.dumps({
                    "passed": True,
                    "failure_reasons": []
                }),
                recommendation_id="rec_test_001"
            ),
            # Tone validation - PASSING
            AuditLog(
                log_id="evt_tone_001",
                user_id="test_user_001",
                event_type="tone_validated",
                timestamp=base_time - timedelta(minutes=30),
                event_data=json.dumps({
                    "passed": True,
                    "detected_violations": []
                }),
                recommendation_id="rec_test_001"
            ),
            # Recommendation generated - WITH DISCLAIMER
            AuditLog(
                log_id="evt_rec_001",
                user_id="test_user_001",
                event_type="recommendation_generated",
                timestamp=base_time,
                event_data=json.dumps({
                    "content_id": "edu_001",
                    "content_title": "Emergency Fund Guide",
                    "guardrail_results": {
                        "disclaimer_present": True,
                        "eligibility_passed": True,
                        "tone_passed": True
                    }
                }),
                recommendation_id="rec_test_001"
            )
        ]

        # User 2: Incomplete trace with failing guardrails
        events_user2 = [
            # Consent event
            AuditLog(
                log_id="evt_consent_002",
                user_id="test_user_002",
                event_type="consent_changed",
                timestamp=base_time - timedelta(days=20),
                event_data=json.dumps({
                    "new_status": "opted_in",
                    "consent_version": "1.0"
                }),
                recommendation_id=None
            ),
            # Eligibility check - FAILING
            AuditLog(
                log_id="evt_elig_002",
                user_id="test_user_002",
                event_type="eligibility_checked",
                timestamp=base_time - timedelta(hours=1),
                event_data=json.dumps({
                    "passed": False,
                    "failure_reasons": ["User already has recommended product"]
                }),
                recommendation_id="rec_test_002"
            ),
            # Tone validation - FAILING
            AuditLog(
                log_id="evt_tone_002",
                user_id="test_user_002",
                event_type="tone_validated",
                timestamp=base_time - timedelta(minutes=30),
                event_data=json.dumps({
                    "passed": False,
                    "detected_violations": ["Shaming language detected"]
                }),
                recommendation_id="rec_test_002"
            ),
            # Recommendation generated - MISSING DISCLAIMER
            AuditLog(
                log_id="evt_rec_002",
                user_id="test_user_002",
                event_type="recommendation_generated",
                timestamp=base_time,
                event_data=json.dumps({
                    "content_id": "edu_002",
                    "content_title": "Budget Tips",
                    "guardrail_results": {
                        "disclaimer_present": False,  # VIOLATION
                        "eligibility_passed": False,
                        "tone_passed": False
                    }
                }),
                recommendation_id="rec_test_002"
            )
        ]

        # Add operator action event for audit log completeness
        operator_event = AuditLog(
            log_id="evt_op_001",
            user_id=None,
            event_type="operator_action",
            timestamp=base_time - timedelta(hours=12),
            event_data=json.dumps({
                "action": "review_flagged_recommendation",
                "operator_id": "op_001"
            }),
            recommendation_id=None
        )

        for event in events_user1 + events_user2 + [operator_event]:
            session.add(event)

        session.commit()

        yield session

    finally:
        session.close()
        engine.dispose()


class TestIntegrationWithRealDatabase:
    """Integration tests with real SQLite database (Enhancement #1)."""

    def test_evaluate_all_integration(self, test_db_with_audit_data):
        """
        Integration test #1: End-to-end evaluate_all() with real database.

        Tests the complete evaluation workflow using a real SQLite database
        with sample audit data. Verifies:
        - All metrics are calculated correctly
        - Metrics structure is valid
        - Compliance scoring works end-to-end
        - Database queries execute successfully
        """
        evaluator = AuditabilityEvaluator(db_session=test_db_with_audit_data)
        metrics = evaluator.evaluate_all()

        # Verify metrics structure
        assert metrics is not None
        assert isinstance(metrics, AuditabilityMetrics)

        # Verify overall compliance score
        assert metrics.overall_compliance_score >= 0.0
        assert metrics.overall_compliance_score <= 100.0

        # Verify consent compliance (should be 100% - both users opted in)
        assert metrics.consent_compliance_rate is not None
        assert metrics.consent_compliance_rate == 100.0

        # Verify eligibility compliance (should be 50% - one pass, one fail)
        assert metrics.eligibility_compliance_rate is not None
        assert metrics.eligibility_compliance_rate == 50.0

        # Verify tone compliance (should be 50% - one pass, one fail)
        assert metrics.tone_compliance_rate is not None
        assert metrics.tone_compliance_rate == 50.0

        # Verify disclaimer presence (should be 50% - one present, one missing)
        assert metrics.disclaimer_presence_rate is not None
        assert metrics.disclaimer_presence_rate == 50.0

        # Verify decision trace completeness (should be 50% - user1 complete, user2 incomplete)
        assert metrics.decision_trace_completeness is not None
        assert metrics.decision_trace_completeness == 50.0

        # Verify audit log completeness (should be 100% - all required event types present)
        assert metrics.audit_log_completeness is not None
        assert metrics.audit_log_completeness == 100.0

        # Verify compliance failures are captured
        assert metrics.compliance_failures is not None
        assert len(metrics.compliance_failures) > 0

        # Verify recommendation ages
        assert metrics.recommendation_ages is not None
        assert metrics.recommendation_ages.total_recommendations == 2

        # Verify data retention status
        assert metrics.data_retention_status is not None
        assert isinstance(metrics.data_retention_status, str)

        # Verify timestamp
        assert metrics.timestamp is not None
        assert isinstance(metrics.timestamp, datetime)

        # Verify metrics can be serialized to dict
        metrics_dict = metrics.to_dict()
        assert isinstance(metrics_dict, dict)
        assert "overall_compliance_score" in metrics_dict
        assert "consent_compliance_rate" in metrics_dict
        assert "compliance_failures" in metrics_dict

    def test_event_data_json_parsing_integration(self, test_db_with_audit_data):
        """
        Integration test #2: Real event_data JSON parsing from database.

        Tests that actual JSON structures from the audit log are parsed correctly.
        Verifies:
        - eligibility_checked event parsing
        - tone_validated event parsing
        - recommendation_generated event parsing
        - Guardrail results extraction
        """
        evaluator = AuditabilityEvaluator(db_session=test_db_with_audit_data)

        # Test eligibility event parsing
        eligibility_report = evaluator.check_guardrail_compliance('eligibility')
        assert eligibility_report is not None
        assert eligibility_report.total_checked == 2
        assert eligibility_report.passed == 1
        assert eligibility_report.failed == 1

        # Verify failure details are parsed from JSON
        elig_failures = [f for f in eligibility_report.failures if f.failure_type == "eligibility_violation"]
        assert len(elig_failures) == 1
        assert "User already has recommended product" in elig_failures[0].details

        # Test tone event parsing
        tone_report = evaluator.check_guardrail_compliance('tone')
        assert tone_report is not None
        assert tone_report.total_checked == 2
        assert tone_report.passed == 1
        assert tone_report.failed == 1

        # Verify tone violation details are parsed from JSON
        tone_failures = [f for f in tone_report.failures if f.failure_type == "tone_violation"]
        assert len(tone_failures) == 1
        assert "Shaming language detected" in tone_failures[0].details

        # Test recommendation event parsing for disclaimer
        disclaimer_report = evaluator.check_disclaimer_presence()
        assert disclaimer_report is not None
        assert disclaimer_report.total_checked == 2
        assert disclaimer_report.passed == 1
        assert disclaimer_report.failed == 1

        # Verify disclaimer missing is detected from JSON
        disclaimer_failures = [f for f in disclaimer_report.failures if f.failure_type == "missing_disclaimer"]
        assert len(disclaimer_failures) == 1
        assert disclaimer_failures[0].recommendation_id == "rec_test_002"

        # Test consent compliance parsing
        consent_report = evaluator.check_consent_compliance()
        assert consent_report is not None
        assert consent_report.total_checked == 2
        assert consent_report.passed == 2  # Both users opted in
        assert consent_report.failed == 0

        # Test decision trace parsing
        trace_analysis = evaluator.verify_decision_traces()
        assert trace_analysis is not None
        assert trace_analysis.total_recommendations == 2
        assert trace_analysis.complete_traces == 1  # Only user1 has complete trace
        assert trace_analysis.incomplete_traces == 1  # user2 missing persona_assigned


class TestMetricsDataclasses:
    """Tests for metrics dataclass serialization."""

    def test_auditability_metrics_to_dict(self):
        """Test AuditabilityMetrics serialization to dictionary."""
        metrics = AuditabilityMetrics(
            decision_trace_completeness=95.0,
            consent_compliance_rate=100.0,
            eligibility_compliance_rate=90.0,
            tone_compliance_rate=98.0,
            disclaimer_presence_rate=100.0,
            audit_log_completeness=100.0,
            compliance_failures=[],
            recommendation_ages=RecommendationAgeStats(
                total_recommendations=5,
                average_age_hours=24.0,
                oldest_recommendation_id="rec_001",
                oldest_age_hours=48.0,
                stale_recommendations=[],
                age_distribution={"0-24h": 3, "1-7d": 2, "7-30d": 0, ">30d": 0}
            ),
            data_retention_status="COMPLIANT",
            timestamp=datetime.utcnow(),
            overall_compliance_score=96.5,
            critical_issues_count=0
        )

        result = metrics.to_dict()

        assert isinstance(result, dict)
        assert result["decision_trace_completeness"] == 95.0
        assert result["consent_compliance_rate"] == 100.0
        assert result["overall_compliance_score"] == 96.5
        assert "recommendation_ages" in result
        assert "compliance_failures" in result

    def test_compliance_failure_serialization(self):
        """Test ComplianceFailure can be serialized."""
        failure = ComplianceFailure(
            recommendation_id="rec_001",
            user_id="user_001",
            failure_type="tone_violation",
            severity=ComplianceSeverity.MEDIUM,
            details="Negative tone detected",
            timestamp=datetime.utcnow().isoformat(),
            event_type="tone_validated",
            missing_elements=["empowering_language"]
        )

        # Verify all fields are accessible
        assert failure.recommendation_id == "rec_001"
        assert failure.severity == ComplianceSeverity.MEDIUM
        assert failure.failure_type == "tone_violation"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
