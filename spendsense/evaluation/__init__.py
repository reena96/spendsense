"""
Evaluation harness for measuring recommendation system quality and performance.

This module provides comprehensive evaluation metrics including:
- Coverage metrics: Persona assignment and signal detection rates
- Explainability metrics: Rationale quality and transparency
- Performance metrics: Latency and throughput
- Auditability metrics: Compliance and regulatory reporting
- Fairness metrics: Bias detection and analysis
"""

from spendsense.evaluation.coverage_metrics import (
    CoverageMetrics,
    calculate_coverage_metrics,
    save_coverage_metrics,
    load_previous_metrics,
    calculate_coverage_trends
)

from spendsense.evaluation.performance_metrics import (
    PerformanceMetrics,
    PerformanceEvaluator,
    measure_component_latency,
    calculate_throughput,
    track_resource_utilization
)

from spendsense.evaluation.explainability_metrics import (
    ExplainabilityMetrics,
    calculate_explainability_metrics,
    calculate_rationale_presence,
    assess_rationale_quality,
    verify_decision_traces,
    extract_sample_rationales,
    log_explainability_failures,
    generate_improvement_recommendations
)

from spendsense.evaluation.auditability_metrics import (
    AuditabilityMetrics,
    AuditabilityEvaluator,
    ComplianceFailure,
    ComplianceSeverity,
    ComplianceStatus,
    DecisionTraceAnalysis,
    GuardrailComplianceReport,
    AuditLogAnalysis,
    RecommendationAgeStats,
    generate_compliance_report
)

from spendsense.evaluation.fairness_metrics import (
    FairnessMetrics,
    analyze_fairness,
    calculate_demographic_parity,
    calculate_equal_opportunity,
    POSITIVE_PERSONAS,
    NEGATIVE_PERSONAS
)

__all__ = [
    'CoverageMetrics',
    'calculate_coverage_metrics',
    'save_coverage_metrics',
    'load_previous_metrics',
    'calculate_coverage_trends',
    'PerformanceMetrics',
    'PerformanceEvaluator',
    'measure_component_latency',
    'calculate_throughput',
    'track_resource_utilization',
    'ExplainabilityMetrics',
    'calculate_explainability_metrics',
    'calculate_rationale_presence',
    'assess_rationale_quality',
    'verify_decision_traces',
    'extract_sample_rationales',
    'log_explainability_failures',
    'generate_improvement_recommendations',
    'AuditabilityMetrics',
    'AuditabilityEvaluator',
    'ComplianceFailure',
    'ComplianceSeverity',
    'ComplianceStatus',
    'DecisionTraceAnalysis',
    'GuardrailComplianceReport',
    'AuditLogAnalysis',
    'RecommendationAgeStats',
    'generate_compliance_report',
    'FairnessMetrics',
    'analyze_fairness',
    'calculate_demographic_parity',
    'calculate_equal_opportunity',
    'POSITIVE_PERSONAS',
    'NEGATIVE_PERSONAS',
]
