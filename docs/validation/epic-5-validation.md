# Epic 5: Consent, Eligibility & Tone Guardrails - Manual Validation Test Plan

**Date:** 2025-11-06
**Branch:** `epic-5-budget-tracking`
**API Base URL:** http://localhost:8000
**UI URL:** http://localhost:8000
**Epic Status:** Ready for validation (88/88 automated tests passing)

---

## Overview

This document provides comprehensive manual validation steps for Epic 5 Guardrails system. Epic 5 implements four critical guardrails to ensure ethical and compliant recommendation delivery:

1. **Consent Management** - User opt-in/opt-out tracking
2. **Eligibility Filtering** - Income/credit requirement enforcement
3. **Tone Validation** - Supportive language verification
4. **Mandatory Disclaimer** - Regulatory disclosure display

**Testing Philosophy:**
- ✅ Verify consent blocking prevents recommendations for opted-out users
- ✅ Validate eligibility filters remove inappropriate offers
- ✅ Confirm tone validation removes shame-based language
- ✅ Verify disclaimer appears prominently in all outputs
- ✅ Test full guardrail pipeline integration
- ✅ Validate performance (<5 seconds requirement)
- ✅ Test error handling and edge cases

---

## Prerequisites

### 1. Start the API Server
```bash
cd /Users/reena/gauntletai/spendsense
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --host 127.0.0.1 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Verify Server Health
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "healthy", "service": "spendsense-api"}
```

### 3. Open UI in Browser
Navigate to: **http://localhost:8000**

**Expected:** SpendSense Dashboard loads with navigation tabs

### 4. Verify Database Exists
```bash
ls -l data/processed/spendsense.db
```

**Expected:** Database file exists with recent timestamp

---

## Quick Validation (10 Minutes)

### Test 1: Disclaimer Visible in UI ✅

**Story:** 5.4 (Mandatory Disclaimer)
**AC:** AC4, AC8 - Disclaimer rendered prominently in UI

**Steps:**
1. Open http://localhost:8000/
2. Click **"💡 Recommendations"** tab
3. Enter User ID: `user_MASKED_000`
4. Select Time Window: `180 Days`
5. Check **"Force Generate"** checkbox
6. Click **"Generate Recommendations"**

**Expected Results:**
- ✅ Page displays **"⚠️ Disclaimer"** section at top of results
- ✅ Text reads: *"This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."*
- ✅ Disclaimer appears BEFORE recommendations list
- ✅ Text is clearly visible (not hidden in fine print)
- ✅ Disclaimer box has warning styling (border/background color)

**Pass Criteria:** Disclaimer is prominently displayed and readable

---

### Test 2: Consent Blocking via API ⚠️

**Story:** 5.1 (Consent Management)
**AC:** AC4, AC5 - Consent checked before processing, halts if not granted

**Steps:**

**Part A: Opt-Out User**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_099", "consent_status": "opted_out"}'
```

**Expected Response:**
```json
{
  "user_id": "user_MASKED_099",
  "consent_status": "opted_out",
  "consent_timestamp": "2025-11-06T...",
  "message": "Consent recorded: opted_out"
}
```

**Part B: Attempt to Generate Recommendations (Should Fail)**
```bash
curl http://localhost:8000/api/recommendations/user_MASKED_099?generate=true
```

**Expected Response:**
- ✅ HTTP Status: **403 Forbidden**
- ✅ Error message mentions consent
- ✅ Example: `{"detail": "Consent required: User user_MASKED_099 has not granted consent..."}`

**Part C: Opt-In User**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_099", "consent_status": "opted_in"}'
```

**Part D: Retry Recommendations (Should Succeed)**
```bash
curl http://localhost:8000/api/recommendations/user_MASKED_099?generate=true
```

**Expected Response:**
- ✅ HTTP Status: **200 OK**
- ✅ Full recommendations JSON returned
- ✅ Disclaimer included in response

**Pass Criteria:** Opted-out users blocked, opted-in users allowed

---

