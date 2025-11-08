"""
Explainability metrics calculation for recommendation quality assessment.

Measures recommendation explainability ensuring all outputs have transparent
rationales with concrete data citations and complete decision traces.
"""

import logging
import re
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Try to import textstat for better readability metrics
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False

logger = logging.getLogger(__name__)

# Quality threshold for rationale assessment (0-5 scale)
QUALITY_THRESHOLD = 3


@dataclass
class ExplainabilityMetrics:
    """
    Explainability metrics for recommendations.

    Attributes:
        rationale_presence_rate: Percentage of recommendations with rationales (target 100%)
        rationale_quality_score: Average quality score across all rationales (0-5 scale)
        explainability_by_persona: Rationale presence rate per persona
        decision_trace_completeness: Percentage with complete audit trails
        failure_cases: List of recommendations with explainability issues
        sample_rationales: Representative rationale samples for manual review
        improvement_recommendations: Actionable recommendations for quality improvements
        timestamp: When metrics were calculated
    """

    rationale_presence_rate: float
    rationale_quality_score: float
    explainability_by_persona: Dict[str, float]
    decision_trace_completeness: float
    failure_cases: List[Dict[str, Any]]
    sample_rationales: List[Dict[str, Any]]
    improvement_recommendations: List[str]
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with datetime serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


