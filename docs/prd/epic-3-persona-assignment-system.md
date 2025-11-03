# Epic 3: Persona Assignment System

**Goal:** Build persona classification logic that assigns each user to exactly one of 6 personas based on their behavioral signals. Implement deterministic prioritization when multiple personas match, maintain comprehensive audit logging of all qualifying personas, and ensure persona assignments are explainable and traceable.

## Story 3.1: Persona Definition Registry

As a **product manager**,
I want **structured persona definitions with clear criteria, focus areas, and prioritization rules**,
so that **persona assignment logic is maintainable, extensible, and auditable**.

### Acceptance Criteria

1. Persona registry created as YAML/JSON configuration file
2. Each persona defined with: ID, name, description, priority rank, match criteria
3. Persona 1 (High Utilization) defined with priority 1 and criteria documented
4. Persona 2 (Variable Income Budgeter) defined with priority 2 and criteria documented
5. Persona 3 (Subscription-Heavy) defined with priority 3 and criteria documented
6. Persona 4 (Savings Builder) defined with priority 4 and criteria documented
7. Persona 5 (Cash Flow Optimizer) defined with priority 5, criteria, and rationale documented
8. Persona 6 (Young Professional) defined with priority 6, criteria, and rationale documented
9. Each persona includes educational focus areas and recommended content types
10. Registry schema validated and documented
11. Registry loaded at application startup

## Story 3.2: Persona Matching Engine

As a **data scientist**,
I want **evaluation of user behavioral signals against all persona criteria**,
so that **all qualifying personas can be identified before prioritization is applied**.

### Acceptance Criteria

1. Matching function evaluates user signals against each persona's criteria
2. Boolean match result returned for each persona with supporting evidence
3. Match logic correctly implements AND/OR conditions per persona criteria
4. Threshold comparisons handle edge cases (exact matches, missing data)
5. All qualifying personas logged before prioritization
6. Match evaluation traced with specific signal values that triggered match
7. Matching supports both 30-day and 180-day time windows
8. Unit tests cover all persona criteria combinations
9. Unit tests verify correct boolean logic for complex criteria

## Story 3.3: Deterministic Prioritization Logic

As a **product manager**,
I want **deterministic selection of highest-priority persona when multiple personas match**,
so that **users receive consistent, predictable persona assignments focused on their most critical need**.

### Acceptance Criteria

1. Prioritization function accepts list of matching personas
2. Function returns single highest-priority persona (lowest priority number)
3. Tie-breaking logic documented if personas have same priority
4. Priority selection traced in audit log
5. All qualifying personas recorded separately from selected persona
6. Selection logic handles edge case of zero qualifying personas
7. Fallback persona or "unclassified" status defined for no-match scenario
8. Unit tests verify prioritization with various match combinations
9. Deterministic behavior verified across multiple runs with same data

## Story 3.4: Persona Assignment & Audit Logging

As a **developer**,
I want **persona assignment results stored with complete audit trail of decision logic**,
so that **every persona assignment is explainable and can be reviewed for quality assurance**.

### Acceptance Criteria

1. Assigned persona stored per user per time window (30-day and 180-day)
2. Assignment record includes: persona ID, assignment timestamp, confidence level
3. All qualifying personas logged with match evidence
4. Audit log includes specific signal values that triggered each match
5. Audit log includes reason why highest-priority persona was selected
6. Assignment accessible via API GET /profile/{user_id}
7. Audit logs stored in structured format (JSON) in database
8. Operator can view full decision trace in UI
9. Unit tests verify complete audit trail generation

## Story 3.5: Custom Personas 5 & 6 Implementation

As a **product manager**,
I want **definition and implementation of two custom personas addressing underserved user segments**,
so that **the system covers diverse user needs from early-career to optimization opportunities**.

### Acceptance Criteria

1. Persona 5 (Cash Flow Optimizer) name, description, and educational focus documented
2. Persona 5 criteria defined: high liquidity (≥6 months expenses), minimal debt usage (<10% utilization)
3. Persona 6 (Young Professional) name, description, and educational focus documented
4. Persona 6 criteria defined: limited transaction history (<180 days), low credit limits (<$3000)
5. Clear behavioral criteria defined using measurable signals for both personas
6. Rationale documented explaining why each persona matters
7. Priority ranks assigned (Persona 5: rank 5, Persona 6: rank 6 - lowest priority)
8. Match criteria implemented in persona matching engine for both personas
9. Educational content recommendations defined for both personas
10. Both persona definitions added to persona registry
11. Documentation explains persona value and target user characteristics for each
12. Unit tests verify Persona 5 and Persona 6 matching criteria work correctly

---
