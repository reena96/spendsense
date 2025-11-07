# Epic 4: Personalized Recommendations - UI Validation Test Plan

**Date:** 2025-11-05
**Branch:** `epic-4-personalized-recommendations`
**URL:** http://localhost:8000
**Tab:** 💡 Recommendations

---

## Overview

This document provides comprehensive validation steps for Epic 4 Personalized Recommendation Engine accessible through the UI. The validation covers all 5 stories: Content Catalog, Partner Offers, Matching Logic, Rationale Generation, and Assembly & Output.

**Testing Philosophy:**
- ✅ Verify personalized recommendations with actual user data
- ✅ Test both time windows (30d and 180d)
- ✅ Validate mandatory disclaimer display
- ✅ Verify data citations and transparency
- ✅ Test different personas get different recommendations
- ✅ Validate performance (< 5 seconds)
- ✅ Test caching functionality
- ✅ Verify error handling

---

## Prerequisites

### 1. Start the Server
```bash
cd /Users/reena/gauntletai/spendsense
source venv/bin/activate
python -m spendsense.api.main
```

### 2. Verify Server Running
Open browser to: **http://localhost:8000**

Expected: SpendSense Dashboard loads successfully

### 3. Navigate to Recommendations Tab
Click: **"💡 Recommendations"** in navigation menu

Expected: Form with User ID input, Time Window dropdown, and Force Generate checkbox

---

## Quick Validation (5 Minutes)

### Test 1: Generate Basic Recommendations

**Steps:**
1. Enter User ID: `user_MASKED_001`
2. Time Window: `30 Days`
3. Force Generate: ✓ (checked)
4. Click: **"Generate Recommendations"**

**Expected Results:**
- ✅ Loading spinner appears
- ✅ Results appear in < 5 seconds (typically < 2 seconds)
- ✅ Purple gradient summary header shows:
  - Persona badge (e.g., "High Utilization")
  - Time window badge ("30d")
  - Generation time badge (e.g., "1247.5ms")
- ✅ Yellow disclaimer box is visible
- ✅ Blue signals box shows detected signals
- ✅ 4-8 recommendation cards appear
- ✅ Mix of 📚 Educational Content and 🎁 Partner Offers

**Validation Points:**
- [ ] Total recommendations: 4-8 items
- [ ] Education items: 3-5
- [ ] Partner offers: 1-3
- [ ] Generation time: < 5000ms
- [ ] Disclaimer text includes: "not financial advice"
- [ ] Disclaimer text includes: "licensed advisor"

---

## Detailed Validation Tests

### Test 2: Validate Mandatory Disclaimer (PRD AC4)

**Purpose:** Verify disclaimer is always visible and correct

**Steps:**
1. Generate recommendations for any user
2. Scroll to find disclaimer box

**Expected Results:**
- ✅ Yellow box with warning icon (⚠️)
- ✅ Text: "This is educational content, not financial advice."
- ✅ Text: "Consult a licensed advisor for personalized guidance."
- ✅ Box is prominent and easy to read

**Validation Points:**
- [ ] Disclaimer visible on initial load
- [ ] Disclaimer remains visible while scrolling
- [ ] Text is exact match (word-for-word)
- [ ] Background is yellow/amber color
- [ ] Text is readable (good contrast)

**CRITICAL:** This MUST pass - PRD compliance requirement

---

### Test 3: Validate Personalized Rationales (PRD AC2)

**Purpose:** Verify rationales include actual user data

**Steps:**
1. Generate recommendations
2. Read the first 3 recommendation rationales (green boxes)
3. Check for specific data points

**Expected Results:**
Each rationale should contain:
- ✅ Specific numbers (percentages, dollar amounts)
- ✅ Account references (masked, e.g., "****4523")
- ✅ "Because" statements explaining relevance
- ✅ Plain language (grade-8 reading level)
- ✅ Personalized to user's situation

