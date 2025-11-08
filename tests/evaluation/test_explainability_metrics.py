"""
Unit tests for explainability metrics calculation.

Tests rationale presence, quality assessment, decision trace verification,
sample extraction, failure logging, and improvement recommendations.
"""

import pytest
from datetime import datetime
from spendsense.evaluation.explainability_metrics import (
    ExplainabilityMetrics,
    calculate_rationale_presence,
    assess_rationale_quality,
    verify_decision_traces,
    extract_sample_rationales,
    log_explainability_failures,
    generate_improvement_recommendations,
    calculate_explainability_metrics,
)


class TestRationalePresence:
    """Test rationale presence calculation."""

    def test_calculate_rationale_presence_all_present(self):
        """Test with 100% rationale presence."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "This is a valid rationale",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "high_utilization",
                "rationale": "Another valid rationale",
            },
        ]

        result = calculate_rationale_presence(recommendations)

        assert result["overall_rate"] == 1.0
        assert result["total_recommendations"] == 2
        assert result["recommendations_with_rationales"] == 2
        assert len(result["missing_rationales"]) == 0

    def test_calculate_rationale_presence_none_present(self):
        """Test with 0% rationale presence."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "high_utilization",
                "rationale": None,
            },
        ]

        result = calculate_rationale_presence(recommendations)

        assert result["overall_rate"] == 0.0
        assert result["total_recommendations"] == 2
        assert result["recommendations_with_rationales"] == 0
        assert len(result["missing_rationales"]) == 2

    def test_calculate_rationale_presence_mixed(self):
        """Test with mixed rationale presence."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "Valid rationale",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "young_professional",
                "rationale": "",
            },
            {
                "user_id": "user_3",
                "item_id": "rec_3",
                "persona_id": "high_utilization",
                "rationale": "Another valid one",
            },
        ]

        result = calculate_rationale_presence(recommendations)

        assert result["overall_rate"] == pytest.approx(0.6667, rel=0.01)
        assert result["total_recommendations"] == 3
        assert result["recommendations_with_rationales"] == 2
        assert len(result["missing_rationales"]) == 1

    def test_calculate_rationale_presence_by_persona(self):
        """Test per-persona rationale presence calculation."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "Valid",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "young_professional",
                "rationale": "",
            },
            {
                "user_id": "user_3",
                "item_id": "rec_3",
                "persona_id": "high_utilization",
                "rationale": "Valid",
            },
        ]

        result = calculate_rationale_presence(recommendations)

        assert "young_professional" in result["by_persona"]
        assert "high_utilization" in result["by_persona"]
        assert result["by_persona"]["young_professional"] == 0.5
        assert result["by_persona"]["high_utilization"] == 1.0

    def test_calculate_rationale_presence_empty_list(self):
        """Test with empty recommendations list."""
        result = calculate_rationale_presence([])

        assert result["overall_rate"] == 0.0
        assert result["total_recommendations"] == 0
        assert result["recommendations_with_rationales"] == 0


