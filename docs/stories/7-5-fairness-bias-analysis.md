# Story 7.5: Fairness & Bias Analysis

Status: review

## Story

As a **data scientist**,
I want **analysis of recommendation fairness across demographic groups if applicable**,
so that **potential bias in persona assignment or recommendations can be detected and mitigated**.

## Acceptance Criteria

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

## Tasks / Subtasks

- [x] Task 1: Create fairness metrics module (AC: #1-10)
  - [x] Create `spendsense/evaluation/fairness_metrics.py`
  - [x] Define `FairnessMetrics` dataclass with fields:
    - `demographic_parity_ratio`: Optional[float]
    - `equal_opportunity_difference`: Optional[float]
    - `persona_distribution_by_group`: Dict[str, Dict[str, int]]
    - `recommendation_distribution_by_group`: Dict[str, Dict[str, int]]
    - `statistical_significance`: Dict[str, float]
    - `bias_indicators`: List[Dict]
    - `fairness_assessment`: str
    - `limitations`: List[str]
    - `mitigation_recommendations`: List[str]
    - `timestamp`: datetime
  - [x] Implement `check_demographic_attributes()` function
  - [x] Implement `calculate_demographic_parity()` function
  - [x] Implement `calculate_equal_opportunity()` function
  - [x] Implement `test_statistical_significance()` function

- [x] Task 2: Check for demographic attributes in data (AC: #1, #8)
  - [x] Query synthetic user data for demographic fields
  - [x] Check if demographic attributes exist:
    - age_group (e.g., 18-24, 25-34, 35-44, 45-54, 55+)
    - income_bracket (e.g., <30K, 30-50K, 50-75K, 75-100K, 100K+)
    - gender (if present)
    - location/region (if present)
    - Other protected attributes
  - [x] If NO demographic data exists:
    - Document limitation: "Fairness analysis limited without demographic data"
    - Return early with limitation note
    - Skip demographic-based calculations
  - [x] If demographic data EXISTS:
    - Proceed with fairness analysis
    - Document which attributes are available

- [x] Task 3: Analyze persona distribution by demographic group (AC: #2)
  - [x] Group users by demographic attribute (age_group, income_bracket, etc.)
  - [x] For each demographic group, calculate persona distribution:
    - Count users per persona (6 personas)
    - Calculate percentage distribution
  - [x] Compare distributions across groups:
    - Are certain personas over-represented in specific groups?
    - Are certain personas under-represented in specific groups?
  - [x] Example analysis:
    - Age 18-24: High % Young Professional persona (expected)
    - Income <30K: High % High Utilization persona (potential concern)
    - Income 100K+: High % Savings Builder persona (expected)
  - [x] Flag disparities that may indicate bias

- [x] Task 4: Analyze recommendation distribution by demographic group (AC: #3)
  - [x] Group recommendations by demographic attribute
  - [x] For each demographic group, analyze:
    - Types of recommendations received (education vs partner offers)
    - Recommendation topics (debt management, savings, investing)
    - Average number of recommendations per user
  - [x] Compare distributions across groups:
    - Do all groups receive similar recommendation diversity?
    - Are certain groups receiving disproportionately negative recommendations?
    - Are certain groups receiving more partner offers (potential bias)?
  - [x] Flag disparities in recommendation treatment

- [x] Task 5: Calculate demographic parity ratio (AC: #6)
  - [x] Demographic Parity Definition: P(Y=1|A=a) ≈ P(Y=1|A=b)
    - Y = positive outcome (e.g., receiving empowering recommendation)
    - A = demographic attribute (e.g., income bracket)
  - [x] For SpendSense context:
    - Define "positive outcome": receiving Savings Builder or Cash Flow Optimizer persona (constructive personas)
    - Calculate rate of positive outcomes per demographic group
  - [x] Calculate parity ratio:
    - Min rate / Max rate across groups
    - Ratio = 1.0 is perfect parity
    - Ratio < 0.8 indicates disparity (common threshold)
  - [x] Return ratio and group-level rates

- [x] Task 6: Calculate equal opportunity difference (AC: #6)
  - [x] Equal Opportunity Definition: P(Ŷ=1|Y=1,A=a) ≈ P(Ŷ=1|Y=1,A=b)
    - True positive rate parity across groups
  - [x] For SpendSense context:
    - Define "qualified users": users with qualifying signals for constructive personas
    - Check if qualified users receive appropriate personas regardless of demographic
  - [x] Calculate equal opportunity difference:
    - Max difference in true positive rates across groups
    - Difference = 0 is perfect equality
    - Difference > 0.1 indicates disparity
  - [x] Return difference and group-level true positive rates

- [x] Task 7: Test statistical significance (AC: #4)
  - [x] Use chi-square test for persona distribution differences
  - [x] For each demographic attribute:
    - Null hypothesis: persona distribution is independent of demographic group
    - Calculate chi-square statistic
    - Calculate p-value
    - Significance threshold: p < 0.05
  - [x] If p < 0.05: Distribution differences are statistically significant
  - [x] If p >= 0.05: Differences may be due to random variation
  - [x] Return p-values and significance flags

- [x] Task 8: Flag potential bias indicators (AC: #5)
  - [x] Define bias thresholds:
    - Demographic parity ratio < 0.8: BIAS WARNING
    - Equal opportunity difference > 0.1: BIAS WARNING
    - Chi-square p-value < 0.05 AND large disparities: BIAS WARNING
  - [x] For each flagged indicator, record:
    - bias_type: "demographic_parity", "equal_opportunity", "representation_disparity"
    - affected_groups: List of demographic groups
    - severity: "high", "medium", "low"
    - description: Human-readable explanation
    - evidence: Statistical values
  - [x] Rank by severity for prioritization
  - [x] Include in JSON output

- [x] Task 9: Document limitations and constraints (AC: #8)
  - [x] Document fairness analysis limitations:
    - "Synthetic data may not reflect real-world demographic distributions"
    - "Limited demographic attributes available (only age/income, no protected classes)"
    - "Small sample size (50-100 users) limits statistical power"
    - "Persona assignment is deterministic based on financial signals, not demographic attributes"
    - "Fairness analysis cannot detect bias in data generation process"
  - [x] Document methodology assumptions:
    - What constitutes "positive outcome" for demographic parity
    - Why certain personas are considered constructive vs negative
    - Threshold choices (0.8 for parity, 0.1 for equal opportunity)
  - [x] Include limitations in JSON output and report

- [x] Task 10: Generate mitigation recommendations (AC: #10)
  - [x] If bias detected, generate actionable recommendations:
    - "Review persona assignment criteria for unintended demographic correlations"
    - "Audit behavioral signals for demographic proxies (e.g., income signals)"
    - "Consider fairness constraints in persona prioritization logic"
    - "Collect more diverse synthetic user data to improve representation"
    - "Conduct regular fairness audits with real data when available"
  - [x] If no bias detected:
    - "Continue monitoring fairness metrics with each evaluation run"
    - "Expand demographic attributes in synthetic data for deeper analysis"
    - "Document fairness as a design constraint in future feature development"
  - [x] Prioritize recommendations by impact and feasibility
  - [x] Include in JSON output

- [x] Task 11: Generate fairness visualizations (AC: #9)
  - [x] Create persona distribution by demographic group (stacked bar chart)
  - [x] Create demographic parity visualization (bar chart showing rates per group)
  - [x] Create recommendation distribution heatmap (demographic groups x recommendation types)
  - [x] Use matplotlib for visualizations
  - [x] Save charts as PNG files to `docs/eval/`
  - [x] Include chart references in JSON output

- [x] Task 12: Create fairness report (AC: #7, #9)
  - [x] Generate structured fairness report:
    - Executive summary: Overall fairness assessment (PASS/CONCERN/FAIL)
    - Demographic parity analysis with interpretation
    - Equal opportunity analysis with interpretation
    - Statistical significance results
    - Bias indicators with severity levels
    - Limitations and constraints
    - Mitigation recommendations
    - Visualizations (embedded or referenced)
  - [x] Format report as Markdown or PDF
  - [x] Include in evaluation output

- [x] Task 13: Create CLI script for fairness evaluation (AC: #1-10)
  - [x] Create `scripts/evaluate_fairness.py`
  - [x] Accept CLI args: --dataset, --output-dir, --demographic-attr (age_group, income_bracket)
  - [x] Check for demographic data availability
  - [x] Run fairness analysis if data exists
  - [x] Generate visualizations
  - [x] Save results to JSON
  - [x] Print summary to console:
    - Demographic attributes available: Yes/No
    - Demographic parity ratio: X (PASS/FAIL)
    - Equal opportunity difference: X (PASS/FAIL)
    - Bias indicators: N
    - Overall assessment: PASS/CONCERN/FAIL
  - [x] Exit with code 0 if no bias, 1 if bias detected

- [x] Task 14: Write comprehensive unit tests (AC: #1-10)
  - [x] Create `tests/evaluation/test_fairness_metrics.py`
  - [x] Test `check_demographic_attributes()` with various data schemas
  - [x] Test `calculate_demographic_parity()` with mock data
  - [x] Test `calculate_equal_opportunity()` with mock data
  - [x] Test `test_statistical_significance()` chi-square calculation
  - [x] Test bias indicator flagging with various threshold scenarios
  - [x] Test edge cases:
    - No demographic data available
    - Perfect parity (ratio = 1.0)
    - Severe disparity (ratio < 0.5)
    - Single demographic group (no comparison possible)
    - Empty dataset
  - [x] Mock statistical functions for deterministic tests

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**
- **Backend:** Python 3.10+ with type hints
- **Database:** SQLite with users table (may or may not have demographic fields)
- **Output Format:** JSON for structured metrics, PNG for visualizations
- **File Storage:** Local filesystem at `docs/eval/`
- **Testing:** pytest with ≥10 tests per story

**From PRD:**
- Synthetic data generation (Epic 1): May include demographic attributes
- Persona assignment (Epic 3): Deterministic based on financial signals, not demographics
- Fairness goal: Ensure system doesn't discriminate based on protected attributes

**Key Requirements:**
- Check if demographic data exists before analysis
- Document limitations with synthetic data
- Use standard fairness metrics: demographic parity, equal opportunity
- Statistical significance testing (chi-square)
- Bias detection with actionable recommendations

### Project Structure Notes

**New Files to Create:**
- `spendsense/evaluation/fairness_metrics.py` - Fairness calculation logic
- `scripts/evaluate_fairness.py` - CLI script
- `tests/evaluation/test_fairness_metrics.py` - Unit tests
- `docs/eval/fairness_metrics_{timestamp}.json` - JSON output
- `docs/eval/persona_distribution_by_demographics_{timestamp}.png` - Visualization
- `docs/eval/demographic_parity_{timestamp}.png` - Visualization
- `docs/eval/fairness_report_{timestamp}.md` - Fairness report

**Files to Reference:**
- `data/spendsense.db` - SQLite database with users table
- `data/synthetic/users/profiles.json` - Synthetic user profiles (may have demographic data)
- `spendsense/personas/persona_matcher.py` - Persona assignment logic (Epic 3)
- `spendsense/recommendations/recommendation_engine.py` - Recommendation generation (Epic 4)

**Database Tables:**
- `users` - user_id, persona, age_group?, income_bracket?, other demographics?

**Dependencies:**
- `scipy` - Statistical tests (chi-square) (add to requirements.txt)
- `matplotlib` - Visualizations (already added in Story 7.3)
- `numpy` - Statistical calculations (add to requirements.txt)

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest
- Coverage target: ≥10 tests per story
- Test types:
  1. Unit tests: Individual fairness metric calculations
  2. Statistical tests: Chi-square, parity ratio calculations
  3. Edge case tests: No demographics, perfect parity, severe bias
  4. Mock tests: Statistical functions for deterministic results

**Test Categories:**
1. Demographic data detection: Present vs absent
2. Demographic parity calculation: Ratio computation
3. Equal opportunity calculation: True positive rate parity
4. Statistical significance: Chi-square test
5. Bias indicator flagging: Threshold detection
6. Mitigation recommendations: Bias-specific suggestions

### Learnings from Previous Stories

**From Story 7.1 (Coverage Metrics Calculation):**
- **Module Structure**: `spendsense/evaluation/` directory established
- **JSON Output Pattern**: Timestamp, dataset, metrics structure
- **CLI Script Pattern**: `scripts/evaluate_*.py` with consistent args

**From Story 7.2 (Explainability Metrics Calculation):**
- **Quality Assessment**: Checklist-based evaluation
- **Sample Extraction**: Useful for bias case studies

**From Story 7.3 (Performance & Latency Metrics):**
- **Visualization**: matplotlib PNG charts saved to docs/eval/
- **Statistical Analysis**: Percentiles and distribution analysis

**From Story 7.4 (Auditability & Compliance Metrics):**
- **Compliance Checks**: Pass/fail status with severity levels
- **Failure Categorization**: Structured reporting with remediation

**Key System Components to Analyze:**
- Epic 1: Synthetic data generation (check for demographic attributes)
- Epic 3: Persona assignment system (analyze for demographic correlation)
- Epic 4: Recommendation engine (analyze for demographic disparities)

**Technical Patterns to Follow:**
- Type hints for all functions (Python 3.10+)
- Optional fields for demographic-dependent metrics
- Graceful degradation if demographic data missing
- Statistical libraries (scipy, numpy) for calculations
- Visualization with matplotlib
- JSON output with ISO 8601 timestamps

### References

- [Source: docs/prd/epic-7-evaluation-harness-metrics.md#Story-7.5] - Story 7.5 acceptance criteria
- [Source: docs/architecture.md] - Fairness and transparency design principles
- [Source: data/synthetic/users/profiles.json] - Synthetic user data schema
- [Source: spendsense/personas/persona_matcher.py] - Persona assignment logic (Epic 3)
- [Source: docs/stories/7-1-coverage-metrics-calculation.md] - Previous story learnings
- [Source: docs/stories/7-2-explainability-metrics-calculation.md] - Previous story learnings
- [Source: docs/stories/7-3-performance-latency-metrics.md] - Previous story learnings
- [Source: docs/stories/7-4-auditability-compliance-metrics.md] - Previous story learnings

## Dev Agent Record

### Context Reference

- docs/stories/7-5-fairness-bias-analysis.context.xml

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

Implementation completed successfully on 2025-11-06.

### Completion Notes List

**Implementation Summary:**

✅ **Core Fairness Metrics Module** (`spendsense/evaluation/fairness_metrics.py` - 700+ lines)
- Created comprehensive FairnessMetrics dataclass with all required fields
- Implemented demographic attribute detection with graceful degradation
- Built demographic parity ratio calculation (threshold: ≥0.8)
- Built equal opportunity difference calculation (threshold: ≤0.1)
- Implemented chi-square statistical significance testing
- Created bias indicator flagging system with severity levels
- Generated limitations documentation for synthetic data constraints
- Built mitigation recommendation engine (bias-specific and general monitoring)

✅ **Reporting & Visualization Module** (`spendsense/evaluation/fairness_reporting.py` - 350+ lines)
- Created persona distribution stacked bar charts
- Built demographic parity bar charts with threshold visualization
- Implemented recommendation distribution heatmaps
- Generated comprehensive Markdown reports with executive summary
- Included methodology documentation and interpretation guidance

✅ **CLI Evaluation Script** (`scripts/evaluate_fairness.py` - 200+ lines)
- Command-line interface with --dataset, --output-dir, --demographic-attr options
- Graceful handling of missing demographic data
- JSON metrics export with timestamps
- PNG visualization generation
- Console summary with color-coded pass/fail indicators
- Exit codes based on bias detection (0=pass, 1=fail)

✅ **Comprehensive Testing** (`tests/evaluation/test_fairness_metrics.py` - 24 tests)
- Test demographic attribute detection (with/without data)
- Test persona distribution analysis
- Test demographic parity calculation (perfect parity, disparities)
- Test equal opportunity calculation
- Test chi-square statistical significance
- Test bias indicator flagging (severe, none)
- Test edge cases (empty dataset, single group, all same persona)
- Test mitigation recommendation generation
- Test overall fairness assessment (PASS/CONCERN/FAIL)
- Test full analysis pipeline with real database
- **All 24 tests passing ✅**

**Key Implementation Decisions:**

1. **Graceful Degradation:** System detects absence of demographic data and documents limitations instead of failing
2. **Positive Personas:** Defined savings_builder and cash_flow_optimizer as "positive outcomes" for parity analysis
3. **Qualified Users:** Used median income as qualification threshold for equal opportunity analysis
4. **Standard Thresholds:** Demographic parity ≥0.8, Equal opportunity ≤0.1, Statistical significance p<0.05
5. **Comprehensive Limitations:** Documented 8 specific limitations with synthetic data and methodology assumptions

**Dependencies Added:**
- scipy>=1.11.0 (chi-square testing)
- matplotlib>=3.8.0 (visualizations)

**Current System Status:**
- ✅ No demographic data exists in current dataset (profiles.json and spendsense.db)
- ✅ System correctly identifies this and provides recommendations
- ✅ Ready for demographic data collection in production
- ✅ All fairness metrics calculations validated with comprehensive tests

### File List

**NEW:**
- `spendsense/evaluation/fairness_metrics.py` - Core fairness metrics calculation module
- `spendsense/evaluation/fairness_reporting.py` - Visualization and report generation
- `scripts/evaluate_fairness.py` - CLI script for fairness evaluation
- `tests/evaluation/test_fairness_metrics.py` - Comprehensive unit tests (24 tests)

**MODIFIED:**
- `requirements.txt` - Added scipy>=1.11.0 and matplotlib>=3.8.0

## Change Log

**2025-11-06 - v1.0 - Story Drafted**
- Initial story creation from Epic 7 PRD
- Epic 7.5: Fifth story in evaluation harness epic
- Focused on fairness and bias analysis across demographic groups
- 14 task groups with 70+ subtasks
- Conditional analysis: Check for demographic data before proceeding
- Demographic parity ratio calculation (target ≥0.8)
- Equal opportunity difference calculation (target ≤0.1)
- Statistical significance testing (chi-square)
- Bias indicator flagging with severity levels
- Limitations documentation (synthetic data constraints)
- Mitigation recommendations if bias detected
- Fairness visualizations (persona distribution, parity charts)
- Fairness report with interpretation and recommendations
- CLI script for reproducible fairness audits
- Integrates with Epic 1 (synthetic data), Epic 3 (personas), Epic 4 (recommendations)
- Status: drafted (ready for story-context workflow)

**2025-11-06 - v2.0 - Story Completed**
- ✅ Implemented complete fairness metrics module (700+ lines)
- ✅ Created reporting and visualization module (350+ lines)
- ✅ Built CLI evaluation script with graceful degradation
- ✅ Wrote 24 comprehensive unit tests (all passing)
- ✅ Added scipy>=1.11.0 and matplotlib>=3.8.0 dependencies
- ✅ Implemented demographic parity ratio calculation
- ✅ Implemented equal opportunity difference calculation
- ✅ Built chi-square statistical significance testing
- ✅ Created bias indicator flagging with severity levels
- ✅ Generated comprehensive limitations documentation
- ✅ Built mitigation recommendation engine
- ✅ Created visualization generators (bar charts, heatmaps)
- ✅ Generated structured Markdown reports
- ✅ Verified system handles missing demographic data gracefully
- ✅ All acceptance criteria met
- Status: review (ready for code review)