### Test 3: End-to-End Pipeline ✅

**Story:** 5.5 (Integration)
**AC:** All guardrails execute in sequence

**Steps:**
1. Ensure user is opted-in (from Test 2 above)
2. Open UI: http://localhost:8000/
3. Navigate to **"Recommendations"** tab
4. Enter User ID: `user_MASKED_000`
5. Click **"Generate Recommendations"**
6. Start timer (measure performance)

**Expected Results:**
- ✅ **Consent:** Request succeeds (user opted-in)
- ✅ **Eligibility:** Only appropriate offers displayed
- ✅ **Tone:** All text uses supportive language
- ✅ **Disclaimer:** Displayed prominently
- ✅ **Performance:** Response time **< 5 seconds**
- ✅ Recommendations list appears with 3-8 items
- ✅ Each recommendation has rationale with data citations

**Pass Criteria:** All guardrails pass, response time < 5 seconds

---

## Comprehensive Validation (30 Minutes)

---

## Story 5.1: Consent Management System

### Validation 5.1.1: Check Consent Status

**AC:** AC9 - GET /api/consent/{user_id} endpoint

**Test Steps:**
```bash
curl http://localhost:8000/api/consent/user_MASKED_000
```

**Expected Response:**
```json
{
  "user_id": "user_MASKED_000",
  "consent_status": "opted_in",
  "consent_timestamp": "2025-11-06T05:23:33.587255",
  "consent_version": "1.0",
  "message": "Current consent status: opted_in"
}
```

**Validation Checklist:**
- [ ] HTTP Status: 200 OK
- [ ] `consent_status` is either "opted_in" or "opted_out"
- [ ] `consent_timestamp` is ISO 8601 format
- [ ] `consent_version` is "1.0"
- [ ] Response includes `message` field

---

### Validation 5.1.2: Record Consent Change

**AC:** AC2, AC3, AC8 - Opt-in/opt-out functionality via API

**Test Steps:**

**Opt-In:**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_MASKED_001",
    "consent_status": "opted_in",
    "consent_version": "1.0"
  }'
```

**Expected Response:**
```json
{
  "user_id": "user_MASKED_001",
  "consent_status": "opted_in",
  "consent_timestamp": "2025-11-06T...",
  "consent_version": "1.0",
  "message": "Consent recorded: opted_in"
}
```

**Validation Checklist:**
- [ ] HTTP Status: 201 Created
- [ ] Timestamp is current (within last minute)
- [ ] Consent status matches request
- [ ] Success message returned

**Opt-Out:**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_MASKED_001",
    "consent_status": "opted_out"
  }'
```

**Validation Checklist:**
- [ ] HTTP Status: 201 Created
- [ ] Status changed to "opted_out"
- [ ] New timestamp generated

---

### Validation 5.1.3: Invalid Consent Status

**AC:** AC8 - API validates consent status values

**Test Steps:**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_MASKED_001",
    "consent_status": "maybe_later"
  }'
```

**Expected Response:**
```json
{
  "detail": "Invalid consent_status: maybe_later. Must be 'opted_in' or 'opted_out'"
}
```

**Validation Checklist:**
- [ ] HTTP Status: 400 Bad Request
- [ ] Error message explains valid values
- [ ] Request rejected (no database change)

---

### Validation 5.1.4: User Not Found

**AC:** AC8, AC9 - Handle missing users gracefully

**Test Steps:**
```bash
curl http://localhost:8000/api/consent/nonexistent_user_12345
```

**Expected Response:**
```json
{
  "detail": "User nonexistent_user_12345 not found"
}
```

**Validation Checklist:**
- [ ] HTTP Status: 404 Not Found
- [ ] Clear error message
- [ ] User ID included in error

---

### Validation 5.1.5: Consent Blocks Recommendations

**AC:** AC4, AC5 - Processing halted for opted-out users

**Test Steps:**
1. Opt-out a test user:
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_050", "consent_status": "opted_out"}'
```

