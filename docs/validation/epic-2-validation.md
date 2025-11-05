# Epic 2: Behavioral Signals - UI Validation Test Plan

**Date:** 2025-11-04
**Branch:** `epic-2-behavioral-signals`
**URL:** http://localhost:8000
**Tab:** Behavioral Signals

---

## Overview

This document provides comprehensive validation steps for all Epic 2 features accessible through the UI. Similar to Epic 1 validation patterns, each feature has specific test cases covering happy paths, edge cases, and data validation.

**Testing Philosophy:**
- ✅ Verify all 4 signal types (Subscriptions, Savings, Credit, Income)
- ✅ Test both time windows (30d and 180d)
- ✅ Validate data accuracy against expected persona behaviors
- ✅ Test edge cases (no data, missing accounts, etc.)
- ✅ Verify UI responsiveness and error handling

---

## Prerequisites

### 1. Start the Server
```bash
cd /Users/reena/gauntletai/spendsense
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Open Browser
Navigate to: **http://localhost:8000**

### 3. Test Data Available
- **100 synthetic users** with 5 persona types
- **19,821 transactions** across various categories
- **0 accounts** (note: limits savings/credit signals but tests fallback behavior)

---

## Test Suite

### Test Group 1: Basic Functionality

#### Test 1.1: Navigate to Behavioral Signals Tab
**Steps:**
1. Open http://localhost:8000
2. Click "Behavioral Signals" tab in navigation

**Expected Result:**
- ✅ Tab switches to Behavioral Signals content
- ✅ Form displays with User ID input and Time Window selector
- ✅ "Analyze Signals" button is visible
- ✅ No results container visible yet

**Pass Criteria:** Tab content loads without errors

---

#### Test 1.2: Submit Form with Valid User ID (180-day window)
**Steps:**
1. Enter User ID: `user_MASKED_000`
2. Select Time Window: `180 Days (Long-term)`
3. Click "Analyze Signals"

**Expected Result:**
- ✅ Loading message appears
- ✅ 4 signal cards appear: Subscriptions, Savings, Credit, Income
- ✅ Each card has metrics displayed
- ✅ Metadata section shows: Generated timestamp, Window: 180 days, Data Completeness JSON

**Pass Criteria:** All 4 cards render with numeric values (may be zeros due to missing accounts)

---

#### Test 1.3: Submit Form with Valid User ID (30-day window)
**Steps:**
1. Enter User ID: `user_MASKED_000`
2. Select Time Window: `30 Days (Short-term)`
3. Click "Analyze Signals"

**Expected Result:**
- ✅ Same 4 signal cards appear
- ✅ Metadata shows "Window: 30 days"
- ✅ Values may differ from 180-day window (shorter time range)

**Pass Criteria:** Window switch works correctly, metadata reflects selected window

---

### Test Group 2: Subscription Detection (Story 2.2)

**Note:** Subscriptions are detected from transactions only (no accounts required)

#### Test 2.1: Subscription-Heavy User (persona: subscription_heavy)
**User IDs to Test:**
- `user_MASKED_002`
- `user_MASKED_007`
- `user_MASKED_012` (every 5th user alternates personas)

**Steps:**
1. Enter User ID from above
2. Select `180 Days`
3. Click "Analyze Signals"
4. Examine **Subscriptions card**

**Expected Result:**
- ✅ **Subscription Count:** > 0 (ideally 3-8 subscriptions)
- ✅ **Monthly Recurring:** > $0 (ideally $50-200)
- ✅ **Share of Spend:** > 0% (ideally 15-30%)

**Pass Criteria:**
- Subscription count detected (based on recurring transactions like Netflix, Spotify, etc.)
- Values are non-zero if user has GENERAL_SERVICES_SUBSCRIPTION transactions

**API Validation:**
```bash
curl http://localhost:8000/api/signals/user_MASKED_002/subscriptions?window_days=180
```
Should return non-zero subscription metrics

---

#### Test 2.2: Compare 30d vs 180d Windows for Subscriptions
**Steps:**
1. Enter `user_MASKED_002`
2. Test with 180 days → Note subscription_count and monthly_recurring_spend
3. Test with 30 days → Compare values

**Expected Result:**
- ✅ 180d window shows more subscriptions detected (longer lookback)
- ✅ 30d window shows subset of active subscriptions
- ✅ Monthly recurring spend should be similar (monthly charges)

**Pass Criteria:** Longer window detects equal or more subscriptions

---

#### Test 2.3: Control User (Low Subscription Activity)
**User IDs to Test:**
- `user_MASKED_004` (control persona)
- `user_MASKED_009`

**Steps:**
1. Enter control user ID
2. Select `180 Days`
3. Click "Analyze Signals"

**Expected Result:**
- ✅ Subscription Count: 0-2 (low activity)
- ✅ Monthly Recurring: Low amount (< $50)
- ✅ Share of Spend: < 10%

**Pass Criteria:** Control users show lower subscription activity than subscription_heavy users

---

### Test Group 3: Savings Behavior Detection (Story 2.3)

**Note:** Savings detection requires accounts table. Currently empty, so testing fallback behavior.

#### Test 3.1: Savings Builder (Missing Accounts - Fallback Test)
**User IDs to Test:**
- `user_MASKED_003` (savings_builder persona)
- `user_MASKED_008`

**Steps:**
1. Enter User ID
2. Select `180 Days`
3. Click "Analyze Signals"
4. Examine **Savings card**

**Expected Result (Current State - No Accounts):**
- ✅ **Has Savings:** No (displayed in muted gray)
- ✅ **Total Balance:** $0.00
- ✅ **Growth Rate:** 0.0%
- ✅ **Emergency Fund:** 0.0 months

**Expected Result (When Accounts Populated):**
- Has Savings: Yes (green)
- Total Balance: > $1000
- Growth Rate: > 0% (positive)
- Emergency Fund: > 1 month

**Pass Criteria:**
- Fallback values displayed correctly when no accounts
- No errors or crashes

**API Validation:**
```bash
curl http://localhost:8000/api/signals/user_MASKED_003/savings?window_days=180
```
Should return all zeros with has_savings_accounts=false

---

#### Test 3.2: Verify Metadata Shows Savings Incompleteness
**Steps:**
1. Analyze any user
2. Scroll to Metadata section
3. Check `Data Completeness` JSON

**Expected Result:**
- ✅ JSON shows: `"savings": false`
- ✅ `fallbacks_applied` includes "savings"

**Pass Criteria:** System correctly reports missing savings data

---

### Test Group 4: Credit Utilization Detection (Story 2.4)

**Note:** Credit requires accounts with type='credit' and balance_limit. Currently empty.

#### Test 4.1: High Utilization User (Missing Accounts - Fallback Test)
**User IDs to Test:**
- `user_MASKED_000` (high_utilization persona)
- `user_MASKED_005`

**Steps:**
1. Enter User ID
2. Select `180 Days`
3. Click "Analyze Signals"
4. Examine **Credit card**

**Expected Result (Current State - No Accounts):**
- ✅ **Credit Cards:** 0
- ✅ **Aggregate Utilization:** 0.0% (displayed as success/green)
- ✅ **High Utilization:** 0 cards
- ✅ **Overdue:** 0 accounts (green)

**Expected Result (When Accounts Populated):**
- Credit Cards: 1-3
- Aggregate Utilization: 70-90% (displayed in red/error)
- High Utilization: 1-2 cards (yellow/warning)
- Overdue: 0 accounts (should remain green)

**Pass Criteria:**
- Fallback values displayed correctly
- Color coding works (green for 0%)

**API Validation:**
```bash
curl http://localhost:8000/api/signals/user_MASKED_000/credit?window_days=180
```
Should return all zeros with num_credit_cards=0

---

#### Test 4.2: Verify Color-Coded Utilization Thresholds
**Steps:**
1. Once accounts are populated, test with different utilization rates
2. Check color classes applied

**Expected Color Coding:**
- ✅ **0-29%:** Green (success) - Low utilization
- ✅ **30-49%:** Orange (caution) - Moderate utilization
- ✅ **50-79%:** Yellow (warning) - High utilization
- ✅ **80-100%:** Red (error) - Very high utilization

**Pass Criteria:** Colors change based on utilization percentage

---

### Test Group 5: Income Stability Detection (Story 2.5)

**Note:** Income detection works from transactions (INCOME_WAGES category)

#### Test 5.1: Stable Income User (Regular Payroll)
**User IDs to Test:**
- `user_MASKED_004` (control - should have stable income)
- `user_MASKED_003` (savings_builder - should have stable income)

**Steps:**
1. Enter User ID
2. Select `180 Days`
3. Click "Analyze Signals"
4. Examine **Income card**

**Expected Result:**
- ✅ **Payment Frequency:** "biweekly" or "monthly" (not "unknown")
- ✅ **Income Transactions:** > 6 (at least 6 paychecks in 180 days)
- ✅ **Total Income:** > $10,000 (meaningful amount)
- ✅ **Regular Income:** Yes (green)

**Pass Criteria:**
- Payment frequency detected correctly
- Regular income flag = true

**API Validation:**
```bash
curl http://localhost:8000/api/signals/user_MASKED_004/income?window_days=180
```
Should show has_regular_income=true and detected frequency

---

#### Test 5.2: Variable Income User (Irregular Payroll)
**User IDs to Test:**
- `user_MASKED_001` (variable_income persona)
- `user_MASKED_006`

**Steps:**
1. Enter User ID
2. Select `180 Days`
3. Click "Analyze Signals"
4. Examine **Income card**

**Expected Result:**
- ✅ **Payment Frequency:** "irregular" or "unknown"
- ✅ **Income Transactions:** Varies (may be lower or inconsistent)
- ✅ **Total Income:** Variable amounts
- ✅ **Regular Income:** No (muted/gray)

**Pass Criteria:** Variable income users show irregular patterns vs. stable users

---

#### Test 5.3: Compare 30d vs 180d for Income Stability
**Steps:**
1. Enter `user_MASKED_001` (variable_income)
2. Test with 180 days
3. Test with 30 days
4. Compare payment_frequency

**Expected Result:**
- ✅ 180d: Better pattern detection (more data points)
- ✅ 30d: May show "unknown" if < 2 paychecks in window
- ✅ Total income differs proportionally

**Pass Criteria:** Longer window provides more accurate frequency detection

---

### Test Group 6: Behavioral Summary (Story 2.6)

#### Test 6.1: Full Signal Analysis - All 4 Signals Together
**Steps:**
1. Enter `user_MASKED_000`
2. Select `180 Days`
3. Click "Analyze Signals"
4. Review all 4 cards simultaneously

**Expected Result:**
- ✅ All 4 cards render without errors
- ✅ Subscriptions card shows data (if transactions exist)
- ✅ Savings card shows zeros (fallback)
- ✅ Credit card shows zeros (fallback)
- ✅ Income card shows data (if INCOME transactions exist)
- ✅ Metadata section complete

**Pass Criteria:** Full behavioral summary displays cohesively

---

#### Test 6.2: Verify Metadata Completeness
**Steps:**
1. Analyze any user
2. Scroll to **Analysis Metadata** section
3. Examine all fields

**Expected Fields:**
- ✅ **Generated:** ISO timestamp (e.g., 2025-11-04T21:53:57.582754)
- ✅ **Window:** Matches selected (30 days or 180 days)
- ✅ **Data Completeness:** JSON object showing true/false for each signal
  ```json
  {
    "subscriptions": false,
    "savings": false,
    "credit": false,
    "income": false
  }
  ```

**Pass Criteria:** Metadata accurately reflects data availability

---

### Test Group 7: Edge Cases & Error Handling

#### Test 7.1: Non-Existent User ID
**Steps:**
1. Enter User ID: `user_INVALID_999`
2. Click "Analyze Signals"

**Expected Result:**
- ✅ Error message displays: "Error: Failed to fetch signals" or similar
- ✅ No crash or blank screen
- ✅ User can retry with different ID

**Pass Criteria:** Graceful error handling for invalid users

---

#### Test 7.2: Empty User ID Field
**Steps:**
1. Leave User ID field blank
2. Click "Analyze Signals"

**Expected Result:**
- ✅ HTML5 validation prevents submission
- ✅ Browser shows "Please fill out this field" message
- ✅ Form does not submit

**Pass Criteria:** Required field validation works

---

#### Test 7.3: Special Characters in User ID
**Steps:**
1. Enter User ID: `user_<script>alert('xss')</script>`
2. Click "Analyze Signals"

**Expected Result:**
- ✅ API returns error (user not found)
- ✅ No script execution (XSS protected)
- ✅ Error message displayed safely

**Pass Criteria:** No XSS vulnerability

---

#### Test 7.4: Rapid Window Switching
**Steps:**
1. Enter `user_MASKED_000`
2. Click "Analyze Signals" with 180 days
3. Immediately switch to 30 days and click again
4. Switch back to 180 days and click again

**Expected Result:**
- ✅ Results update each time
- ✅ No stale data displayed
- ✅ Metadata reflects current window
- ✅ No race conditions or UI glitches

**Pass Criteria:** UI handles rapid state changes correctly

---

### Test Group 8: API Direct Testing

These tests validate the API endpoints directly (not through UI).

#### Test 8.1: Full Behavioral Summary Endpoint
```bash
curl -s http://localhost:8000/api/signals/user_MASKED_000 | jq
```

**Expected Result:**
- ✅ Returns JSON with all 4 signal types
- ✅ Each signal has both 30d and 180d windows
- ✅ Metadata included
- ✅ Valid JSON structure

---

#### Test 8.2: Individual Signal Endpoints
```bash
# Subscriptions
curl -s http://localhost:8000/api/signals/user_MASKED_002/subscriptions?window_days=180 | jq

