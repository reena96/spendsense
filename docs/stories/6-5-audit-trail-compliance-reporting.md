# Story 6.5: Audit Trail & Compliance Reporting

Status: drafted

## Story

As a **compliance officer**,
I want **comprehensive audit trail of all system decisions and operator actions**,
so that **the system can demonstrate compliance with ethical guidelines and regulatory requirements**.

## Acceptance Criteria

1. Audit log displays all recommendation decisions with full trace
2. Audit log displays all consent changes with timestamps
3. Audit log displays all eligibility check results
4. Audit log displays all tone validation results
5. Audit log displays all operator actions (approvals, overrides, flags)
6. Search and filter capabilities: date range, user ID, operator ID, action type
7. Export functionality allows downloading audit logs as CSV/JSON
8. Compliance metrics displayed: consent opt-in rate, eligibility failure reasons, tone validation issues
9. Data retention policy documented for audit logs
10. Audit log access restricted to admin and compliance roles

## Tasks / Subtasks

- [ ] Task 1: Design consolidated audit log database schema (AC: #1-5, #9)
  - [ ] Create `audit_log` table:
    - log_id (PK)
    - event_type (enum: recommendation_generated, consent_changed, eligibility_checked, tone_validated, operator_action, persona_assigned)
    - user_id (nullable for operator-only events)
    - operator_id (nullable for system events)
    - recommendation_id (nullable)
    - timestamp (indexed)
    - event_data (JSON with full trace)
    - ip_address (for security)
    - user_agent (for security)
  - [ ] Create indexes on: timestamp, event_type, user_id, operator_id
  - [ ] Define data retention policy: 7 years (financial services standard)
  - [ ] Add automated archival logic for logs >2 years old
  - [ ] Create database migration script

- [ ] Task 2: Integrate audit logging with Epic 5 guardrails (AC: #1-4)
  - [ ] Modify consent service (`spendsense/guardrails/consent.py`):
    - Log all consent changes (event_type: consent_changed)
    - Include: user_id, old_status, new_status, consent_version, timestamp
  - [ ] Modify eligibility service (`spendsense/guardrails/eligibility.py`):
    - Log all eligibility checks (event_type: eligibility_checked)
    - Include: user_id, recommendation_id, pass/fail, failure_reasons (age/income/credit/debt), timestamp
  - [ ] Modify tone validator (`spendsense/guardrails/tone.py`):
    - Log all tone validations (event_type: tone_validated)
    - Include: user_id, recommendation_id, pass/fail, detected_violations, severity, timestamp
  - [ ] Modify recommendation assembler:
    - Log all recommendations generated (event_type: recommendation_generated)
    - Include: user_id, recommendation_id, persona_id, content_ids, guardrail_results, timestamp

- [ ] Task 3: Integrate audit logging with Epic 6 operator actions (AC: #5)
  - [ ] Modify authentication service (Story 6.1):
    - Log login attempts (success/failure) - already implemented in Story 6.1
    - Reuse auth_audit_log table or consolidate into audit_log
  - [ ] Modify persona override (Story 6.3):
    - Log persona overrides (event_type: persona_overridden)
    - Include: user_id, operator_id, old_persona, new_persona, justification, timestamp
  - [ ] Modify review queue (Story 6.4):
    - Log approve/override/flag actions (event_type: operator_action)
    - Include: recommendation_id, operator_id, action (approved/overridden/flagged), justification, timestamp

- [ ] Task 4: Create backend API endpoints for audit log (AC: #6, #7, #10)
  - [ ] GET `/api/operator/audit/log` - Get audit log entries with pagination
    - Query params: event_type, user_id, operator_id, start_date, end_date, limit, offset
    - Require admin or compliance role
  - [ ] GET `/api/operator/audit/export` - Export audit logs as CSV or JSON
    - Query params: format (csv/json), filters (same as above)
    - Require admin or compliance role
    - Stream large exports to avoid memory issues
  - [ ] GET `/api/operator/audit/metrics` - Get compliance metrics
    - Require admin or compliance role
  - [ ] Implement authentication requirement (admin or compliance role only)
  - [ ] Add rate limiting to prevent abuse

- [ ] Task 5: Implement compliance metrics calculation (AC: #8)
  - [ ] Consent metrics:
    - Total users, opted-in count, opted-out count, opt-in rate (%)
    - Consent changes over time (monthly trend)
    - Time to consent (avg days from user creation to opt-in)
  - [ ] Eligibility metrics:
    - Total eligibility checks, pass count, fail count, pass rate (%)
    - Failure reasons breakdown (age, income, credit score, debt ratio, residency)
    - Most common failure combinations
  - [ ] Tone validation metrics:
    - Total validations, pass count, fail count, pass rate (%)
    - Detected violations by category (shame-based, pressure, misleading)
    - Severity distribution (warning vs critical)
  - [ ] Operator action metrics:
    - Total actions, approvals, overrides, flags
    - Action distribution by operator
    - Avg review time per recommendation

- [ ] Task 6: Design and implement audit log UI (AC: #1-5, #6)
  - [ ] Create `AuditLog` page component
  - [ ] Display audit log table with columns:
    - Timestamp, Event Type, User ID, Operator ID, Action/Result, Details (expandable)
  - [ ] Add filter panel:
    - Event type dropdown (all types)
    - Date range picker (last 7 days, 30 days, 90 days, custom)
    - User ID search
    - Operator ID dropdown
  - [ ] Add sorting: Timestamp (newest/oldest), Event type (alphabetical)
  - [ ] Add pagination for large logs
  - [ ] Add "View Details" modal showing full JSON event_data
  - [ ] Style with TailwindCSS and event-specific colors

- [ ] Task 7: Implement export functionality (AC: #7)
  - [ ] Add "Export" button on audit log page
  - [ ] Create export modal:
    - Format selection: CSV or JSON
    - Date range selection
    - Apply current filters checkbox
    - Estimated file size warning
  - [ ] Generate CSV format:
    - Headers: timestamp, event_type, user_id, operator_id, action, details
    - Flatten JSON event_data for CSV compatibility
  - [ ] Generate JSON format:
    - Array of full audit log objects with complete event_data
  - [ ] Trigger browser download
  - [ ] Show progress indicator for large exports
  - [ ] Log export action in audit trail (who exported what)

- [ ] Task 8: Implement compliance metrics dashboard (AC: #8)
  - [ ] Create `ComplianceMetrics` page component
  - [ ] Display consent metrics:
    - Pie chart: Opted-in vs Opted-out users
    - Line chart: Consent changes over time
    - KPI cards: Total users, Opt-in rate, Avg time to consent
  - [ ] Display eligibility metrics:
    - Bar chart: Failure reasons breakdown
    - KPI cards: Total checks, Pass rate, Most common failure
  - [ ] Display tone metrics:
    - Bar chart: Violations by category
    - KPI cards: Total validations, Pass rate, Critical violations
  - [ ] Display operator metrics:
    - Bar chart: Actions by operator
    - KPI cards: Total reviews, Avg review time, Override rate
  - [ ] Add time range selector (last 30 days, 90 days, 1 year, all time)
  - [ ] Use charting library (recharts or Chart.js)

- [ ] Task 9: Implement data retention and archival (AC: #9)
  - [ ] Document data retention policy:
    - Active logs: 2 years in primary database
    - Archived logs: 2-7 years in archive storage (Parquet files)
    - Deletion: After 7 years (configurable)
  - [ ] Create archival script:
    - Run monthly via cron or scheduled task
    - Move logs older than 2 years to Parquet files
    - Compress and store in `data/audit_archives/YYYY-MM/`
    - Update audit_log table to remove archived entries
  - [ ] Create retrieval function for archived logs
  - [ ] Document archive location and access procedure
  - [ ] Add archive access to export functionality (optional)

- [ ] Task 10: Write comprehensive unit and integration tests (AC: #1-10)
  - [ ] Test database schema creation and indexes
  - [ ] Test audit log insertion from consent changes
  - [ ] Test audit log insertion from eligibility checks
  - [ ] Test audit log insertion from tone validations
  - [ ] Test audit log insertion from operator actions
  - [ ] Test audit log API endpoint returns correct filtered results
  - [ ] Test authentication enforcement (admin or compliance role only)
  - [ ] Test CSV export generates correct format
  - [ ] Test JSON export includes full event_data
  - [ ] Test compliance metrics calculation accuracy
  - [ ] Test data retention archival script
  - [ ] Test React components render audit log and metrics correctly

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**

- **Backend:** FastAPI with Pydantic validation
- **Frontend:** React 18 + TypeScript + shadcn/ui
- **Database:** SQLite with `audit_log` table (may need PostgreSQL for high-volume production)
- **Logging:** structlog for structured JSON logging
- **Authentication:** Requires Story 6.1 RBAC (admin or compliance role)
- **Export:** Stream large files to avoid memory issues

**Key Requirements:**
- Comprehensive audit trail for all system decisions and operator actions
- 7-year data retention for financial services compliance
- Export to CSV/JSON for regulatory reporting
- Compliance metrics for monitoring system behavior
- Restricted access (admin and compliance roles only)

**Data Retention Policy:**
- **Active logs**: 2 years in SQLite database
- **Archived logs**: 2-7 years in Parquet files
- **Deletion**: After 7 years (configurable)
- **Rationale**: Financial services typically require 7-year retention for audit trails

### Project Structure Notes

**New Files to Create:**
- `spendsense/models/audit_log.py` - AuditLog model
- `spendsense/api/operator_audit.py` - Audit log API endpoints
- `spendsense/services/audit_service.py` - Audit logging business logic
- `spendsense/services/compliance_metrics.py` - Compliance metrics calculation
- `spendsense/tasks/archive_audit_logs.py` - Archival cron script
- `ui/src/pages/AuditLog.tsx` - Main audit log page
- `ui/src/pages/ComplianceMetrics.tsx` - Compliance dashboard
- `ui/src/components/AuditLogTable.tsx` - Audit log table component
- `ui/src/components/AuditExport.tsx` - Export functionality
- `ui/src/components/MetricsCharts.tsx` - Charts for compliance metrics
- `ui/src/hooks/useAuditLog.ts` - React Query hook
- `tests/test_audit_log.py` - Backend tests
- `ui/src/tests/AuditLog.test.tsx` - Frontend tests

**Files to Modify:**
- `spendsense/guardrails/consent.py` - Add audit logging
- `spendsense/guardrails/eligibility.py` - Add audit logging
- `spendsense/guardrails/tone.py` - Add audit logging
- `spendsense/recommendations/assembler.py` - Add audit logging
- `spendsense/api/main.py` - Register operator_audit routes
- `ui/src/App.tsx` - Add AuditLog and ComplianceMetrics routes
- `ui/src/navigation/OperatorNav.tsx` - Add audit links (compliance section)

**Database Schema:**
```sql
CREATE TABLE audit_log (
    log_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL CHECK(event_type IN (
        'recommendation_generated',
        'consent_changed',
        'eligibility_checked',
        'tone_validated',
        'operator_action',
        'persona_assigned',
        'persona_overridden',
        'login_attempt',
        'unauthorized_access'
    )),
    user_id TEXT,  -- nullable for operator-only events
    operator_id TEXT,  -- nullable for system events
    recommendation_id TEXT,  -- nullable
    timestamp TIMESTAMP NOT NULL,
    event_data TEXT NOT NULL,  -- JSON with full trace
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
);

CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_operator ON audit_log(operator_id);
```

**Event Data JSON Examples:**
```json
{
  "consent_changed": {
    "old_status": "opted_out",
    "new_status": "opted_in",
    "consent_version": "1.0",
    "changed_by": "operator_admin_001"
  },
  "eligibility_checked": {
    "recommendation_id": "rec_123",
    "pass": false,
    "failure_reasons": ["age_below_18", "income_below_threshold"],
    "thresholds": {"age": 18, "income": 20000},
    "user_values": {"age": 17, "income": 15000}
  },
  "tone_validated": {
    "recommendation_id": "rec_456",
    "pass": false,
    "detected_violations": ["irresponsible", "bad with money"],
    "severity": "critical",
    "original_text": "You're irresponsible with money..."
  },
  "operator_action": {
    "action": "overridden",
    "recommendation_id": "rec_789",
    "justification": "Content not appropriate for user's financial situation",
    "review_time_seconds": 120
  }
}
```

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest for backend, Jest/React Testing Library for frontend
- Coverage target: ≥10 tests per story
- Integration tests: Full audit trail from event → database → API → UI
- Security tests: Verify admin/compliance role enforcement

**Test Categories:**
1. Database tests: Schema, indexes, event insertion
2. Integration tests: Guardrail events logged, operator actions logged
3. API tests: Filtered log retrieval, export generation, metrics calculation
4. RBAC tests: Verify admin/compliance role requirement
5. Frontend tests: Log table rendering, export UI, metrics dashboard
6. Archival tests: Old logs moved to Parquet, retrieval from archive

### Learnings from Previous Stories

**From Story 6.1 (Operator Authentication & Authorization)**
- **Audit Logging Pattern**: structlog for structured JSON logs
- **RBAC Enforcement**: Use `@require_role('admin')` or `@require_role('compliance')` for audit endpoints
- **Auth Audit Log**: Already implemented in Story 6.1, may consolidate or reference

**From Story 6.4 (Recommendation Review & Approval Queue)**
- **Operator Actions**: Approve, override, flag actions need audit logging
- **Justification Requirement**: Override actions include justification text

**From Story 6.3 (Persona Assignment Review Interface)**
- **Persona Overrides**: Manual persona overrides need audit logging

**Epic 5 Context:**
- **Guardrail Audit Trails**: Epic 5 established audit trail patterns in metadata
- **Story 5.5**: Comprehensive integration testing with audit trail validation
- **GUARDRAILS_OVERVIEW.md**: Documents audit trail structure and integration points

### References

- [Source: docs/prd/epic-6-operator-view-oversight-interface.md#Story-6.5] - Story 6.5 acceptance criteria
- [Source: docs/architecture.md#Tech-Stack] - structlog, FastAPI, SQLite/Parquet
- [Source: docs/GUARDRAILS_OVERVIEW.md] - Audit trail patterns from Epic 5
- [Source: docs/stories/6-1-operator-authentication-authorization.md] - RBAC and auth audit logging
- [Source: docs/stories/6-3-persona-assignment-review-interface.md] - Persona override logging
- [Source: docs/stories/6-4-recommendation-review-approval-queue.md] - Operator action logging
- [Source: spendsense/guardrails/consent.py] - Consent service to modify
- [Source: spendsense/guardrails/eligibility.py] - Eligibility service to modify
- [Source: spendsense/guardrails/tone.py] - Tone validator to modify

## Dev Agent Record

### Context Reference

- docs/stories/6-5-audit-trail-compliance-reporting.context.xml

### Agent Model Used

<!-- Will be filled in by dev agent -->

### Debug Log References

<!-- Will be filled in by dev agent -->

### Completion Notes List

<!-- Will be filled in by dev agent during implementation -->

### File List

<!-- Will be filled in by dev agent:
NEW: List new files created
MODIFIED: List files modified (including consent.py, eligibility.py, tone.py, assembler.py)
DELETED: List files deleted (if any)
-->

## Change Log

**2025-11-06 - v1.0 - Story Drafted**
- Initial story creation from Epic 6 PRD
- Integrated with Epic 5 guardrails (consent, eligibility, tone)
- Integrated with Epic 6 operator actions (Stories 6.1, 6.3, 6.4)
- Designed consolidated audit_log database schema
- Defined 7-year data retention policy with archival strategy
- Outlined comprehensive compliance metrics (consent, eligibility, tone, operator actions)
- Designed export functionality (CSV/JSON)
- Created audit log UI and compliance metrics dashboard
- Outlined 10 task groups with 55+ subtasks
- Status: drafted (ready for story-context workflow)
