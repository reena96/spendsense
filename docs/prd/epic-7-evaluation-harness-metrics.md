# Epic 7: Evaluation Harness & Metrics

**Goal:** Create comprehensive evaluation system measuring recommendation quality, system performance, and ethical compliance. Generate reproducible metrics reports with fairness analysis and per-user decision traces for transparency and continuous improvement.

## Story 7.1: Coverage Metrics Calculation

As a **data scientist**,
I want **calculation of user coverage metrics showing persona assignment and behavioral signal detection rates**,
so that **system completeness and data quality can be quantified**.

### Acceptance Criteria

1. Coverage metric calculated: % of users with assigned persona (target 100%)
2. Coverage metric calculated: % of users with ≥3 detected behavioral signals (target 100%)
3. Coverage by persona calculated: distribution of users across 5 personas
4. Coverage by time window calculated: 30-day vs. 180-day completion rates
5. Missing data analysis performed: users with insufficient history
6. Coverage metrics computed for both synthetic test dataset and any real data
7. Metrics stored in JSON format with timestamp
8. Coverage trends tracked over time if multiple evaluation runs
9. Unit tests verify calculation accuracy
10. Failure case reporting: list of users missing signals or personas with reasons

## Story 7.2: Explainability Metrics Calculation

As a **data scientist**,
I want **measurement of recommendation explainability ensuring all outputs have transparent rationales**,
so that **system transparency can be verified and rationale quality can be assessed**.

### Acceptance Criteria

1. Explainability metric calculated: % of recommendations with rationales (target 100%)
2. Rationale quality check: presence of concrete data citations in each rationale
3. Rationale completeness check: signal values, account identifiers, numeric specifics included
4. Explainability by persona calculated: rationale presence across all persona types
5. Decision trace completeness verified: all recommendations have full audit trail
6. Explainability failures logged: recommendations missing or incomplete rationales
7. Sample rationales extracted for manual quality review
8. Metrics stored in JSON format with examples
9. Unit tests verify calculation and quality checks
10. Improvement recommendations generated for low-quality rationales

## Story 7.3: Performance & Latency Metrics

As a **developer**,
I want **measurement of system performance including recommendation generation latency**,
so that **user experience quality and scalability limits can be assessed**.

### Acceptance Criteria

1. Latency metric measured: time to generate recommendations per user (target <5 seconds)
2. Latency breakdown by component: signal detection, persona assignment, recommendation matching, guardrail checks
3. Performance metrics: throughput (users processed per minute)
4. Resource utilization tracked: memory, CPU during batch processing
5. Performance tested with full 50-100 user synthetic dataset
6. Latency percentiles calculated: p50, p95, p99
7. Performance bottlenecks identified if latency exceeds target
8. Metrics compared across multiple runs to verify consistency
9. Performance report generated with visualization of latency distribution
10. Scalability projections documented: estimated performance at 1K, 10K, 100K users

## Story 7.4: Auditability & Compliance Metrics

As a **compliance officer**,
I want **verification that all recommendations are fully auditable with complete decision traces**,
so that **regulatory compliance and ethical transparency can be demonstrated**.

### Acceptance Criteria

1. Auditability metric calculated: % of recommendations with decision traces (target 100%)
2. Consent compliance verified: 0% processing without consent
3. Eligibility compliance measured: % of recommendations passing eligibility checks
4. Tone compliance measured: % of recommendations passing tone validation
5. Disclaimer presence verified: 100% of recommendations include mandatory disclaimer
6. Audit log completeness verified: all user actions and system decisions logged
7. Compliance failures categorized: consent violations, eligibility issues, tone problems
8. Compliance report generated with pass/fail status per guardrail
9. Recommendation age tracked: time from generation to delivery
10. Data retention compliance verified: audit logs persisted per policy

## Story 7.5: Fairness & Bias Analysis

As a **data scientist**,
I want **analysis of recommendation fairness across demographic groups if applicable**,
so that **potential bias in persona assignment or recommendations can be detected and mitigated**.

### Acceptance Criteria

1. Demographic parity calculated if synthetic data includes demographic attributes
2. Persona distribution analyzed by demographic group
3. Recommendation distribution analyzed by demographic group
4. Statistical significance tested for observed differences
5. Potential bias indicators flagged if disparities exceed threshold
6. Fairness metrics computed: demographic parity ratio, equal opportunity difference
7. Bias analysis documented with interpretation of results
8. Limitations documented: fairness analysis constraints with synthetic data
9. Fairness report generated with visualizations
10. Mitigation recommendations provided if bias detected

## Story 7.6: Evaluation Report Generation & Output

As a **product manager**,
I want **automated generation of comprehensive evaluation report with all metrics and analysis**,
so that **system quality can be assessed and communicated to stakeholders**.

### Acceptance Criteria

1. Evaluation script executes all metric calculations in sequence
2. JSON metrics file generated with structured results
3. CSV summary file generated for spreadsheet analysis
4. Per-user decision traces exported showing full recommendation logic
5. 1-2 page summary report generated (Markdown/PDF) with key findings
6. Report includes: coverage, explainability, latency, auditability, fairness metrics
7. Report includes: success criteria status (target met/not met per metric)
8. Report includes: failure case analysis and improvement recommendations
9. Report includes: assumptions and limitations documentation
10. Evaluation reproducible with fixed seed for synthetic data generation
11. Evaluation runs via single command with results in `docs/eval/` directory

---
