# Story 6.3: Persona Assignment Review Interface

Status: ready-for-dev

## Story

As an **operator**,
I want **view of persona assignments with complete decision trace**,
so that **I can audit persona classification accuracy and understand prioritization logic**.

## Acceptance Criteria

1. Persona assignment displayed prominently for selected user
2. Both 30-day and 180-day persona assignments shown
3. All qualifying personas listed with match evidence (specific signal values that triggered match)
4. Prioritization logic explanation shown (why highest-priority persona was selected)
5. Persona definition displayed: criteria, educational focus, priority rank
6. Assignment confidence level displayed if applicable
7. Assignment timestamp and data version shown
8. Persona change history displayed if persona shifted between time windows
9. Manual persona override capability for admin role
10. Override actions logged with operator ID and justification required

## Tasks / Subtasks

- [ ] Task 1: Create backend API endpoints for persona data (AC: #1, #2, #3, #4, #7)
  - [ ] GET `/api/operator/personas/{user_id}` - Get persona assignments for both time windows
  - [ ] GET `/api/operator/personas/{user_id}/history` - Get persona change history
  - [ ] POST `/api/operator/personas/{user_id}/override` - Manual persona override (admin only)
  - [ ] GET `/api/operator/personas/definitions` - Get all persona definitions with criteria
  - [ ] Implement authentication requirement (viewer for GET, admin for POST)
  - [ ] Return complete decision trace with match evidence and prioritization reason

- [ ] Task 2: Design and implement persona assignment UI (AC: #1, #2, #5)
  - [ ] Create `PersonaAssignmentView` component
  - [ ] Display current persona prominently with icon/badge
  - [ ] Show persona definition: name, educational focus, priority rank
  - [ ] Create split view for 30-day vs 180-day assignments
  - [ ] Highlight differences between time windows
  - [ ] Add persona description tooltip
  - [ ] Style with TailwindCSS and persona-specific colors

- [ ] Task 3: Implement qualifying personas and match evidence display (AC: #3)
  - [ ] Display list of all personas that matched criteria
  - [ ] For each qualifying persona, show:
    - Persona name and priority rank
    - Signal values that triggered match (e.g., "credit_max_utilization_pct: 75% > 70% threshold")
    - Match timestamp
  - [ ] Highlight which persona was selected (highest priority)
  - [ ] Show signal citations with links to Signal Dashboard (Story 6.2)
  - [ ] Add "View Full Criteria" button showing persona definition

- [ ] Task 4: Implement prioritization logic explanation (AC: #4)
  - [ ] Display prioritization reason from database (e.g., "Selected 'High Credit Utilization' over 'Subscription-Heavy' due to higher priority rank (1 vs 3)")
  - [ ] Show priority ranking table: "Rank 1: High Credit Utilization, Rank 2: Low Savings, ..."
  - [ ] Explain tie-breaking logic if multiple personas have same priority
  - [ ] Add tooltip explaining deterministic prioritization approach
  - [ ] Cite source: persona registry with priority ranks

- [ ] Task 5: Implement persona change history display (AC: #8)
  - [ ] Create timeline component showing persona changes over time
  - [ ] Display: date, previous persona, new persona, reason for change
  - [ ] Show signal changes that triggered persona shift (e.g., "credit_max_utilization_pct dropped from 75% to 45%")
  - [ ] Add filters: last 30 days, last 180 days, all time
  - [ ] Highlight manual overrides vs automatic assignments
  - [ ] Link to historical signal values (if available)

- [ ] Task 6: Implement manual persona override (AC: #9, #10)
  - [ ] Add "Override Persona" button (visible to admin role only)
  - [ ] Create override modal with:
    - Dropdown of all available personas
    - Required justification text field (min 20 characters)
    - Warning message about override impact
    - Confirm/Cancel buttons
  - [ ] POST override to backend with operator_id, new_persona_id, justification
  - [ ] Show success confirmation with new persona assignment
  - [ ] Log override in audit trail (operator_id, user_id, old_persona, new_persona, justification, timestamp)
  - [ ] Refresh assignment view after override
  - [ ] Display override indicator (badge: "Manually Overridden by {operator_name}")

- [ ] Task 7: Integrate with persona registry and definitions (AC: #5)
  - [ ] Load persona definitions from persona registry (Epic 3)
  - [ ] Display for each persona:
    - Persona ID (e.g., "high_utilization")
    - Display name (e.g., "High Credit Utilization")
    - Educational focus (e.g., "Debt reduction strategies")
    - Matching criteria (e.g., "credit_max_utilization_pct > 70%")
    - Priority rank (1-6)
  - [ ] Show definitions in expandable/collapsible sections
  - [ ] Highlight criteria that matched for this user
  - [ ] Add link to full persona documentation

- [ ] Task 8: Implement confidence level display (AC: #6)
  - [ ] If confidence score exists in assignment data, display it
  - [ ] Show confidence as percentage with visual indicator (progress bar)
  - [ ] Add confidence interpretation: High (>80%), Medium (50-80%), Low (<50%)
  - [ ] If no confidence score, display "Deterministic Assignment" badge
  - [ ] Add tooltip explaining confidence calculation (if applicable)

- [ ] Task 9: Implement timestamp and data version display (AC: #7)
  - [ ] Display assignment timestamp with timezone (e.g., "2025-11-06 10:30:15 UTC")
  - [ ] Show data version (e.g., "Signals v1.0, Personas v2.1")
  - [ ] Display "Last Updated" relative time (e.g., "2 hours ago")
  - [ ] Show signal computation timestamp (from Story 6.2)
  - [ ] Add refresh button to recompute persona assignment

- [ ] Task 10: Write comprehensive unit and integration tests (AC: #1-10)
  - [ ] Test persona API endpoints return correct assignment data
  - [ ] Test authentication enforcement (viewer for GET, admin for POST override)
  - [ ] Test persona override requires justification (400 if missing)
  - [ ] Test override logs audit entry with operator_id and justification
  - [ ] Test React component renders assignment with qualifying personas
  - [ ] Test match evidence displays correct signal values
  - [ ] Test prioritization logic explanation is accurate
  - [ ] Test persona change history timeline renders correctly
  - [ ] Test override modal only visible to admin role
  - [ ] Test override updates assignment and refreshes UI

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**

- **Frontend:** React 18 + TypeScript + shadcn/ui components
- **Backend:** FastAPI with Pydantic validation
- **Database Models:**
  - `PersonaAssignment`: assignment_id, user_id, assigned_persona_id, qualifying_personas (JSON), match_evidence (JSON), prioritization_reason
  - `Persona`: persona_id, name, criteria (JSON), educational_focus, priority_rank
- **Authentication:** Requires Story 6.1 RBAC (viewer for view, admin for override)
- **Audit Logging:** structlog for all override actions

**Key Requirements:**
- Display complete decision trace for transparency
- Show all qualifying personas, not just selected one
- Explain prioritization logic in plain language
- Support manual override with audit trail
- Integrate with Signal Dashboard for context

**Persona Registry (Epic 3):**
- 6 total personas: High Credit Utilization, Subscription-Heavy, Low Savings, Irregular Income, Cash Flow Optimizer, Young Professional
- Deterministic prioritization by rank (1 = highest priority)
- Matching criteria based on behavioral signals (Epic 2)

### Project Structure Notes

**New Files to Create:**
- `spendsense/api/operator_personas.py` - Persona assignment API endpoints
- `ui/src/pages/PersonaAssignmentView.tsx` - Main persona assignment page
- `ui/src/components/PersonaCard.tsx` - Display persona with definition
- `ui/src/components/QualifyingPersonas.tsx` - List of all matching personas
- `ui/src/components/MatchEvidence.tsx` - Signal citations that triggered match
- `ui/src/components/PersonaChangeHistory.tsx` - Timeline of persona changes
- `ui/src/components/PersonaOverrideModal.tsx` - Override form for admin
- `ui/src/hooks/usePersonaAssignment.ts` - React Query hook
- `tests/test_operator_personas.py` - Backend API tests
- `ui/src/tests/PersonaAssignmentView.test.tsx` - Frontend tests

**Files to Modify:**
- `spendsense/api/main.py` - Register operator_personas routes
- `ui/src/App.tsx` - Add Persona Assignment route
- `ui/src/navigation/OperatorNav.tsx` - Add persona link

**API Response Format:**
```json
{
  "user_id": "user_MASKED_000",
  "assignments": {
    "30_day": {
      "assignment_id": "assign_123",
      "assigned_persona_id": "high_utilization",
      "assigned_persona_name": "High Credit Utilization",
      "assigned_at": "2025-11-06T10:30:00Z",
      "priority_rank": 1,
      "qualifying_personas": [
        {
          "persona_id": "high_utilization",
          "persona_name": "High Credit Utilization",
          "priority_rank": 1,
          "match_evidence": {
            "credit_max_utilization_pct": {"value": 75.0, "threshold": 70.0, "matched": true}
          }
        },
        {
          "persona_id": "subscription_heavy",
          "persona_name": "Subscription-Heavy",
          "priority_rank": 3,
          "match_evidence": {
            "subscription_share_pct": {"value": 32.0, "threshold": 25.0, "matched": true}
          }
        }
      ],
      "prioritization_reason": "Selected 'High Credit Utilization' (rank 1) over 'Subscription-Heavy' (rank 3) due to higher priority",
      "confidence_level": null,
      "is_override": false
    },
    "180_day": { /* same structure */ }
  },
  "change_history": [
    {
      "changed_at": "2025-10-15T08:00:00Z",
      "previous_persona": "low_savings",
      "new_persona": "high_utilization",
      "reason": "credit_max_utilization_pct increased from 45% to 75%",
      "is_override": false
    }
  ]
}
```

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest for backend, Jest/React Testing Library for frontend
- Coverage target: ≥10 tests per story
- Security tests: Verify admin-only override enforcement
- Audit tests: Verify all overrides logged with justification

**Test Categories:**
1. Backend API tests: Assignment retrieval, override authorization, audit logging
2. Frontend tests: Component rendering, override modal, role-based visibility
3. Integration tests: Full flow from API to UI display
4. E2E tests: View assignment → override persona (admin) → verify audit log

### Learnings from Previous Stories

**From Story 6.1 (Operator Authentication & Authorization)**
- **RBAC Enforcement**: Use `@require_role('viewer')` for GET, `@require_role('admin')` for POST override
- **Audit Logging**: Log all override actions with operator_id, user_id, action, justification
- **Testing Pattern**: TestClient with auth headers

**From Story 6.2 (User Signal Dashboard)**
- **Signal Context**: Persona assignments display signal values that triggered match
- **Link Integration**: Link match evidence to Signal Dashboard for full context
- **Time Window Comparison**: Show 30-day vs 180-day assignments side-by-side

**Previous Epics Context:**
- **Epic 3 (Persona Assignment)**: PersonaAssignment table with qualifying_personas and match_evidence JSON fields
- **Persona Registry**: 6 personas with deterministic priority ranking
- **Story 3-3**: Prioritization logic implemented (deterministic by rank)

### References

- [Source: docs/prd/epic-6-operator-view-oversight-interface.md#Story-6.3] - Story 6.3 acceptance criteria
- [Source: docs/architecture.md#Data-Models] - PersonaAssignment model schema
- [Source: docs/stories/6-1-operator-authentication-authorization.md] - RBAC patterns
- [Source: docs/stories/6-2-user-signal-dashboard.md] - Signal display integration
- [Source: docs/stories/3-3-deterministic-prioritization-logic.md] - Prioritization implementation (Epic 3)

## Dev Agent Record

### Context Reference

- docs/stories/6-3-persona-assignment-review-interface.context.xml

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
- Initial story creation from Epic 6 PRD
- Integrated with Story 6.1 authentication (viewer for view, admin for override)
- Integrated with Story 6.2 signal dashboard (match evidence links)
- Mapped to Epic 3 persona assignment system
- Designed API response format with qualifying personas and match evidence
- Outlined 10 task groups for backend API and React UI
- Defined override workflow with audit trail
- Added persona change history timeline requirement
- Status: drafted (ready for story-context workflow)
