# Story 3.4: Persona Assignment & Audit Logging

Status: drafted

## Story

As a **developer**,
I want **persona assignment results stored with complete audit trail of decision logic**,
so that **every persona assignment is explainable and can be reviewed for quality assurance**.

## Acceptance Criteria

1. Assigned persona stored per user per time window (30-day and 180-day)
2. Assignment record includes: persona ID, assignment timestamp, confidence level
3. All qualifying personas logged with match evidence
4. Audit log includes specific signal values that triggered each match
5. Audit log includes reason why highest-priority persona was selected
6. Assignment accessible via API GET /profile/{user_id}
7. Audit logs stored in structured format (JSON) in database
8. Operator can view full decision trace in UI
9. Unit tests verify complete audit trail generation

## Tasks / Subtasks

- [ ] Task 1: Create database schema for persona_assignments table (AC: 1, 2, 7)
  - [ ] Add PersonaAssignmentRecord SQLAlchemy model to database_writer.py
  - [ ] Fields: assignment_id, user_id, time_window, assigned_persona_id, assigned_at
  - [ ] Fields: priority, qualifying_personas (JSON), match_evidence (JSON), prioritization_reason
  - [ ] Create database migration or schema update
  - [ ] Add indexes for user_id and time_window

- [ ] Task 2: Create assignment storage module (AC: 3, 4, 5, 7)
  - [ ] Create `spendsense/personas/assigner.py`
  - [ ] Implement `store_assignment()` function
  - [ ] Store PersonaAssignment to database
  - [ ] Store match evidence from all qualifying personas
  - [ ] Generate unique assignment_id (UUID)

- [ ] Task 3: Add API endpoint for persona profile (AC: 6, 8)
  - [ ] Add GET `/api/profile/{user_id}` endpoint
  - [ ] Return current persona assignment for both 30d and 180d windows
  - [ ] Include full audit trail in response
  - [ ] Return 404 if user not found
  - [ ] Return empty/unclassified if no assignment exists

- [ ] Task 4: Integrate matcher → prioritizer → assigner (AC: 1, 2, 3, 4, 5)
  - [ ] Create orchestration function that chains all three modules
  - [ ] Input: user_id, reference_date, time_window
  - [ ] Steps: generate behavioral summary → match personas → prioritize → store assignment
  - [ ] Return PersonaAssignment with database ID

- [ ] Task 5: Write comprehensive unit tests (AC: 9)
  - [ ] Test database storage and retrieval
  - [ ] Test API endpoint responses
  - [ ] Test audit trail completeness
  - [ ] Test both 30d and 180d windows
  - [ ] Test unclassified status storage
  - [ ] Mock database for unit tests

## Dev Notes

### Architecture Alignment

**From architecture.md (lines 1481-1494):**
```sql
CREATE TABLE persona_assignments (
    assignment_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    signal_id TEXT NOT NULL,
    time_window TEXT CHECK(time_window IN ('30_day', '180_day')),
    assigned_persona_id TEXT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    qualifying_personas TEXT, -- JSON array
    match_evidence TEXT, -- JSON object
    prioritization_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (signal_id) REFERENCES behavioral_signals(signal_id)
);
```

**Note:** The architecture includes `signal_id` foreign key, but Stories 3.1-3.3 don't generate behavioral_signals records. For this story, we'll make `signal_id` optional or create a lightweight behavioral_signals record during assignment.

### Project Structure Notes

**Files to Create:**
- `spendsense/personas/assigner.py` - Assignment storage logic

**Files to Modify:**
- `spendsense/ingestion/database_writer.py` - Add PersonaAssignmentRecord model
- `spendsense/api/main.py` - Add GET /api/profile/{user_id} endpoint

**Database Model:**
```python
class PersonaAssignmentRecord(Base):
    __tablename__ = 'persona_assignments'

    assignment_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    time_window = Column(String, nullable=False)  # "30d" or "180d"
    assigned_persona_id = Column(String, nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    priority = Column(Integer)  # None for unclassified
    qualifying_personas = Column(JSON)  # List[str]
    match_evidence = Column(JSON)  # Dict[str, Dict]
    prioritization_reason = Column(Text)
```

### Dependencies

**Consumes:**
- Story 3.1: Persona registry
- Story 3.2: PersonaMatcher, PersonaMatch
- Story 3.3: PersonaPrioritizer, PersonaAssignment
- Epic 2: BehavioralSummaryGenerator