# Savings
curl -s http://localhost:8000/api/signals/user_MASKED_003/savings?window_days=180 | jq

# Credit
curl -s http://localhost:8000/api/signals/user_MASKED_000/credit?window_days=180 | jq

# Income
curl -s http://localhost:8000/api/signals/user_MASKED_001/income?window_days=180 | jq
```

**Expected Result:**
- ✅ Each endpoint returns specific signal metrics
- ✅ Query params work (window_days)
- ✅ Data matches persona characteristics

---

#### Test 8.3: Invalid Window Days
```bash
curl -s http://localhost:8000/api/signals/user_MASKED_000/subscriptions?window_days=999
```

**Expected Result:**
- ✅ API returns 400 or 422 error
- ✅ Error message indicates valid values (30 or 180)

---

### Test Group 9: Persona-Specific Validation

This section tests that each persona exhibits expected behavioral signals.

#### Test 9.1: High Utilization Persona
**Users:** `user_MASKED_000`, `user_MASKED_005`, `user_MASKED_010`, ...

**Expected Signals:**
- 💳 **Credit:** High utilization when accounts exist (70-90%)
- 📺 **Subscriptions:** Moderate activity
- 💰 **Savings:** Low or zero
- 💵 **Income:** Regular income

**Validation:** Credit utilization should be highest for this persona

---

#### Test 9.2: Variable Income Persona
**Users:** `user_MASKED_001`, `user_MASKED_006`, `user_MASKED_011`, ...

**Expected Signals:**
- 💵 **Income:** Irregular payment frequency, high CV
- 💰 **Savings:** Lower emergency fund
- 💳 **Credit:** Moderate utilization
- 📺 **Subscriptions:** Normal

**Validation:** payment_frequency should be "irregular" or "unknown"

---

#### Test 9.3: Subscription Heavy Persona
**Users:** `user_MASKED_002`, `user_MASKED_007`, `user_MASKED_012`, ...

**Expected Signals:**
- 📺 **Subscriptions:** 5-10 subscriptions, 20-30% share of spend
- 💵 **Income:** Regular
- 💳 **Credit:** Normal
- 💰 **Savings:** Normal

**Validation:** subscription_share should be highest for this persona

---

#### Test 9.4: Savings Builder Persona
**Users:** `user_MASKED_003`, `user_MASKED_008`, `user_MASKED_013`, ...

**Expected Signals (when accounts exist):**
- 💰 **Savings:** High balance, positive growth rate, 3+ months emergency fund
- 💵 **Income:** Regular income
- 💳 **Credit:** Low utilization (< 30%)
- 📺 **Subscriptions:** Normal

**Validation:** total_savings_balance should be highest for this persona

---

#### Test 9.5: Control Persona (Baseline)
**Users:** `user_MASKED_004`, `user_MASKED_009`, `user_MASKED_014`, ...

**Expected Signals:**
- All metrics in normal ranges
- No extreme behaviors
- Stable income
- Moderate utilization
- Some savings

**Validation:** All signals should be in "healthy" ranges

---

### Test Group 10: UI/UX Quality

#### Test 10.1: Responsive Design
**Steps:**
1. Open browser DevTools
2. Toggle device toolbar (mobile view)
3. Test with different screen sizes:
   - iPhone (375px)
   - iPad (768px)
   - Desktop (1200px+)

**Expected Result:**
- ✅ Signal cards stack vertically on mobile
- ✅ Grid adjusts to screen width
- ✅ Form remains usable on small screens
- ✅ No horizontal scrolling

**Pass Criteria:** UI adapts to all screen sizes

---

#### Test 10.2: Loading States
**Steps:**
1. Enter user ID and submit
2. Observe loading behavior

**Expected Result:**
- ✅ "Loading behavioral signals..." message appears immediately
- ✅ Previous results cleared
- ✅ Loading indicator visible
- ✅ New results replace loading state smoothly

**Pass Criteria:** Clear feedback during API calls

---

#### Test 10.3: Color Accessibility
**Steps:**
1. Analyze a user
2. Check metric colors

**Color Guidelines:**
- ✅ Green (success): #28a745 - Good values
- ✅ Yellow (warning): #ffc107 - Caution needed
- ✅ Orange (caution): #ff9800 - Moderate concern
- ✅ Red (error): #dc3545 - High concern
- ✅ Gray (muted): #6c757d - Neutral/unavailable

**Pass Criteria:** Colors have sufficient contrast and convey meaning clearly

---

## Test Execution Checklist

Use this checklist to track your validation progress:

### Core Functionality
- [ ] Test 1.1: Navigate to tab
- [ ] Test 1.2: Submit 180-day analysis
- [ ] Test 1.3: Submit 30-day analysis

### Subscriptions (Story 2.2)
- [ ] Test 2.1: Subscription-heavy user
- [ ] Test 2.2: Compare 30d vs 180d
- [ ] Test 2.3: Control user (low activity)

### Savings (Story 2.3)
- [ ] Test 3.1: Savings builder fallback
- [ ] Test 3.2: Metadata completeness

### Credit (Story 2.4)
- [ ] Test 4.1: High utilization fallback
- [ ] Test 4.2: Color-coded thresholds

### Income (Story 2.5)
- [ ] Test 5.1: Stable income user
- [ ] Test 5.2: Variable income user
- [ ] Test 5.3: Compare 30d vs 180d

### Behavioral Summary (Story 2.6)
- [ ] Test 6.1: Full signal analysis
- [ ] Test 6.2: Metadata verification

### Edge Cases
- [ ] Test 7.1: Invalid user ID
- [ ] Test 7.2: Empty field validation
- [ ] Test 7.3: Special characters (XSS)
- [ ] Test 7.4: Rapid window switching

### API Testing
- [ ] Test 8.1: Full summary endpoint
- [ ] Test 8.2: Individual signal endpoints
- [ ] Test 8.3: Invalid parameters

### Persona Validation
- [ ] Test 9.1: High utilization persona
- [ ] Test 9.2: Variable income persona
- [ ] Test 9.3: Subscription heavy persona
- [ ] Test 9.4: Savings builder persona
- [ ] Test 9.5: Control persona

### UI/UX Quality
- [ ] Test 10.1: Responsive design
- [ ] Test 10.2: Loading states
- [ ] Test 10.3: Color accessibility

---

## Known Limitations & Future Improvements

### Current Limitations
1. **Empty Accounts Table:**
   - Savings detection returns all zeros (fallback behavior)
   - Credit detection returns all zeros (fallback behavior)
   - Testing fallback logic instead of actual detection

2. **No Balance History:**
   - Cannot test savings growth rate accurately
   - Cannot test historical credit utilization trends

3. **Limited Income Categories:**
   - Income detection relies on INCOME_WAGES category
   - May miss some income sources (gig economy, investments)

### Recommended Test Data Enhancements
To enable full feature testing:

```sql
-- Add sample accounts for each persona
INSERT INTO accounts (account_id, user_id, type, subtype, balance_current, balance_limit)
VALUES
  -- Savings builder
  ('acc_sav_001', 'user_MASKED_003', 'depository', 'savings', 15000.00, NULL),

  -- High utilization
  ('acc_cc_001', 'user_MASKED_000', 'credit', 'credit_card', 8500.00, 10000.00),

  -- Control
  ('acc_chk_001', 'user_MASKED_004', 'depository', 'checking', 5000.00, NULL);
