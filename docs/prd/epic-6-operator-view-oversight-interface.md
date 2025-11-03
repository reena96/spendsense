# Epic 6: Operator View & Oversight Interface

**Goal:** Build administrative interface providing human oversight of recommendation system. Enable operators to view behavioral signals, review recommendations with decision traces, approve or override suggestions, and monitor consent/eligibility compliance.

## Story 6.1: Operator Authentication & Authorization

As a **system administrator**,
I want **secure operator authentication with role-based access control**,
so that **only authorized personnel can access sensitive user data and override decisions**.

### Acceptance Criteria

1. Operator login system implemented with username/password authentication
2. Role-based permissions defined: viewer (read-only), reviewer (approve/flag), admin (override)
3. Session management implemented with secure tokens
4. Access control enforced on all operator endpoints
5. Unauthorized access attempts logged and blocked
6. Operator actions logged with operator ID and timestamp
7. Password security requirements enforced (minimum length, complexity)
8. Login failures limited to prevent brute force attacks
9. Unit tests verify access control enforcement
10. Security review completed for authentication implementation

## Story 6.2: User Signal Dashboard

As an **operator**,
I want **comprehensive view of detected behavioral signals for any user**,
so that **I can verify signal detection accuracy and understand persona assignment rationale**.

### Acceptance Criteria

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

## Story 6.3: Persona Assignment Review Interface

As an **operator**,
I want **view of persona assignments with complete decision trace**,
so that **I can audit persona classification accuracy and understand prioritization logic**.

### Acceptance Criteria

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

## Story 6.4: Recommendation Review & Approval Queue

As an **operator**,
I want **review queue of generated recommendations with approve/override/flag capabilities**,
so that **I can ensure recommendation quality and appropriateness before user delivery**.

### Acceptance Criteria

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

## Story 6.5: Audit Trail & Compliance Reporting

As a **compliance officer**,
I want **comprehensive audit trail of all system decisions and operator actions**,
so that **the system can demonstrate compliance with ethical guidelines and regulatory requirements**.

### Acceptance Criteria

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

---
