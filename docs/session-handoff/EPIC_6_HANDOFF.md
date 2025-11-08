# Epic 6: Operator View & Oversight Interface - Implementation Handoff

**Date:** 2025-11-06
**Branch:** `epic-6-operator-view` (created from main after Epic 5 merge)
**Epic Status:** 100% Drafted - Ready for Implementation
**Context Usage:** 55% (110k/200k)

---

## Executive Summary

Epic 6 implements the complete operator oversight interface, providing authenticated human supervision of the recommendation system. All 6 stories have been drafted with comprehensive acceptance criteria, task breakdowns, and integration plans.

**Key Achievements:**
- ✅ All 6 stories drafted and ready for implementation
- ✅ Epic 5 deferred items explicitly addressed in Stories 6.1, 6.4, 6.6
- ✅ Story dependencies mapped and implementation sequence defined
- ✅ Integration points with Epics 2, 3, 5 documented
- ✅ Database schema designed for operators, review queue, audit trail
- ✅ Authentication foundation (RBAC) designed for all operator endpoints

**Epic 5 Integration - CRITICAL:**
- **Story 6.1**: Adds authentication to Epic 5 consent endpoints (deferred from Story 5.1)
- **Story 6.4**: Completes Epic 5 manual review queue (Stories 5.3 AC7, 5.5 AC5 deferred items)
- **Story 6.6**: Completes Epic 5 consent system with operator UI (backlog item)

---

## Stories Overview

### ✅ Story 6.1: Operator Authentication & Authorization
**Status:** Drafted
**Priority:** HIGHEST (Foundation for all other stories)
**File:** `docs/stories/6-1-operator-authentication-authorization.md`

**Purpose:** Secure operator login with role-based access control (RBAC)

**Key Features:**
- Username/password authentication with JWT tokens
- 3 roles: viewer (read-only), reviewer (approve/flag), admin (override)
- Session management with secure tokens
- Password security (bcrypt, min 12 chars, complexity)
- Rate limiting (max 5 failed attempts per 15 min)
- Audit logging for all auth events

**Database Tables:**
- `operators` - Operator users with roles
- `operator_sessions` - Active sessions
- `auth_audit_log` - Authentication events

**Dependencies:**
- None (foundation story)

**Addresses Epic 5:**
- Adds authentication to POST `/api/consent` and GET `/api/consent/{user_id}` (deferred from Story 5.1)

**Acceptance Criteria:** 10 ACs
**Task Groups:** 9 tasks with 40+ subtasks
**Estimated Tests:** 15-20 tests

---

### ✅ Story 6.2: User Signal Dashboard
**Status:** Drafted
**Priority:** HIGH (Provides context for Stories 6.3, 6.4, 6.6)
**File:** `docs/stories/6-2-user-signal-dashboard.md`

**Purpose:** Comprehensive view of user behavioral signals for verification

**Key Features:**
- Display subscription, savings, credit, income metrics
- Side-by-side comparison of 30-day vs 180-day signals
- Time window toggle (30d / 180d / both)
- Raw signal data view with timestamps
- CSV export for compliance

**Database Tables:**
- Uses existing `behavioral_signals` from Epic 2 (read-only)

**Dependencies:**
- Story 6.1 (authentication - requires viewer role)
- Epic 2 (behavioral signals)

**Integration Points:**
- Linked from Stories 6.3 (persona context), 6.4 (recommendation rationale), 6.6 (consent decisions)

**Acceptance Criteria:** 10 ACs
**Task Groups:** 10 tasks
**Estimated Tests:** 10-15 tests

---

### ✅ Story 6.3: Persona Assignment Review Interface
**Status:** Drafted
**Priority:** HIGH (Provides context for Story 6.4)
**File:** `docs/stories/6-3-persona-assignment-review-interface.md`

**Purpose:** View persona assignments with complete decision trace and manual override

**Key Features:**
- Display assigned persona with match evidence (signal citations)
- Show all qualifying personas and prioritization logic
- Persona change history timeline
- Manual persona override (admin only) with justification
- Links to Signal Dashboard for context