**Produces:**
- Database table: persona_assignments
- Assigner module with store/retrieve functions
- API endpoint: GET /profile/{user_id}
- Orchestration function for end-to-end assignment

### Testing Strategy

**Unit Tests:**
- Test PersonaAssignmentRecord model creation
- Test store_assignment() with various PersonaAssignment objects
- Test retrieve_assignment() by user_id and time_window
- Test API endpoint with existing/non-existing users
- Test JSON serialization of qualifying_personas and match_evidence
- Mock database using fixtures

**Integration Test:**
- End-to-end test: user_id → behavioral summary → matching → prioritization → storage → API retrieval
- Verify complete audit trail from database

**Test File:** `tests/test_persona_assigner.py`

### API Endpoint Design

**Endpoint:** `GET /api/profile/{user_id}`

**Query Parameters:**
- `time_window` (optional): "30d" or "180d" (default: both)

**Response (200 OK):**
```json
{
  "user_id": "user_001",
  "assignments": {
    "30d": {
      "assignment_id": "uuid-here",
      "assigned_persona_id": "high_utilization",
      "priority": 1,
      "assigned_at": "2025-11-05T10:30:00Z",
      "all_qualifying_personas": ["high_utilization", "low_savings"],
      "prioritization_reason": "Highest priority match among 2 qualifying personas (priority 1)",
      "match_evidence": {
        "high_utilization": {
          "matched": true,
          "evidence": {"credit_max_utilization_pct": 60.0},
          "matched_conditions": ["credit_max_utilization_pct >= 50.0"]
        },
        "low_savings": {
          "matched": true,
          "evidence": {"savings_emergency_fund_months": 2.5},
          "matched_conditions": ["savings_emergency_fund_months < 3.0"]
        }
      }
    },
    "180d": { ... }
  }
}
```

**Response (404 Not Found):**
```json
{
  "detail": "User not found"
}
```

**Response (200 OK - No Assignment):**
```json
{
  "user_id": "user_001",
  "assignments": {
    "30d": {
      "assigned_persona_id": "unclassified",
      "prioritization_reason": "No assignment found for this time window"
    },
    "180d": null
  }
}
```

### Orchestration Function

**Function:** `assign_persona(user_id: str, reference_date: date, time_window: str, db_path: str) -> PersonaAssignment`

**Steps:**
1. Generate behavioral summary (Epic 2)
2. Match personas (Story 3.2)
3. Prioritize (Story 3.3)
4. Store assignment (Story 3.4)
5. Return assignment with database ID

**Location:** `spendsense/personas/assigner.py`

### Signal ID Handling

**Issue:** Architecture shows `signal_id` foreign key, but we don't have behavioral_signals table yet.

**Solutions:**
1. **Option A (Simplest):** Make signal_id nullable for now, add it in future story when behavioral_signals table is created
2. **Option B:** Create minimal behavioral_signals record during assignment
3. **Option C:** Remove foreign key constraint for this story

**Recommendation:** Option A - Make signal_id nullable. This allows Story 3.4 to be complete without blocking on behavioral_signals table creation.

### References

- [Source: docs/prd/epic-3-persona-assignment-system.md#Story-3.4]
- [Source: docs/architecture.md#Database-Schema (lines 1481-1494)]
- [Source: spendsense/personas/matcher.py - PersonaMatch model]
- [Source: spendsense/personas/prioritizer.py - PersonaAssignment model]

## Dev Agent Record

### Context Reference

**From Story 3.3:**
- PersonaAssignment model available with: assigned_persona_id, priority, all_qualifying_personas, prioritization_reason, assigned_at
- PersonaPrioritizer.prioritize_persona() returns PersonaAssignment

**From Story 3.2:**
- PersonaMatcher.match_personas() returns List[PersonaMatch]
- PersonaMatch includes: persona_id, matched, evidence, matched_conditions

**From Epic 2:**
- BehavioralSummaryGenerator available for generating behavioral summary
- API endpoint /api/signals/{user_id} exists

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

TBD after implementation

### Completion Notes List

TBD after implementation

### File List

**NEW:**
- `spendsense/personas/assigner.py`
- `tests/test_persona_assigner.py`

**MODIFIED:**
- `spendsense/ingestion/database_writer.py` (add PersonaAssignmentRecord model)
- `spendsense/api/main.py` (add GET /api/profile/{user_id} endpoint)
