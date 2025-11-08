# Story 3.2: Persona Matching Engine

Status: drafted

## Story

As a **data scientist**,
I want **evaluation of user behavioral signals against all persona criteria**,
so that **all qualifying personas can be identified before prioritization is applied**.

## Acceptance Criteria

1. Matching function evaluates user signals against each persona's criteria
2. Boolean match result returned for each persona with supporting evidence
3. Match logic correctly implements AND/OR conditions per persona criteria
4. Threshold comparisons handle edge cases (exact matches, missing data)
5. All qualifying personas logged before prioritization
6. Match evaluation traced with specific signal values that triggered match
7. Matching supports both 30-day and 180-day time windows
8. Unit tests cover all persona criteria combinations
9. Unit tests verify correct boolean logic for complex criteria

## Tasks / Subtasks

- [ ] Task 1: Create matcher module with core matching function (AC: 1, 2, 6)
  - [ ] Create `spendsense/personas/matcher.py`
  - [ ] Implement `match_personas(user_signals: BehavioralSignal, time_window: str) -> List[PersonaMatch]`
  - [ ] Define `PersonaMatch` Pydantic model with fields: persona_id, matched (bool), evidence (dict)
  - [ ] Load persona registry using `load_persona_registry()` from Story 3.1
  - [ ] Return list of PersonaMatch objects for all personas

- [ ] Task 2: Implement condition evaluation logic (AC: 3, 4)
  - [ ] Create `_evaluate_condition(signal_value, operator, threshold_value) -> bool` helper
  - [ ] Support operators: `>=`, `<=`, `>`, `<`, `==`
  - [ ] Handle missing signal values (treat as non-match)
  - [ ] Handle edge cases: exact matches, None values, type mismatches
  - [ ] Add logging for each condition evaluation

- [ ] Task 3: Implement AND/OR criteria logic (AC: 3)
  - [ ] Create `_evaluate_criteria(user_signals, criteria: PersonaCriteria) -> Tuple[bool, dict]` helper
  - [ ] Implement AND logic: all conditions must be True
  - [ ] Implement OR logic: at least one condition must be True
  - [ ] Return tuple: (matched: bool, evidence: dict of signal values)
  - [ ] Store actual signal values in evidence dict for audit trail

- [ ] Task 4: Calculate missing signals (AC: 1, 7)
  - [ ] Add `_calculate_transaction_history_days(user_id: int, reference_date: date, time_window: str) -> int`
  - [ ] Add `_calculate_credit_total_limits(user_id: int) -> float`
  - [ ] Query database for first transaction date
  - [ ] Query database for sum of credit card limits
  - [ ] Handle cases where user has no transactions or no credit accounts

- [ ] Task 5: Integrate with Epic 2 signals (AC: 1, 7)
  - [ ] Import `BehavioralSignal` from Epic 2
  - [ ] Accept time_window parameter ("30d" or "180d")
  - [ ] Access all signal fields from BehavioralSignal object
  - [ ] Augment with calculated signals (transaction_history_days, credit_total_limits)

- [ ] Task 6: Write comprehensive unit tests (AC: 8, 9)
  - [ ] Test each persona's criteria individually
  - [ ] Test AND logic with all conditions True/False
  - [ ] Test OR logic with various combinations
  - [ ] Test missing signal handling
  - [ ] Test edge cases: exact threshold matches, zero values, negative values
  - [ ] Test both 30-day and 180-day time windows
  - [ ] Test evidence dict contains correct signal values
  - [ ] Mock database queries for calculated signals

- [ ] Task 7: Add logging and audit trail (AC: 5, 6)
  - [ ] Log all qualifying personas before returning
  - [ ] Log match evidence (signal values) for each qualifying persona
  - [ ] Use structured logging with persona_id, matched status, evidence
  - [ ] Add debug-level logging for non-matching personas

## Dev Notes

### Architecture Alignment

