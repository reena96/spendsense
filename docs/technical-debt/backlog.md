# Engineering Backlog

This backlog collects cross-cutting or future action items that emerge from reviews and planning.

Routing guidance:

- Use this file for non-urgent optimizations, refactors, or follow-ups that span multiple stories/epics.
- Must-fix items to ship a story belong in that story's `Tasks / Subtasks`.
- Same-epic improvements may also be captured under the epic Tech Spec `Post-Review Follow-ups` section.

| Date | Story | Epic | Type | Severity | Owner | Status | Notes |
| ---- | ----- | ---- | ---- | -------- | ----- | ------ | ----- |
| 2025-11-05 | 5.1 | 5 | Bug | High | Claude | Complete | ✅ Integrated consent checking with recommendation workflow (AC4). Added at main.py:848-868, returns 403 if consent not granted. |
| 2025-11-05 | 5.1 | 5 | Dependency | - | Epic 6.1 | Deferred | Authentication deferred to Epic 6.1 (Operator Authentication & Authorization). Epic 6.1 AC4 will enforce access control on all operator endpoints including consent APIs. Avoids throwaway implementation. |
| 2025-11-05 | 5.1 | 5 | Testing | Med | Claude | Complete | ✅ Added 7 FastAPI integration tests using TestClient. Verifies HTTP status codes (200, 400, 404, 422). Total: 23 tests. |
| 2025-11-05 | 5.1 | 5 | Refactor | Low | TBD | Wont-Fix | DB session dependency injection: Not applicable for SQLite + demo traffic. Current approach acceptable. Revisit only if migrating to PostgreSQL or expecting production load (>10 req/sec). Connection pooling provides no benefit for file-based SQLite. |
| 2025-11-05 | 5.1 | 5 | Refactor | Low | TBD | Wont-Fix | Import organization in consent.py: Style preference, no functional impact. Current inline imports prevent circular dependency issues. Acceptable as-is. |
| 2025-11-06 | 5.1 | 5 | Enhancement | Low | Epic 6.6 | Planned | Consent Management UI: Operator interface for managing user consent (toggle opt-in/opt-out, view history). Epic 5 APIs satisfy functional requirements. UI added as Story 6.6 in Epic 6 for operator convenience. |
| 2025-11-06 | 5.4 | 5 | Documentation | Low | Claude | Resolved | Disclaimer UI rendering: Incorrectly marked as "deferred" in handoff. Disclaimer IS rendered in existing UI at localhost:8000 (app.js:679). Added API integration tests to verify AC4 & AC8. Story 5.4 is 100% complete. |