```

After adding accounts, re-run Tests 3.1, 4.1 to validate actual detection vs. fallback.

---

## Success Criteria Summary

**Epic 2 UI validation is successful when:**
- ✅ All 4 signal types display without errors
- ✅ Both time windows (30d/180d) work correctly
- ✅ Metadata accurately reflects data completeness
- ✅ Fallback behavior handles missing accounts gracefully
- ✅ Color coding provides clear visual feedback
- ✅ Edge cases handled (invalid users, empty fields, etc.)
- ✅ API endpoints return expected JSON structures
- ✅ Persona behaviors align with expectations
- ✅ UI is responsive and accessible
- ✅ No console errors or crashes

---

## Quick Test Script

For rapid validation, run this sequence:

```bash
# 1. Start server
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --reload --host 127.0.0.1 --port 8000 &

# 2. Test all 5 personas (one from each)
curl -s http://localhost:8000/api/signals/user_MASKED_000 | jq '.income."180d".payment_frequency'  # high_utilization
curl -s http://localhost:8000/api/signals/user_MASKED_001 | jq '.income."180d".payment_frequency'  # variable_income
curl -s http://localhost:8000/api/signals/user_MASKED_002 | jq '.subscriptions."180d".subscription_count'  # subscription_heavy
curl -s http://localhost:8000/api/signals/user_MASKED_003 | jq '.savings."180d".has_savings_accounts'  # savings_builder
curl -s http://localhost:8000/api/signals/user_MASKED_004 | jq '.income."180d".has_regular_income'  # control

# 3. Open UI and spot-check 3-5 users manually
open http://localhost:8000
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-04
**Maintained By:** SpendSense Team
