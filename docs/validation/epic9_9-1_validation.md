# Story 9.1 Validation Guide: Recommendations Data Integration

**Story:** 9.1 - Recommendations Data Integration
**Epic:** 9 - Frontend-Backend Data Integration
**Created:** 2025-11-08
**Status:** Ready for Validation

---

## 30-Second Quick Test

```bash
# 1. Ensure backend is running
curl http://localhost:8000/api/recommendations/user_MASKED_000?time_window=30d | python3 -m json.tool | head -20

# 2. Start frontend (in new terminal)
cd spendsense/ui && npm run dev

# 3. Open browser to http://localhost:5173/dashboard
# 4. Verify recommendations section shows real data (not "Loading..." forever)
# 5. Toggle time window (30d <-> 180d) and verify recommendations update
```

**Expected Result:** Dashboard displays 4 recommendation cards with real titles, descriptions, and disclaimer.

---

## Manual Testing Steps

### Prerequisites
```bash
# Backend server must be running on port 8000
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend dev server on port 5173
cd spendsense/ui
npm run dev
```

### Test 1: Dashboard Recommendations Display (AC 1-4)
**Steps:**
1. Navigate to http://localhost:5173/onboarding/welcome
2. Complete onboarding with user_MASKED_000
3. Land on dashboard
4. Scroll to "Your Personalized Recommendations" section

**Expected:**
- [ ] Section shows 4 recommendation cards (not hardcoded data)
- [ ] Each card has: icon, type badge, title, description, rationale, "Learn more" button
- [ ] No "Loading..." spinner stuck permanently
- [ ] No console errors

**Verify:**
```bash
# Check that recommendations came from API
# Open browser DevTools -> Network tab -> Filter: recommendations
# Should see: GET /api/recommendations/user_MASKED_000?time_window=30d -> 200 OK
```

### Test 2: Time Window Toggle (AC 4)
**Steps:**
1. On dashboard, locate time window toggle (30d / 180d)
2. Click "180d" toggle
3. Observe recommendations section

**Expected:**
- [ ] Recommendations section shows loading spinner briefly
- [ ] Recommendations update with different content (180d persona likely different)
- [ ] Network tab shows new request: `/api/recommendations/user_MASKED_000?time_window=180d`
- [ ] No errors in console

### Test 3: Loading State (AC 5)
**Steps:**
1. Clear browser cache
2. Hard refresh dashboard (Cmd+Shift+R)
3. Observe recommendations section during load

**Expected:**
- [ ] Shows spinner with "Loading recommendations..." message
- [ ] Spinner disappears when data loads
- [ ] No flash of wrong content

### Test 4: Error State (AC 6)
**Steps:**
1. Stop backend server (Ctrl+C in backend terminal)
2. Refresh dashboard
3. Observe recommendations section

**Expected:**
- [ ] Shows error message: "Failed to load recommendations" (or similar)
- [ ] Shows "Retry" button
- [ ] Click retry button -> still shows error (server still down)
- [ ] Restart server, click retry -> recommendations load successfully

### Test 5: Empty State (AC 7)
**Steps:**
1. Temporarily modify API to return empty recommendations array:
```python
# In spendsense/api/recommendations.py (line ~50)
# Change: return RecommendationsResponse(...)
# To: return RecommendationsResponse(..., recommendations=[], ...)
```
2. Restart backend server
3. Refresh dashboard

**Expected:**
- [ ] Shows message: "No recommendations available yet"
- [ ] Shows subtext: "Check back after more transactions are processed"
- [ ] No error state (different from error)

**Restore:**
```bash
# Undo the temporary change and restart server
```

### Test 6: Recommendations Feed Page (AC 8-10)
**Steps:**
1. From dashboard, click "View All →" button in recommendations section
2. Should navigate to `/dashboard/tips`
3. Observe full recommendations feed

**Expected:**
- [ ] All recommendations displayed (not just first 4)
- [ ] Filter tabs work: All | Education | Tools | Partner Offers
- [ ] Search bar works: type "budget" -> filters to matching titles/descriptions
- [ ] Results count updates: "Showing X recommendations"
- [ ] All data comes from API (no hardcoded recommendations)

### Test 7: Disclaimer Display (AC 11)
**Steps:**
1. Check dashboard recommendations section (bottom)
2. Check recommendations feed page (bottom)

**Expected:**
- [ ] Yellow disclaimer box displayed on both pages
- [ ] Text: "This is educational content, not financial advice. Consult a licensed advisor for personalized guidance."
- [ ] Warning icon (⚠️) visible
- [ ] Readable contrast (WCAG AA compliant)

### Test 8: Recommendation Card Content (AC 12-13)
**Steps:**
1. On recommendations feed, inspect a recommendation card

**Expected:**
- [ ] **Title:** content.title displayed
- [ ] **Description:** content.description displayed
- [ ] **Type Badge:** content.type (e.g., "article", "savings_account")
- [ ] **Rationale:** rationale text displayed
- [ ] **Icon:** Education items show BookOpen, Partner offers show Building2
- [ ] **Clickable:** Card navigates to `/dashboard/recommendations/{item_id}` on click

