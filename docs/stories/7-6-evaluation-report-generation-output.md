# Story 7.6: Evaluation Report Generation & Output

Status: drafted

## Story

As a **product manager**,
I want **automated generation of comprehensive evaluation report with all metrics and analysis**,
so that **system quality can be assessed and communicated to stakeholders**.

## Acceptance Criteria

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

## Tasks / Subtasks

- [ ] Task 1: Create master evaluation orchestrator (AC: #1, #11)
  - [ ] Create `spendsense/evaluation/evaluator.py`
  - [ ] Define `EvaluationOrchestrator` class that coordinates all evaluation modules
  - [ ] Implement `run_full_evaluation()` method:
    - Execute coverage metrics (Story 7.1)
    - Execute explainability metrics (Story 7.2)
    - Execute performance metrics (Story 7.3)
    - Execute auditability metrics (Story 7.4)
    - Execute fairness metrics (Story 7.5)
  - [ ] Handle failures gracefully: continue if one module fails, report error
  - [ ] Aggregate all results into single evaluation output
  - [ ] Support configuration: which modules to run, output format

- [ ] Task 2: Implement JSON metrics output (AC: #2)
  - [ ] Create consolidated JSON output format:
    ```json
    {
      "evaluation_metadata": {
        "timestamp": "2025-11-06T10:30:00Z",
        "dataset": "synthetic_50_users",
        "reproducibility_seed": 42,
        "evaluation_version": "1.0.0"
      },
      "coverage_metrics": { ... },
      "explainability_metrics": { ... },
      "performance_metrics": { ... },
      "auditability_metrics": { ... },
      "fairness_metrics": { ... },
      "overall_assessment": {
        "score": 85,
        "grade": "B",
        "status": "PASS_WITH_WARNINGS"
      }
    }
    ```
  - [ ] Save to `docs/eval/evaluation_results_{timestamp}.json`
  - [ ] Validate JSON schema before saving
  - [ ] Pretty-print for readability

- [ ] Task 3: Implement CSV summary output (AC: #3)
  - [ ] Create CSV format for spreadsheet analysis:
    - Columns: metric_category, metric_name, value, target, status, notes
    - Example rows:
      - coverage, persona_assignment_rate, 0.98, 1.0, PASS, "2% missing personas"
      - explainability, rationale_presence_rate, 1.0, 1.0, PASS, "All recommendations have rationales"
      - performance, avg_latency_seconds, 3.2, 5.0, PASS, "Well under target"
      - auditability, consent_compliance, 1.0, 1.0, PASS, "No consent violations"
      - fairness, demographic_parity_ratio, 0.85, 0.8, PASS, "Acceptable parity"
  - [ ] Save to `docs/eval/evaluation_summary_{timestamp}.csv`
  - [ ] Include all key metrics from all modules
  - [ ] Add status column: PASS/WARN/FAIL

- [ ] Task 4: Export per-user decision traces (AC: #4)
  - [ ] For each user, compile decision trace:
    - user_id
    - persona_assigned
    - behavioral_signals_detected: [list]
    - recommendations_generated: [list with rationales]
    - guardrail_checks: {consent, eligibility, tone, disclaimer}
    - audit_log_entries: [list]
  - [ ] Format as JSON Lines (JSONL) for large datasets
  - [ ] Save to `docs/eval/decision_traces_{timestamp}.jsonl`
  - [ ] Include top 10-20 users as samples, or all if dataset is small (<100 users)
  - [ ] Useful for debugging and manual review

- [ ] Task 5: Generate executive summary report (AC: #5, #6, #7)
  - [ ] Create Markdown report template (1-2 pages)
  - [ ] Report structure:
    - **Title**: SpendSense Evaluation Report
    - **Date & Dataset**: Timestamp, dataset name, user count
    - **Overall Assessment**: Score, grade, status
    - **Coverage Metrics**: Persona assignment rate, signal detection rate, status
    - **Explainability Metrics**: Rationale presence, quality score, status
    - **Performance Metrics**: Latency, throughput, status
    - **Auditability Metrics**: Compliance rates (consent, eligibility, tone), status
    - **Fairness Metrics**: Demographic parity, bias indicators, status
    - **Success Criteria Summary**: Table with target met/not met per metric
  - [ ] Use clear visual indicators: ✅ PASS, ⚠️ WARN, ❌ FAIL
  - [ ] Save to `docs/eval/evaluation_report_{timestamp}.md`

- [ ] Task 6: Add failure case analysis section (AC: #8)
  - [ ] In summary report, add "Failure Analysis" section:
    - List all failed or warning metrics
    - For each failure, provide:
      - Metric name and value
      - Target value
      - Gap analysis (how far from target)
      - Affected users or recommendations
      - Root cause (if identifiable)
  - [ ] Add "Improvement Recommendations" section:
    - Aggregate recommendations from all modules
    - Prioritize by severity: CRITICAL > HIGH > MEDIUM
    - Provide actionable next steps with code module references
  - [ ] Include examples of failure cases for debugging

- [ ] Task 7: Document assumptions and limitations (AC: #9)
  - [ ] Add "Assumptions & Limitations" section to report:
    - **Data Limitations**: "Synthetic data may not reflect real-world complexity"
    - **Sample Size**: "Small dataset (50-100 users) limits statistical power"
    - **Fairness Constraints**: "Limited demographic data for bias analysis"
    - **Performance Context**: "Latency measured on local laptop, cloud performance may differ"
    - **Temporal Validity**: "Evaluation snapshot at specific timestamp, system may evolve"
  - [ ] Document methodology assumptions:
    - Quality scoring criteria
    - Bias detection thresholds
    - Success criteria definitions
  - [ ] Include in summary report and JSON output

- [ ] Task 8: Implement reproducibility controls (AC: #10)
  - [ ] Accept `--seed` parameter for random seed
  - [ ] Set seed for all randomness sources:
    - Python random module
    - NumPy random
    - Synthetic data generation (if re-generating data)
  - [ ] Document seed in evaluation metadata
  - [ ] Verify reproducibility: run twice with same seed, compare results
  - [ ] Log seed to console and in all output files

- [ ] Task 9: Optional PDF report generation (AC: #5)
  - [ ] Add optional PDF export functionality
  - [ ] Use markdown-to-PDF converter (e.g., `mdpdf`, `weasyprint`)
  - [ ] Accept `--format pdf` CLI flag
  - [ ] Include visualizations from performance and fairness modules
  - [ ] Save to `docs/eval/evaluation_report_{timestamp}.pdf`
  - [ ] Fallback to Markdown if PDF generation fails

- [ ] Task 10: Create master CLI script (AC: #11)
  - [ ] Create `scripts/run_evaluation.py`
  - [ ] Accept CLI args:
    - `--dataset` (synthetic/real)
    - `--output-dir` (default: docs/eval/)
    - `--seed` (for reproducibility)
    - `--modules` (all/coverage/explainability/performance/auditability/fairness)
    - `--format` (json/csv/markdown/pdf/all)
    - `--verbose` (detailed logging)
  - [ ] Run full evaluation pipeline
  - [ ] Generate all outputs
  - [ ] Print progress indicators
  - [ ] Print final summary to console:
    - Overall score: X/100
    - Status: PASS/WARN/FAIL
    - Key findings (top 3-5)
    - Output files generated
  - [ ] Exit with code 0 if PASS, 1 if WARN, 2 if FAIL

- [ ] Task 11: Implement evaluation scoring system (AC: #7)
  - [ ] Define scoring rubric (0-100 points):
    - Coverage: 20 points (persona assignment + signal detection)
    - Explainability: 20 points (rationale presence + quality)
    - Performance: 15 points (latency target met)
    - Auditability: 25 points (consent + guardrails compliance)
    - Fairness: 20 points (demographic parity + no bias)
  - [ ] Calculate total score from module metrics
  - [ ] Assign grade: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)
  - [ ] Determine status:
    - PASS: Score ≥80, no critical failures
    - PASS_WITH_WARNINGS: Score ≥70, some warnings
    - FAIL: Score <70 or any critical failures
  - [ ] Include in JSON output and summary report

- [ ] Task 12: Add visualization aggregation (AC: #5)
  - [ ] Collect all visualizations generated by modules:
    - Performance: latency_distribution.png, component_breakdown.png
    - Fairness: persona_distribution_by_demographics.png, demographic_parity.png
  - [ ] Reference visualizations in summary report with inline links
  - [ ] Optionally embed visualizations in PDF report
  - [ ] Create master visualization index in report

- [ ] Task 13: Write comprehensive unit tests (AC: #1-11)
  - [ ] Create `tests/evaluation/test_evaluator.py`
  - [ ] Test `EvaluationOrchestrator.run_full_evaluation()` with mock modules
  - [ ] Test JSON output generation and schema validation
  - [ ] Test CSV output generation and format
  - [ ] Test decision trace export with mock data
  - [ ] Test summary report generation
  - [ ] Test scoring system calculation
  - [ ] Test reproducibility with fixed seed
  - [ ] Test error handling: module failures, missing data
  - [ ] Test CLI script argument parsing
  - [ ] Test edge cases:
    - Empty dataset
    - All metrics pass
    - All metrics fail
    - Partial module execution

- [ ] Task 14: Integration testing and documentation (AC: #11)
  - [ ] Test full evaluation pipeline end-to-end:
    - Run `python scripts/run_evaluation.py --dataset synthetic --seed 42`
    - Verify all output files generated
    - Verify JSON structure and completeness
    - Verify CSV format and metrics
    - Verify summary report readability
  - [ ] Document evaluation usage in README:
    - Quick start: single command to run evaluation
    - Output files explained
    - Interpreting results
    - Troubleshooting common issues
  - [ ] Create example evaluation output for reference

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**
- **Backend:** Python 3.10+ with type hints
- **Output Formats:** JSON, CSV, Markdown, PDF (optional)
- **File Storage:** Local filesystem at `docs/eval/`
- **Testing:** pytest with ≥10 tests per story

**From PRD:**
- Goal: Comprehensive evaluation system measuring quality and compliance
- Reproducibility: Fixed seed for consistent results
- Stakeholder communication: Clear reports for product managers, compliance officers

**Key Requirements:**
- Single command evaluation execution
- Multiple output formats (JSON, CSV, Markdown, PDF)
- Per-user decision traces for debugging
- Overall assessment with score and grade
- Reproducibility with seed control

### Project Structure Notes

**New Files to Create:**
- `spendsense/evaluation/evaluator.py` - Master orchestrator
- `scripts/run_evaluation.py` - CLI script (master evaluation command)
- `tests/evaluation/test_evaluator.py` - Unit tests
- `docs/eval/evaluation_results_{timestamp}.json` - JSON output
- `docs/eval/evaluation_summary_{timestamp}.csv` - CSV output
- `docs/eval/decision_traces_{timestamp}.jsonl` - Decision traces
- `docs/eval/evaluation_report_{timestamp}.md` - Summary report
- `docs/eval/evaluation_report_{timestamp}.pdf` - PDF report (optional)

**Files to Reference:**
- `spendsense/evaluation/coverage_metrics.py` - Story 7.1
- `spendsense/evaluation/explainability_metrics.py` - Story 7.2
- `spendsense/evaluation/performance_metrics.py` - Story 7.3
- `spendsense/evaluation/auditability_metrics.py` - Story 7.4
- `spendsense/evaluation/fairness_metrics.py` - Story 7.5
- `scripts/evaluate_coverage.py` - Individual module scripts
- `scripts/evaluate_explainability.py`
- `scripts/evaluate_performance.py`
- `scripts/evaluate_auditability.py`
- `scripts/evaluate_fairness.py`

**Dependencies:**
- `mdpdf` or `weasyprint` - PDF generation (optional, add to requirements.txt)
- Standard library: `json`, `csv`, `random`
- Previously added: `psutil`, `matplotlib`, `scipy`, `numpy`

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest
- Coverage target: ≥10 tests per story
- Test types:
  1. Unit tests: Individual orchestrator methods
  2. Integration tests: Full evaluation pipeline
  3. Output tests: JSON/CSV format validation
  4. Reproducibility tests: Seed-based consistency

**Test Categories:**
1. Orchestrator: Module execution sequencing
2. JSON output: Schema validation and completeness
3. CSV output: Format and metrics coverage
4. Report generation: Markdown structure
5. Scoring system: Calculation accuracy
6. Reproducibility: Seed-based determinism
7. Error handling: Graceful degradation

### Learnings from Previous Stories

**From Story 7.1 (Coverage Metrics Calculation):**
- **Module Structure**: Individual evaluation modules in `spendsense/evaluation/`
- **CLI Pattern**: `scripts/evaluate_*.py` with consistent args
- **JSON Output**: Timestamp, dataset, metrics structure

**From Story 7.2 (Explainability Metrics Calculation):**
- **Quality Assessment**: Scoring systems (0-5 scale)
- **Sample Extraction**: Representative examples for review

**From Story 7.3 (Performance & Latency Metrics):**
- **Visualization**: matplotlib PNG charts
- **Statistical Analysis**: Percentiles and distributions

**From Story 7.4 (Auditability & Compliance Metrics):**
- **Compliance Checks**: Pass/fail status with severity
- **Failure Categorization**: CRITICAL/HIGH/MEDIUM

**From Story 7.5 (Fairness & Bias Analysis):**
- **Conditional Analysis**: Graceful handling of missing data
- **Limitations Documentation**: Transparent constraints
- **Mitigation Recommendations**: Actionable next steps

**Integration Points:**
- All five previous stories (7.1-7.5) provide evaluation modules
- Each module has individual CLI script for standalone execution
- This story orchestrates all modules and generates unified report

**Technical Patterns to Follow:**
- Type hints for all functions (Python 3.10+)
- Pydantic models for data validation
- JSON output with ISO 8601 timestamps
- Markdown formatting for readability
- Exit codes for CI/CD integration

### References

- [Source: docs/prd/epic-7-evaluation-harness-metrics.md#Story-7.6] - Story 7.6 acceptance criteria
- [Source: docs/architecture.md] - Evaluation system design
- [Source: spendsense/evaluation/coverage_metrics.py] - Story 7.1 module
- [Source: spendsense/evaluation/explainability_metrics.py] - Story 7.2 module
- [Source: spendsense/evaluation/performance_metrics.py] - Story 7.3 module
- [Source: spendsense/evaluation/auditability_metrics.py] - Story 7.4 module
- [Source: spendsense/evaluation/fairness_metrics.py] - Story 7.5 module
- [Source: docs/stories/7-1-coverage-metrics-calculation.md] - Previous story
- [Source: docs/stories/7-2-explainability-metrics-calculation.md] - Previous story
- [Source: docs/stories/7-3-performance-latency-metrics.md] - Previous story
- [Source: docs/stories/7-4-auditability-compliance-metrics.md] - Previous story
- [Source: docs/stories/7-5-fairness-bias-analysis.md] - Previous story

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- Will be filled in by dev agent -->

### Debug Log References

<!-- Will be filled in by dev agent -->

### Completion Notes List

<!-- Will be filled in by dev agent during implementation -->

### File List

<!-- Will be filled in by dev agent:
NEW: List new files created
MODIFIED: List files modified
DELETED: List files deleted (if any)
-->

## Change Log

**2025-11-06 - v1.0 - Story Drafted**
- Initial story creation from Epic 7 PRD
- Epic 7.6: Final story in evaluation harness epic (orchestration and reporting)
- 14 task groups with 70+ subtasks
- Master evaluation orchestrator coordinates all modules (Stories 7.1-7.5)
- JSON metrics output with consolidated results
- CSV summary for spreadsheet analysis
- Per-user decision traces for debugging
- Executive summary report (Markdown/PDF) with key findings
- Scoring system (0-100) with grade assignment (A-F)
- Success criteria status tracking (target met/not met)
- Failure case analysis with improvement recommendations
- Assumptions and limitations documentation
- Reproducibility controls with fixed seed
- Single command execution: `run_evaluation.py`
- Multiple output formats: JSON, CSV, Markdown, PDF
- Visualization aggregation from performance and fairness modules
- Integration of all Epic 7 evaluation modules
- Comprehensive testing with end-to-end pipeline validation
- Status: drafted (ready for story-context workflow)
