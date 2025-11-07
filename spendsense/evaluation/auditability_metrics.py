"""
Auditability and Compliance Metrics Module for Epic 7 Story 7.4.

This module provides comprehensive compliance verification including:
- Decision trace completeness (100% target)
- Consent compliance (0% violations - CRITICAL)
- Eligibility compliance verification
- Tone compliance verification
- Disclaimer presence verification (100% target)
- Audit log completeness analysis
- Compliance failure categorization and reporting

Integrates with Epic 5 guardrails and Epic 6 audit trail systems.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from spendsense.config.database import get_db_session
from spendsense.ingestion.database_writer import AuditLog, User, FlaggedRecommendation


class ComplianceSeverity(str, Enum):
    """Severity levels for compliance violations."""
    CRITICAL = "CRITICAL"  # Consent violations
    HIGH = "HIGH"  # Eligibility issues, missing disclaimers
    MEDIUM = "MEDIUM"  # Tone problems, incomplete decision traces
    LOW = "LOW"  # Minor issues


class ComplianceStatus(str, Enum):
    """Compliance status values."""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


@dataclass
class ComplianceFailure:
    """Individual compliance failure record."""
    recommendation_id: Optional[str]
    user_id: Optional[str]
    failure_type: str
    severity: ComplianceSeverity
    details: str
    timestamp: str
    event_type: Optional[str] = None
    missing_elements: Optional[List[str]] = None


@dataclass
class DecisionTraceAnalysis:
    """Analysis of decision trace completeness."""
    total_recommendations: int
    complete_traces: int
    incomplete_traces: int
    completeness_rate: float
    missing_steps: Dict[str, int]  # Step name -> count of missing
    incomplete_recommendation_ids: List[str]


@dataclass
class GuardrailComplianceReport:
    """Compliance report for a specific guardrail."""
    guardrail_type: str
    total_checked: int
    passed: int
    failed: int
    compliance_rate: float
    status: ComplianceStatus
    failures: List[ComplianceFailure]


@dataclass
class AuditLogAnalysis:
    """Analysis of audit log completeness."""
    total_events: int
    required_event_types: List[str]
    present_event_types: List[str]
    missing_event_types: List[str]
    completeness_score: float
    gaps_detected: List[Dict[str, Any]]
    event_type_counts: Dict[str, int]


@dataclass
class RecommendationAgeStats:
    """Statistics about recommendation ages."""
    total_recommendations: int
    average_age_hours: float
    oldest_recommendation_id: Optional[str]
    oldest_age_hours: Optional[float]
    stale_recommendations: List[Dict[str, Any]]  # >30 days old
    age_distribution: Dict[str, int]  # Age range buckets


@dataclass
class AuditabilityMetrics:
    """
    Complete auditability and compliance metrics.

    Attributes:
        decision_trace_completeness: % of recommendations with complete decision traces (target 100%)
        consent_compliance_rate: % of recommendations for opted-in users (target 100%)
        eligibility_compliance_rate: % passing eligibility checks
        tone_compliance_rate: % passing tone validation
        disclaimer_presence_rate: % with mandatory disclaimer (target 100%)
        audit_log_completeness: Audit log completeness score (0-100%)
        compliance_failures: List of all compliance violations
        recommendation_ages: Statistics on recommendation staleness
        data_retention_status: Status of data retention compliance
        timestamp: When metrics were calculated
        overall_compliance_score: Aggregate compliance score (0-100%)
        critical_issues_count: Count of critical violations requiring immediate action
    """
    decision_trace_completeness: float
    consent_compliance_rate: float
    eligibility_compliance_rate: float
    tone_compliance_rate: float
    disclaimer_presence_rate: float
    audit_log_completeness: float
    compliance_failures: List[ComplianceFailure]
    recommendation_ages: RecommendationAgeStats
    data_retention_status: str
    timestamp: datetime
    overall_compliance_score: float = 0.0
    critical_issues_count: int = 0

    # Detailed reports
    decision_trace_analysis: Optional[DecisionTraceAnalysis] = None
    consent_report: Optional[GuardrailComplianceReport] = None
    eligibility_report: Optional[GuardrailComplianceReport] = None
    tone_report: Optional[GuardrailComplianceReport] = None
    disclaimer_report: Optional[GuardrailComplianceReport] = None
    audit_log_analysis: Optional[AuditLogAnalysis] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "decision_trace_completeness": self.decision_trace_completeness,
            "consent_compliance_rate": self.consent_compliance_rate,
            "eligibility_compliance_rate": self.eligibility_compliance_rate,
            "tone_compliance_rate": self.tone_compliance_rate,
            "disclaimer_presence_rate": self.disclaimer_presence_rate,
            "audit_log_completeness": self.audit_log_completeness,
            "overall_compliance_score": self.overall_compliance_score,
            "critical_issues_count": self.critical_issues_count,
            "data_retention_status": self.data_retention_status,
            "timestamp": self.timestamp.isoformat(),
            "compliance_failures": [
                {
                    "recommendation_id": f.recommendation_id,
                    "user_id": f.user_id,
                    "failure_type": f.failure_type,
                    "severity": f.severity.value,
                    "details": f.details,
                    "timestamp": f.timestamp,
                    "event_type": f.event_type,
                    "missing_elements": f.missing_elements
                }
                for f in self.compliance_failures
            ],
            "recommendation_ages": {
                "total_recommendations": self.recommendation_ages.total_recommendations,
                "average_age_hours": self.recommendation_ages.average_age_hours,
                "oldest_recommendation_id": self.recommendation_ages.oldest_recommendation_id,
                "oldest_age_hours": self.recommendation_ages.oldest_age_hours,
                "stale_count": len(self.recommendation_ages.stale_recommendations),
                "stale_recommendations": self.recommendation_ages.stale_recommendations,
                "age_distribution": self.recommendation_ages.age_distribution
            },
            "detailed_reports": {
                "decision_trace_analysis": asdict(self.decision_trace_analysis) if self.decision_trace_analysis else None,
                "consent_report": self._guardrail_report_to_dict(self.consent_report),
                "eligibility_report": self._guardrail_report_to_dict(self.eligibility_report),
                "tone_report": self._guardrail_report_to_dict(self.tone_report),
                "disclaimer_report": self._guardrail_report_to_dict(self.disclaimer_report),
                "audit_log_analysis": asdict(self.audit_log_analysis) if self.audit_log_analysis else None
            }
        }

    def _guardrail_report_to_dict(self, report: Optional[GuardrailComplianceReport]) -> Optional[Dict[str, Any]]:
        """Convert guardrail report to dictionary."""
        if not report:
            return None
        return {
            "guardrail_type": report.guardrail_type,
            "total_checked": report.total_checked,
            "passed": report.passed,
            "failed": report.failed,
            "compliance_rate": report.compliance_rate,
            "status": report.status.value,
            "failure_count": len(report.failures),
            "sample_failures": [
                {
                    "recommendation_id": f.recommendation_id,
                    "user_id": f.user_id,
                    "failure_type": f.failure_type,
                    "severity": f.severity.value,
                    "details": f.details
                }
                for f in report.failures[:5]  # First 5 failures as samples
            ]
        }


class AuditabilityEvaluator:
    """
    Evaluator for auditability and compliance metrics.

    Verifies complete decision traces, consent compliance, guardrail enforcement,
    and audit log completeness per Epic 7 Story 7.4 requirements.
    """

    # Required event types for complete audit trail (Epic 6 Story 6.5)
    REQUIRED_EVENT_TYPES = {
        'consent_changed',
        'persona_assigned',
        'recommendation_generated',
        'eligibility_checked',
        'tone_validated',
        'operator_action'
    }

    # Mandatory disclaimer text (FR29)
    MANDATORY_DISCLAIMER = "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance"

    def __init__(self, db_session: Optional[Session] = None):
        """
        Initialize auditability evaluator.

        Args:
            db_session: SQLAlchemy database session (creates new if not provided)
        """
        self.db_session = db_session or get_db_session()
        self._close_session = db_session is None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session if we created it."""
        if self._close_session and self.db_session:
            self.db_session.close()

    def evaluate_all(self) -> AuditabilityMetrics:
        """
        Evaluate all auditability and compliance metrics.

        Returns:
            AuditabilityMetrics with comprehensive compliance analysis
        """
        all_failures: List[ComplianceFailure] = []

        # 1. Verify decision trace completeness
        trace_analysis = self.verify_decision_traces()
        decision_trace_completeness = trace_analysis.completeness_rate
        all_failures.extend(self._trace_failures_to_compliance_failures(trace_analysis))

        # 2. Check consent compliance (CRITICAL - 0% violations required)
        consent_report = self.check_consent_compliance()
        consent_compliance_rate = consent_report.compliance_rate
        all_failures.extend(consent_report.failures)

        # 3. Check eligibility compliance
        eligibility_report = self.check_guardrail_compliance('eligibility')
        eligibility_compliance_rate = eligibility_report.compliance_rate
        all_failures.extend(eligibility_report.failures)

        # 4. Check tone compliance
        tone_report = self.check_guardrail_compliance('tone')
        tone_compliance_rate = tone_report.compliance_rate
        all_failures.extend(tone_report.failures)

        # 5. Verify disclaimer presence
        disclaimer_report = self.check_disclaimer_presence()
        disclaimer_presence_rate = disclaimer_report.compliance_rate
        all_failures.extend(disclaimer_report.failures)

        # 6. Analyze audit log completeness
        audit_log_analysis = self.analyze_audit_log_completeness()
        audit_log_completeness = audit_log_analysis.completeness_score

        # 7. Track recommendation ages
        recommendation_ages = self.track_recommendation_ages()

        # 8. Verify data retention compliance
        data_retention_status = self.verify_data_retention()

        # Calculate overall compliance score (weighted average)
        overall_score = self._calculate_overall_compliance_score(
            decision_trace_completeness,
            consent_compliance_rate,
            eligibility_compliance_rate,
            tone_compliance_rate,
            disclaimer_presence_rate,
            audit_log_completeness
        )

        # Count critical issues
        critical_issues_count = sum(
            1 for f in all_failures if f.severity == ComplianceSeverity.CRITICAL
        )

        # Sort failures by severity
        all_failures.sort(key=lambda f: (
            0 if f.severity == ComplianceSeverity.CRITICAL else
            1 if f.severity == ComplianceSeverity.HIGH else
            2 if f.severity == ComplianceSeverity.MEDIUM else 3
        ))

        return AuditabilityMetrics(
            decision_trace_completeness=decision_trace_completeness,
            consent_compliance_rate=consent_compliance_rate,
            eligibility_compliance_rate=eligibility_compliance_rate,
            tone_compliance_rate=tone_compliance_rate,
            disclaimer_presence_rate=disclaimer_presence_rate,
            audit_log_completeness=audit_log_completeness,
            compliance_failures=all_failures,
            recommendation_ages=recommendation_ages,
            data_retention_status=data_retention_status,
            timestamp=datetime.utcnow(),
            overall_compliance_score=overall_score,
            critical_issues_count=critical_issues_count,
            decision_trace_analysis=trace_analysis,
            consent_report=consent_report,
            eligibility_report=eligibility_report,
            tone_report=tone_report,
            disclaimer_report=disclaimer_report,
            audit_log_analysis=audit_log_analysis
        )

    def verify_decision_traces(self) -> DecisionTraceAnalysis:
        """
        Verify that all recommendations have complete decision traces in audit log.

        A complete decision trace requires:
        - User consent status checked and logged
        - Persona assignment decision logged with rationale
        - Recommendation matching logic logged
        - Eligibility check performed and logged
        - Tone validation performed and logged
        - Final recommendation assembly logged

        Returns:
            DecisionTraceAnalysis with completeness metrics
        """
        # Get all recommendation_generated events
        rec_events = self.db_session.query(AuditLog).filter(
            AuditLog.event_type == 'recommendation_generated'
        ).all()

        total_recommendations = len(rec_events)
        if total_recommendations == 0:
            return DecisionTraceAnalysis(
                total_recommendations=0,
                complete_traces=0,
                incomplete_traces=0,
                completeness_rate=100.0,  # No recommendations = 100% compliant
                missing_steps={},
                incomplete_recommendation_ids=[]
            )

        required_steps = [
            'consent_changed',  # or user already opted in
            'persona_assigned',
            'eligibility_checked',
            'tone_validated',
            'recommendation_generated'
        ]

        complete_traces = 0
        incomplete_traces = 0
        incomplete_rec_ids = []
        missing_steps_count: Dict[str, int] = {step: 0 for step in required_steps}

        # OPTIMIZATION: Batch load all users and audit events to avoid N+1 queries
        # Load all unique user_ids from recommendations
        user_ids = list(set(e.user_id for e in rec_events))
        users_map = {u.user_id: u for u in self.db_session.query(User).filter(User.user_id.in_(user_ids)).all()}

        # Load all recommendation_ids
        rec_ids = [e.recommendation_id for e in rec_events]

        # Load all relevant audit events at once
        audit_events = self.db_session.query(AuditLog).filter(
            or_(
                AuditLog.recommendation_id.in_(rec_ids),
                AuditLog.user_id.in_(user_ids)
            )
        ).all()

        # Group audit events by recommendation_id and event_type for fast lookup
        events_by_rec_and_type = {}
        events_by_user_and_type = {}
        for event in audit_events:
            if event.recommendation_id:
                key = (event.recommendation_id, event.event_type)
                events_by_rec_and_type[key] = event
            if event.user_id:
                key = (event.user_id, event.event_type)
                if key not in events_by_user_and_type:
                    events_by_user_and_type[key] = event

        for rec_event in rec_events:
            rec_id = rec_event.recommendation_id
            user_id = rec_event.user_id

            # Check for each required step in audit log
            missing_steps = []

            # 1. Check consent (either consent_changed event or user is opted_in)
            consent_event = events_by_user_and_type.get((user_id, 'consent_changed'))
            user = users_map.get(user_id)
            if not consent_event and (not user or user.consent_status != 'opted_in'):
                missing_steps.append('consent_changed')
                missing_steps_count['consent_changed'] += 1

            # 2. Check persona assignment
            persona_event = events_by_user_and_type.get((user_id, 'persona_assigned'))
            if not persona_event:
                missing_steps.append('persona_assigned')
                missing_steps_count['persona_assigned'] += 1

            # 3. Check eligibility
            eligibility_event = events_by_rec_and_type.get((rec_id, 'eligibility_checked'))
            if not eligibility_event:
                missing_steps.append('eligibility_checked')
                missing_steps_count['eligibility_checked'] += 1

            # 4. Check tone validation
            tone_event = events_by_rec_and_type.get((rec_id, 'tone_validated'))
            if not tone_event:
                missing_steps.append('tone_validated')
                missing_steps_count['tone_validated'] += 1

            # Determine if trace is complete
            if len(missing_steps) == 0:
                complete_traces += 1
            else:
                incomplete_traces += 1
                incomplete_rec_ids.append(rec_id)

        completeness_rate = (complete_traces / total_recommendations * 100.0) if total_recommendations > 0 else 100.0

        return DecisionTraceAnalysis(
            total_recommendations=total_recommendations,
            complete_traces=complete_traces,
            incomplete_traces=incomplete_traces,
            completeness_rate=completeness_rate,
            missing_steps=missing_steps_count,
            incomplete_recommendation_ids=incomplete_rec_ids
        )

    def check_consent_compliance(self) -> GuardrailComplianceReport:
        """
        Verify 0% processing without consent (target: 100% opted-in users).

        CRITICAL compliance requirement per FR23-FR25.

        Returns:
            GuardrailComplianceReport for consent compliance
        """
        failures: List[ComplianceFailure] = []

        # Get all recommendation_generated events
        rec_events = self.db_session.query(AuditLog).filter(
            AuditLog.event_type == 'recommendation_generated'
        ).all()

        total_checked = len(rec_events)
        passed = 0
        failed = 0

        for rec_event in rec_events:
            user_id = rec_event.user_id
            rec_id = rec_event.recommendation_id

            # Check user consent status
            user = self.db_session.query(User).filter(User.user_id == user_id).first()

            if not user:
                # User not found - critical violation
                failures.append(ComplianceFailure(
                    recommendation_id=rec_id,
                    user_id=user_id,
                    failure_type="consent_violation",
                    severity=ComplianceSeverity.CRITICAL,
                    details=f"Recommendation generated for non-existent user {user_id}",
                    timestamp=rec_event.timestamp.isoformat(),
                    event_type="recommendation_generated"
                ))
                failed += 1
                continue

            if user.consent_status != 'opted_in':
                # User not opted in - critical violation
                failures.append(ComplianceFailure(
                    recommendation_id=rec_id,
                    user_id=user_id,
                    failure_type="consent_violation",
                    severity=ComplianceSeverity.CRITICAL,
                    details=f"Recommendation generated for opted-out user (status: {user.consent_status})",
                    timestamp=rec_event.timestamp.isoformat(),
                    event_type="recommendation_generated"
                ))
                failed += 1
                continue

            # Check if recommendation was generated before consent timestamp
            if user.consent_timestamp and rec_event.timestamp < user.consent_timestamp:
                failures.append(ComplianceFailure(
                    recommendation_id=rec_id,
                    user_id=user_id,
                    failure_type="consent_violation",
                    severity=ComplianceSeverity.CRITICAL,
                    details=f"Recommendation generated before consent timestamp",
                    timestamp=rec_event.timestamp.isoformat(),
                    event_type="recommendation_generated"
                ))
                failed += 1
                continue

            passed += 1

        compliance_rate = (passed / total_checked * 100.0) if total_checked > 0 else 100.0
        status = ComplianceStatus.PASS if compliance_rate == 100.0 else ComplianceStatus.FAIL

        return GuardrailComplianceReport(
            guardrail_type="consent",
            total_checked=total_checked,
            passed=passed,
            failed=failed,
            compliance_rate=compliance_rate,
            status=status,
            failures=failures
        )

    def check_guardrail_compliance(self, guardrail_type: str) -> GuardrailComplianceReport:
        """
        Check compliance rate for eligibility or tone guardrails.

        Args:
            guardrail_type: 'eligibility' or 'tone'

        Returns:
            GuardrailComplianceReport for the specified guardrail
        """
        event_type_map = {
            'eligibility': 'eligibility_checked',
            'tone': 'tone_validated'
        }

        if guardrail_type not in event_type_map:
            raise ValueError(f"Invalid guardrail_type: {guardrail_type}")

        event_type = event_type_map[guardrail_type]
        failures: List[ComplianceFailure] = []

        # Get all events for this guardrail type
        guardrail_events = self.db_session.query(AuditLog).filter(
            AuditLog.event_type == event_type
        ).all()

        total_checked = len(guardrail_events)
        passed = 0
        failed = 0

        severity = ComplianceSeverity.HIGH if guardrail_type == 'eligibility' else ComplianceSeverity.MEDIUM

        for event in guardrail_events:
            # Parse event_data JSON
            try:
                event_data = json.loads(event.event_data)
                check_passed = event_data.get('passed', False)

                if check_passed:
                    passed += 1
                else:
                    failed += 1

                    # Extract failure details
                    failure_reasons = event_data.get('failure_reasons', [])
                    detected_violations = event_data.get('detected_violations', [])

                    details_text = f"{guardrail_type.capitalize()} check failed"
                    if failure_reasons:
                        details_text += f": {', '.join(failure_reasons)}"
                    elif detected_violations:
                        details_text += f": {', '.join(detected_violations)}"

                    failures.append(ComplianceFailure(
                        recommendation_id=event.recommendation_id,
                        user_id=event.user_id,
                        failure_type=f"{guardrail_type}_violation",
                        severity=severity,
                        details=details_text,
                        timestamp=event.timestamp.isoformat(),
                        event_type=event_type
                    ))

            except (json.JSONDecodeError, KeyError) as e:
                # Invalid event data structure
                failures.append(ComplianceFailure(
                    recommendation_id=event.recommendation_id,
                    user_id=event.user_id,
                    failure_type=f"{guardrail_type}_invalid_data",
                    severity=ComplianceSeverity.MEDIUM,
                    details=f"Invalid event data structure: {str(e)}",
                    timestamp=event.timestamp.isoformat(),
                    event_type=event_type
                ))
                failed += 1

        compliance_rate = (passed / total_checked * 100.0) if total_checked > 0 else 100.0

        # Status determination
        if compliance_rate == 100.0:
            status = ComplianceStatus.PASS
        elif compliance_rate >= 95.0:
            status = ComplianceStatus.WARNING
        else:
            status = ComplianceStatus.FAIL

        return GuardrailComplianceReport(
            guardrail_type=guardrail_type,
            total_checked=total_checked,
            passed=passed,
            failed=failed,
            compliance_rate=compliance_rate,
            status=status,
            failures=failures
        )

    def check_disclaimer_presence(self) -> GuardrailComplianceReport:
        """
        Verify 100% of recommendations include mandatory disclaimer (FR29).

        Returns:
            GuardrailComplianceReport for disclaimer presence
        """
        failures: List[ComplianceFailure] = []

        # Get all recommendation_generated events
        rec_events = self.db_session.query(AuditLog).filter(
            AuditLog.event_type == 'recommendation_generated'
        ).all()

        total_checked = len(rec_events)
        passed = 0
        failed = 0

        for rec_event in rec_events:
            # Parse event data to check for disclaimer
            try:
                event_data = json.loads(rec_event.event_data)

                # Check if guardrail_results contains disclaimer info
                guardrail_results = event_data.get('guardrail_results', {})
                disclaimer_present = guardrail_results.get('disclaimer_present', False)

                if disclaimer_present:
                    passed += 1
                else:
                    failed += 1
                    failures.append(ComplianceFailure(
                        recommendation_id=rec_event.recommendation_id,
                        user_id=rec_event.user_id,
                        failure_type="missing_disclaimer",
                        severity=ComplianceSeverity.HIGH,
                        details="Mandatory disclaimer not present in recommendation",
                        timestamp=rec_event.timestamp.isoformat(),
                        event_type="recommendation_generated"
                    ))

            except (json.JSONDecodeError, KeyError):
                # Cannot verify disclaimer - mark as failure
                failed += 1
                failures.append(ComplianceFailure(
                    recommendation_id=rec_event.recommendation_id,
                    user_id=rec_event.user_id,
                    failure_type="missing_disclaimer",
                    severity=ComplianceSeverity.HIGH,
                    details="Cannot verify disclaimer presence - invalid event data",
                    timestamp=rec_event.timestamp.isoformat(),
                    event_type="recommendation_generated"
                ))

        compliance_rate = (passed / total_checked * 100.0) if total_checked > 0 else 100.0
        status = ComplianceStatus.PASS if compliance_rate == 100.0 else ComplianceStatus.FAIL

        return GuardrailComplianceReport(
            guardrail_type="disclaimer",
            total_checked=total_checked,
            passed=passed,
            failed=failed,
            compliance_rate=compliance_rate,
            status=status,
            failures=failures
        )

    def analyze_audit_log_completeness(self) -> AuditLogAnalysis:
        """
        Verify audit log has all required event types logged.

        Returns:
            AuditLogAnalysis with completeness metrics
        """
        # Get all events
        all_events = self.db_session.query(AuditLog).all()
        total_events = len(all_events)

        # Get present event types
        present_event_types = set(
            row[0] for row in self.db_session.query(AuditLog.event_type).distinct().all()
        )

        # Calculate missing event types
        missing_event_types = list(self.REQUIRED_EVENT_TYPES - present_event_types)

        # Count events by type
        event_type_counts = {}
        for event_type in self.REQUIRED_EVENT_TYPES:
            count = self.db_session.query(AuditLog).filter(
                AuditLog.event_type == event_type
            ).count()
            event_type_counts[event_type] = count

        # Calculate completeness score
        completeness_score = (
            len(present_event_types & self.REQUIRED_EVENT_TYPES) /
            len(self.REQUIRED_EVENT_TYPES) * 100.0
        ) if self.REQUIRED_EVENT_TYPES else 100.0

        # Detect gaps (periods with no events)
        gaps_detected = self._detect_audit_log_gaps(all_events)

        return AuditLogAnalysis(
            total_events=total_events,
            required_event_types=sorted(list(self.REQUIRED_EVENT_TYPES)),
            present_event_types=sorted(list(present_event_types)),
            missing_event_types=sorted(missing_event_types),
            completeness_score=completeness_score,
            gaps_detected=gaps_detected,
            event_type_counts=event_type_counts
        )

    def track_recommendation_ages(self) -> RecommendationAgeStats:
        """
        Track recommendation ages from generation to current time.

        Returns:
            RecommendationAgeStats with age distribution and staleness metrics
        """
        # Get all recommendation_generated events
        rec_events = self.db_session.query(AuditLog).filter(
            AuditLog.event_type == 'recommendation_generated'
        ).all()

        total_recommendations = len(rec_events)
        if total_recommendations == 0:
            return RecommendationAgeStats(
                total_recommendations=0,
                average_age_hours=0.0,
                oldest_recommendation_id=None,
                oldest_age_hours=None,
                stale_recommendations=[],
                age_distribution={}
            )

        current_time = datetime.utcnow()
        ages_hours = []
        stale_recommendations = []
        oldest_rec_id = None
        oldest_age = None

        for rec_event in rec_events:
            age = current_time - rec_event.timestamp
            age_hours = age.total_seconds() / 3600

            ages_hours.append(age_hours)

            # Track oldest
            if oldest_age is None or age_hours > oldest_age:
                oldest_age = age_hours
                oldest_rec_id = rec_event.recommendation_id

            # Check if stale (>30 days = 720 hours)
            if age_hours > 720:
                stale_recommendations.append({
                    "recommendation_id": rec_event.recommendation_id,
                    "user_id": rec_event.user_id,
                    "age_hours": age_hours,
                    "age_days": age_hours / 24,
                    "generated_at": rec_event.timestamp.isoformat()
                })

        # Calculate average age
        average_age_hours = sum(ages_hours) / len(ages_hours) if ages_hours else 0.0

        # Age distribution buckets
        age_distribution = {
            "0-24h": sum(1 for a in ages_hours if a <= 24),
            "1-7d": sum(1 for a in ages_hours if 24 < a <= 168),
            "7-30d": sum(1 for a in ages_hours if 168 < a <= 720),
            ">30d": sum(1 for a in ages_hours if a > 720)
        }

        return RecommendationAgeStats(
            total_recommendations=total_recommendations,
            average_age_hours=average_age_hours,
            oldest_recommendation_id=oldest_rec_id,
            oldest_age_hours=oldest_age,
            stale_recommendations=stale_recommendations,
            age_distribution=age_distribution
        )

    def verify_data_retention(self) -> str:
        """
        Verify data retention compliance.

        Checks:
        - Audit logs exist for all time periods
        - No suspicious gaps or deletions
        - Log integrity (no tampering)

        Returns:
            Data retention status: "COMPLIANT" or "NON-COMPLIANT"
        """
        # Get oldest and newest audit log entries
        oldest = self.db_session.query(func.min(AuditLog.timestamp)).scalar()
        newest = self.db_session.query(func.max(AuditLog.timestamp)).scalar()

        if not oldest or not newest:
            return "COMPLIANT - NO DATA"

        # Check for suspicious gaps (>7 days with no events)
        all_events = self.db_session.query(AuditLog).order_by(AuditLog.timestamp).all()
        gaps = self._detect_audit_log_gaps(all_events, gap_threshold_days=7)

        # Verify log integrity (basic check - all events have required fields)
        total_events = self.db_session.query(AuditLog).count()
        valid_events = self.db_session.query(AuditLog).filter(
            and_(
                AuditLog.log_id.isnot(None),
                AuditLog.event_type.isnot(None),
                AuditLog.timestamp.isnot(None),
                AuditLog.event_data.isnot(None)
            )
        ).count()

        if valid_events < total_events:
            return f"NON-COMPLIANT - {total_events - valid_events} events with missing fields"

        if len(gaps) > 0:
            return f"WARNING - {len(gaps)} gaps detected in audit log"

        return "COMPLIANT"

    def _detect_audit_log_gaps(
        self,
        events: List[AuditLog],
        gap_threshold_days: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Detect gaps in audit log (periods with no events).

        Args:
            events: List of audit log events ordered by timestamp
            gap_threshold_days: Minimum gap size in days to report

        Returns:
            List of gaps with start/end timestamps and duration
        """
        if len(events) < 2:
            return []

        gaps = []
        threshold = timedelta(days=gap_threshold_days)

        for i in range(len(events) - 1):
            current_event = events[i]
            next_event = events[i + 1]
            gap_duration = next_event.timestamp - current_event.timestamp

            if gap_duration > threshold:
                gaps.append({
                    "start_time": current_event.timestamp.isoformat(),
                    "end_time": next_event.timestamp.isoformat(),
                    "duration_hours": gap_duration.total_seconds() / 3600,
                    "duration_days": gap_duration.days
                })

        return gaps

    def _trace_failures_to_compliance_failures(
        self,
        trace_analysis: DecisionTraceAnalysis
    ) -> List[ComplianceFailure]:
        """Convert decision trace failures to compliance failure records."""
        failures = []

        for rec_id in trace_analysis.incomplete_recommendation_ids:
            # Get the recommendation event to find user_id
            rec_event = self.db_session.query(AuditLog).filter(
                and_(
                    AuditLog.recommendation_id == rec_id,
                    AuditLog.event_type == 'recommendation_generated'
                )
            ).first()

            missing_steps = []
            for step, count in trace_analysis.missing_steps.items():
                if count > 0:
                    # Check if this specific recommendation is missing this step
                    # This is a simplified check - in production might want more detailed tracking
                    missing_steps.append(step)

            failures.append(ComplianceFailure(
                recommendation_id=rec_id,
                user_id=rec_event.user_id if rec_event else None,
                failure_type="incomplete_decision_trace",
                severity=ComplianceSeverity.MEDIUM,
                details=f"Incomplete decision trace - missing audit log events",
                timestamp=rec_event.timestamp.isoformat() if rec_event else datetime.utcnow().isoformat(),
                event_type="recommendation_generated",
                missing_elements=missing_steps[:5]  # First 5 missing elements
            ))

        return failures

    def _calculate_overall_compliance_score(
        self,
        decision_trace: float,
        consent: float,
        eligibility: float,
        tone: float,
        disclaimer: float,
        audit_log: float
    ) -> float:
        """
        Calculate weighted overall compliance score.

        Weights:
        - Consent: 30% (CRITICAL)
        - Decision Trace: 20%
        - Eligibility: 20%
        - Disclaimer: 15%
        - Tone: 10%
        - Audit Log: 5%
        """
        score = (
            consent * 0.30 +
            decision_trace * 0.20 +
            eligibility * 0.20 +
            disclaimer * 0.15 +
            tone * 0.10 +
            audit_log * 0.05
        )
        return round(score, 2)


def generate_compliance_report(metrics: AuditabilityMetrics) -> Dict[str, Any]:
    """
    Generate structured compliance report with pass/fail status per guardrail.

    Args:
        metrics: AuditabilityMetrics to generate report from

    Returns:
        Structured compliance report dictionary
    """
    report = {
        "overall_compliance_score": metrics.overall_compliance_score,
        "overall_status": "PASS" if metrics.overall_compliance_score >= 100.0 else "FAIL",
        "critical_issues_count": metrics.critical_issues_count,
        "timestamp": metrics.timestamp.isoformat(),
        "guardrail_status": {
            "consent_compliance": {
                "status": "PASS" if metrics.consent_compliance_rate == 100.0 else "FAIL",
                "compliance_rate": metrics.consent_compliance_rate,
                "target": 100.0,
                "severity": "CRITICAL"
            },
            "eligibility_compliance": {
                "status": "PASS" if metrics.eligibility_compliance_rate >= 100.0 else "WARNING" if metrics.eligibility_compliance_rate >= 95.0 else "FAIL",
                "compliance_rate": metrics.eligibility_compliance_rate,
                "target": 100.0,
                "severity": "HIGH"
            },
            "tone_compliance": {
                "status": "PASS" if metrics.tone_compliance_rate >= 100.0 else "WARNING" if metrics.tone_compliance_rate >= 95.0 else "FAIL",
                "compliance_rate": metrics.tone_compliance_rate,
                "target": 100.0,
                "severity": "MEDIUM"
            },
            "disclaimer_presence": {
                "status": "PASS" if metrics.disclaimer_presence_rate == 100.0 else "FAIL",
                "compliance_rate": metrics.disclaimer_presence_rate,
                "target": 100.0,
                "severity": "HIGH"
            },
            "decision_trace_completeness": {
                "status": "PASS" if metrics.decision_trace_completeness == 100.0 else "WARNING" if metrics.decision_trace_completeness >= 90.0 else "FAIL",
                "compliance_rate": metrics.decision_trace_completeness,
                "target": 100.0,
                "severity": "MEDIUM"
            },
            "audit_log_completeness": {
                "status": "PASS" if metrics.audit_log_completeness == 100.0 else "WARNING" if metrics.audit_log_completeness >= 80.0 else "FAIL",
                "compliance_rate": metrics.audit_log_completeness,
                "target": 100.0,
                "severity": "LOW"
            }
        },
        "violations_by_type": {},
        "violations_by_severity": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        },
        "recommendations_for_remediation": []
    }

    # Count violations by type and severity
    for failure in metrics.compliance_failures:
        failure_type = failure.failure_type
        report["violations_by_type"][failure_type] = report["violations_by_type"].get(failure_type, 0) + 1
        report["violations_by_severity"][failure.severity.value] += 1

    # Generate remediation recommendations
    if metrics.consent_compliance_rate < 100.0:
        report["recommendations_for_remediation"].append(
            "CRITICAL: Stop processing for opted-out users immediately - review consent checks"
        )

    if metrics.disclaimer_presence_rate < 100.0:
        report["recommendations_for_remediation"].append(
            "HIGH: Ensure mandatory disclaimer is added to all recommendations"
        )

    if metrics.eligibility_compliance_rate < 95.0:
        report["recommendations_for_remediation"].append(
            "HIGH: Review eligibility filtering logic to prevent unqualified recommendations"
        )

    if metrics.tone_compliance_rate < 95.0:
        report["recommendations_for_remediation"].append(
            "MEDIUM: Review tone validation rules and update content to meet standards"
        )

    if metrics.decision_trace_completeness < 90.0:
        report["recommendations_for_remediation"].append(
            "MEDIUM: Ensure all system decisions are logged to audit trail"
        )

    if len(metrics.recommendation_ages.stale_recommendations) > 0:
        report["recommendations_for_remediation"].append(
            f"INFO: {len(metrics.recommendation_ages.stale_recommendations)} stale recommendations (>30 days) should be reviewed"
        )

    return report