**Example Good Rationale:**
```
"You're currently at 68% credit utilization on your Visa ****4523,
which is above the recommended 30% threshold. This puts you at risk
of credit score damage because high utilization signals financial stress
to lenders. Reducing your balance by $1,200 would bring you to a
healthier 30% utilization rate."
```

**Example Bad Rationale (Generic):**
```
"Credit utilization is an important factor in your credit score.
Keeping it below 30% is recommended."
```

**Validation Points:**
- [ ] Rationale 1 includes specific numbers
- [ ] Rationale 2 includes specific account/amounts
- [ ] Rationale 3 uses "because" statements
- [ ] All rationales are unique (not copy-paste)
- [ ] Language is conversational and clear
- [ ] No technical jargon

**CRITICAL:** Personalization is the core value proposition

---

### Test 4: Validate Data Citations (PRD AC3)

**Purpose:** Verify transparency through data citations

**Steps:**
1. Generate recommendations
2. Find recommendation with yellow citation box
3. Read data citations

**Expected Results:**
- ✅ Yellow box titled "📊 Data Citations:"
- ✅ Bulleted list of specific data points:
  - "Percentage: 68%"
  - "Amount: $3,400"
  - "Account: ****4523"
- ✅ Citations match data mentioned in rationale

**Validation Points:**
- [ ] Citation box present on at least 3 recommendations
- [ ] Citations use format: "Type: Value"
- [ ] Percentages include % symbol
- [ ] Amounts include $ symbol
- [ ] Account numbers are masked (****XXXX)
- [ ] Citations correspond to rationale content

**Cross-Check:**
Pick one recommendation and verify:
- If rationale mentions "68%", citation should list "Percentage: 68%"
- If rationale mentions "$3,400", citation should list "Amount: $3,400"

---

### Test 5: Validate Persona Matching (PRD AC3)

**Purpose:** Different personas get different recommendations

**Setup:** You'll need 3 users with different personas

**Steps:**
1. Generate for high_utilization user
2. Note recommendations
3. Generate for low_savings user
4. Note recommendations
5. Generate for irregular_income user
6. Note recommendations

**Expected Results:**

**High Utilization User:**
- ✅ Focus on credit card management
- ✅ Balance transfer offers
- ✅ Rationales mention utilization percentages
- ✅ Signals include "Credit Utilization"

**Low Savings User:**
- ✅ Focus on emergency fund building
- ✅ High-yield savings account offers
- ✅ Rationales mention savings balances
- ✅ Signals include "Low Savings"

**Irregular Income User:**
- ✅ Focus on cash flow management
- ✅ Budgeting tool offers
- ✅ Rationales mention income variability
- ✅ Signals include "Irregular Income"

**Validation Points:**
- [ ] Each persona gets 4+ different recommendations
- [ ] Recommendations are contextually appropriate
- [ ] Rationales reference persona-specific issues
- [ ] Partner offers align with persona needs

---

### Test 6: Validate Time Windows (PRD AC3)

**Purpose:** 30d and 180d windows show different patterns

**Steps:**
1. Generate 30-day recommendations for user
2. Note which signals detected
3. Switch to 180-day window
4. Generate again
5. Compare signals and recommendations

**Expected Results:**
- ✅ Both windows generate successfully
- ✅ Badge shows correct window ("30d" or "180d")
- ✅ Different signals may be detected
- ✅ Some recommendations may differ
- ✅ Both complete in < 5 seconds

**Validation Points:**
- [ ] 30d window completes successfully
- [ ] 180d window completes successfully
- [ ] Time window badge updates
- [ ] Metadata shows correct time_window value
- [ ] Generation time < 5000ms for both

**Why Different?**
- 30d: Recent behavior, short-term patterns
- 180d: Long-term trends, more data points

---

### Test 7: Validate Caching (PRD AC8)

**Purpose:** Verify cached recommendations load instantly

**Steps:**
1. Generate recommendations with Force Generate ✓
2. Note generation time (should be 1000-2000ms)
3. Uncheck Force Generate checkbox
4. Click Generate again
5. Note generation time (should be < 100ms)