### Test 9: No Hardcoded Data (AC 14)
**Steps:**
```bash
# From project root
grep -r "mock" spendsense/ui/src/pages/EndUserDashboard.tsx
grep -r "mock" spendsense/ui/src/pages/RecommendationsFeed.tsx
grep -r "hardcoded" spendsense/ui/src/pages/EndUserDashboard.tsx
grep -r "TODO" spendsense/ui/src/pages/RecommendationsFeed.tsx | grep -i recommend
```

**Expected:**
- [ ] No results (all mock data removed)
- [ ] No "TODO" comments related to recommendations

### Test 10: TypeScript Compilation
**Steps:**
```bash
cd spendsense/ui
npm run build
```

**Expected:**
- [ ] Build succeeds with no TypeScript errors
- [ ] No warnings about missing types for recommendations

### Test 11: Different Users (Bonus)
**Steps:**
1. Log out (clear localStorage: `localStorage.clear()` in console)
2. Complete onboarding as user_MASKED_001
3. Check recommendations

**Expected:**
- [ ] Different recommendations than user_MASKED_000
- [ ] Different persona assignment (likely)
- [ ] API call uses correct user_id

---

## Edge Cases & Error Handling

### Edge Case 1: Rapid Time Window Toggle
**Steps:**
1. Click 30d -> 180d -> 30d -> 180d quickly (5 times in 2 seconds)

**Expected:**
- [ ] No race conditions
- [ ] Final displayed recommendations match selected time window
- [ ] No duplicate API requests (or properly cancelled)

### Edge Case 2: Network Timeout
**Steps:**
1. Slow down network in DevTools (Network tab -> Throttling -> Slow 3G)
2. Refresh dashboard

**Expected:**
- [ ] Loading state shows for longer duration
- [ ] Eventually loads successfully (or times out gracefully)
- [ ] No hanging spinner forever

### Edge Case 3: Malformed API Response
**Steps:**
1. Temporarily break API response structure (return invalid JSON)
2. Refresh dashboard

**Expected:**
- [ ] Error state displayed
- [ ] Console shows parsing error (but app doesn't crash)
- [ ] Retry button available

---

## Acceptance Criteria Checklist

From Story 9.1:

1. ✅ Dashboard Recommendations Section (`EndUserDashboard.tsx`) removes hardcoded data
2. ✅ Calls `GET /api/recommendations/{user_id}?time_window={timeWindow}` on mount
3. ✅ Displays first 4 recommendations (education + partner offers mixed)
4. ✅ Updates when time window changes (30d ↔ 180d toggle)
5. ✅ Loading state while fetching
6. ✅ Error state with retry button
7. ✅ Empty state if no recommendations available
8. ✅ Recommendations Feed Page (`RecommendationsFeed.tsx`) uses API
9. ✅ Filter by type: All | Education | Tools | Partner Offers
10. ✅ Search functionality across title and description
11. ✅ Mandatory disclaimer displayed from API response
12. ✅ Recommendation cards show: title, description, rationale, persona_match_reason, signal_citations
13. ✅ Partner offer savings estimates displayed
14. ✅ All hardcoded recommendations removed

**Status:** All ACs passing in implementation. Manual validation required.

---

## Known Issues & Limitations

### Current Implementation Notes
1. **Recommendation Detail Page:** Currently navigates to `/dashboard/recommendations/{item_id}` but detail page not yet implemented (Story 9.1 scope: list view only)
2. **Consent Error Handling:** 403 consent errors handled in fetchRecommendations but might need UX refinement
3. **Caching:** No caching implemented yet (every time window toggle refetches). Could optimize with React Query or SWR in future.

### Future Improvements (Out of Scope for 9.1)
- Skeleton loaders instead of spinner
- Optimistic UI updates
- Offline support
- Recommendation detail page implementation
- Pagination for recommendations feed (currently loads all)

---

## Rollback Plan

If critical issues found during validation:

### Quick Rollback (Emergency)
```bash
# Revert to previous commit before Story 9.1
git log --oneline | head -5  # Find commit before Story 9.1
git revert <commit-hash>
git push origin epic-9-frontend-backend-integration
```

### Selective Rollback (Partial Fix)
```bash
# Restore just the hardcoded recommendations temporarily
git show <previous-commit>:spendsense/ui/src/pages/EndUserDashboard.tsx > temp_dashboard.tsx
# Copy back the hardcoded recommendations section
```

### Data Rollback
No database changes in this story. Frontend-only changes.

---

## Sign-Off

**Developer:** Claude Code
**Validation Date:** _____________
**Validated By:** _____________
**Result:** ☐ Pass  ☐ Fail (see issues below)

**Issues Found:**

1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

**Approved for Merge:** ☐ Yes  ☐ No (fix required)

---

## Related Documentation

- Story File: `docs/stories/9-1-recommendations-data-integration.md`
- Story Context: `docs/stories/9-1-recommendations-data-integration.context.xml`
- Epic 9 PRD: `docs/prd/epic-9-frontend-backend-integration.md`
- Architecture: `docs/architecture.md` (React SPA Frontend section)
- API Endpoint: `GET /api/recommendations/{user_id}?time_window={timeWindow}` in `spendsense/api/recommendations.py`
