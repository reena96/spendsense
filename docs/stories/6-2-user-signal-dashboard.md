# Story 6.2: User Signal Dashboard

Status: ready-for-dev

## Story

As an **operator**,
I want **comprehensive view of detected behavioral signals for any user**,
so that **I can verify signal detection accuracy and understand persona assignment rationale**.

## Acceptance Criteria

1. User search interface allows lookup by user ID or masked account number
2. Signal dashboard displays subscription metrics: recurring merchants, monthly spend, subscription share
3. Signal dashboard displays savings metrics: net inflow, growth rate, emergency fund coverage
4. Signal dashboard displays credit metrics: utilization by card, minimum payment behavior, overdue status
5. Signal dashboard displays income metrics: pay frequency, median gap, cash-flow buffer
6. Dashboard shows signals for both 30-day and 180-day windows side-by-side
7. Time window toggle allows switching between short-term and long-term views
8. Raw signal values displayed alongside computed metrics
9. Signal calculation timestamps shown
10. Export functionality allows downloading signal data as CSV

## Tasks / Subtasks

- [ ] Task 1: Create backend API endpoints for signal data (AC: #1, #8, #9)
  - [ ] GET `/api/operator/users/search?q={query}` - Search users by ID or name
  - [ ] GET `/api/operator/signals/{user_id}?time_window={window}` - Get signals for user
  - [ ] GET `/api/operator/signals/{user_id}/raw` - Get raw signal data with timestamps
  - [ ] Implement authentication requirement (requires Story 6.1 RBAC - viewer or higher)
  - [ ] Return 403 if operator lacks permission, 404 if user not found
  - [ ] Include signal calculation timestamps and data version in response

- [ ] Task 2: Design and implement React dashboard UI (AC: #1, #6, #7)
  - [ ] Create `SignalDashboard` component with user search bar
  - [ ] Implement user search with autocomplete (debounced)
  - [ ] Create time window toggle (30-day / 180-day / side-by-side)
  - [ ] Design responsive layout for signal categories
  - [ ] Add loading states and error handling
  - [ ] Style with TailwindCSS following design system

- [ ] Task 3: Implement subscription metrics display (AC: #2)
  - [ ] Display `subscription_recurring_merchants` with label "Recurring Merchants"
  - [ ] Display `subscription_monthly_spend` formatted as currency
  - [ ] Display `subscription_share_pct` as percentage with visual indicator
  - [ ] Show comparison between 30-day and 180-day values
  - [ ] Add tooltip explaining each metric
  - [ ] Highlight concerning values (e.g., >30% subscription share)

- [ ] Task 4: Implement savings metrics display (AC: #3)
  - [ ] Display `savings_net_inflow` formatted as currency
  - [ ] Display `savings_growth_rate_pct` as percentage with trend indicator
  - [ ] Display `savings_emergency_fund_months` with target comparison (goal: 3-6 months)
  - [ ] Show comparison between 30-day and 180-day values
  - [ ] Add visual indicators (green for healthy, yellow for concerning, red for critical)
  - [ ] Add tooltip explaining emergency fund calculation

- [ ] Task 5: Implement credit metrics display (AC: #4)
  - [ ] Display `credit_max_utilization_pct` as percentage with color coding (<30% green, >70% red)
  - [ ] Display `credit_has_interest_charges` as boolean badge
  - [ ] Display `credit_minimum_payment_only` as boolean badge (flag if true)
  - [ ] Display `credit_overdue_status` prominently if true
  - [ ] Show per-card utilization breakdown if available
  - [ ] Add tooltip explaining healthy utilization thresholds

- [ ] Task 6: Implement income metrics display (AC: #5)
  - [ ] Display `income_payroll_count` with label "Payroll Deposits"
  - [ ] Display `income_median_pay_gap_days` with interpretation (e.g., "Bi-weekly pay")
  - [ ] Display `income_cash_flow_buffer_months` with target comparison
  - [ ] Show comparison between 30-day and 180-day values
  - [ ] Add visual indicator for income stability (regular vs irregular)
  - [ ] Add tooltip explaining cash flow buffer calculation

- [ ] Task 7: Implement side-by-side comparison view (AC: #6)
  - [ ] Create split-pane layout for 30-day vs 180-day signals
  - [ ] Highlight differences between time windows (arrows for increase/decrease)
  - [ ] Show percentage change for numeric values
  - [ ] Add summary section showing key changes
  - [ ] Allow toggling between side-by-side and single view

- [ ] Task 8: Implement raw data view and export (AC: #8, #9, #10)
  - [ ] Create "View Raw Data" accordion/modal showing JSON structure
  - [ ] Display all signal values with full precision (no rounding)
  - [ ] Show signal calculation timestamp with timezone
  - [ ] Show data version and source (e.g., "v1.0 from 2025-11-05 14:32:15 UTC")
  - [ ] Implement CSV export button
  - [ ] Generate CSV with headers: user_id, time_window, metric_name, metric_value, computed_at
  - [ ] Trigger browser download on export

- [ ] Task 9: Write comprehensive unit and integration tests (AC: #1-10)
  - [ ] Test user search API endpoint returns correct results
  - [ ] Test signals API endpoint returns complete signal data
  - [ ] Test authentication enforcement (401 without token, 403 without viewer role)
  - [ ] Test React component renders all signal categories
  - [ ] Test time window toggle switches data correctly
  - [ ] Test CSV export generates correct format
  - [ ] Test side-by-side comparison calculates differences correctly
  - [ ] Test loading and error states display correctly
  - [ ] Test responsive layout on mobile and desktop

- [ ] Task 10: Integration with existing signal detection pipeline (AC: #8, #9)
  - [ ] Verify signals are pre-computed by Epic 2 signal detection pipeline
  - [ ] Confirm database schema has all required signal fields
  - [ ] Test with real user data from existing database
  - [ ] Validate signal timestamps are accurate
  - [ ] Document any missing signal fields or data gaps

## Dev Notes

### Architecture Patterns and Constraints

**From architecture.md:**

- **Frontend Framework:** React 18 + TypeScript + Vite
- **UI Library:** shadcn/ui or Material-UI for components
- **Styling:** TailwindCSS for utility-first CSS
- **State Management:** React Query for server state (caching, refetching)
- **Routing:** React Router for navigation
- **Backend:** FastAPI with Pydantic validation
- **Authentication:** Requires Story 6.1 RBAC (viewer or higher)

**Key Requirements:**
- Display all 4 signal categories: subscription, savings, credit, income
- Support both 30-day and 180-day time windows
- Provide side-by-side comparison of time windows
- Show raw data for transparency and debugging
- Export functionality for compliance and analysis
- Responsive design for desktop and tablet use

**Data Sources (Epic 2):**
- `BehavioralSignal` table stores pre-computed signals
- Signals computed by Epic 2 pipeline (Stories 2.1-2.6)
- Each user has 2 signal records (30-day and 180-day)

### Project Structure Notes

**New Files to Create:**
- `spendsense/api/operator_signals.py` - Signal dashboard API endpoints
- `ui/src/pages/SignalDashboard.tsx` - Main dashboard page component
- `ui/src/components/SignalCategory.tsx` - Reusable signal category display
- `ui/src/components/UserSearch.tsx` - User search with autocomplete
- `ui/src/components/TimeWindowToggle.tsx` - 30d/180d/both toggle
- `ui/src/components/SignalExport.tsx` - CSV export functionality
- `ui/src/hooks/useSignalData.ts` - React Query hook for signal data
- `tests/test_operator_signals.py` - Backend API tests
- `ui/src/tests/SignalDashboard.test.tsx` - Frontend component tests

**Files to Modify:**
- `spendsense/api/main.py` - Register operator_signals routes
- `ui/src/App.tsx` - Add Signal Dashboard route
- `ui/src/navigation/OperatorNav.tsx` - Add dashboard link to navigation

**API Response Format:**
```json
{
  "user_id": "user_MASKED_000",
  "time_window": "30_day",
  "computed_at": "2025-11-06T10:30:00Z",
  "subscription": {
    "recurring_merchants": 5,
    "monthly_spend": 127.50,
    "subscription_share_pct": 18.2
  },
  "savings": {
    "net_inflow": 450.00,
    "growth_rate_pct": 5.2,
    "emergency_fund_months": 2.3
  },
  "credit": {
    "max_utilization_pct": 65.0,
    "has_interest_charges": true,
    "minimum_payment_only": false,
    "overdue_status": false,
    "utilization_by_card": [
      {"card_name": "Chase Sapphire", "utilization_pct": 65.0},
      {"card_name": "Amex Blue", "utilization_pct": 32.0}
    ]
  },
  "income": {
    "payroll_count": 2,
    "median_pay_gap_days": 14,
    "cash_flow_buffer_months": 0.8
  }
}
```

### Testing Standards Summary

**From architecture.md:**
- Test framework: pytest for backend, Jest/React Testing Library for frontend
- Coverage target: ≥10 tests per story
- API tests: FastAPI TestClient with authentication
- Frontend tests: Component rendering, user interactions, data display

**Test Categories:**
1. Backend API tests: Endpoint authorization, data retrieval, search functionality
2. Frontend component tests: Rendering, time window toggle, CSV export
3. Integration tests: Full flow from API to UI display
4. E2E tests: User search → view signals → export CSV

### Learnings from Previous Story

**From Story 6.1 (Operator Authentication & Authorization)**

- **Authentication Foundation**: RBAC with viewer/reviewer/admin roles
- **Endpoint Protection**: Use `@require_role('viewer')` decorator for signal endpoints
- **Audit Logging**: Log all operator access to user signals (operator_id, user_id, timestamp)
- **Session Tokens**: JWT-based authentication with HTTP-only cookies or Authorization headers
- **Testing Pattern**: FastAPI TestClient with auth headers

**Integration Points:**
- Signal endpoints require authentication from Story 6.1
- Use established audit logging pattern from Epic 5
- Follow API endpoint structure from `/operator/review` pattern

**Previous Epics Context:**
- Epic 2 (Stories 2.1-2.6): Signal detection pipeline already implemented
- Signals stored in `behavioral_signals` table with 30-day and 180-day windows
- Signal schema includes all metrics required by this story

### References

- [Source: docs/prd/epic-6-operator-view-oversight-interface.md#Story-6.2] - Story 6.2 acceptance criteria
- [Source: docs/architecture.md#Data-Models] - BehavioralSignal model schema
- [Source: docs/architecture.md#Tech-Stack] - React, TypeScript, TailwindCSS stack
- [Source: docs/stories/6-1-operator-authentication-authorization.md] - RBAC authentication patterns
- [Source: docs/stories/2-6-behavioral-summary-aggregation.md] - Signal computation implementation (Epic 2)

## Dev Agent Record

### Context Reference

- docs/stories/6-2-user-signal-dashboard.context.xml

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
- Integrated with Story 6.1 authentication (requires viewer role)
- Mapped to Epic 2 signal detection (BehavioralSignal table)
- Designed API response format with all 4 signal categories
- Outlined 10 task groups for backend API and React dashboard
- Defined CSV export format for compliance
- Added side-by-side comparison requirement for 30d vs 180d signals
- Status: drafted (ready for story-context workflow)