class TestRationaleQuality:
    """Test rationale quality assessment."""

    def test_assess_rationale_quality_high_quality(self):
        """Test high-quality rationale with all criteria met."""
        rationale = (
            "Based on your credit utilization of 68% on your account ****4523, "
            "we recommend this because you have $3,400 in credit card debt. "
            "This straightforward solution can help you reduce your balance."
        )

        result = assess_rationale_quality(rationale)

        assert result["quality_score"] >= 4
        assert result["is_high_quality"] is True
        assert result["criteria_met"]["has_numeric_specifics"] is True
        assert result["criteria_met"]["has_account_identifiers"] is True
        assert result["criteria_met"]["cites_behavioral_signals"] is True

    def test_assess_rationale_quality_low_quality(self):
        """Test low-quality rationale missing key criteria."""
        rationale = "We recommend this product for you."

        result = assess_rationale_quality(rationale)

        assert result["quality_score"] < 3
        assert result["is_high_quality"] is False
        assert result["criteria_met"]["has_data_citations"] is False
        assert result["criteria_met"]["has_account_identifiers"] is False

    def test_assess_rationale_quality_empty(self):
        """Test empty rationale."""
        result = assess_rationale_quality("")

        assert result["quality_score"] == 0
        assert result["is_high_quality"] is False
        assert all(not v for v in result["criteria_met"].values())

    def test_assess_rationale_quality_data_citations(self):
        """Test detection of concrete data citations."""
        rationale = "Your credit_utilization signal shows 75% usage based on transaction_history."

        result = assess_rationale_quality(rationale)

        assert result["criteria_met"]["has_data_citations"] is True

    def test_assess_rationale_quality_numeric_specifics(self):
        """Test detection of numeric specifics."""
        rationale = "You spent $500 last month, which is 15% more than usual over 30 days."

        result = assess_rationale_quality(rationale)

        assert result["criteria_met"]["has_numeric_specifics"] is True
        assert len(result["citations_found"]) > 0

    def test_assess_rationale_quality_account_identifiers(self):
        """Test detection of account identifiers."""
        rationale = "Your checking account ****1234 shows irregular deposits."

        result = assess_rationale_quality(rationale)

        assert result["criteria_met"]["has_account_identifiers"] is True
        assert any("Account:" in c for c in result["citations_found"])

    def test_assess_rationale_quality_plain_language(self):
        """Test plain language readability check."""
        # Simple, readable rationale
        simple = "You can save money. Your account has a high balance. This helps you."

        result = assess_rationale_quality(simple)

        assert result["criteria_met"]["uses_plain_language"] is True
        assert result["readability_metrics"]["avg_sentence_length"] < 20

    def test_assess_rationale_quality_behavioral_signals(self):
        """Test detection of behavioral signal references."""
        rationale = "Because your spending pattern shows irregular income, we recommend budgeting."

        result = assess_rationale_quality(rationale)

        assert result["criteria_met"]["cites_behavioral_signals"] is True


class TestDecisionTraceVerification:
    """Test decision trace completeness verification."""

    def test_verify_decision_traces_complete(self):
        """Test with complete decision traces."""
        recommendations = [
            {"user_id": "user_1", "item_id": "rec_1", "persona_id": "young_professional"}
        ]

        audit_logs = [
            {"user_id": "user_1", "event_type": "persona_assignment"},
            {"user_id": "user_1", "event_type": "signals_detected"},
            {"user_id": "user_1", "event_type": "recommendation_matched"},
            {"user_id": "user_1", "event_type": "guardrail_check"},
            {"user_id": "user_1", "event_type": "recommendation_assembled"},
        ]

        result = verify_decision_traces(recommendations, audit_logs)

        assert result["completeness_rate"] == 1.0
        assert result["complete_traces"] == 1
        assert len(result["incomplete_traces"]) == 0

    def test_verify_decision_traces_incomplete(self):
        """Test with incomplete decision traces."""
        recommendations = [
            {"user_id": "user_1", "item_id": "rec_1", "persona_id": "young_professional"}
        ]

        audit_logs = [
            {"user_id": "user_1", "event_type": "persona_assignment"},
            {"user_id": "user_1", "event_type": "signals_detected"},
            # Missing: recommendation_matched, guardrail_check, recommendation_assembled
        ]

        result = verify_decision_traces(recommendations, audit_logs)

        assert result["completeness_rate"] == 0.0
        assert result["complete_traces"] == 0
        assert len(result["incomplete_traces"]) == 1
        assert len(result["incomplete_traces"][0]["missing_events"]) > 0

    def test_verify_decision_traces_empty_logs(self):
        """Test with no audit logs."""
        recommendations = [
            {"user_id": "user_1", "item_id": "rec_1", "persona_id": "young_professional"}
        ]

        result = verify_decision_traces(recommendations, [])

        assert result["completeness_rate"] == 0.0
        assert result["complete_traces"] == 0

    def test_verify_decision_traces_empty_recommendations(self):
        """Test with no recommendations."""
        result = verify_decision_traces([], [])

        assert result["completeness_rate"] == 0.0