**Database Tables:**
- Uses existing `persona_assignments` from Epic 3 (read-only for view)
- Modifies for manual overrides

**Dependencies:**
- Story 6.1 (authentication - viewer for view, admin for override)
- Story 6.2 (signal dashboard integration)
- Epic 3 (persona assignments)

**Acceptance Criteria:** 10 ACs
**Task Groups:** 10 tasks
**Estimated Tests:** 10-15 tests

---

### ✅ Story 6.4: Recommendation Review & Approval Queue
**Status:** Drafted
**Priority:** CRITICAL (Completes Epic 5 deferred items)
**File:** `docs/stories/6-4-recommendation-review-approval-queue.md`

**Purpose:** Review queue for flagged recommendations with approve/override/flag actions

**Key Features:**
- Review queue UI with filters (status, persona, guardrail failures)
- Display full recommendation details with guardrail results
- Approve/override/flag actions with audit trail
- Batch approval for high-confidence recommendations
- **Completes Epic 5**: Database persistence for flagged recommendations

**Database Tables:**
- `flagged_recommendations` - **NEW** (addresses Epic 5 Stories 5.3 AC7, 5.5 AC5)

**Dependencies:**
- Story 6.1 (authentication - reviewer for approve/flag, admin for override)
- Story 6.2 (signal context)
- Story 6.3 (persona context)
- Story 6.5 (audit trail)
- Epic 5 (guardrails integration)

**Epic 5 Integration - CRITICAL:**
- Modifies `spendsense/guardrails/tone.py` - Add database flagging
- Modifies `spendsense/guardrails/eligibility.py` - Add database flagging
- Modifies `spendsense/recommendations/assembler.py` - Check review status

**Addresses Epic 5:**
- **Story 5.3 AC7**: "Manual review queue for flagged recommendations" - DATABASE DEFERRED → COMPLETED HERE
- **Story 5.5 AC5**: "Failed recommendations flagged for manual review" - PARTIALLY IMPLEMENTED → COMPLETED HERE

**Acceptance Criteria:** 10 ACs
**Task Groups:** 10 tasks with 50+ subtasks
**Estimated Tests:** 20+ tests (critical integration)

---

### ✅ Story 6.5: Audit Trail & Compliance Reporting
**Status:** Drafted
**Priority:** HIGH (Central logging for all Epic 6 stories)
**File:** `docs/stories/6-5-audit-trail-compliance-reporting.md`

**Purpose:** Comprehensive audit trail of all system decisions and operator actions

**Key Features:**
- Consolidated audit log (recommendations, consent, eligibility, tone, operator actions)
- Search and filter by date range, user ID, operator ID, event type
- Export to CSV/JSON for regulatory reporting
- Compliance metrics dashboard (consent opt-in rate, eligibility failures, tone violations)
- 7-year data retention with archival to Parquet

**Database Tables:**
- `audit_log` - Central audit trail for all events

**Dependencies:**
- Story 6.1 (authentication - admin or compliance role)
- Epic 5 (guardrails to log events)
- Stories 6.3, 6.4, 6.6 (operator actions to log)

**Epic 5 Integration:**
- Modifies `spendsense/guardrails/consent.py` - Add audit logging
- Modifies `spendsense/guardrails/eligibility.py` - Add audit logging
- Modifies `spendsense/guardrails/tone.py` - Add audit logging
- Modifies `spendsense/recommendations/assembler.py` - Add audit logging

**Acceptance Criteria:** 10 ACs
**Task Groups:** 10 tasks with 55+ subtasks
**Estimated Tests:** 15-20 tests

---

### ✅ Story 6.6: Consent Management Interface
**Status:** Drafted
**Priority:** MEDIUM (Completes Epic 5 consent system)
**File:** `docs/stories/6-6-consent-management-interface.md`

**Purpose:** Operator interface to view and manage user consent status

