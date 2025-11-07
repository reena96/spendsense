# Story 7.2: Explainability Metrics Calculation

Status: review

## Story

As a **data scientist**,
I want **measurement of recommendation explainability ensuring all outputs have transparent rationales**,
so that **system transparency can be verified and rationale quality can be assessed**.

## Acceptance Criteria

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

## Tasks / Subtasks

- [x] Task 1: Create explainability metrics module (AC: #1-10)
  - [x] Create `spendsense/evaluation/explainability_metrics.py`
  - [x] Define `ExplainabilityMetrics` dataclass with fields:
    - `rationale_presence_rate`: float
    - `rationale_quality_score`: float
    - `explainability_by_persona`: Dict[str, float]
    - `decision_trace_completeness`: float
    - `failure_cases`: List[Dict]
    - `sample_rationales`: List[Dict]
    - `improvement_recommendations`: List[str]
    - `timestamp`: datetime
  - [x] Implement `calculate_rationale_presence()` function
  - [x] Implement `assess_rationale_quality()` function
  - [x] Implement `verify_decision_traces()` function
  - [x] Implement `extract_sample_rationales()` function

- [x] Task 2: Implement rationale presence check (AC: #1, #4)
  - [x] Load all recommendations from database/output files
  - [x] For each recommendation, check if rationale field is non-empty
  - [x] Calculate % with rationales (target 100%)
  - [x] Group by persona and calculate per-persona rates
  - [x] Identify recommendations missing rationales
  - [x] Return structured metrics with persona breakdown

- [x] Task 3: Implement rationale quality assessment (AC: #2, #3)
  - [x] Define quality criteria checklist:
    - Contains concrete data citations (signal names, values)
    - Includes account identifiers or transaction details
    - Provides numeric specifics (amounts, percentages, dates)
    - Uses plain language (grade-8 readability per FR22)
    - Cites specific behavioral signals
  - [x] For each rationale, score against checklist (0-5 points)
  - [x] Calculate average quality score across all rationales
  - [x] Identify low-quality rationales (score <3)
  - [x] Generate detailed quality report per recommendation

- [x] Task 4: Verify decision trace completeness (AC: #5)
  - [x] Load audit logs from database (Epic 6 audit trail)
  - [x] For each recommendation, verify audit trail exists:
    - Persona assignment decision logged
    - Behavioral signals detected and logged
    - Recommendation matching logic logged
    - Guardrail checks logged (consent, eligibility, tone)
    - Final recommendation assembly logged
  - [x] Calculate % with complete decision traces
  - [x] Identify recommendations with incomplete traces
  - [x] Return trace completeness metrics

- [x] Task 5: Extract and analyze sample rationales (AC: #7)
  - [x] Select representative samples:
    - 2-3 rationales per persona (12-18 total for 6 personas)
    - Include both high-quality and low-quality examples
    - Cover different recommendation types (education, partner offers)
  - [x] Extract full rationale text
  - [x] Include metadata: user_id, persona, recommendation_type, quality_score
  - [x] Format for manual review in JSON output
  - [x] Highlight quality strengths and weaknesses per sample

- [x] Task 6: Log explainability failures (AC: #6)
  - [x] For each failure case, record:
    - recommendation_id
    - user_id
    - persona
    - failure_type: "missing_rationale", "incomplete_rationale", "low_quality_rationale", "missing_decision_trace"
    - details: specific issues identified
    - severity: high/medium/low
  - [x] Group failures by type and persona
  - [x] Sort by severity for prioritization
  - [x] Include in JSON output for debugging

- [x] Task 7: Generate improvement recommendations (AC: #10)
  - [x] Analyze failure patterns:
    - If >10% missing rationales → "Review rationale generation logic in recommendation engine"
    - If quality score <3 average → "Enhance data citation specificity"
    - If incomplete traces → "Verify audit logging in guardrail pipeline"
    - If persona-specific issues → "Review persona-specific rationale templates"
  - [x] Generate actionable recommendations with priority
  - [x] Reference specific code modules that need attention
  - [x] Include in JSON output for development team

- [x] Task 8: Implement metrics storage (AC: #8)
  - [x] Create JSON output format with schema:
    ```json
    {
      "timestamp": "2025-11-06T10:30:00Z",
      "dataset": "synthetic_50_users",
      "explainability_metrics": {
        "rationale_presence_rate": 0.98,
        "average_quality_score": 4.2,
        "explainability_by_persona": {
          "high_utilization": 1.0,
          "variable_income": 0.97,
          ...
        },
        "decision_trace_completeness": 0.99
      },
      "failure_cases": [...],
      "sample_rationales": [...],
      "improvement_recommendations": [...]
    }
    ```
  - [x] Save to `docs/eval/explainability_metrics_{timestamp}.json`
  - [x] Include sample rationales for manual review
  - [x] Format for readability and debugging

- [x] Task 9: Create CLI script for explainability evaluation (AC: #1-10)
  - [x] Create `scripts/evaluate_explainability.py`
  - [x] Accept CLI args: --dataset, --output-dir, --sample-count
  - [x] Load recommendations from database or JSON files
  - [x] Run explainability metric calculations
  - [x] Save results to JSON
  - [x] Print summary to console:
    - Rationale presence rate: X%
    - Average quality score: X/5
    - Decision trace completeness: X%
    - Failure cases: N
  - [x] Exit with code 0 if all targets met, 1 otherwise

- [x] Task 10: Write comprehensive unit tests (AC: #9)
  - [x] Create `tests/evaluation/test_explainability_metrics.py`
  - [x] Test `calculate_rationale_presence()` with various scenarios
  - [x] Test `assess_rationale_quality()` scoring logic
  - [x] Test quality criteria: data citations, numeric specifics, account identifiers
  - [x] Test `verify_decision_traces()` with complete and incomplete traces
  - [x] Test `extract_sample_rationales()` selection logic
  - [x] Test edge cases:
    - All recommendations have rationales (100%)
    - No recommendations have rationales (0%)
    - Mixed quality scores (1-5 range)
    - Missing decision traces
  - [x] Test JSON serialization of sample rationales
  - [x] Verify improvement recommendation generation

- [x] Task 11: Integration with existing system (AC: #1-10)
  - [x] Verify compatibility with recommendation engine (Epic 4)
  - [x] Verify compatibility with audit trail system (Epic 6, Story 6.5)
  - [x] Test with full recommendation output dataset
  - [x] Ensure references to rationale generation module (Story 4.4)
  - [x] Test with different personas and recommendation types

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**
- **Backend:** Python 3.10+ with type hints
- **Database:** SQLite with recommendations, audit_log tables
- **Output Format:** JSON for structured metrics with sample rationales
- **File Storage:** Local filesystem at `docs/eval/`
- **Testing:** pytest with ≥10 tests per story

**From PRD (FR21-FR22):**
- FR21: Include concrete "because" rationale for every recommendation citing specific data signals
- FR22: Use plain-language explanations with grade-8 readability
- Target: 100% of recommendations have rationales

**Key Requirements:**
- Rationale presence: 100% target
- Quality criteria: data citations, numeric specifics, account identifiers
- Decision trace completeness: full audit trail per recommendation
- Sample extraction for manual quality review

### Project Structure Notes

**New Files to Create:**
- `spendsense/evaluation/explainability_metrics.py` - Explainability calculation logic
- `scripts/evaluate_explainability.py` - CLI script
- `tests/evaluation/test_explainability_metrics.py` - Unit tests
- `docs/eval/explainability_metrics_{timestamp}.json` - Output file

**Files to Reference:**
- `spendsense/recommendations/recommendation_engine.py` - Recommendation generation (Epic 4)
- `spendsense/recommendations/rationale_generator.py` - Rationale generation (Story 4.4)
- `data/spendsense.db` - SQLite database with recommendations table
- `spendsense/models/audit_log.py` - Audit trail (Epic 6, Story 6.5)

**Database Tables:**
- `recommendations` - recommendation_id, user_id, persona, content, rationale, created_at
- `audit_log` - event_id, user_id, event_type, event_data, timestamp
- `users` - user_id, persona

**Integration Points:**
- Epic 4 (Story 4.4): Rationale generation engine produces "because" explanations
- Epic 6 (Story 6.5): Audit trail logs decision traces
- Epic 3: Persona assignment system (6 personas for breakdown)

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest
- Coverage target: ≥10 tests per story
- Test types:
  1. Unit tests: Quality scoring, rationale parsing
  2. Integration tests: End-to-end explainability evaluation
  3. Edge case tests: Missing rationales, incomplete traces
  4. Quality assessment tests: Scoring against criteria

**Test Categories:**
1. Rationale presence: Counting and percentage calculation
2. Quality assessment: Scoring logic for 5-point scale
3. Decision trace verification: Audit log completeness
4. Sample extraction: Representative selection
5. Failure logging: Correct categorization
6. Improvement recommendations: Pattern-based generation

### Learnings from Previous Story

**From Story 7.1 (Coverage Metrics Calculation):**
- **New Module Created**: `spendsense/evaluation/` for evaluation harness
- **JSON Output Pattern**: Timestamp, dataset name, metrics, failure cases structure
- **CLI Script Pattern**: `scripts/evaluate_*.py` with --dataset and --output-dir args
- **Exit Codes**: 0 for success (targets met), 1 for failure
- **Test Structure**: `tests/evaluation/test_*.py` with ≥10 tests
- **Reuse**: Can import common evaluation utilities from 7.1 module

**Key System Components Available:**
- Epic 4: Recommendation engine generates recommendations with rationales
- Story 4.4: Rationale generation engine (may be in backlog, verify implementation)
- Epic 6 (Story 6.5): Audit trail system logs all decision traces
- SQLite database: Contains recommendations and audit_log tables

**Technical Patterns to Follow:**
- Type hints for all functions (Python 3.10+)
- Pydantic models for data validation
- JSON output with ISO 8601 timestamps
- CLI scripts in `scripts/` directory
- Test files mirror source structure

### References

- [Source: docs/prd/epic-7-evaluation-harness-metrics.md#Story-7.2] - Story 7.2 acceptance criteria
- [Source: docs/prd.md#FR21-FR22] - Rationale and readability requirements
- [Source: docs/prd.md#FR12-FR17] - 6 persona types for breakdown
- [Source: docs/architecture.md] - Python 3.10+, SQLite, pytest
- [Source: spendsense/recommendations/rationale_generator.py] - Rationale generation logic (Story 4.4)
- [Source: spendsense/models/audit_log.py] - Audit trail integration (Story 6.5)
- [Source: docs/stories/7-1-coverage-metrics-calculation.md] - Previous story learnings

## Dev Agent Record

### Context Reference

- `docs/stories/7-2-explainability-metrics-calculation.context.xml` - Story context with documentation artifacts, code references, interfaces, constraints, and testing guidance

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

No debug issues encountered during implementation.

### Completion Notes List

1. **Core Module Implementation**: Created comprehensive explainability metrics module with all required functions for rationale presence, quality assessment, decision trace verification, sample extraction, failure logging, and improvement recommendations.

2. **Quality Assessment System**: Implemented 5-point quality scoring system based on:
   - Concrete data citations (signal names, values)
   - Account identifiers or transaction details
   - Numeric specifics (amounts, percentages, dates)
   - Plain language readability (grade-8 level)
   - Behavioral signal references

3. **CLI Script**: Created fully functional CLI script (`evaluate_explainability.py`) that loads recommendations from JSON files, calculates comprehensive metrics, saves results to JSON, and provides console summary with exit codes.

4. **Comprehensive Testing**: Wrote 31 unit tests covering:
   - Rationale presence calculation (5 tests)
   - Quality assessment with all criteria (8 tests)
   - Decision trace verification (4 tests)
   - Sample extraction with quality diversity (4 tests)
   - Failure logging and categorization (3 tests)
   - Improvement recommendations (4 tests)
   - End-to-end integration (3 tests)

5. **Integration Testing**: Successfully tested with real recommendation data (48 recommendations from 6 users) showing:
   - 100% rationale presence rate (meeting target)
   - Average quality score of 2.0/5 (identifies areas for improvement)
   - Proper JSON output format with sample rationales and failure cases
   - Actionable improvement recommendations generated

6. **Key Implementation Details**:
   - Handles both JSON file-based and database-based recommendations
   - Robust null/empty value handling for rationales
   - Flexible decision trace matching with normalization for various event naming patterns
   - Per-persona metrics breakdown for targeted improvements
   - Severity-based failure sorting (high, medium, low)

### File List

NEW:
- `spendsense/evaluation/explainability_metrics.py` - Core explainability metrics module (700+ lines)
- `scripts/evaluate_explainability.py` - CLI script for explainability evaluation
- `tests/evaluation/test_explainability_metrics.py` - Comprehensive unit tests (31 tests)
- `docs/eval/` - Created output directory for metrics JSON files

MODIFIED:
- `spendsense/evaluation/__init__.py` - Added exports for explainability metrics functions

## Change Log

**2025-11-06 - v2.2 - Optional Enhancements Implemented**
- Enhancement #1: Improved Readability Calculation
  - Added `textstat>=0.7.0` library to requirements.txt for Flesch-Kincaid Grade Level calculation
  - Updated `assess_rationale_quality()` in `explainability_metrics.py` to use textstat.flesch_kincaid_grade()
  - Target: Grade 8 or lower for plain language compliance (FR22)
  - Falls back to existing heuristics (sentence/word length) if textstat unavailable or fails
  - Updated docstring to document Flesch-Kincaid integration
  - Added `flesch_kincaid_grade` field to readability_metrics output when calculated
- Enhancement #2: CLI Path Validation
  - Added `validate_paths()` function to `evaluate_explainability.py`
  - Validates --data-dir exists before attempting to load recommendations
  - Validates --db-path exists before attempting database connection (warns if missing, doesn't fail)
  - Clear error messages with suggestions: "Data directory not found: {path}. Please check --data-dir argument."
  - Exits with code 3 if validation fails (data directory missing)
  - Fixed print_summary() function to handle nested metrics structure correctly
- All 31 existing unit tests still passing
- Status: ready for final review

**2025-11-06 - v2.1 - Code Review Fixes Applied**
- Fixed missing exports in `spendsense/evaluation/__init__.py`: Added ExplainabilityMetrics and 7 related functions to module exports
- Verified sqlalchemy>=2.0.0 present in requirements.txt (no change needed)
- Fixed duplicate field serialization in `scripts/evaluate_explainability.py`: Removed duplicate root-level fields (lines 281-284)
- Added QUALITY_THRESHOLD module constant to `spendsense/evaluation/explainability_metrics.py`: Replaced 3 hardcoded threshold values with constant
- All 31 unit tests pass successfully after fixes
- Status: ready for final review and merge

**2025-11-06 - v2.0 - Story Implementation Complete**
- Implemented comprehensive explainability metrics calculation module
- Created `ExplainabilityMetrics` dataclass with 8 fields tracking all AC requirements
- Implemented 6 core functions: rationale presence, quality assessment, decision trace verification, sample extraction, failure logging, improvement recommendations
- Built CLI script `evaluate_explainability.py` with JSON file and database loading
- Wrote 31 unit tests (exceeding ≥10 requirement) with 100% pass rate
- Validated integration with real data: 48 recommendations across 6 users
- Results show 100% rationale presence, quality system identifies improvement areas
- Status: review (ready for code review)

**2025-11-06 - v1.0 - Story Drafted**
- Initial story creation from Epic 7 PRD
- Epic 7.2: Second story in evaluation harness epic
- Focused on explainability metrics: rationale presence, quality, decision traces
- 11 task groups with 50+ subtasks
- Target: 100% rationale presence, quality score ≥3, complete decision traces
- Quality assessment with 5-point checklist
- Sample rationale extraction for manual review
- Improvement recommendations based on failure patterns
- JSON output format includes sample rationales
- CLI script for reproducible evaluation
- Integrates with Epic 4 (recommendation engine) and Epic 6 (audit trail)
- Status: drafted (ready for story-context workflow)