**Expected Results:**
- ✅ First generation: 1000-2000ms
- ✅ Cached retrieval: < 100ms (instant)
- ✅ Same recommendations returned
- ✅ Same timestamp in metadata

**Validation Points:**
- [ ] Force generate takes 1-2 seconds
- [ ] Cached response is instant
- [ ] Recommendations identical
- [ ] Timestamp proves it's cached

**Performance Check:**
- [ ] First generation < 5000ms
- [ ] Typically < 2000ms
- [ ] Cached < 100ms

---

### Test 8: Validate Recommendation Structure

**Purpose:** Each recommendation card has required elements

**Steps:**
1. Generate recommendations
2. Examine first card in detail
3. Check all sections present

**Expected Card Structure:**

**Header (Purple Gradient):**
- [ ] Numbered circle (1, 2, 3, etc.)
- [ ] Type badge (📚 Educational or 🎁 Partner Offer)
- [ ] Title in large text
- [ ] Provider name (if partner offer)

**Body - Description:**
- [ ] Clear explanation of recommendation
- [ ] 2-4 sentences
- [ ] Readable font size

**Body - Rationale Box (Green):**
- [ ] Green left border
- [ ] Title: "💬 Why this recommendation:"
- [ ] Personalized text with user data
- [ ] 2-4 sentences explaining relevance

**Body - Persona Match (Blue):**
- [ ] Blue left border
- [ ] Title: "🎯 Persona Match:"
- [ ] Explanation of why fits persona
- [ ] Mentions persona name

**Body - Data Citations (Yellow):**
- [ ] Yellow left border (if present)
- [ ] Title: "📊 Data Citations:"
- [ ] Bulleted list of data points

**Body - Details:**
- [ ] Priority badge (colored by priority level)
- [ ] Type badge (article/calculator/video/etc.)
- [ ] Difficulty badge (for education)
- [ ] Time commitment badge
- [ ] Impact badge

**Body - Key Benefits (Partner Offers):**
- [ ] "✨ Key Benefits:" heading
- [ ] 3-5 bulleted benefits
- [ ] Specific and actionable

**Body - Learn More Button:**
- [ ] Blue button at bottom
- [ ] "Learn More →" text
- [ ] Hover effect works

---

### Test 9: Validate Mix and Diversity

**Purpose:** Recommendations provide variety

**Steps:**
1. Generate recommendations
2. Count types and categories
3. Check for diversity

**Expected Results:**
- ✅ 3-5 educational items (📚)
- ✅ 1-3 partner offers (🎁)
- ✅ Different educational types:
  - Articles
  - Templates
  - Calculators
  - Videos
- ✅ Different priorities (not all priority 1)

**Validation Points:**
- [ ] Total = education + offers
- [ ] Education count: 3-5
- [ ] Offer count: 1-3
- [ ] At least 2 different education types
- [ ] Priority levels vary (1, 2, 3, etc.)
- [ ] Not all same difficulty level

---

### Test 10: Validate Generation Metadata

**Purpose:** Verify metadata accuracy

**Steps:**
1. Generate recommendations
2. Scroll to bottom
3. Read metadata JSON

**Expected Metadata:**
```json
{
  "total_recommendations": 6,
  "education_count": 4,
  "partner_offer_count": 2,
  "generation_time_ms": 1247.5,
  "signals_detected": ["credit_utilization"],
  "generated_at": "2025-11-05T23:30:15.123456"
}
```

**Validation Points:**
- [ ] total = education_count + partner_offer_count
- [ ] generation_time_ms < 5000
- [ ] signals_detected is array
- [ ] signals_detected matches signals box
- [ ] generated_at is recent ISO timestamp
- [ ] JSON is valid and formatted

---

### Test 11: Error Handling - Invalid User

**Purpose:** Verify graceful error handling

**Steps:**
1. Enter User ID: `invalid_user_999`
2. Click Generate

**Expected Results:**
- ✅ Error message displays (red box)
- ✅ Message: "User invalid_user_999 not found or no persona assigned"
- ✅ Previous results are hidden
- ✅ No JavaScript errors in console
- ✅ UI remains functional