**Key Features:**
- View current consent status with badge (opted-in/opted-out)
- Change consent status with confirmation dialog and required reason
- Consent change history timeline
- Batch consent operations (admin only)
- Filters: opted-in, opted-out, recently changed
- Export consent report (CSV/JSON)

**Database Tables:**
- Uses existing `users` table with consent columns from Epic 5 Story 5.1

**Dependencies:**
- Story 6.1 (authentication - admin or reviewer role)
- Story 6.5 (audit trail for consent history)
- Epic 5 Story 5.1 (consent API endpoints)

**Epic 5 Integration:**
- Uses existing POST `/api/consent` and GET `/api/consent/{user_id}` from Story 5.1
- Adds batch endpoints: POST `/api/operator/consent/batch`, GET `/api/operator/consent/users`

**Addresses Epic 5 Backlog:**
- "Consent Management UI: Operator interface for managing user consent" - COMPLETED HERE

**Acceptance Criteria:** 14 ACs
**Task Groups:** 11 tasks with 50+ subtasks
**Estimated Tests:** 15-20 tests

---

## Epic 5 Deferred Items - Resolution Matrix

| Epic 5 Item | Source | Priority | Resolution | Epic 6 Story |
|-------------|--------|----------|------------|--------------|
| Consent API authentication | Story 5.1 | HIGH | Auth added to POST/GET /api/consent | 6.1 |
| Manual review queue database | Story 5.3 AC7 | MEDIUM | flagged_recommendations table | 6.4 |
| Failed recs database persistence | Story 5.5 AC5 | MEDIUM | tone.py, eligibility.py modified | 6.4 |
| Consent Management UI | Backlog | LOW | Full operator consent interface | 6.6 |

**All Epic 5 deferred items are addressed in Epic 6.**

---

## Story Dependencies & Implementation Sequence

### Recommended Implementation Order:

**Phase 1: Foundation (Week 1)**
1. **Story 6.1** - Operator Authentication & Authorization
   - **Why First**: Foundation for all other stories
   - **Blocks**: Stories 6.2, 6.3, 6.4, 6.5, 6.6 (all require authentication)

**Phase 2: Logging & Context (Week 2)**
2. **Story 6.5** - Audit Trail & Compliance Reporting
   - **Why Second**: Central logging for Stories 6.3, 6.4, 6.6
   - **Blocks**: Story 6.6 (consent history), Story 6.4 (review actions)

3. **Story 6.2** - User Signal Dashboard
   - **Why Third**: Provides context for Stories 6.3, 6.4
   - **Blocks**: None (read-only view)

**Phase 3: Core Operator Functions (Week 3)**
4. **Story 6.3** - Persona Assignment Review Interface
   - **Why Fourth**: Provides context for Story 6.4
   - **Depends On**: Stories 6.1, 6.2, 6.5

5. **Story 6.4** - Recommendation Review & Approval Queue
   - **Why Fifth**: CRITICAL - Completes Epic 5 deferred items
   - **Depends On**: Stories 6.1, 6.2, 6.3, 6.5

**Phase 4: Consent UI (Week 4)**
6. **Story 6.6** - Consent Management Interface
   - **Why Last**: Completes Epic 5, depends on audit trail
   - **Depends On**: Stories 6.1, 6.5

### Alternative Parallel Approach:
- **Week 1**: Story 6.1 (authentication)
- **Week 2**: Stories 6.5 (audit) + 6.2 (signals) in parallel
- **Week 3**: Stories 6.3 (persona) + 6.4 (review queue) in parallel
- **Week 4**: Story 6.6 (consent UI)

---

## Database Schema Overview

### New Tables (Epic 6):