class TestSampleRationaleExtraction:
    """Test sample rationale extraction."""

    def test_extract_sample_rationales_basic(self):
        """Test basic sample extraction."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "High quality rationale with $500 and 15% on account ****1234",
                "item_type": "education",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "young_professional",
                "rationale": "Low quality rationale",
                "item_type": "education",
            },
            {
                "user_id": "user_3",
                "item_id": "rec_3",
                "persona_id": "high_utilization",
                "rationale": "Another rationale based on your savings_balance",
                "item_type": "partner_offer",
            },
        ]

        samples = extract_sample_rationales(recommendations, samples_per_persona=2)

        assert len(samples) > 0
        assert all("quality_score" in s for s in samples)
        assert all("persona" in s for s in samples)

    def test_extract_sample_rationales_quality_diversity(self):
        """Test extraction includes quality diversity."""
        recommendations = []
        for i in range(6):
            quality = "High quality with $500 and ****1234" if i < 3 else "Low quality"
            recommendations.append(
                {
                    "user_id": f"user_{i}",
                    "item_id": f"rec_{i}",
                    "persona_id": "young_professional",
                    "rationale": quality,
                    "item_type": "education",
                }
            )

        samples = extract_sample_rationales(recommendations, samples_per_persona=3)

        quality_scores = [s["quality_score"] for s in samples]
        # Should have diversity in quality scores
        assert len(set(quality_scores)) > 1

    def test_extract_sample_rationales_empty_list(self):
        """Test with empty recommendations."""
        samples = extract_sample_rationales([])

        assert samples == []

    def test_extract_sample_rationales_no_rationales(self):
        """Test with recommendations lacking rationales."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "",
            }
        ]

        samples = extract_sample_rationales(recommendations)

        assert len(samples) == 0


