# Epic 5: Consent, Eligibility & Tone Guardrails

**Goal:** Implement ethical constraints ensuring user control, recommendation appropriateness, and supportive communication. Build consent management system, eligibility filtering, and tone validation to maintain trust and compliance.

## Story 5.1: Consent Management System

As a **compliance officer**,
I want **explicit consent tracking with opt-in/opt-out capabilities and audit logging**,
so that **user data is only processed with permission and consent changes are traceable**.

### Acceptance Criteria

1. Consent database table created with fields: user_id, consent_status (opted_in/opted_out), timestamp, consent_version
2. Consent opt-in flow implemented requiring explicit user action (no pre-checked boxes)
3. Consent opt-out/revoke functionality implemented allowing anytime withdrawal
4. Consent status checked before any data processing or recommendation generation
5. Processing halted immediately upon consent revocation
6. Consent changes logged in audit trail with timestamp and user ID
7. Consent audit log accessible to operators
8. API endpoint POST /consent implemented for recording consent changes
9. API endpoint GET /consent/{user_id} implemented for checking consent status
10. Unit tests verify processing blocked without consent

## Story 5.2: Eligibility Filtering System

As a **compliance officer**,
I want **eligibility checks preventing inappropriate product recommendations**,
so that **users only see offers they qualify for and don't already have**.

### Acceptance Criteria

1. Eligibility checker evaluates minimum income requirements against user profile
2. Eligibility checker evaluates credit requirements against user credit signals
3. Eligibility checker prevents duplicate recommendations (filters existing accounts)
4. Eligibility checker blocks harmful/predatory products (payday loans, etc.)
5. Eligibility rules loaded from partner offer catalog metadata
6. Failed eligibility checks logged with specific reason
7. Only eligible recommendations passed to final output
8. Eligibility check results included in recommendation audit trail
9. Unit tests verify filtering across various eligibility scenarios
10. Unit tests confirm harmful products never recommended

## Story 5.3: Tone Validation & Language Safety

As a **UX writer**,
I want **automated validation ensuring all recommendation text uses supportive, non-judgmental language**,
so that **users feel empowered and educated, never shamed or blamed**.

### Acceptance Criteria

1. Tone validation rules defined prohibiting shaming phrases ("overspending", "bad with money", "irresponsible")
2. Tone validator checks all recommendation rationales against prohibited phrases
3. Validator ensures neutral, empowering language (e.g., "opportunity to optimize" vs. "you're doing it wrong")
4. Readability checker validates grade-8 reading level for all text
5. Tone validation runs before recommendations are stored/delivered
6. Failed validations logged with specific flagged phrases
7. Manual review queue created for flagged recommendations
8. Tone validation results included in audit trail
9. Unit tests verify detection of problematic language
10. Unit tests confirm acceptable language passes validation

## Story 5.4: Mandatory Disclaimer System

As a **compliance officer**,
I want **automatic inclusion of "not financial advice" disclaimer on all recommendations**,
so that **regulatory boundaries are clear and users understand the educational nature of content**.

### Acceptance Criteria

1. Standard disclaimer text defined: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
2. Disclaimer automatically appended to every recommendation set
3. Disclaimer included in all API responses containing recommendations
4. Disclaimer rendered prominently in UI (not hidden in fine print)
5. Disclaimer text configurable for future regulatory updates
6. Disclaimer presence verified in recommendation validation checks
7. Unit tests confirm all recommendation outputs include disclaimer
8. Integration tests verify disclaimer appears in UI

## Story 5.5: Guardrails Integration & Testing

As a **developer**,
I want **integrated guardrail pipeline enforcing all ethical constraints before recommendation delivery**,
so that **every recommendation passes consent, eligibility, tone, and disclaimer checks**.

### Acceptance Criteria

1. Guardrail pipeline created executing checks in sequence: consent → eligibility → tone → disclaimer
2. Pipeline halts at first failure and logs specific violation
3. Only fully validated recommendations proceed to storage/delivery
4. Pipeline execution traced in audit log with pass/fail status per check
5. Failed recommendations flagged for manual operator review
6. Guardrail metrics tracked: total checks, pass rate, failure reasons
7. Pipeline integrated into recommendation generation workflow
8. Integration tests verify end-to-end guardrail enforcement
9. Performance tested to ensure <5 second total recommendation generation
10. Documentation created explaining each guardrail check and rationale

---