**1. `operators` (Story 6.1)**
```sql
CREATE TABLE operators (
    operator_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('viewer', 'reviewer', 'admin')),
    created_at TIMESTAMP NOT NULL,
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

**2. `operator_sessions` (Story 6.1)**
```sql
CREATE TABLE operator_sessions (
    session_id TEXT PRIMARY KEY,
    operator_id TEXT NOT NULL,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL,
    FOREIGN KEY (operator_id) REFERENCES operators(operator_id)
);
```

**3. `flagged_recommendations` (Story 6.4) - COMPLETES EPIC 5**
```sql
CREATE TABLE flagged_recommendations (
    recommendation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    content_id TEXT NOT NULL,
    content_title TEXT NOT NULL,
    content_type TEXT NOT NULL,
    rationale TEXT NOT NULL,
    flagged_at TIMESTAMP NOT NULL,
    flagged_by TEXT,
    flag_reason TEXT NOT NULL,
    guardrail_status TEXT NOT NULL,
    decision_trace TEXT NOT NULL,
    review_status TEXT NOT NULL DEFAULT 'pending',
    reviewed_at TIMESTAMP,
    reviewed_by TEXT,
    review_notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

**4. `audit_log` (Story 6.5)**
```sql
CREATE TABLE audit_log (
    log_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    user_id TEXT,
    operator_id TEXT,
    recommendation_id TEXT,
    timestamp TIMESTAMP NOT NULL,
    event_data TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT
);
```

### Modified Tables:
- `users` - Already has consent columns from Epic 5 Story 5.1 (no changes needed)

---

## Frontend Architecture

### New React Pages:
1. `/operator/login` - Login page (Story 6.1)
2. `/operator/signals` - Signal Dashboard (Story 6.2)
3. `/operator/personas` - Persona Review (Story 6.3)
4. `/operator/review-queue` - Review Queue (Story 6.4)
5. `/operator/audit` - Audit Log (Story 6.5)
6. `/operator/compliance` - Compliance Metrics (Story 6.5)
7. `/operator/consent` - Consent Management (Story 6.6)

### UI Component Library:
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: TailwindCSS
- **Components**: shadcn/ui or Material-UI
- **State Management**: React Query (server state)
- **Routing**: React Router 6+
- **Charts**: recharts or Chart.js (Story 6.5)

### Navigation Structure:
```
Operator Dashboard
├── Signals (Story 6.2)
├── Personas (Story 6.3)
├── Review Queue (Story 6.4)
├── Compliance
│   ├── Audit Log (Story 6.5)
│   └── Metrics (Story 6.5)
└── Consent (Story 6.6)
```

---

## Epic 5 Integration Points - CRITICAL

### Files to Modify (Epic 5 Guardrails):

**1. `spendsense/guardrails/consent.py` (Story 6.5)**
- Add audit logging for consent changes
- Integration: Log event_type='consent_changed' to audit_log table

**2. `spendsense/guardrails/eligibility.py` (Stories 6.4, 6.5)**
- Add database flagging for eligibility failures (Story 6.4)
- Add audit logging for eligibility checks (Story 6.5)
- Integration: Save to flagged_recommendations when eligibility fails

**3. `spendsense/guardrails/tone.py` (Stories 6.4, 6.5)**
- Add database flagging for tone violations (Story 6.4)
- Add audit logging for tone validations (Story 6.5)
- Integration: Save to flagged_recommendations when tone fails

**4. `spendsense/recommendations/assembler.py` (Stories 6.4, 6.5)**
- Check review status before delivery (Story 6.4)
- Add audit logging for recommendation generation (Story 6.5)
- Integration: Query flagged_recommendations, only deliver if approved

**5. `spendsense/api/main.py` (Story 6.1)**
- Add authentication to consent endpoints
- Integration: Apply @require_role decorator to POST /api/consent, GET /api/consent/{user_id}

---

## Testing Requirements

### Total Estimated Tests: 100+ tests

**Story 6.1**: 15-20 tests (authentication, RBAC, security)
**Story 6.2**: 10-15 tests (signal display, CSV export)
**Story 6.3**: 10-15 tests (persona view, override, history)
**Story 6.4**: 20+ tests (review queue, Epic 5 integration, batch ops)
**Story 6.5**: 15-20 tests (audit log, metrics, export, archival)
**Story 6.6**: 15-20 tests (consent UI, batch ops, history)

### Test Coverage by Type:

**Unit Tests:**
- Password hashing, token generation (Story 6.1)
- RBAC decorator enforcement (Story 6.1)
- Compliance metrics calculation (Story 6.5)
- CSV/JSON export generation (Stories 6.2, 6.5, 6.6)

**Integration Tests:**
- Full auth flow: login → token → authenticated request (Story 6.1)
- Guardrail → database flagging (Story 6.4)
- Consent change → audit log entry (Story 6.5)
- Operator action → audit trail (Stories 6.3, 6.4, 6.6)

**E2E Tests:**
- Login → view signals → export CSV (Stories 6.1, 6.2)
- Login → view review queue → approve recommendation (Stories 6.1, 6.4)
- Login → change consent → verify audit log (Stories 6.1, 6.6, 6.5)

### Testing Frameworks:
- **Backend**: pytest + pytest-cov + FastAPI TestClient
- **Frontend**: Jest + React Testing Library
- **E2E**: pytest + requests (API-level E2E)

---

## Technology Stack Summary

### Backend:
- **Framework**: FastAPI 0.104+
- **Authentication**: python-jose (JWT), passlib (bcrypt)
- **Database**: SQLite 3.40+ (may need PostgreSQL for high-volume production)
- **Logging**: structlog 23+ (structured JSON logs)
- **Data Processing**: pandas 2.1+ (signal aggregation)

### Frontend:
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite 5+
- **UI Library**: shadcn/ui or Material-UI
- **Styling**: TailwindCSS 3+
- **State**: React Query 5+
- **Routing**: React Router 6+
- **Charts**: recharts or Chart.js (Story 6.5)

### Development:
- **Linting**: ruff 0.1+ (Python), ESLint (TypeScript)
- **Formatting**: black 23+ (Python), Prettier (TypeScript)
- **Type Checking**: mypy 1.7+ (Python), TypeScript

---

## Files to Create (Epic 6)

### Backend Files (~25 new files):

**Authentication (Story 6.1):**
- `spendsense/auth/operator.py`
- `spendsense/auth/rbac.py`
- `spendsense/auth/tokens.py`
- `spendsense/api/operator_auth.py`

**Signal Dashboard (Story 6.2):**
- `spendsense/api/operator_signals.py`

**Persona Review (Story 6.3):**
- `spendsense/api/operator_personas.py`

**Review Queue (Story 6.4):**
- `spendsense/models/review_queue.py`
- `spendsense/api/operator_review.py`
- `spendsense/services/review_service.py`

**Audit Trail (Story 6.5):**
- `spendsense/models/audit_log.py`
- `spendsense/api/operator_audit.py`
- `spendsense/services/audit_service.py`
- `spendsense/services/compliance_metrics.py`
- `spendsense/tasks/archive_audit_logs.py`

**Consent UI (Story 6.6):**
- `spendsense/api/operator_consent.py`

**Tests (~25 test files):**
- `tests/test_operator_auth.py`
- `tests/test_operator_rbac.py`
- `tests/test_operator_signals.py`
- `tests/test_operator_personas.py`
- `tests/test_review_queue.py`
- `tests/test_audit_log.py`
- `tests/test_operator_consent.py`

### Frontend Files (~40 new files):

**Pages:**
- `ui/src/pages/Login.tsx`
- `ui/src/pages/SignalDashboard.tsx`
- `ui/src/pages/PersonaAssignmentView.tsx`
- `ui/src/pages/ReviewQueue.tsx`
- `ui/src/pages/AuditLog.tsx`
- `ui/src/pages/ComplianceMetrics.tsx`
- `ui/src/pages/ConsentManagement.tsx`

**Components (~25 components):**
- Story 6.1: LoginForm, SessionInfo
- Story 6.2: SignalCategory, UserSearch, TimeWindowToggle, SignalExport
- Story 6.3: PersonaCard, QualifyingPersonas, MatchEvidence, PersonaChangeHistory, PersonaOverrideModal
- Story 6.4: RecommendationDetailModal, GuardrailResults, ReviewActions, BatchApproval
- Story 6.5: AuditLogTable, AuditExport, MetricsCharts
- Story 6.6: ConsentStatus, ConsentChangeModal, ConsentHistory, BatchConsentModal, ConsentListView, ConsentExport

**Hooks (~8 hooks):**
- `ui/src/hooks/useAuth.ts`
- `ui/src/hooks/useSignalData.ts`
- `ui/src/hooks/usePersonaAssignment.ts`
- `ui/src/hooks/useReviewQueue.ts`
- `ui/src/hooks/useAuditLog.ts`
- `ui/src/hooks/useConsent.ts`

**Tests (~8 test files):**
- One test file per page component

---

## Git Workflow

**Current Branch:** `epic-6-operator-view` (already created and switched)

**Base Branch:** `main` (includes Epic 5 merge commit b4506c6)

**Recommended Commit Strategy:**
1. Commit after each story completion
2. Run full test suite before committing
3. Use conventional commit format: `feat(story-6.x): Description`

**Example Commits:**
```bash
git commit -m "feat(story-6.1): Implement operator authentication with JWT and RBAC"
git commit -m "feat(story-6.4): Complete Epic 5 review queue with database flagging"
git commit -m "test(story-6.1): Add comprehensive authentication and RBAC tests"
```

**PR Creation:**
- Create PR after all 6 stories complete
- Title: "Epic 6: Operator View & Oversight Interface"
- Include summary of Epic 5 integration

---

## Risk Assessment

**LOW RISK** - All stories fully specified with clear acceptance criteria

### Potential Risks:

1. **Frontend Complexity (MEDIUM)**
   - Risk: React + TypeScript + TailwindCSS stack may have learning curve
   - Mitigation: Use shadcn/ui for pre-built accessible components
   - Impact: May slow Stories 6.2-6.6 if team unfamiliar with stack

2. **Epic 5 Integration (MEDIUM)**
   - Risk: Modifying existing guardrail code (tone.py, eligibility.py) may introduce bugs
   - Mitigation: Comprehensive tests for guardrail → database integration
   - Impact: Story 6.4 requires careful testing of Epic 5 modifications

3. **Authentication Security (HIGH IMPACT, LOW LIKELIHOOD)**
   - Risk: JWT implementation vulnerabilities, password security issues
   - Mitigation: Story 6.1 includes security review checklist (AC10)
   - Impact: Security vulnerability in authentication affects all operator endpoints

4. **Database Performance (LOW)**
   - Risk: SQLite may not scale for high-volume audit logs
   - Mitigation: 7-year retention with archival to Parquet (Story 6.5)
   - Impact: May need PostgreSQL migration for production (documented in architecture.md)

### Mitigation Strategy:

- Comprehensive security review for Story 6.1 (AC10)
- Integration tests for Epic 5 guardrail modifications (Story 6.4)
- Performance testing for audit log queries (Story 6.5)
- Frontend component library (shadcn/ui) for consistent UI (Stories 6.2-6.6)

---

## Decision Log

### Key Architectural Decisions:

**1. JWT Authentication (Story 6.1)**
- Decision: JWT with HTTP-only cookies or Authorization headers
- Rationale: Stateless authentication, standard approach, easy to implement
- Alternative: Session-based (more complex, requires session storage)

**2. RBAC with 3 Roles (Story 6.1)**
- Decision: viewer (read-only), reviewer (approve/flag), admin (override)
- Rationale: Matches operator workflow, separates concerns, allows delegation
- Alternative: Single admin role (less flexible)

**3. Consolidated Audit Log (Story 6.5)**
- Decision: Single audit_log table for all event types
- Rationale: Simplifies queries, single source of truth, easier compliance reporting
- Alternative: Separate tables per event type (more complex)

**4. 7-Year Data Retention with Archival (Story 6.5)**
- Decision: 2 years active in SQLite, 2-7 years in Parquet, delete after 7 years
- Rationale: Financial services standard, balances compliance with performance
- Alternative: Keep all in database (performance issues)

**5. React SPA for Operator UI (Stories 6.2-6.6)**
- Decision: React 18 + TypeScript + TailwindCSS
- Rationale: Rich interactive experience, matches architecture.md specification
- Alternative: Server-rendered Flask templates (less interactive)

**6. Manual Review Queue Database (Story 6.4)**
- Decision: flagged_recommendations table separate from recommendations
- Rationale: Separates review workflow from recommendation generation, cleaner schema
- Alternative: Add review fields to recommendations table (pollutes schema)

---

## Questions for Stakeholders

1. **Frontend Implementation:** Should operator UI be built in Epic 6, or can it be deferred to a later epic?
   - **Recommendation:** Build in Epic 6 as specified (Stories 6.2-6.6 include full React UI)

2. **Database Migration:** Is SQLite sufficient for production, or should we migrate to PostgreSQL?
   - **Recommendation:** Start with SQLite, document PostgreSQL migration path for high-volume production

3. **Authentication Upgrade:** When should we implement OAuth2 (Google/GitHub) login?
   - **Recommendation:** Epic 6 uses username/password, document OAuth2 upgrade path for multi-operator production use

4. **Epic 6 Retrospective:** Should we run retrospective after Epic 6 completion?
   - **Recommendation:** Yes (marked as optional in sprint-status.yaml)

---

## Next Steps

### Immediate Actions:

1. **Review Handoff** - Confirm all 6 stories are ready for implementation
2. **Allocate Resources** - Assign developers to stories based on dependencies
3. **Start Story 6.1** - Begin with authentication foundation

### Week-by-Week Plan:

**Week 1: Foundation**
- Implement Story 6.1 (Operator Authentication)
- Run security review (AC10)
- Test RBAC enforcement

**Week 2: Logging & Context**
- Implement Story 6.5 (Audit Trail) - Central logging
- Implement Story 6.2 (Signal Dashboard) - Read-only view
- Integrate Epic 5 guardrails with audit logging

**Week 3: Core Operator Functions**
- Implement Story 6.3 (Persona Review) - Read-only view + override
- Implement Story 6.4 (Review Queue) - CRITICAL Epic 5 completion
- Modify Epic 5 guardrails for database flagging
- Test Epic 5 integration thoroughly

**Week 4: Consent UI & Polish**
- Implement Story 6.6 (Consent Management)
- Complete Epic 5 consent system
- End-to-end testing
- Create PR

---

## Approval

**Epic 6 Status:** READY FOR IMPLEMENTATION
**Recommended Action:** Begin implementation with Story 6.1
**Blocking Issues:** None
**Outstanding Work:** None (all stories drafted)

---

## Appendix: Story File Locations

1. Story 6.1: `/docs/stories/6-1-operator-authentication-authorization.md`
2. Story 6.2: `/docs/stories/6-2-user-signal-dashboard.md`
3. Story 6.3: `/docs/stories/6-3-persona-assignment-review-interface.md`
4. Story 6.4: `/docs/stories/6-4-recommendation-review-approval-queue.md`
5. Story 6.5: `/docs/stories/6-5-audit-trail-compliance-reporting.md`
6. Story 6.6: `/docs/stories/6-6-consent-management-interface.md`

**Sprint Status:** `/docs/sprint-status.yaml` (all stories marked "drafted")
**Epic 6 PRD:** `/docs/prd/epic-6-operator-view-oversight-interface.md`
**Architecture:** `/docs/architecture.md`
**Epic 5 Handoff:** `/docs/session-handoff/EPIC_5_FINAL_HANDOFF.md`
**Backlog:** `/docs/backlog.md`

---

**End of Epic 6 Implementation Handoff**

**Generated:** 2025-11-06
**Context Usage:** 55% (110k/200k)
**Branch:** `epic-6-operator-view`
**Ready for Implementation:** ✅
