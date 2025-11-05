# Story 3.3: Deterministic Prioritization Logic

Status: drafted

## Story

As a **product manager**,
I want **deterministic selection of highest-priority persona when multiple personas match**,
so that **users receive consistent, predictable persona assignments focused on their most critical need**.

## Acceptance Criteria

1. Prioritization function accepts list of matching personas
2. Function returns single highest-priority persona (lowest priority number)
3. Tie-breaking logic documented if personas have same priority
4. Priority selection traced in audit log
5. All qualifying personas recorded separately from selected persona
6. Selection logic handles edge case of zero qualifying personas
7. Fallback persona or "unclassified" status defined for no-match scenario
8. Unit tests verify prioritization with various match combinations
9. Deterministic behavior verified across multiple runs with same data

## Tasks / Subtasks

- [ ] Task 1: Create prioritizer module with core prioritization function (AC: 1, 2)
  - [ ] Create `spendsense/personas/prioritizer.py`
  - [ ] Implement `prioritize_persona(matches: List[PersonaMatch]) -> PersonaAssignment`
  - [ ] Define `PersonaAssignment` Pydantic model
  - [ ] Sort qualifying personas by priority (1 = highest)
  - [ ] Return highest-priority persona (first in sorted list)

- [ ] Task 2: Handle edge cases (AC: 3, 6, 7)
  - [ ] Check for zero qualifying personas
  - [ ] Return "unclassified" status when no personas match
  - [ ] Document tie-breaking logic (shouldn't happen - unique priorities enforced)
  - [ ] Add warning log if tie detected

- [ ] Task 3: Create PersonaAssignment model (AC: 4, 5)
  - [ ] Fields: assigned_persona_id, priority, all_qualifying_personas, prioritization_reason
  - [ ] Store list of all qualifying persona IDs
  - [ ] Store reason for selection (e.g., "Highest priority match (priority 1)")
  - [ ] Include timestamp of assignment

- [ ] Task 4: Add audit logging (AC: 4, 5)
  - [ ] Log all qualifying personas before selection
  - [ ] Log selected persona with reason
  - [ ] Log unclassified status if no matches
  - [ ] Use structured logging for traceability

- [ ] Task 5: Write comprehensive unit tests (AC: 8, 9)
  - [ ] Test single persona match
  - [ ] Test multiple persona matches (select highest priority)
  - [ ] Test zero persona matches (unclassified status)
  - [ ] Test deterministic behavior (same input = same output)
  - [ ] Test all 6 personas as highest priority
  - [ ] Test audit log completeness

## Dev Notes

### Architecture Alignment

**From architecture.md (lines 912-947):**
- Prioritizer selects single persona from list of matches
- Uses priority field from persona registry (1 = highest priority)
- Returns assignment with audit trail

**From Story 3.2 Completion:**
- PersonaMatch available from matcher module
- Each match has: persona_id, matched (bool), evidence (dict), matched_conditions (list)
- Need to filter matches where matched=True before prioritizing

### Project Structure Notes

**Module Location:** `spendsense/personas/prioritizer.py`

**Imports Needed:**
- `from spendsense.personas.matcher import PersonaMatch`
- `from spendsense.personas.registry import load_persona_registry`
- `from pydantic import BaseModel`
- `from typing import List, Optional`
- `from datetime import datetime`

**New Pydantic Model:**
```python
class PersonaAssignment(BaseModel):
    assigned_persona_id: str  # "unclassified" if no matches
    priority: Optional[int]  # None if unclassified
    all_qualifying_personas: List[str]  # List of persona IDs that matched
    prioritization_reason: str  # Why this persona was selected
    assigned_at: datetime  # Timestamp of assignment
```

### Dependencies

**Consumes:**
- Story 3.1: Persona registry (for priority lookups)
- Story 3.2: PersonaMatch list from matcher

**Produces:**
- Prioritizer module with `prioritize_persona()` function
- PersonaAssignment model
- Single persona assignment with audit trail

**Depends On:**
- Persona registry for priority information

### Testing Strategy

**Unit Tests:**
- Test with 1 qualifying persona → returns that persona
- Test with 3 qualifying personas → returns highest priority
- Test with 0 qualifying personas → returns "unclassified"
- Test priority ordering (persona 1 > persona 2 > ... > persona 6)
- Test deterministic behavior (run 10 times with same input)
- Test all_qualifying_personas list is complete
- Test prioritization_reason is descriptive

**Test File:** `tests/test_persona_prioritizer.py`

**Test Data:**
- Create PersonaMatch fixtures for each persona
- Test all combinations of 2-3 personas matching
- Test edge case: all 6 personas match (should select persona 1)

### Prioritization Logic

**Algorithm:**
1. Filter matches to only `matched=True`
2. If zero matches → return "unclassified" assignment
3. Look up priority for each matching persona from registry
4. Sort by priority (ascending: 1, 2, 3, ...)
5. Select first (lowest number = highest priority)
6. Build PersonaAssignment with all qualifying personas + reason

**Priority Order (from Story 3.1):**
1. high_utilization (Priority 1)
2. irregular_income (Priority 2)
3. low_savings (Priority 3)
4. subscription_heavy (Priority 4)
5. cash_flow_optimizer (Priority 5)
6. young_professional (Priority 6)

**Example:**
- User matches: low_savings (3), irregular_income (2), subscription_heavy (4)
- Sorted by priority: irregular_income (2), low_savings (3), subscription_heavy (4)
- Selected: irregular_income (priority 2)
- Reason: "Highest priority match among 3 qualifying personas"

### Unclassified Status

**When:** No personas match the user's behavioral signals

**Assignment:**
- `assigned_persona_id`: "unclassified"
- `priority`: None
- `all_qualifying_personas`: []
- `prioritization_reason`: "No qualifying personas found"

**Implications:**
- User sees generic financial advice (no persona-specific content)
- May indicate data quality issues or new user with insufficient history
- Should be rare in production (persona 6 is a catch-all)

### References

- [Source: docs/prd/epic-3-persona-assignment-system.md#Story-3.3]
- [Source: docs/architecture.md#Personas-Module (lines 912-947)]
- [Source: EPIC_3_HANDOFF.md - Story 3.2 completion notes]
- [Source: spendsense/config/personas.yaml - Priority values]

## Dev Agent Record

### Context Reference

**From Story 3.2:**
- PersonaMatch model available with: persona_id, matched, evidence, matched_conditions
- Matcher returns List[PersonaMatch] for all 6 personas
- Need to filter for matched=True before prioritizing

**From Story 3.1:**
- Persona registry has priority field (1-6, unique)
- Registry available via `load_persona_registry()`
- Can get persona by ID: `registry.get_persona_by_id(persona_id)`

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

TBD after implementation

### Completion Notes List

TBD after implementation

### File List

**NEW:**
- `spendsense/personas/prioritizer.py`
- `tests/test_persona_prioritizer.py`

**MODIFIED:**
- None expected
