# Epic 3: Persona Assignment System - Handoff Document

**Date**: 2025-11-05
**Status**: Story 3.1 Complete (1 of 5 stories done)
**Approach**: One-at-a-time (create story → implement → review → next story)

---

## Executive Summary

**Completed**: Story 3.1 - Persona Definition Registry ✅
- Created YAML registry with 6 personas
- Built registry loader with Pydantic validation
- 24 unit tests (all passing)
- Code review: APPROVED

**Next**: Story 3.2 - Persona Matching Engine

---

## Story 3.1 Complete - What Was Built

### Files Created

1. **`spendsense/config/personas.yaml`** - Persona Registry
   - 6 personas defined with priorities 1-6
   - Each has: id, name, description, criteria (operator + conditions), focus_areas, content_types
   - Criteria format: `operator` (AND/OR) with list of `conditions`
   - Each condition: `signal` (field name), `operator` (>=, <=, etc.), `value` (threshold)

2. **`spendsense/personas/registry.py`** - Registry Loader
   - `load_persona_registry()` - Main function to load and cache registry
   - Pydantic models: `Persona`, `PersonaCriteria`, `PersonaCondition`, `PersonaRegistry`
   - Singleton caching pattern
   - Strong validation (unique IDs, unique priorities, lowercase enforcement)

3. **`tests/test_persona_registry.py`** - Unit Tests
   - 24 tests covering loading, validation, criteria, metadata
   - All tests passing ✅

### The 6 Personas (Priority Order)

1. **High Credit Utilization** (Priority 1)
   - Criteria: `credit_max_utilization_pct >= 50.0`
   - Focus: Debt management, interest reduction

2. **Variable Income Budgeter** (Priority 2)
   - Criteria: `income_median_pay_gap_days > 45` OR `income_payroll_count < 2` (30d)
   - Focus: Cash flow budgeting, irregular income strategies

3. **Low Savings / Emergency Fund Builder** (Priority 3)
   - Criteria: `savings_emergency_fund_months < 3.0`
   - Focus: Emergency fund building, financial resilience

4. **Subscription-Heavy Spending** (Priority 4)
   - Criteria: `subscription_share_pct >= 0.20`
   - Focus: Subscription audit, recurring cost optimization

5. **Cash Flow Optimizer** (Priority 5)
   - Criteria: `savings_emergency_fund_months >= 6.0` AND `credit_max_utilization_pct < 10.0`
   - Focus: Investment basics, wealth optimization

6. **Young Professional / Credit Builder** (Priority 6)
   - Criteria: `transaction_history_days < 180` OR `credit_total_limits < 3000`
   - Focus: Credit building, budgeting basics, financial literacy

### Key Learnings for Next Story

**For Story 3.2 (Persona Matching Engine):**
- Registry is ready at `spendsense/config/personas.yaml`
- Use `load_persona_registry()` to get all personas
- Reuse existing models: `PersonaCondition`, `PersonaCriteria`, `Persona`
- Criteria format is well-defined:
  - `operator`: "AND" or "OR"
  - `conditions`: list of `{signal, operator, value}`
- Need to evaluate these criteria against `BehavioralSignal` data from Epic 2
- Signal field names from Epic 2:
  - `credit_max_utilization_pct`
  - `income_median_pay_gap_days`
  - `income_payroll_count`
  - `savings_emergency_fund_months`
  - `subscription_share_pct`
  - (Note: `transaction_history_days` and `credit_total_limits` need to be calculated)

---

## Remaining Stories in Epic 3

### Story 3.2: Persona Matching Engine (NEXT)
**Goal**: Evaluate user behavioral signals against all persona criteria

**Acceptance Criteria**:
1. Matching function evaluates user signals against each persona's criteria
2. Boolean match result returned for each persona with supporting evidence
3. Match logic correctly implements AND/OR conditions per persona criteria
4. Threshold comparisons handle edge cases (exact matches, missing data)
5. All qualifying personas logged before prioritization
6. Match evaluation traced with specific signal values that triggered match
7. Matching supports both 30-day and 180-day time windows
8. Unit tests cover all persona criteria combinations
9. Unit tests verify correct boolean logic for complex criteria