**Validation Points:**
- [ ] Error message is clear
- [ ] Error message is user-friendly
- [ ] UI doesn't crash
- [ ] Can try again with valid user

---

### Test 12: Error Handling - Invalid Time Window

**Purpose:** Verify validation of time window parameter

**Steps:**
1. Open browser console (F12)
2. Run: `fetch('/api/recommendations/user_MASKED_001?time_window=90d&generate=true').then(r => r.json()).then(console.log)`

**Expected Results:**
- ✅ HTTP 400 error
- ✅ Error message: "time_window must be '30d' or '180d'"

**Validation Points:**
- [ ] Invalid window rejected
- [ ] Error code is 400 (bad request)
- [ ] Error message is clear

---

### Test 13: Visual Design Validation

**Purpose:** Verify professional appearance

**Checklist:**

**Colors:**
- [ ] Purple gradient headers look good
- [ ] Green rationale boxes stand out
- [ ] Blue persona boxes are distinct
- [ ] Yellow disclaimer/citations are noticeable
- [ ] Badge colors are appropriate
- [ ] Text has good contrast on all backgrounds

**Typography:**
- [ ] Headings are clear hierarchy
- [ ] Body text is comfortable size (not too small)
- [ ] Line height makes reading easy
- [ ] No text overflow or cut-off

**Spacing:**
- [ ] Cards have good margins
- [ ] Content within cards isn't cramped
- [ ] Form fields are spaced well
- [ ] Page doesn't feel cluttered

**Responsive:**
- [ ] Works on desktop (1920px wide)
- [ ] Works on laptop (1366px wide)
- [ ] Works on tablet (768px wide) - optional
- [ ] Works on mobile (375px wide) - optional

**Polish:**
- [ ] Hover effects work smoothly
- [ ] No visual glitches
- [ ] Loading spinner is smooth
- [ ] Transitions are professional

---

### Test 14: Performance Validation

**Purpose:** Verify meets performance requirements

**Test A: Generation Time**

**Steps:**
1. Generate recommendations
2. Note generation_time_ms in metadata
3. Repeat 3 times with Force Generate checked

**Expected:**
- ✅ All 3 runs < 5000ms
- ✅ Most runs 1000-2000ms
- ✅ Consistent performance

**Validation Points:**
- [ ] Run 1: _____ ms (< 5000ms)
- [ ] Run 2: _____ ms (< 5000ms)
- [ ] Run 3: _____ ms (< 5000ms)
- [ ] Average: _____ ms (< 2000ms ideal)

**Test B: Cache Performance**

**Steps:**
1. Generate once (Force Generate ✓)
2. Measure time to complete
3. Generate again (Force Generate ✗)
4. Measure time to complete

**Expected:**
- ✅ First: 1000-2000ms
- ✅ Second: < 100ms
- ✅ Speed increase of 10-20x

---

### Test 15: End-to-End User Journey

**Purpose:** Validate complete user experience

**Scenario:** User wants financial recommendations

**Steps:**
1. **Discover**: User opens dashboard
2. **Navigate**: User clicks Recommendations tab
3. **Input**: User enters their ID
4. **Generate**: User clicks button
5. **Wait**: User sees loading state
6. **Review**: User sees results
7. **Read**: User reads first recommendation
8. **Understand**: User reads rationale
9. **Trust**: User sees data citations
10. **Notice**: User sees disclaimer
11. **Act**: User clicks Learn More

**Validation:**
- [ ] Flow is intuitive (no confusion)
- [ ] Each step is clear
- [ ] Loading states are obvious
- [ ] Results are easy to understand
- [ ] Rationales make sense
- [ ] Citations build trust
- [ ] Disclaimer is noticed
- [ ] Action buttons are clear

**User Experience Check:**
- Would a non-technical user understand this? YES / NO
- Would you trust these recommendations? YES / NO
- Is anything confusing or unclear? _____________

---

## Comprehensive Test Matrix

### Feature Coverage