**From architecture.md (lines 912-947):**
- Matcher evaluates signals against persona criteria
- Returns list of all matching personas with evidence
- Does NOT prioritize (that's Story 3.3)
- Must support both 30-day and 180-day time windows

**From Story 3.1 Completion:**
- Registry available via `load_persona_registry()`
- Criteria format: `operator` (AND/OR) + list of `conditions`
- Each condition: `{signal: str, operator: str, value: float/int}`
- 6 personas defined with clear criteria

### Project Structure Notes

**Module Location:** `spendsense/personas/matcher.py`

**Imports Needed:**
- `from spendsense.personas.registry import load_persona_registry, Persona, PersonaCriteria`
- `from spendsense.features.behavioral_summary import BehavioralSignal`
- `from pydantic import BaseModel`
- `from typing import List, Tuple, Dict, Any, Optional`
- `from datetime import date`

**New Pydantic Model:**
```python
class PersonaMatch(BaseModel):
    persona_id: str
    matched: bool
    evidence: Dict[str, Any]  # Signal values that were evaluated
```

### Dependencies

**Consumes:**
- Story 3.1: Persona registry (personas.yaml, registry.py)
- Epic 2: BehavioralSignal model

**Produces:**
- Matcher module with `match_personas()` function
- PersonaMatch model
- List of all matching personas with evidence

**Depends On:**
- Database access for calculated signals (transaction_history_days, credit_total_limits)

### Testing Strategy

**Unit Tests:**
- Test each of 6 personas individually with matching signals
- Test each of 6 personas with non-matching signals
- Test AND logic (Persona 5: two conditions must both be True)
- Test OR logic (Persona 2: either condition can be True)
- Test missing signals handled gracefully
- Test edge cases: threshold exact matches, None values
- Test evidence dict accuracy
- Mock database queries for calculated signals

**Test File:** `tests/test_persona_matcher.py`

**Test Data:**
- Use fixtures to create BehavioralSignal objects with known values
- Create signals that match exactly one persona
- Create signals that match multiple personas
- Create signals that match zero personas

### Signal Mapping

**From Epic 2 (BehavioralSignal fields):**
- `subscription_share_pct` → Persona 4
- `credit_max_utilization_pct` → Personas 1, 5
- `savings_emergency_fund_months` → Personas 3, 5
- `income_median_pay_gap_days` → Persona 2
- `income_payroll_count` → Persona 2

**Calculated Signals (need to add):**
- `transaction_history_days` → Persona 6
- `credit_total_limits` → Persona 6

### Missing Signal Handling

**Strategy:**
- If signal is missing/None → condition evaluates to False
- Log warning when signals are missing
- Persona won't match if any required signal is missing (for AND logic)
- Persona might still match if other conditions are True (for OR logic)

**Examples:**
- User has no credit cards → `credit_max_utilization_pct` is None → Persona 1 won't match
- User has no savings account → `savings_emergency_fund_months` is None → Persona 3 won't match

### References

- [Source: docs/prd/epic-3-persona-assignment-system.md#Story-3.2]
- [Source: docs/architecture.md#Personas-Module (lines 912-947)]
- [Source: docs/session-handoff/EPIC_3_HANDOFF.md - Story 3.1 completion notes]
- [Source: spendsense/config/personas.yaml - Criteria definitions]

## Dev Agent Record

### Context Reference

**From Story 3.1:**
- Persona registry ready at `spendsense/config/personas.yaml`
- Registry loader available: `load_persona_registry()`
- Pydantic models: Persona, PersonaCriteria, PersonaCondition, PersonaRegistry
- All 6 personas defined with clear criteria structure

**From Epic 2:**
- BehavioralSignal model available from `spendsense.features.behavioral_summary`
- All signal fields documented in docs/session-handoff/EPIC_3_HANDOFF.md lines 150-163

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

TBD after implementation

### Completion Notes List

TBD after implementation

### File List

**NEW:**
- `spendsense/personas/matcher.py`
- `tests/test_persona_matcher.py`

**MODIFIED:**
- None expected