2. Try to generate recommendations:
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_050?generate=true"
```

**Expected Response:**
- HTTP Status: **403 Forbidden**
- Error mentions consent requirement

3. Opt user back in:
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_050", "consent_status": "opted_in"}'
```

4. Retry recommendations:
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_050?generate=true"
```

**Expected Response:**
- HTTP Status: **200 OK**
- Recommendations returned

**Validation Checklist:**
- [ ] Opted-out user: 403 Forbidden
- [ ] Opted-in user: 200 OK with recommendations
- [ ] Error message is clear and actionable
- [ ] No recommendations leaked for opted-out user

---

## Story 5.2: Eligibility Filtering System

### Validation 5.2.1: Income Requirement Filtering

**AC:** AC1, AC2 - Filter offers by minimum income

**Test Steps:**

1. Get user's annual income:
```bash
curl http://localhost:8000/api/profiles/user_MASKED_000 | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['annual_income'])"
```

2. Generate recommendations:
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_000?generate=true" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
for rec in data['recommendations']:
    if rec['item_type'] == 'partner_offer':
        min_income = rec['content'].get('minimum_income', 0)
        print(f\"{rec['content']['title']}: min_income={min_income}\")
"
```

**Manual Validation:**
- [ ] Compare each `minimum_income` to user's `annual_income`
- [ ] Verify: All `minimum_income` ≤ user's `annual_income`
- [ ] No offers displayed that user doesn't qualify for

---

### Validation 5.2.2: Credit Score Requirement Filtering

**AC:** AC2, AC3 - Filter offers by minimum credit score

**Test Steps:**

1. Check if user has credit score in profile:
```bash
curl http://localhost:8000/api/profiles/user_MASKED_000 | \
  python3 -m json.tool | grep credit_score
```

2. Review recommendations and verify credit requirements

**Manual Validation:**
- [ ] If user has low credit (<650), no premium credit cards shown
- [ ] If user has high credit (>750), premium offers may appear
- [ ] No offers requiring better credit than user has

---

### Validation 5.2.3: Harmful Product Exclusion

**AC:** AC4 - Block harmful financial products

**Test Steps:**

1. Generate recommendations for multiple users:
```bash
for user in user_MASKED_000 user_MASKED_010 user_MASKED_020; do
  echo "=== $user ==="
  curl -s "http://localhost:8000/api/recommendations/${user}?generate=true" | \
    python3 -c "
import sys, json
data = json.load(sys.stdin)
for rec in data['recommendations']:
    cat = rec['content'].get('category', 'N/A')
    title = rec['content']['title']
    print(f'{cat}: {title}')
"
done
```

**Manual Validation:**
- [ ] No "payday_loan" category recommendations
- [ ] No "predatory_lending" products
- [ ] No "rent-to-own" schemes
- [ ] No harmful financial products displayed

---

### Validation 5.2.4: Duplicate Product Filtering

**AC:** AC5 - Prevent recommending products user already has

**Test Steps:**

1. Check user's existing accounts:
```bash
curl http://localhost:8000/api/profiles/user_MASKED_000 | \
  python3 -c "
import sys, json
user = json.load(sys.stdin)
print('Existing accounts:')
for acc in user['accounts']:
    print(f'  - {acc[\"type\"]}: {acc[\"subtype\"]}')
"
```

2. Generate recommendations and verify no duplicates suggested

**Manual Validation:**
- [ ] User with checking account: No checking account offers
- [ ] User with credit card: No duplicate credit card offers (same issuer)
- [ ] Recommendations complement existing products

---

## Story 5.3: Tone Validation & Language Safety

### Validation 5.3.1: Supportive Language Check

**AC:** AC1, AC2, AC3 - No shame-based or negative language

**Test Steps:**

1. Generate recommendations in UI
2. Read all rationales carefully

**Manual Review Checklist:**

**Prohibited Words/Phrases (Should NOT appear):**
- [ ] ❌ "bad with money"
- [ ] ❌ "poor choices"
- [ ] ❌ "irresponsible"
- [ ] ❌ "overspending"
- [ ] ❌ "financial trouble"
- [ ] ❌ "debt problem"
- [ ] ❌ "can't manage"