| Feature | Test # | Status | Notes |
|---------|--------|--------|-------|
| Basic Generation | 1 | ⬜ | |
| Disclaimer Display | 2 | ⬜ | CRITICAL |
| Personalized Rationales | 3 | ⬜ | CRITICAL |
| Data Citations | 4 | ⬜ | |
| Persona Matching | 5 | ⬜ | |
| Time Windows | 6 | ⬜ | |
| Caching | 7 | ⬜ | |
| Card Structure | 8 | ⬜ | |
| Mix & Diversity | 9 | ⬜ | |
| Metadata | 10 | ⬜ | |
| Error: Invalid User | 11 | ⬜ | |
| Error: Invalid Window | 12 | ⬜ | |
| Visual Design | 13 | ⬜ | |
| Performance | 14 | ⬜ | CRITICAL |
| End-to-End UX | 15 | ⬜ | |

### Persona Coverage

| Persona | Tested | Recommendations Appropriate | Notes |
|---------|--------|----------------------------|-------|
| High Utilization | ⬜ | ⬜ | Credit focus |
| Low Savings | ⬜ | ⬜ | Savings focus |
| Irregular Income | ⬜ | ⬜ | Cash flow focus |
| Subscription Heavy | ⬜ | ⬜ | Subscription management |
| Cash Flow Optimizer | ⬜ | ⬜ | Optimization tips |
| Young Professional | ⬜ | ⬜ | Getting started |

### Browser Coverage (Optional)

| Browser | Tested | Issues |
|---------|--------|--------|
| Chrome | ⬜ | |
| Firefox | ⬜ | |
| Safari | ⬜ | |
| Edge | ⬜ | |

---

## Success Criteria

Validation is **PASSED** when:

### Must-Pass (Critical)
- [x] All recommendations generate successfully
- [x] Disclaimer always visible and correct (Test 2)
- [x] Rationales include specific user data (Test 3)
- [x] Generation time < 5 seconds (Test 14)
- [x] Different personas get different recommendations (Test 5)

### Should-Pass (Important)
- [ ] Data citations present and accurate (Test 4)
- [ ] Both time windows work (Test 6)
- [ ] Caching works correctly (Test 7)
- [ ] Error handling is graceful (Tests 11-12)
- [ ] UI looks professional (Test 13)

### Nice-to-Have
- [ ] Performance typically < 2 seconds
- [ ] Responsive design works
- [ ] Cross-browser compatibility
- [ ] End-to-end UX is smooth (Test 15)

---

## Troubleshooting

### API Won't Start

**Symptom:** `python -m spendsense.api.main` fails

**Check:**
```bash
# Are you in correct directory?
pwd

# Is venv activated?
which python

# Are dependencies installed?
pip list | grep fastapi
```

**Solution:** See `docs/session-handoff/TROUBLESHOOTING_HANDOFF.md`

### No Data / 404 Errors

**Symptom:** User not found errors

**Cause:** Database not populated

**Solution:** Need to run Epic 1-3 data ingestion first

### UI Doesn't Load

**Symptom:** Blank page or 404

**Check:**
- Is API server running?
- Is URL correct (http://localhost:8000)?
- Check browser console for errors

**Solution:** Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Recommendations Don't Generate

**Symptom:** Click button, nothing happens

**Check:**
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check Network tab for failed requests

**Solution:** Share console errors for diagnosis

---

## Validation Sign-Off

**Tester Name:** ___________________________
**Date:** ___________________________
**Environment:** ___________________________

**Overall Result:** PASS / FAIL / PARTIAL

**Critical Issues Found:**
1. ___________________________
2. ___________________________
3. ___________________________

**Non-Critical Issues:**
1. ___________________________
2. ___________________________

**Recommendations for Production:**
- [ ] Ready to deploy as-is
- [ ] Ready with minor fixes
- [ ] Needs significant work
- [ ] Not ready for production

**Notes:**
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

**Epic 4 Validation Complete**
**Next:** Epic 5 - Guardrails & Compliance