**Implementation Notes**:
- Create `spendsense/personas/matcher.py`
- Main function: `match_personas(user_signals: BehavioralSignal) -> List[PersonaMatch]`
- Return type: `PersonaMatch` with fields: `persona_id`, `matched`, `evidence` (dict of signal values that triggered match)
- Handle missing signals gracefully (treat as non-match or use defaults)
- Test with actual Epic 2 data

### Story 3.3: Deterministic Prioritization Logic
**Goal**: Select highest-priority persona when multiple match

**Key Points**:
- Input: List of matching personas from Story 3.2
- Output: Single persona (lowest priority number = highest priority)
- Tie-breaking: Shouldn't happen (unique priorities enforced in registry)
- Fallback: "unclassified" status if zero personas match
- Audit: Log all qualifying personas + reason for selection

### Story 3.4: Persona Assignment & Audit Logging
**Goal**: Store assignments with complete audit trail

**Key Points**:
- Create `persona_assignments` table (schema in architecture.md lines 1481-1494)
- Store: persona ID, timestamp, qualifying_personas (JSON), match_evidence (JSON), prioritization_reason
- API endpoint: GET `/profile/{user_id}` returns persona assignment
- Support both 30-day and 180-day time windows

### Story 3.5: Custom Personas 5 & 6 Implementation
**Goal**: Verify Personas 5 & 6 work correctly

**Key Points**:
- Already defined in registry (Story 3.1)
- This story focuses on:
  - Testing with real data
  - Validating criteria work correctly
  - Ensuring educational content is appropriate
  - Documenting rationale clearly

---

## Technical Context

### Epic 2 (Completed) - Behavioral Signals Available

Story 3.2 will consume these signals from Epic 2:

**API Endpoint**: `GET /api/signals/{user_id}`

**Returns**: `BehavioralSignal` with fields:
- `subscription_recurring_merchants`: int
- `subscription_monthly_spend`: float
- `subscription_share_pct`: float (0.0-1.0)
- `savings_net_inflow`: float
- `savings_growth_rate_pct`: float
- `savings_emergency_fund_months`: float
- `credit_max_utilization_pct`: float (0.0-100.0)
- `credit_has_interest_charges`: bool
- `credit_minimum_payment_only`: bool
- `credit_overdue_status`: bool
- `income_payroll_count`: int
- `income_median_pay_gap_days`: float
- `income_cash_flow_buffer_months`: float

**Missing signals that need calculation**:
- `transaction_history_days`: Calculate from first transaction date to reference date
- `credit_total_limits`: Sum of all credit card limits

### Project Structure

```
spendsense/
├── config/
│   └── personas.yaml          ← Story 3.1 ✅
├── features/                  ← Epic 2 (complete)
│   ├── time_windows.py
│   ├── subscription_detector.py
│   ├── savings_detector.py
│   ├── credit_detector.py
│   ├── income_detector.py
│   └── behavioral_summary.py
├── personas/                  ← Epic 3 (in progress)
│   ├── definitions.py         ← Pre-existing (for synthetic data generation)
│   ├── registry.py            ← Story 3.1 ✅
│   ├── matcher.py             ← Story 3.2 (next)
│   ├── prioritizer.py         ← Story 3.3 (todo)
│   └── assigner.py            ← Story 3.4 (todo)
└── api/
    └── main.py                ← Add persona endpoints in Story 3.4
```

### Testing Approach

**Virtual Environment**: `/Users/reena/gauntletai/spendsense/venv`

**Run tests**:
```bash
source venv/bin/activate
python -m pytest tests/test_persona_registry.py -v      # Story 3.1 ✅
python -m pytest tests/test_persona_matcher.py -v       # Story 3.2 (todo)
python -m pytest tests/test_persona_prioritizer.py -v   # Story 3.3 (todo)
python -m pytest tests/test_persona_assigner.py -v      # Story 3.4 (todo)
```