**Required Tone (Should appear):**
- [ ] ✅ Supportive language ("opportunity", "consider", "strengthen")
- [ ] ✅ Empowering framing ("optimize", "build", "improve")
- [ ] ✅ Data-driven rationales (cites specific numbers)
- [ ] ✅ Future-focused suggestions

**Example Good Rationale:**
> "Based on your consistent savings behavior averaging $450/month, you may benefit from a high-yield savings account to optimize your returns."

**Example Bad Rationale (should NOT appear):**
> "Your overspending and poor money management indicate you need debt consolidation immediately."

---

### Validation 5.3.2: Readability Check

**AC:** AC4 - Language accessible at 8th grade reading level

**Test Steps:**

1. Read recommendation text aloud
2. Check for complex jargon

**Manual Validation:**
- [ ] No unexplained financial jargon (or jargon explained)
- [ ] Sentences are concise (< 25 words)
- [ ] No multi-clause complex sentences
- [ ] Language is clear and direct

---

### Validation 5.3.3: Flagged Phrase Handling

**AC:** AC6 - System logs problematic language (visible in audit trail)

**Note:** This is tested by automated tests. Manual validation checks that NO problematic language reaches the UI.

**Test Steps:**
1. Review all displayed recommendations
2. Read all rationales and content

**Validation Checklist:**
- [ ] All displayed text passed tone validation
- [ ] No shame-based language visible
- [ ] No fear-based messaging

---

## Story 5.4: Mandatory Disclaimer System

### Validation 5.4.1: Disclaimer in UI

**AC:** AC4 - Disclaimer rendered prominently in UI

**Test Steps:**
1. Open http://localhost:8000/
2. Navigate to **"Recommendations"** tab
3. Generate recommendations for any user
4. Locate disclaimer section

**Visual Checklist:**
- [ ] Disclaimer has ⚠️ warning icon
- [ ] Disclaimer box has colored border/background
- [ ] Disclaimer appears ABOVE recommendation list
- [ ] Text is readable (not fine print, adequate font size)
- [ ] Disclaimer not hidden in accordion/collapse
- [ ] Disclaimer visible without scrolling (top of results)

---

### Validation 5.4.2: Disclaimer Content

**AC:** AC1, AC2 - Standard regulatory text present

**Test Steps:**
Review disclaimer text in UI

**Expected Text:**
```
This is educational content, not financial advice.
Consult a licensed advisor for personalized guidance.
```

**Validation Checklist:**
- [ ] Contains "not financial advice"
- [ ] Contains "licensed advisor"
- [ ] Contains "educational content"
- [ ] Text is complete (not truncated)
- [ ] Text matches regulatory requirement

---

### Validation 5.4.3: Disclaimer in API Response

**AC:** AC3, AC7 - Disclaimer included in all API responses

**Test Steps:**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_000?generate=true" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print('Disclaimer present:', 'disclaimer' in data)
print('Disclaimer text:', data.get('disclaimer', 'MISSING')[:80])
"
```

**Validation Checklist:**
- [ ] `disclaimer` field exists in JSON response
- [ ] Disclaimer text is non-empty
- [ ] Contains "not financial advice"
- [ ] Same text as UI disclaimer

---

### Validation 5.4.4: Disclaimer Always Present

**AC:** AC2, AC7 - Disclaimer in every response

**Test Multiple Scenarios:**

**Scenario A: Force Generate**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_001?generate=true"
```
- [ ] Disclaimer present

**Scenario B: Cached Results**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_001"
```
- [ ] Disclaimer present

**Scenario C: Different Time Window**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_001?time_window=30"
```
- [ ] Disclaimer present

**Scenario D: Different User**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_050?generate=true"
```
- [ ] Disclaimer present

---

## Story 5.5: Guardrails Integration & Testing

### Validation 5.5.1: Full Pipeline Sequence

**AC:** AC1 - Guardrails execute in order: consent → eligibility → tone → disclaimer

**Test Steps:**

1. **Start with opted-in user:**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_010", "consent_status": "opted_in"}'
```

