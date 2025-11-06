# SpendSense Guardrails Overview

**Epic 5: Consent, Eligibility & Tone Guardrails**

This document explains the ethical constraints and guardrails implemented in SpendSense to ensure user control, recommendation appropriateness, and supportive communication.

## Table of Contents

1. [Overview](#overview)
2. [Guardrail Pipeline Architecture](#guardrail-pipeline-architecture)
3. [Guardrail Details](#guardrail-details)
4. [Integration Points](#integration-points)
5. [Audit Trail & Compliance](#audit-trail--compliance)
6. [Performance](#performance)

---

## Overview

SpendSense implements a comprehensive guardrail pipeline that enforces ethical constraints on all recommendations. The pipeline consists of four guardrails executed in sequence:

1. **Consent Management** - Ensures user permission before processing
2. **Eligibility Filtering** - Prevents inappropriate product recommendations
3. **Tone Validation** - Ensures supportive, non-judgmental language
4. **Mandatory Disclaimer** - Clarifies educational nature of content

### Design Principles

- **User Control**: Users must explicitly opt in to data processing
- **Appropriateness**: Only recommend products users qualify for
- **Supportive Communication**: Never shame or blame users
- **Regulatory Compliance**: Clear boundaries with mandatory disclaimers
- **Transparency**: Full audit trail of all guardrail decisions

---

## Guardrail Pipeline Architecture

### Execution Sequence

```
User Request
    │
    ├─> 1. CONSENT CHECK (API Level)
    │   └─> ❌ Not opted in → HTTP 403 (HALT)
    │   └─> ✅ Opted in → Continue
    │
    ├─> 2. ELIGIBILITY FILTERING (Assembler Level)
    │   └─> Filter out ineligible offers
    │   └─> Continue with eligible offers
    │
    ├─> 3. TONE VALIDATION (Assembler Level)
    │   └─> Filter out problematic language
    │   └─> Continue with validated recommendations
    │
    └─> 4. DISCLAIMER (Automatic)
        └─> Include in all responses
        └─> Return final recommendations
```

### Early Exit Behavior

- **Consent Failure**: Halts immediately with HTTP 403, no processing occurs
- **Eligibility Failure**: Individual offers filtered, eligible ones proceed
- **Tone Failure**: Individual recommendations filtered, clean ones proceed
- **Disclaimer**: Always included (no failure case)

---

## Guardrail Details

### 1. Consent Management System

**Purpose**: Ensure explicit user permission before any data processing or recommendation generation.

**Implementation**: `spendsense/guardrails/consent.py`

**Key Features**:
- Opt-in flow requiring explicit user action (no pre-checked boxes)
- Opt-out/revoke functionality allowing anytime withdrawal
- Consent status checked before any processing
- Full audit logging of consent changes

**Decision Points**:
- `opted_in`: Process recommendations normally
- `opted_out`: Return HTTP 403 with clear error message

**Audit Trail**: User ID, consent status, timestamp, version

**Integration**: API endpoint `/api/recommendations` checks consent at line 848

**Story**: 5.1 - Consent Management System

---

### 2. Eligibility Filtering System

**Purpose**: Prevent inappropriate product recommendations by checking income, credit, duplicates, and harmful products.

**Implementation**: `spendsense/guardrails/eligibility.py`

**Key Features**:
- Income requirement checking against user profile
- Credit requirement checking (with utilization proxy when score unavailable)
- Duplicate account prevention
- Harmful/predatory product blocking

**Harmful Products Blocked**:
- Payday loans
- Title loans
- High-fee credit products
- Predatory lending
- Crypto leverage products
- High-risk investments
- Any product with APR > 36% (usury threshold)

**Decision Points**:
- All checks pass: Include offer in recommendations
- Any check fails: Filter out offer, log specific reason

**Audit Trail**: Offer ID, user ID, eligibility status, checks performed, failure reasons, timestamp

**Integration**: Recommendation assembler at line 214 (after matching, before rationale generation)

**Story**: 5.2 - Eligibility Filtering System

---

### 3. Tone Validation & Language Safety

**Purpose**: Ensure all recommendation text uses supportive, non-judgmental language that empowers users.

**Implementation**: `spendsense/guardrails/tone.py`

**Key Features**:
- Prohibited phrase detection (20+ shaming/judgmental phrases)
- Empowering alternatives suggested for problematic language
- Readability checking (Flesch-Kincaid grade-8 level)
- Manual review queue for flagged recommendations

**Prohibited Phrase Categories**:
- Direct shaming: "overspending", "bad with money", "irresponsible"
- Judgmental: "you should know better", "obviously wrong", "foolish"
- Blame-oriented: "your fault", "you caused", "you're the problem"
- Negative characterizations: "bad at managing", "can't handle money"

**Empowering Alternatives**:
- "overspending" → "spending more than planned"
- "bad with money" → "building money management skills"
- "irresponsible" → "opportunity to strengthen financial habits"

**Decision Points**:
- No prohibited phrases + readable: Include recommendation
- Prohibited phrases or too complex: Filter out, log flagged phrases

**Audit Trail**: Text ID, tone pass/fail, flagged phrases, grade level, timestamp

**Integration**: Recommendation assembler at line 251 (after eligibility, before final assembly)

**Story**: 5.3 - Tone Validation & Language Safety

---

### 4. Mandatory Disclaimer System

**Purpose**: Clarify regulatory boundaries and ensure users understand the educational nature of recommendations.

**Implementation**: `spendsense/recommendations/assembler.py`

**Disclaimer Text**:
```
"This is educational content, not financial advice.
Consult a licensed advisor for personalized guidance."
```

**Key Features**:
- Automatically included in every recommendation set
- Present in all API responses
- Configurable for future regulatory updates
- Presence verified in all outputs

**Decision Points**:
- No decision - always included

**Integration**: Automatic in `AssembledRecommendationSet` creation at line 302

**Story**: 5.4 - Mandatory Disclaimer System

---

## Integration Points

### API Level: Consent Check

**File**: `spendsense/api/main.py`

**Location**: Line 848-868

**Behavior**:
```python
# Check consent before processing
consent_result = consent_service.check_consent_status(user_id)
if consent_result.consent_status != "opted_in":
    raise HTTPException(
        status_code=403,
        detail="User has not opted in to data processing"
    )
# Continue with recommendation generation...
```

**Result**: HTTP 403 if not opted in, processing continues if opted in

---

### Assembler Level: Eligibility → Tone → Disclaimer

**File**: `spendsense/recommendations/assembler.py`

**Sequence**:

1. **Matching** (lines 185-212): Match recommendations to user persona/signals
2. **Eligibility Filtering** (lines 214-227): Check each partner offer for eligibility
3. **Tone Validation** (lines 251-272): Validate tone for all recommendations
4. **Disclaimer** (line 302): Automatically included in recommendation set

**Result**: Only eligible, tone-validated recommendations with disclaimer proceed to output

---

## Audit Trail & Compliance

### Metadata Structure

All recommendation responses include comprehensive metadata with guardrail results:

```python
{
    "total_recommendations": 5,
    "education_count": 2,
    "partner_offer_count": 3,

    # Eligibility metrics
    "offers_checked": 10,
    "offers_eligible": 3,
    "offers_filtered": 7,
    "eligibility_audit_trail": [
        {
            "action": "eligibility_check",
            "offer_id": "...",
            "eligible": false,
            "checks_performed": {...},
            "failure_reasons": ["Income too low"],
            "timestamp": "2025-11-05T..."
        },
        // ... more results
    ],

    # Tone validation metrics
    "tone_checked": 5,
    "tone_passed": 5,
    "tone_filtered": 0,
    "tone_audit_trail": [
        {
            "action": "tone_validation",
            "text_id": "...",
            "passes": true,
            "passes_tone": true,
            "passes_readability": true,
            "flagged_count": 0,
            "timestamp": "2025-11-05T..."
        },
        // ... more results
    ],

    "disclaimer": "This is educational content...",
    "generation_time_ms": 234.56
}
```

### Compliance Features

- **Full Transparency**: Every guardrail decision logged
- **Traceability**: Audit trail includes timestamps and reasons
- **Metrics**: Pass rates and failure reasons tracked
- **Regulatory Compliance**: Disclaimer on all outputs, harmful products blocked

---

## Performance

### Performance Target

**< 5 seconds** total recommendation generation time including all guardrails

### Actual Performance

Based on integration testing:
- **Eligibility checking**: < 50ms for 20 offers
- **Tone validation**: < 50ms for 10 recommendations
- **Total pipeline**: Typically < 500ms

### Optimization Strategies

1. **Efficient Filtering**: Eligibility checked before expensive rationale generation
2. **Sequential Processing**: Tone validation only on eligible recommendations
3. **Lightweight Checks**: Regex-based phrase detection, simple readability metrics
4. **Minimal Database Queries**: Consent check uses cached results when possible

---

## Testing

### Test Coverage

- **Story 5.1 (Consent)**: 23 tests (16 unit + 7 integration)
- **Story 5.2 (Eligibility)**: 20 comprehensive unit tests
- **Story 5.3 (Tone)**: 20 comprehensive unit tests
- **Story 5.4 (Disclaimer)**: 8 unit tests
- **Story 5.5 (Integration)**: 14 integration tests

**Total**: 85 tests covering all guardrail functionality

### Test Files

- `tests/test_consent.py` - Consent management tests
- `tests/test_eligibility.py` - Eligibility filtering tests
- `tests/test_tone.py` - Tone validation tests
- `tests/test_disclaimer.py` - Disclaimer system tests
- `tests/test_guardrails_integration.py` - End-to-end integration tests

---

## Future Enhancements

### Potential Improvements

1. **Manual Review Queue (AC5)**: Database table for flagged recommendations awaiting operator review
2. **Configuration Management**: Move constants to configuration files for easier regulatory updates
3. **Advanced Readability**: More sophisticated readability metrics beyond Flesch-Kincaid
4. **ML-based Tone Detection**: Machine learning model for nuanced tone analysis
5. **Consent Versioning**: Track consent version changes for GDPR compliance
6. **A/B Testing**: Test different disclaimer wording for clarity

---

## References

### Implementation Files

- `spendsense/guardrails/consent.py` - Consent management
- `spendsense/guardrails/eligibility.py` - Eligibility filtering
- `spendsense/guardrails/tone.py` - Tone validation
- `spendsense/recommendations/assembler.py` - Integration point
- `spendsense/api/main.py` - API consent check

### Documentation

- `docs/stories/5-1-consent-management-system.md`
- `docs/stories/5-2-eligibility-filtering-system.md`
- `docs/stories/5-3-tone-validation-language-safety.md`
- `docs/stories/5-4-mandatory-disclaimer-system.md`
- `docs/stories/5-5-guardrails-integration-testing.md`
- `docs/prd/epic-5-consent-eligibility-tone-guardrails.md`

---

**Last Updated**: 2025-11-05
**Epic**: 5 - Consent, Eligibility & Tone Guardrails
**Status**: Complete