---

## Next Steps

1. **Create Story 3.2** - Persona Matching Engine
   - Read Story 3.1 completion notes (this file)
   - Create story file: `docs/stories/3-2-persona-matching-engine.md`
   - Include learnings from Story 3.1

2. **Implement Story 3.2**
   - Create `spendsense/personas/matcher.py`
   - Implement `match_personas()` function
   - Handle AND/OR logic correctly
   - Support both time windows
   - Calculate missing signals (transaction_history_days, credit_total_limits)
   - Create comprehensive tests

3. **Code Review Story 3.2**
   - Verify all criteria work correctly
   - Test with real Epic 2 data
   - Validate boolean logic
   - Check edge case handling

4. **Continue with Stories 3.3, 3.4, 3.5**

5. **Add UI Components** (after all 5 stories complete)
   - Display persona assignment for each user
   - Show audit trail (qualifying personas, evidence, reasoning)
   - Add filters/search for testing
   - Interactive demo of all 6 personas

---

## Important Files to Reference

**Requirements & Design**:
- `/docs/prd/epic-3-persona-assignment-system.md` - Epic 3 PRD with all 5 stories
- `/docs/architecture.md` (lines 912-947) - Personas module specs
- `/docs/architecture.md` (lines 1481-1494) - persona_assignments table schema

**Completed Work**:
- `/docs/stories/3-1-persona-definition-registry.md` - Story 3.1 with implementation notes
- `/spendsense/config/personas.yaml` - Persona registry
- `/spendsense/personas/registry.py` - Registry loader
- `/tests/test_persona_registry.py` - Registry tests

**Context from Epic 2**:
- `/docs/stories/2-1-time-window-aggregation-framework.md`
- `/docs/stories/2-2-subscription-pattern-detection.md`
- `/docs/stories/2-3-savings-behavior-detection.md`
- `/docs/stories/2-4-credit-utilization-debt-detection.md`
- `/docs/stories/2-5-income-stability-detection.md`
- `/docs/stories/2-6-behavioral-summary-aggregation.md`
- `/spendsense/features/` - All signal detectors
- `/spendsense/api/main.py` - Existing API endpoints

**Server Running**:
- Uvicorn server on http://127.0.0.1:8000
- Watch for file changes (auto-reload enabled)
- API docs: http://127.0.0.1:8000/docs

---

## Questions & Decisions

**Q: Why one-at-a-time approach?**
A: BMM workflow design extracts learnings from previous story's implementation to inform next story creation. This ensures Story 3.2 knows exactly what Story 3.1 built.

**Q: Are Personas 5 & 6 already implemented?**
A: They're **defined** in the registry (Story 3.1) but Story 3.5 will **validate** they work correctly with real data and document their rationale.

**Q: How to handle missing signals (e.g., user has no credit cards)?**
A: Story 3.2 should handle gracefully:
- If credit signals missing → don't match high_utilization persona
- If savings signals missing → don't match low_savings persona
- Document this behavior in matcher.py

**Q: What about the existing `personas/definitions.py`?**
A: That file is for **synthetic data generation** (creating users WITH specific personas). Epic 3 builds the **detection system** (identifying personas from observed behavior). They serve different purposes.

---

## Status Summary

| Story | Status | Files | Tests | Review |
|-------|--------|-------|-------|--------|
| 3.1 - Persona Definition Registry | ✅ DONE | 3 files | 24/24 ✅ | APPROVED |
| 3.2 - Persona Matching Engine | 📝 NEXT | - | - | - |
| 3.3 - Deterministic Prioritization | ⏳ TODO | - | - | - |
| 3.4 - Persona Assignment & Audit | ⏳ TODO | - | - | - |
| 3.5 - Custom Personas 5 & 6 | ⏳ TODO | - | - | - |
| UI Components | ⏳ TODO | - | - | - |

**Estimated Remaining Work**: 4 stories + UI = ~4-6 hours

---

**Ready to continue with Story 3.2 in fresh context!**