2. **Generate recommendations and observe:**
```bash
time curl -s "http://localhost:8000/api/recommendations/user_MASKED_010?generate=true" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total recommendations: {len(data[\"recommendations\"])}')
print(f'Disclaimer present: {\"disclaimer\" in data}')
print(f'Metadata: {data.get(\"metadata\", {})}')
"
```

**Validation Checklist:**
- [ ] Request succeeds (consent granted)
- [ ] Recommendations filtered (eligibility + tone)
- [ ] Disclaimer present in response
- [ ] Response time < 5 seconds

---

### Validation 5.5.2: Performance Testing

**AC:** AC9 - Response time < 5 seconds

**Test Steps:**

Run performance test with timing:
```bash
for i in {1..5}; do
  echo "=== Run $i ==="
  time curl -s "http://localhost:8000/api/recommendations/user_MASKED_0${i}0?generate=true" > /dev/null
done
```

**Validation Checklist:**
- [ ] All requests complete in < 5 seconds
- [ ] Average response time < 2 seconds
- [ ] No requests timeout
- [ ] Performance consistent across runs

**Record Results:**
- Run 1: _____ seconds
- Run 2: _____ seconds
- Run 3: _____ seconds
- Run 4: _____ seconds
- Run 5: _____ seconds
- **Average:** _____ seconds

**Pass Criteria:** Average < 5 seconds (target: < 2 seconds)

---

### Validation 5.5.3: Error Handling

**AC:** AC8 - Graceful error handling with audit trail

**Test Edge Cases:**

**Test A: Invalid User**
```bash
curl "http://localhost:8000/api/recommendations/invalid_user_999?generate=true"
```
- [ ] Returns appropriate error (404 or 500)
- [ ] Error message is helpful
- [ ] No system crash

**Test B: Opted-Out User**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_020", "consent_status": "opted_out"}'

curl "http://localhost:8000/api/recommendations/user_MASKED_020?generate=true"
```
- [ ] Returns 403 Forbidden
- [ ] Error mentions consent
- [ ] No partial recommendations leaked

---

### Validation 5.5.4: Metadata and Audit Trail

**AC:** AC7, AC10 - Comprehensive audit trail

**Test Steps:**
```bash
curl -s "http://localhost:8000/api/recommendations/user_MASKED_000?generate=true" | \
  python3 -c "
import sys, json
data = json.load(sys.stdin)
metadata = data.get('metadata', {})
print('Generation time (ms):', metadata.get('generation_time_ms'))
print('Total recommendations:', metadata.get('total_recommendations'))
print('Education count:', metadata.get('education_count'))
print('Partner offer count:', metadata.get('partner_offer_count'))
print('Signals detected:', metadata.get('signals_detected'))
"
```

**Validation Checklist:**
- [ ] Metadata section exists
- [ ] Generation time reported
- [ ] Recommendation counts included
- [ ] Signals detected listed
- [ ] All audit data present

---

## Full Workflow Test (20 Minutes)

### End-to-End Validation Scenario

**Persona:** Compliance officer validating the system

**Scenario:** Test all guardrails with a new user

**Steps:**

**1. Create baseline - User starts opted-out (default)**
```bash
# Check initial status
curl http://localhost:8000/api/consent/user_MASKED_099
```
Expected: Either 404 (new user) or "opted_out"

**2. Verify blocking works**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_099?generate=true"
```
Expected: 403 Forbidden (no consent)