class TestFailureLogging:
    """Test explainability failure logging."""

    def test_log_explainability_failures_missing_rationale(self):
        """Test logging of missing rationales."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "",
            }
        ]

        presence_metrics = {
            "missing_rationales": [
                {
                    "user_id": "user_1",
                    "item_id": "rec_1",
                    "persona": "young_professional",
                    "item_type": "education",
                }
            ]
        }

        failures = log_explainability_failures(
            recommendations, presence_metrics, {}, {}
        )

        assert len(failures) > 0
        assert failures[0]["failure_type"] == "missing_rationale"
        assert failures[0]["severity"] == "high"

    def test_log_explainability_failures_low_quality(self):
        """Test logging of low-quality rationales."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "Low quality",
                "item_type": "education",
            }
        ]

        quality_assessments = {
            "rec_1": {
                "quality_score": 1,
                "is_high_quality": False,
                "criteria_met": {
                    "has_data_citations": False,
                    "has_account_identifiers": False,
                    "has_numeric_specifics": False,
                    "uses_plain_language": True,
                    "cites_behavioral_signals": False,
                },
            }
        }

        failures = log_explainability_failures(
            recommendations, {"missing_rationales": []}, quality_assessments, {}
        )

        assert len(failures) > 0
        assert failures[0]["failure_type"] == "low_quality_rationale"
        assert failures[0]["severity"] == "medium"

    def test_log_explainability_failures_severity_ordering(self):
        """Test failures are sorted by severity."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "high_utilization",
                "rationale": "Low quality",
                "item_type": "education",
            },
        ]

        presence_metrics = {
            "missing_rationales": [
                {
                    "user_id": "user_1",
                    "item_id": "rec_1",
                    "persona": "young_professional",
                    "item_type": "education",
                }
            ]
        }

        quality_assessments = {
            "rec_2": {
                "quality_score": 1,
                "is_high_quality": False,
                "criteria_met": {
                    "has_data_citations": False,
                    "has_account_identifiers": False,
                    "has_numeric_specifics": False,
                    "uses_plain_language": True,
                    "cites_behavioral_signals": False,
                },
            }
        }

        failures = log_explainability_failures(
            recommendations, presence_metrics, quality_assessments, {}
        )

        # High severity should come first
        assert failures[0]["severity"] == "high"


class TestImprovementRecommendations:
    """Test improvement recommendation generation."""

    def test_generate_improvement_recommendations_low_presence(self):
        """Test recommendations for low rationale presence."""
        presence_metrics = {"overall_rate": 0.7}

        recommendations = generate_improvement_recommendations(
            presence_metrics, {}, {}, []
        )

        assert len(recommendations) > 0
        assert any("HIGH PRIORITY" in r for r in recommendations)
        assert any("rationale generation" in r.lower() for r in recommendations)

    def test_generate_improvement_recommendations_low_quality(self):
        """Test recommendations for low quality scores."""
        presence_metrics = {"overall_rate": 1.0, "by_persona": {}}
        quality_assessments = {
            "rec_1": {"quality_score": 2},
            "rec_2": {"quality_score": 1},
        }

        recommendations = generate_improvement_recommendations(
            presence_metrics, quality_assessments, {}, []
        )

        assert len(recommendations) > 0
        assert any("quality score" in r.lower() for r in recommendations)

    def test_generate_improvement_recommendations_low_trace_completeness(self):
        """Test recommendations for incomplete decision traces."""
        presence_metrics = {"overall_rate": 1.0, "by_persona": {}}
        trace_metrics = {"completeness_rate": 0.8}

        recommendations = generate_improvement_recommendations(
            presence_metrics, {}, trace_metrics, []
        )

        assert len(recommendations) > 0
        assert any("audit" in r.lower() for r in recommendations)

    def test_generate_improvement_recommendations_all_good(self):
        """Test recommendations when all metrics are good."""
        presence_metrics = {"overall_rate": 1.0, "by_persona": {}}
        quality_assessments = {"rec_1": {"quality_score": 5}}
        trace_metrics = {"completeness_rate": 1.0}

        recommendations = generate_improvement_recommendations(
            presence_metrics, quality_assessments, trace_metrics, []
        )

        assert len(recommendations) > 0
        assert any("SUCCESS" in r for r in recommendations)


class TestCalculateExplainabilityMetrics:
    """Test main explainability metrics calculation."""

    def test_calculate_explainability_metrics_complete(self):
        """Test complete metrics calculation."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "Based on your credit_utilization of 68% on account ****4523, "
                "we recommend this because you have $3,400 in debt.",
                "item_type": "education",
            },
            {
                "user_id": "user_2",
                "item_id": "rec_2",
                "persona_id": "high_utilization",
                "rationale": "Your savings_balance shows $5,000 available.",
                "item_type": "partner_offer",
            },
        ]

        audit_logs = [
            {"user_id": "user_1", "event_type": "persona_assignment"},
            {"user_id": "user_1", "event_type": "signals_detected"},
            {"user_id": "user_2", "event_type": "persona_assignment"},
        ]

        metrics = calculate_explainability_metrics(recommendations, audit_logs)

        assert isinstance(metrics, ExplainabilityMetrics)
        assert metrics.rationale_presence_rate > 0
        assert metrics.rationale_quality_score >= 0
        assert len(metrics.explainability_by_persona) > 0
        assert len(metrics.improvement_recommendations) > 0
        assert isinstance(metrics.timestamp, datetime)

    def test_calculate_explainability_metrics_empty(self):
        """Test with empty recommendations."""
        metrics = calculate_explainability_metrics([])

        assert isinstance(metrics, ExplainabilityMetrics)
        assert metrics.rationale_presence_rate == 0.0
        assert metrics.rationale_quality_score == 0.0
        assert len(metrics.improvement_recommendations) > 0

    def test_calculate_explainability_metrics_to_dict(self):
        """Test metrics serialization to dict."""
        recommendations = [
            {
                "user_id": "user_1",
                "item_id": "rec_1",
                "persona_id": "young_professional",
                "rationale": "Valid rationale with data",
                "item_type": "education",
            }
        ]

        metrics = calculate_explainability_metrics(recommendations)
        metrics_dict = metrics.to_dict()

        assert isinstance(metrics_dict, dict)
        assert "timestamp" in metrics_dict
        assert "rationale_presence_rate" in metrics_dict
        assert "rationale_quality_score" in metrics_dict
