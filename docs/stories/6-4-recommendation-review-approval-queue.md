# Story 6.4: Recommendation Review & Approval Queue

Status: drafted

## Story

As an **operator**,
I want **review queue of generated recommendations with approve/override/flag capabilities**,
so that **I can ensure recommendation quality and appropriateness before user delivery**.

## Acceptance Criteria

1. Review queue displays pending recommendations requiring operator approval
2. Each recommendation shown with full details: content/offer, rationale, persona match, signal citations
3. Guardrail check results displayed: consent status, eligibility pass/fail, tone validation
4. Decision trace displayed showing why recommendation was generated
5. Operator can approve recommendation (marks as ready for delivery)
6. Operator can override recommendation (blocks delivery and requires justification)
7. Operator can flag recommendation for further review (adds to watch list)
8. Approval/override actions logged in audit trail
9. Filters available: persona type, recommendation type, guardrail failures
10. Batch approval capability for high-confidence recommendations

## Tasks / Subtasks

- [ ] Task 1: Create database schema for review queue (AC: #1, **EPIC 5 DEFERRED AC7/AC5**)
  - [ ] Create `flagged_recommendations` table:
    - recommendation_id (PK)
    - user_id
    - content_id
    - flagged_at (timestamp)
    - flagged_by (operator_id)
    - flag_reason (text)
    - guardrail_status (enum: eligibility_fail, tone_fail, manual_flag)
    - review_status (enum: pending, approved, overridden, escalated)
    - reviewed_at (timestamp, nullable)
    - reviewed_by (operator_id, nullable)
    - review_notes (text, nullable)
  - [ ] Create indexes on: flagged_at, review_status, guardrail_status
  - [ ] Add foreign key constraints to users, operators tables
  - [ ] Create database migration script

- [ ] Task 2: Create backend API endpoints for review queue (AC: #1, #9, #10)
  - [ ] GET `/api/operator/review/queue` - Get pending recommendations with filters
    - Query params: status (pending/approved/overridden/flagged), persona, guardrail_status, limit, offset
  - [ ] GET `/api/operator/review/{recommendation_id}` - Get full recommendation details
  - [ ] POST `/api/operator/review/{recommendation_id}/approve` - Approve recommendation
  - [ ] POST `/api/operator/review/{recommendation_id}/override` - Override with justification
  - [ ] POST `/api/operator/review/{recommendation_id}/flag` - Flag for escalation
  - [ ] POST `/api/operator/review/batch-approve` - Approve multiple recommendations
  - [ ] Implement authentication requirement (reviewer or admin role)
  - [ ] Return complete guardrail check results and decision trace

- [ ] Task 3: Integrate with Epic 5 guardrail pipeline (AC: #3, **EPIC 5 INTEGRATION**)
  - [ ] Modify tone validator (`spendsense/guardrails/tone.py`) to save flagged recommendations to database
  - [ ] Modify eligibility filter (`spendsense/guardrails/eligibility.py`) to save filtered recommendations to database
  - [ ] Update recommendation assembler to check manual flag status before delivery
  - [ ] Add auto-flagging logic: flag recommendations that fail tone or eligibility
  - [ ] Include guardrail metadata in review queue responses:
    - Consent status (opted_in/opted_out)
    - Eligibility pass/fail with reason (age, income, credit score, etc.)
    - Tone validation pass/fail with detected violations
    - Disclaimer presence confirmation

- [ ] Task 4: Design and implement review queue UI (AC: #1, #2, #9)
  - [ ] Create `ReviewQueue` component with table/card layout
  - [ ] Display columns: User ID, Persona, Content Title, Flagged Reason, Flagged Date, Status
  - [ ] Add filters: Status (pending/all), Persona type, Guardrail failure type
  - [ ] Add sorting: Date (newest/oldest), Severity (high/low)
  - [ ] Add pagination for large queues
  - [ ] Add search by user ID or content ID
  - [ ] Show item count and statistics (pending count, avg review time)
  - [ ] Style with TailwindCSS and status-specific colors

- [ ] Task 5: Implement recommendation detail view (AC: #2, #4)
  - [ ] Create `RecommendationDetailModal` component
  - [ ] Display full recommendation:
    - Content title and summary
    - Content type (education / partner offer)
    - Rationale with signal citations
    - Persona assignment and match evidence
    - User context (link to Signal Dashboard and Persona View)
  - [ ] Display decision trace:
    - Why recommendation was generated (persona match + signals)
    - Matching logic explanation
    - Ranking score (if applicable)
  - [ ] Add "View User Profile" link to Stories 6.2/6.3 pages

- [ ] Task 6: Implement guardrail results display (AC: #3)
  - [ ] Create `GuardrailResults` component
  - [ ] Display consent status with badge (opted_in green, opted_out red)
  - [ ] Display eligibility check results:
    - Age eligibility: pass/fail with reason
    - Income eligibility: pass/fail with threshold
    - Credit score eligibility: pass/fail
    - Debt ratio eligibility: pass/fail
    - Show which criteria failed
  - [ ] Display tone validation results:
    - Pass/fail status
    - Detected violations (list of problematic phrases)
    - Severity level (warning/critical)
  - [ ] Display disclaimer presence confirmation
  - [ ] Use color coding: green (pass), yellow (warning), red (fail)

- [ ] Task 7: Implement approve/override/flag actions (AC: #5, #6, #7, #8)
  - [ ] Add "Approve" button (reviewer or admin role)
    - Confirmation dialog: "Approve recommendation for delivery?"
    - POST to approve endpoint
    - Update status to "approved" and show success message
  - [ ] Add "Override" button (admin role only)
    - Modal with required justification field (min 50 characters)
    - Warning message about blocking delivery
    - POST to override endpoint with justification
    - Update status to "overridden" and log action
  - [ ] Add "Flag for Escalation" button (reviewer or admin)
    - Modal with flag reason selection (dropdown: quality_concern, policy_violation, needs_review, other)
    - Optional notes field
    - POST to flag endpoint
    - Update status to "escalated"
  - [ ] Log all actions to audit trail (Epic 6.5) with operator_id, action, timestamp, justification

- [ ] Task 8: Implement batch approval (AC: #10)
  - [ ] Add checkbox selection for recommendations in queue
  - [ ] Add "Select All" checkbox in header
  - [ ] Add "Batch Approve" button (enabled when 1+ selected)
  - [ ] Show confirmation modal: "Approve {count} recommendations?"
  - [ ] POST batch request with array of recommendation_ids
  - [ ] Show progress indicator during batch operation
  - [ ] Show success summary: "{approved}/{total} approved, {failed} failed"
  - [ ] Refresh queue after batch operation

- [ ] Task 9: Implement filters and search (AC: #9)
  - [ ] Create filter panel with:
    - Status dropdown: Pending, Approved, Overridden, Flagged, All
    - Persona multi-select: All 6 personas
    - Guardrail failure multi-select: Eligibility, Tone, Manual Flag
    - Content type: Education, Partner Offer, All
  - [ ] Implement search bar for user ID or content ID
  - [ ] Add "Clear Filters" button
  - [ ] Update URL query params with filters (shareable URLs)
  - [ ] Show active filter count badge
  - [ ] Apply filters client-side for quick response, then fetch from API

- [ ] Task 10: Write comprehensive unit and integration tests (AC: #1-10)
  - [ ] Test database schema creation and migrations
  - [ ] Test review queue API endpoints return correct data
  - [ ] Test authentication enforcement (reviewer for approve, admin for override)
  - [ ] Test guardrail integration saves flagged recommendations to database
  - [ ] Test approve endpoint updates status and logs action
  - [ ] Test override requires justification (400 if missing)
  - [ ] Test flag endpoint adds to escalation queue
  - [ ] Test batch approval processes multiple recommendations
  - [ ] Test filters return correct subset of queue
  - [ ] Test React components render queue and detail views correctly

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**

- **Backend:** FastAPI with Pydantic validation
- **Frontend:** React 18 + TypeScript + shadcn/ui
- **Database:** SQLite with new `flagged_recommendations` table
- **Authentication:** Requires Story 6.1 RBAC (reviewer for approve/flag, admin for override)
- **Audit Logging:** structlog for all review actions (integrates with Story 6.5)

**Key Requirements:**
- Database persistence for flagged recommendations (ADDRESSES EPIC 5 DEFERRED AC7/AC5)
- Integration with Epic 5 guardrails (tone, eligibility)
- Complete decision trace for transparency
- Operator actions (approve, override, flag) with audit trail
- Batch operations for efficiency

**Epic 5 Deferred Items:**
- **Story 5.3 AC7**: "Manual review queue for flagged recommendations" - Logging in place, DATABASE DEFERRED
- **Story 5.5 AC5**: "Failed recommendations flagged for manual review" - PARTIALLY IMPLEMENTED, DATABASE DEFERRED
- **This story completes**: Database table, UI, and full workflow for manual review queue

### Project Structure Notes

**New Files to Create:**
- `spendsense/models/review_queue.py` - FlaggedRecommendation model
- `spendsense/api/operator_review.py` - Review queue API endpoints
- `spendsense/services/review_service.py` - Review queue business logic
- `ui/src/pages/ReviewQueue.tsx` - Main review queue page
- `ui/src/components/RecommendationDetailModal.tsx` - Detail view modal
- `ui/src/components/GuardrailResults.tsx` - Guardrail status display
- `ui/src/components/ReviewActions.tsx` - Approve/override/flag buttons
- `ui/src/components/BatchApproval.tsx` - Batch approval UI
- `ui/src/hooks/useReviewQueue.ts` - React Query hook
- `tests/test_review_queue.py` - Backend tests
- `ui/src/tests/ReviewQueue.test.tsx` - Frontend tests

**Files to Modify:**
- `spendsense/guardrails/tone.py` - Add database flagging for tone violations
- `spendsense/guardrails/eligibility.py` - Add database flagging for eligibility failures
- `spendsense/recommendations/assembler.py` - Check review status before delivery
- `spendsense/ingestion/database_writer.py` - Add FlaggedRecommendation model
- `spendsense/api/main.py` - Register operator_review routes
- `ui/src/App.tsx` - Add ReviewQueue route
- `ui/src/navigation/OperatorNav.tsx` - Add review queue link with pending count badge

**Database Schema:**
```sql
CREATE TABLE flagged_recommendations (
    recommendation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    content_title TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK(content_type IN ('education', 'partner_offer')),
    rationale TEXT NOT NULL,
    flagged_at TIMESTAMP NOT NULL,
    flagged_by TEXT,  -- operator_id or 'system' for auto-flags
    flag_reason TEXT NOT NULL,  -- eligibility_fail, tone_fail, manual_flag
    guardrail_status TEXT NOT NULL,  -- JSON with full guardrail check results
    decision_trace TEXT NOT NULL,  -- JSON with persona, signals, matching logic
    review_status TEXT NOT NULL DEFAULT 'pending' CHECK(review_status IN ('pending', 'approved', 'overridden', 'escalated')),
    reviewed_at TIMESTAMP,
    reviewed_by TEXT,  -- operator_id
    review_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (flagged_by) REFERENCES operators(operator_id),
    FOREIGN KEY (reviewed_by) REFERENCES operators(operator_id)
);

CREATE INDEX idx_flagged_recs_status ON flagged_recommendations(review_status);
CREATE INDEX idx_flagged_recs_flagged_at ON flagged_recommendations(flagged_at DESC);
CREATE INDEX idx_flagged_recs_user ON flagged_recommendations(user_id);
```

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest for backend, Jest/React Testing Library for frontend
- Coverage target: ≥10 tests per story (aim for 20+ given critical epic 5 integration)
- Integration tests: Full guardrail → database → review queue → approval flow
- Security tests: Verify reviewer/admin role enforcement

**Test Categories:**
1. Database tests: Schema creation, flagged_recommendations CRUD
2. Guardrail integration tests: Tone/eligibility failures save to database
3. API tests: Queue retrieval, approve/override/flag actions, batch approval
4. RBAC tests: Verify reviewer can approve/flag, only admin can override
5. Frontend tests: Queue rendering, action buttons, batch selection
6. E2E tests: Recommendation flagged → appears in queue → operator approves → status updated

### Learnings from Previous Stories

**From Story 6.1 (Operator Authentication & Authorization)**
- **RBAC Enforcement**: Use `@require_role('reviewer')` for approve/flag, `@require_role('admin')` for override
- **Audit Logging**: Log all review actions with operator_id, action, recommendation_id, timestamp, justification

**From Story 6.2 (User Signal Dashboard)**
- **Link Integration**: Link to Signal Dashboard to view user's behavioral signals

**From Story 6.3 (Persona Assignment Review Interface)**
- **Link Integration**: Link to Persona View to understand why recommendation was generated

**Epic 5 Context - CRITICAL INTEGRATION:**
- **Story 5.3 AC7**: "Recommendations with problematic tone flagged for manual operator review with logging"
  - **Status**: Logging implemented, DATABASE FLAGGING DEFERRED to this story
  - **Integration Point**: `spendsense/guardrails/tone.py` - Add database insert for flagged recommendations
- **Story 5.5 AC5**: "Failed recommendations flagged for manual review"
  - **Status**: Partially implemented (logging), DATABASE PERSISTENCE DEFERRED
  - **Integration Point**: Both tone and eligibility guardrails need database integration
- **Guardrail Pipeline**: Consent → Eligibility → Tone → Disclaimer (from Story 5.5)
  - This story adds persistence layer for flagged items

### References

- [Source: docs/prd/epic-6-operator-view-oversight-interface.md#Story-6.4] - Story 6.4 acceptance criteria
- [Source: docs/architecture.md#Data-Models] - Recommendation model schema
- [Source: docs/backlog.md] - Epic 5 deferred items (manual review queue database)
- [Source: docs/stories/5-3-tone-validation-language-safety.md] - AC7 deferred to this story
- [Source: docs/stories/5-5-guardrails-integration-testing.md] - AC5 partially implemented
- [Source: docs/stories/6-1-operator-authentication-authorization.md] - RBAC patterns
- [Source: docs/stories/6-2-user-signal-dashboard.md] - Signal display integration
- [Source: docs/stories/6-3-persona-assignment-review-interface.md] - Persona context integration
- [Source: spendsense/guardrails/tone.py] - Tone validation implementation to modify
- [Source: spendsense/guardrails/eligibility.py] - Eligibility filtering implementation to modify

## Dev Agent Record

### Context Reference

- docs/stories/6-4-recommendation-review-approval-queue.context.xml

### Agent Model Used

<!-- Will be filled in by dev agent -->

### Debug Log References

<!-- Will be filled in by dev agent -->

### Completion Notes List

<!-- Will be filled in by dev agent during implementation -->

### File List

<!-- Will be filled in by dev agent:
NEW: List new files created
MODIFIED: List files modified (including tone.py, eligibility.py, assembler.py)
DELETED: List files deleted (if any)
-->

## Change Log

**2025-11-06 - v1.0 - Story Drafted**
- Initial story creation from Epic 6 PRD
- **ADDRESSES EPIC 5 DEFERRED ITEMS**: Stories 5.3 AC7 and 5.5 AC5 (manual review queue database)
- Integrated with Story 6.1 authentication (reviewer for approve/flag, admin for override)
- Integrated with Stories 6.2/6.3 for user context (signals and persona)
- Designed database schema for `flagged_recommendations` table
- Outlined guardrail integration (tone.py, eligibility.py modifications)
- Defined review queue API endpoints and UI components
- Included batch approval capability for efficiency
- Added comprehensive audit logging for all review actions
- Outlined 10 task groups with 50+ subtasks
- Status: drafted (ready for story-context workflow)