**3. Grant consent**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_099", "consent_status": "opted_in"}'
```
Expected: 201 Created, consent recorded

**4. Generate recommendations via UI**
- Open http://localhost:8000/
- Click "Recommendations" tab
- Enter: `user_MASKED_099`
- Time window: 180 days
- Click "Generate Recommendations"

**5. Validate all guardrails:**
- [ ] ✅ **Consent:** Request succeeded (opted-in)
- [ ] ✅ **Eligibility:** Check income requirements match user
- [ ] ✅ **Tone:** Read rationales - all supportive language
- [ ] ✅ **Disclaimer:** Visible at top with warning icon
- [ ] ✅ **Performance:** Response < 5 seconds

**6. Revoke consent**
```bash
curl -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_MASKED_099", "consent_status": "opted_out"}'
```

**7. Verify blocking restored**
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_099?generate=true"
```
Expected: 403 Forbidden

**Validation Checklist:**
- [ ] Default opt-out protects users
- [ ] Opt-in enables processing
- [ ] All guardrails execute correctly
- [ ] Disclaimer always displayed
- [ ] Opt-out immediately blocks access
- [ ] Audit trail captured (check logs)

---

## Troubleshooting

### Issue: API returns 403 for all users

**Cause:** Users not opted-in by default

**Solution:**
```bash
# Opt-in test users
for i in {0..10}; do
  curl -X POST http://localhost:8000/api/consent \
    -H "Content-Type: application/json" \
    -d "{\"user_id\": \"user_MASKED_0${i}0\", \"consent_status\": \"opted_in\"}"
done
```

---

### Issue: Disclaimer not visible in UI

**Troubleshooting:**
1. Check browser console for JavaScript errors
2. Verify API response includes disclaimer:
```bash
curl "http://localhost:8000/api/recommendations/user_MASKED_000?generate=true" | grep disclaimer
```
3. Check if element exists in DOM (browser DevTools)
4. Clear browser cache and reload

---

### Issue: Recommendations take > 5 seconds

**Troubleshooting:**
1. Check if running in development mode (--reload adds overhead)
2. Verify database not locked:
```bash
sqlite3 data/processed/spendsense.db "SELECT COUNT(*) FROM users;"
```
3. Check system resources (CPU/memory)
4. Try with cached results (remove `?generate=true`)

---

### Issue: "User not found" errors

**Solution:**
1. Verify database has users:
```bash
sqlite3 data/processed/spendsense.db "SELECT user_id FROM users LIMIT 5;"
```
2. Use a valid user_id from the output

---

## Validation Sign-Off

### Tester Information
- **Name:** _______________________
- **Date:** _______________________
- **Environment:** _______________________
- **Branch:** epic-5-budget-tracking

### Story Completion Checklist

- [ ] **Story 5.1:** Consent Management (all consent tests passing)
- [ ] **Story 5.2:** Eligibility Filtering (all eligibility tests passing)
- [ ] **Story 5.3:** Tone Validation (all tone tests passing)
- [ ] **Story 5.4:** Mandatory Disclaimer (disclaimer visible in UI)
- [ ] **Story 5.5:** Integration (full pipeline tested)

### Overall Assessment

**Test Results:**
- Total Tests Executed: _____ / 30+
- Tests Passed: _____
- Tests Failed: _____
- Blockers Found: _____

**Performance:**
- Average Response Time: _____ seconds
- Performance Requirement Met (<5s): [ ] Yes [ ] No

**Recommendation:**
- [ ] **APPROVE** - All validations passing, Epic 5 ready for production
- [ ] **APPROVE WITH NOTES** - Minor issues documented, Epic 5 acceptable
- [ ] **REJECT** - Critical issues found, requires fixes

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Signature:** _____________________ **Date:** __________

---

## Automated Test Coverage

**Reference:** These manual validation steps complement the automated test suite.

**Automated Tests:** 88/88 passing
- Story 5.1 (Consent): 23 tests
- Story 5.2 (Eligibility): 20 tests
- Story 5.3 (Tone): 20 tests
- Story 5.4 (Disclaimer): 11 tests
- Story 5.5 (Integration): 14 tests

**Manual validation focuses on:**
- Visual UI rendering
- End-user experience
- Real-world workflows
- Performance under realistic conditions
- Subjective assessments (tone, readability)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-06
**Maintainer:** SpendSense Engineering Team