def calculate_rationale_presence(
    recommendations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculate rationale presence metrics (AC #1, #4).

    Checks each recommendation for non-empty rationale field and calculates
    presence rate overall and per-persona.

    Args:
        recommendations: List of recommendation dicts with rationale and persona fields

    Returns:
        Dict with overall rate, per-persona rates, and missing rationale list
    """
    if not recommendations:
        return {
            "overall_rate": 0.0,
            "by_persona": {},
            "missing_rationales": [],
            "total_recommendations": 0,
            "recommendations_with_rationales": 0,
        }

    total = len(recommendations)
    with_rationales = 0
    missing_rationales = []
    persona_stats = defaultdict(lambda: {"total": 0, "with_rationales": 0})

    for rec in recommendations:
        rationale = rec.get("rationale") or ""
        rationale = rationale.strip() if isinstance(rationale, str) else ""
        persona = rec.get("persona_id") or rec.get("persona", "unknown")

        persona_stats[persona]["total"] += 1

        if rationale:
            with_rationales += 1
            persona_stats[persona]["with_rationales"] += 1
        else:
            missing_rationales.append(
                {
                    "user_id": rec.get("user_id"),
                    "item_id": rec.get("item_id"),
                    "persona": persona,
                    "item_type": rec.get("item_type", "unknown"),
                }
            )

    overall_rate = with_rationales / total if total > 0 else 0.0

    by_persona = {}
    for persona, stats in persona_stats.items():
        rate = (
            stats["with_rationales"] / stats["total"] if stats["total"] > 0 else 0.0
        )
        by_persona[persona] = round(rate, 4)

    return {
        "overall_rate": round(overall_rate, 4),
        "by_persona": by_persona,
        "missing_rationales": missing_rationales,
        "total_recommendations": total,
        "recommendations_with_rationales": with_rationales,
    }


def assess_rationale_quality(rationale: str) -> Dict[str, Any]:
    """
    Assess rationale quality against criteria checklist (AC #2, #3).

    Quality criteria (0-5 point scale):
    1. Contains concrete data citations (signal names, values)
    2. Includes account identifiers or transaction details
    3. Provides numeric specifics (amounts, percentages, dates)
    4. Uses plain language (grade-8 readability via Flesch-Kincaid Grade Level)
    5. Cites specific behavioral signals

    Readability Assessment:
    - Uses textstat library's Flesch-Kincaid Grade Level when available
    - Target: Grade 8 or lower for plain language compliance (FR22)
    - Falls back to heuristics (sentence/word length) if textstat unavailable

    Args:
        rationale: Rationale text to assess

    Returns:
        Dict with quality score, criteria breakdown, and assessment details
    """
    if not rationale or not rationale.strip():
        return {
            "quality_score": 0,
            "criteria_met": {
                "has_data_citations": False,
                "has_account_identifiers": False,
                "has_numeric_specifics": False,
                "uses_plain_language": False,
                "cites_behavioral_signals": False,
            },
            "citations_found": [],
            "is_high_quality": False,
        }

    score = 0
    criteria_met = {}
    citations_found = []

    # 1. Check for concrete data citations (signal names, values)
    # Look for technical signal names or data patterns
    signal_patterns = [
        r"credit[_\s]utilization",
        r"savings[_\s]balance",
        r"transaction[_\s]history",
        r"income[_\s]stability",
        r"subscription[_\s]pattern",
        r"debt[_\s]signal",
    ]
    has_data_citations = any(
        re.search(pattern, rationale, re.IGNORECASE) for pattern in signal_patterns
    )
    if has_data_citations:
        score += 1
    criteria_met["has_data_citations"] = has_data_citations

    # 2. Check for account identifiers (masked account numbers)
    account_pattern = r"\*{4}\d{4}|account|card|checking|savings"
    has_account_identifiers = bool(
        re.search(account_pattern, rationale, re.IGNORECASE)
    )
    if has_account_identifiers:
        score += 1
        # Extract account references
        accounts = re.findall(r"\*{4}\d{4}", rationale)
        citations_found.extend([f"Account: {acc}" for acc in accounts])
    criteria_met["has_account_identifiers"] = has_account_identifiers

    # 3. Check for numeric specifics (amounts, percentages, dates, numbers)
    numeric_patterns = [
        (r"\$[\d,]+(?:\.\d{2})?", "amount"),  # Dollar amounts
        (r"\d+(?:\.\d+)?%", "percentage"),  # Percentages
        (r"\b\d+\s*days?", "duration"),  # Days
        (r"\b\d+\s*months?", "duration"),  # Months
        (r"\b\d{1,2}/\d{1,2}/\d{2,4}", "date"),  # Dates
    ]
    has_numeric_specifics = False
    for pattern, citation_type in numeric_patterns:
        matches = re.findall(pattern, rationale)
        if matches:
            has_numeric_specifics = True
            citations_found.extend([f"{citation_type}: {m}" for m in matches[:3]])

    if has_numeric_specifics:
        score += 1
    criteria_met["has_numeric_specifics"] = has_numeric_specifics

    # 4. Check for plain language (grade-8 readability)
    # Use Flesch-Kincaid Grade Level if textstat is available, otherwise fall back to heuristics
    words = rationale.split()
    sentences = [s.strip() for s in rationale.split(".") if s.strip()]

    avg_sentence_length = len(words) / max(len(sentences), 1)
    avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
    complex_words = [w for w in words if len(w) > 10]
    complexity_ratio = len(complex_words) / max(len(words), 1)

    # Try Flesch-Kincaid Grade Level (target: ≤8 for plain language)
    uses_plain_language = False
    grade_level = None

    if TEXTSTAT_AVAILABLE:
        try:
            grade_level = textstat.flesch_kincaid_grade(rationale)
            # Grade 8 or lower is considered plain language
            uses_plain_language = grade_level <= 8.0
        except Exception as e:
            logger.debug(f"Textstat calculation failed, falling back to heuristics: {e}")
            # Fall back to heuristics
            uses_plain_language = (
                avg_sentence_length < 20 and avg_word_length < 6 and complexity_ratio < 0.1
            )
    else:
        # Use heuristics if textstat not available
        uses_plain_language = (
            avg_sentence_length < 20 and avg_word_length < 6 and complexity_ratio < 0.1
        )

    if uses_plain_language:
        score += 1
    criteria_met["uses_plain_language"] = uses_plain_language

    # 5. Check for behavioral signal references
    # Look for "because" statements or causal language
    behavioral_indicators = [
        "because",
        "based on",
        "given your",
        "your current",
        "you're currently",
        "you have",
        "your recent",
    ]
    cites_behavioral_signals = any(
        indicator in rationale.lower() for indicator in behavioral_indicators
    )
    if cites_behavioral_signals:
        score += 1
    criteria_met["cites_behavioral_signals"] = cites_behavioral_signals

    readability_metrics = {
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_word_length": round(avg_word_length, 1),
        "complexity_ratio": round(complexity_ratio, 2),
    }

    # Include Flesch-Kincaid Grade Level if calculated
    if grade_level is not None:
        readability_metrics["flesch_kincaid_grade"] = round(grade_level, 1)

    return {
        "quality_score": score,
        "criteria_met": criteria_met,
        "citations_found": list(set(citations_found)),
        "is_high_quality": score >= QUALITY_THRESHOLD,
        "readability_metrics": readability_metrics,
    }


def verify_decision_traces(
    recommendations: List[Dict[str, Any]], audit_logs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Verify decision trace completeness in audit logs (AC #5).

    Checks for complete audit trail for each recommendation:
    - Persona assignment decision
    - Behavioral signals detected
    - Recommendation matching logic
    - Guardrail checks (consent, eligibility, tone)
    - Final recommendation assembly

    Args:
        recommendations: List of recommendation dicts
        audit_logs: List of audit log entries

    Returns:
        Dict with completeness rate, incomplete traces, and details
    """
    if not recommendations:
        return {
            "completeness_rate": 0.0,
            "complete_traces": 0,
            "incomplete_traces": [],
            "required_events": [
                "persona_assignment",
                "signals_detected",
                "recommendation_matched",
                "guardrail_check",
                "recommendation_assembled",
            ],
        }

    # Index audit logs by user_id and recommendation_id
    logs_by_user = defaultdict(list)
    logs_by_rec = defaultdict(list)

    for log in audit_logs:
        user_id = log.get("user_id")
        rec_id = log.get("recommendation_id")
        if user_id:
            logs_by_user[user_id].append(log)
        if rec_id:
            logs_by_rec[rec_id].append(log)

    required_events = [
        "persona_assignment",
        "signals_detected",
        "recommendation_matched",
        "guardrail_check",
        "recommendation_assembled",
    ]

    complete_count = 0
    incomplete_traces = []

    for rec in recommendations:
        user_id = rec.get("user_id")
        rec_id = rec.get("item_id") or rec.get("recommendation_id")

        # Get relevant audit logs for this recommendation
        relevant_logs = logs_by_user.get(user_id, [])
        if rec_id:
            relevant_logs.extend(logs_by_rec.get(rec_id, []))

        # Check which required events are present
        found_events = set()
        for log in relevant_logs:
            event_type = log.get("event_type", "").lower().replace(" ", "").replace("-", "").replace("_", "")
            for required_event in required_events:
                # Normalize required_event for comparison
                normalized_required = required_event.lower().replace("_", "")
                # Match if event_type contains required_event or vice versa
                if normalized_required in event_type or event_type in normalized_required:
                    found_events.add(required_event)
                    break

        missing_events = set(required_events) - found_events

        if not missing_events:
            complete_count += 1
        else:
            incomplete_traces.append(
                {
                    "user_id": user_id,
                    "item_id": rec_id,
                    "persona": rec.get("persona_id") or rec.get("persona", "unknown"),
                    "missing_events": list(missing_events),
                    "found_events": list(found_events),
                }
            )

    total = len(recommendations)
    completeness_rate = complete_count / total if total > 0 else 0.0

    return {
        "completeness_rate": round(completeness_rate, 4),
        "complete_traces": complete_count,
        "total_recommendations": total,
        "incomplete_traces": incomplete_traces[:10],  # Limit to first 10
        "required_events": required_events,
    }


def extract_sample_rationales(
    recommendations: List[Dict[str, Any]], samples_per_persona: int = 3
) -> List[Dict[str, Any]]:
    """
    Extract representative sample rationales for manual review (AC #7).

    Selects diverse samples:
    - 2-3 rationales per persona
    - Mix of high and low quality examples
    - Different recommendation types

    Args:
        recommendations: List of recommendation dicts
        samples_per_persona: Number of samples to extract per persona

    Returns:
        List of sample rationale dicts with metadata
    """
    if not recommendations:
        return []

    # Group recommendations by persona
    by_persona = defaultdict(list)
    for rec in recommendations:
        persona = rec.get("persona_id") or rec.get("persona", "unknown")
        rationale = rec.get("rationale", "").strip()

        if rationale:  # Only include recommendations with rationales
            quality_assessment = assess_rationale_quality(rationale)
            rec_copy = rec.copy()
            rec_copy["quality_assessment"] = quality_assessment
            by_persona[persona].append(rec_copy)

    # Extract samples per persona
    samples = []
    for persona, recs in by_persona.items():
        # Sort by quality score (high to low)
        recs_sorted = sorted(
            recs,
            key=lambda r: r["quality_assessment"]["quality_score"],
            reverse=True,
        )

        # Select diverse samples: high quality, medium quality, low quality
        selected = []

        # Try to get at least one high-quality sample
        high_quality = [
            r for r in recs_sorted if r["quality_assessment"]["is_high_quality"]
        ]
        if high_quality:
            selected.append(high_quality[0])

        # Try to get at least one low-quality sample
        low_quality = [
            r for r in recs_sorted if not r["quality_assessment"]["is_high_quality"]
        ]
        if low_quality:
            selected.append(low_quality[-1])

        # Fill remaining slots with medium quality
        remaining_slots = samples_per_persona - len(selected)
        if remaining_slots > 0:
            middle_recs = [r for r in recs_sorted if r not in selected]
            selected.extend(middle_recs[:remaining_slots])

        # Format samples for output
        for rec in selected:
            quality_assessment = rec.pop("quality_assessment")
            samples.append(
                {
                    "user_id": rec.get("user_id"),
                    "persona": persona,
                    "item_id": rec.get("item_id"),
                    "item_type": rec.get("item_type", "unknown"),
                    "rationale": rec.get("rationale"),
                    "quality_score": quality_assessment["quality_score"],
                    "criteria_met": quality_assessment["criteria_met"],
                    "citations_found": quality_assessment["citations_found"],
                    "is_high_quality": quality_assessment["is_high_quality"],
                }
            )

    return samples


def log_explainability_failures(
    recommendations: List[Dict[str, Any]],
    presence_metrics: Dict[str, Any],
    quality_assessments: Dict[str, Dict[str, Any]],
    trace_metrics: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Log explainability failures for debugging (AC #6).

    Failure types:
    - missing_rationale: No rationale provided
    - incomplete_rationale: Rationale missing key elements
    - low_quality_rationale: Quality score < 3
    - missing_decision_trace: Incomplete audit trail

    Args:
        recommendations: List of recommendation dicts
        presence_metrics: Output from calculate_rationale_presence
        quality_assessments: Dict mapping item_id to quality assessment
        trace_metrics: Output from verify_decision_traces

    Returns:
        List of failure case dicts with details and severity
    """
    failures = []

    # Missing rationales (High severity)
    for missing in presence_metrics.get("missing_rationales", []):
        failures.append(
            {
                "failure_type": "missing_rationale",
                "severity": "high",
                "user_id": missing["user_id"],
                "item_id": missing["item_id"],
                "persona": missing["persona"],
                "item_type": missing.get("item_type"),
                "details": "Recommendation has no rationale provided",
            }
        )

    # Low quality rationales (Medium severity)
    for item_id, assessment in quality_assessments.items():
        if not assessment["is_high_quality"]:
            # Find the recommendation
            rec = next(
                (r for r in recommendations if r.get("item_id") == item_id), None
            )
            if rec:
                missing_criteria = [
                    k for k, v in assessment["criteria_met"].items() if not v
                ]
                failures.append(
                    {
                        "failure_type": "low_quality_rationale",
                        "severity": "medium",
                        "user_id": rec.get("user_id"),
                        "item_id": item_id,
                        "persona": rec.get("persona_id")
                        or rec.get("persona", "unknown"),
                        "item_type": rec.get("item_type"),
                        "quality_score": assessment["quality_score"],
                        "missing_criteria": missing_criteria,
                        "details": f"Rationale quality score {assessment['quality_score']}/5. Missing: {', '.join(missing_criteria)}",
                    }
                )

    # Incomplete decision traces (Medium severity)
    for incomplete in trace_metrics.get("incomplete_traces", []):
        failures.append(
            {
                "failure_type": "missing_decision_trace",
                "severity": "medium",
                "user_id": incomplete["user_id"],
                "item_id": incomplete["item_id"],
                "persona": incomplete["persona"],
                "missing_events": incomplete["missing_events"],
                "found_events": incomplete.get("found_events", []),
                "details": f"Audit trail incomplete. Missing: {', '.join(incomplete['missing_events'])}",
            }
        )

    # Sort by severity (high, medium, low)
    severity_order = {"high": 0, "medium": 1, "low": 2}
    failures.sort(key=lambda f: severity_order.get(f["severity"], 3))

    return failures


def generate_improvement_recommendations(
    presence_metrics: Dict[str, Any],
    quality_assessments: Dict[str, Dict[str, Any]],
    trace_metrics: Dict[str, Any],
    failures: List[Dict[str, Any]],
) -> List[str]:
    """
    Generate actionable improvement recommendations (AC #10).

    Analyzes failure patterns and generates specific recommendations
    with references to code modules that need attention.

    Args:
        presence_metrics: Rationale presence metrics
        quality_assessments: Quality assessment results
        trace_metrics: Decision trace metrics
        failures: List of failure cases

    Returns:
        List of improvement recommendation strings with priority
    """
    recommendations = []

    # Check rationale presence rate
    presence_rate = presence_metrics.get("overall_rate", 0)
    if presence_rate < 1.0:
        missing_pct = (1.0 - presence_rate) * 100
        recommendations.append(
            f"[HIGH PRIORITY] {missing_pct:.1f}% of recommendations lack rationales. "
            "Review rationale generation logic in spendsense/recommendations/rationale_generator.py "
            "and ensure all recommendation types trigger rationale generation."
        )

    # Check average quality score
    if quality_assessments:
        avg_quality = sum(
            qa["quality_score"] for qa in quality_assessments.values()
        ) / len(quality_assessments)

        if avg_quality < QUALITY_THRESHOLD:
            recommendations.append(
                f"[HIGH PRIORITY] Average rationale quality score is {avg_quality:.1f}/5 (target: ≥{QUALITY_THRESHOLD}). "
                "Enhance data citation specificity in rationale templates. "
                "Review spendsense/recommendations/rationale_generator.py placeholder replacement logic."
            )

    # Check decision trace completeness
    trace_completeness = trace_metrics.get("completeness_rate", 0)
    if trace_completeness < 0.95:
        recommendations.append(
            f"[MEDIUM PRIORITY] {(1.0 - trace_completeness) * 100:.1f}% of recommendations have incomplete audit trails. "
            "Verify audit logging in guardrail pipeline and recommendation engine. "
            "Review spendsense/services/audit_service.py and ensure all decision points are logged."
        )

    # Check for persona-specific issues
    persona_rates = presence_metrics.get("by_persona", {})
    low_persona_rates = {
        persona: rate for persona, rate in persona_rates.items() if rate < 0.9
    }

    if low_persona_rates:
        personas_str = ", ".join(low_persona_rates.keys())
        recommendations.append(
            f"[MEDIUM PRIORITY] Low rationale presence for personas: {personas_str}. "
            "Review persona-specific rationale templates and ensure all personas have proper template coverage."
        )

    # Check for missing specific criteria
    if quality_assessments:
        criteria_failures = defaultdict(int)
        for qa in quality_assessments.values():
            criteria_met = qa.get("criteria_met", {})
            for criterion, met in criteria_met.items():
                if not met:
                    criteria_failures[criterion] += 1

        total_assessments = len(quality_assessments)
        for criterion, count in criteria_failures.items():
            failure_rate = count / total_assessments
            if failure_rate > 0.3:  # More than 30% failing this criterion
                criterion_name = criterion.replace("_", " ").title()
                recommendations.append(
                    f"[MEDIUM PRIORITY] {failure_rate * 100:.0f}% of rationales fail criterion: {criterion_name}. "
                    "Review rationale templates and enhance placeholder data for this criterion."
                )

    # If no issues found
    if not recommendations:
        recommendations.append(
            "[SUCCESS] All explainability metrics meet or exceed targets. "
            "Continue monitoring rationale quality in production."
        )

    return recommendations


def calculate_explainability_metrics(
    recommendations: List[Dict[str, Any]],
    audit_logs: Optional[List[Dict[str, Any]]] = None,
    samples_per_persona: int = 3,
) -> ExplainabilityMetrics:
    """
    Calculate comprehensive explainability metrics (AC #1-10).

    Main entry point for explainability evaluation. Calculates all metrics
    and generates improvement recommendations.

    Args:
        recommendations: List of recommendation dicts
        audit_logs: Optional list of audit log entries for trace verification
        samples_per_persona: Number of sample rationales per persona

    Returns:
        ExplainabilityMetrics dataclass with all calculated metrics
    """
    if not recommendations:
        return ExplainabilityMetrics(
            rationale_presence_rate=0.0,
            rationale_quality_score=0.0,
            explainability_by_persona={},
            decision_trace_completeness=0.0,
            failure_cases=[],
            sample_rationales=[],
            improvement_recommendations=[
                "[ERROR] No recommendations provided for evaluation"
            ],
            timestamp=datetime.utcnow(),
        )

    # Calculate rationale presence
    logger.info(f"Calculating rationale presence for {len(recommendations)} recommendations")
    presence_metrics = calculate_rationale_presence(recommendations)

    # Assess quality for all rationales
    logger.info("Assessing rationale quality")
    quality_assessments = {}
    for rec in recommendations:
        rationale = rec.get("rationale", "").strip()
        if rationale:
            item_id = rec.get("item_id") or rec.get("recommendation_id")
            quality_assessments[item_id] = assess_rationale_quality(rationale)

    avg_quality_score = 0.0
    if quality_assessments:
        avg_quality_score = sum(
            qa["quality_score"] for qa in quality_assessments.values()
        ) / len(quality_assessments)

    # Verify decision traces
    logger.info("Verifying decision trace completeness")
    trace_metrics = verify_decision_traces(recommendations, audit_logs or [])

    # Extract sample rationales
    logger.info(f"Extracting sample rationales ({samples_per_persona} per persona)")
    sample_rationales = extract_sample_rationales(recommendations, samples_per_persona)

    # Log failures
    logger.info("Logging explainability failures")
    failures = log_explainability_failures(
        recommendations, presence_metrics, quality_assessments, trace_metrics
    )

    # Generate improvement recommendations
    logger.info("Generating improvement recommendations")
    improvement_recs = generate_improvement_recommendations(
        presence_metrics, quality_assessments, trace_metrics, failures
    )

    logger.info(
        f"Explainability evaluation complete: "
        f"presence={presence_metrics['overall_rate']:.2%}, "
        f"quality={avg_quality_score:.1f}/5, "
        f"trace_completeness={trace_metrics['completeness_rate']:.2%}"
    )

    return ExplainabilityMetrics(
        rationale_presence_rate=presence_metrics["overall_rate"],
        rationale_quality_score=round(avg_quality_score, 2),
        explainability_by_persona=presence_metrics["by_persona"],
        decision_trace_completeness=trace_metrics["completeness_rate"],
        failure_cases=failures,
        sample_rationales=sample_rationales,
        improvement_recommendations=improvement_recs,
        timestamp=datetime.utcnow(),
    )
