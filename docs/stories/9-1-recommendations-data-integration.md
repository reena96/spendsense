# Story 9.1: Recommendations Data Integration

**Epic:** 9 - Frontend-Backend Data Integration
**Status:** drafted
**Priority:** 🔴 CRITICAL

## Story

As an **end user**,
I want **to see real personalized recommendations based on my actual financial behavior**,
so that **I receive relevant advice tailored to my situation, not generic mock data**.

## Acceptance Criteria

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

## Tasks / Subtasks

### Task 1: Add API Service Methods
- [ ] Create `spendsense/ui/src/services/api.ts` methods
- [ ] Define TypeScript interfaces:
  - `RecommendationContent`
  - `Recommendation`
  - `RecommendationsResponse`
- [ ] Implement `fetchRecommendations(userId, timeWindow)`
- [ ] Handle response errors (403 consent, 404 not found, 500 server error)
- [ ] Test API method with real user_id

### Task 2: Update EndUserDashboard.tsx
- [ ] Remove hardcoded recommendations array (lines 195-199)
- [ ] Add state: `recommendations`, `recsLoading`, `recsError`
- [ ] Create `useEffect` to fetch recommendations on mount
- [ ] Re-fetch when `timeWindow` changes
- [ ] Slice first 4 recommendations for dashboard display
- [ ] Implement loading state UI (skeleton or spinner)
- [ ] Implement error state UI with retry button
- [ ] Implement empty state UI
- [ ] Map API data to recommendation cards
- [ ] Extract disclaimer from API and display prominently

### Task 3: Update RecommendationsFeed.tsx
- [ ] Remove hardcoded `allRecommendations` array (lines 19-66)
- [ ] Add state: `recommendations`, `loading`, `error`
- [ ] Create `useEffect` to fetch on mount
- [ ] Implement filter logic using API data
- [ ] Update search to work with real data structure
- [ ] Map `item_type` to filter categories:
  - education → "Education" filter
  - partner_offer → "Partner Offers" filter
  - Tools → filter by content.type (calculator, template)
- [ ] Display recommendation count from API
- [ ] Show loading skeleton during fetch
- [ ] Error handling with retry

### Task 4: Update RecommendationCard Component
- [ ] Accept `Recommendation` prop with full API structure
- [ ] Display `content.title`
- [ ] Display `content.description`
- [ ] Display `content.type` as badge
- [ ] Display `rationale` in collapsible section
- [ ] Display `persona_match_reason`
- [ ] Display `signal_citations` as bullet list
- [ ] Show `content.key_benefits` if available
- [ ] Show savings estimate for partner offers
- [ ] Map `item_type` to appropriate icon

### Task 5: Implement Time Window Integration
- [ ] Pass `timeWindow` state to `fetchRecommendations`
- [ ] Add dependency to useEffect: `[userId, timeWindow]`
- [ ] Show time window indicator: "Based on last X days"
- [ ] Prevent redundant fetches with proper dependencies
- [ ] Cache recommendations per time window (optional optimization)

### Task 6: Implement Disclaimer Display
- [ ] Extract `disclaimer` from API response
- [ ] Create Disclaimer component or section
- [ ] Style with warning icon (⚠️) and yellow background
- [ ] Display on both dashboard and recommendations feed
- [ ] Ensure WCAG AA contrast compliance

### Task 7: Testing & Validation
- [ ] Test with user_MASKED_000 (young_professional)
- [ ] Test with user_MASKED_001 (different persona)
- [ ] Verify different recommendations for different users
- [ ] Test time window toggle (30d vs 180d)
- [ ] Test filter functionality (All, Education, Partner Offers)
- [ ] Test search functionality
- [ ] Test loading states
- [ ] Test error states (disconnect network, test retry)
- [ ] Test empty state (user with no recommendations)
- [ ] Verify no hardcoded data remains (grep for "mock")
- [ ] Check console for errors/warnings
- [ ] Test responsive design (mobile, tablet, desktop)

### Task 8: Code Cleanup
- [ ] Remove all mock recommendation data
- [ ] Remove "TODO" and "Mock data" comments
- [ ] Add proper TypeScript types
- [ ] Add JSDoc comments to new functions
- [ ] Format code with Prettier
- [ ] Lint with ESLint
- [ ] Git grep for "mock" - should find nothing in recommendations files

## Dev Notes

### API Response Structure
```json
{
  "user_id": "user_MASKED_000",
  "persona_id": "young_professional",
  "time_window": "30d",
  "recommendations": [
    {
      "item_type": "education",
      "item_id": "budgeting_fundamentals",
      "content": {
        "title": "Budgeting Fundamentals",
        "description": "...",
        "type": "article",
        "priority": 3,
        "content_url": "/content/budgeting-basics"
      },
      "rationale": "We recommend this because...",
      "persona_match_reason": "This is relevant for young professionals...",
      "signal_citations": ["Credit utilization: 50%"]
    }
  ],
  "disclaimer": "This is educational content, not financial advice...",
  "metadata": {
    "total_recommendations": 2,
    "education_count": 5,
    "partner_offer_count": 3
  }
}
```

### Files to Modify
- `spendsense/ui/src/services/api.ts` (NEW methods)
- `spendsense/ui/src/pages/EndUserDashboard.tsx` (lines 184-225)
- `spendsense/ui/src/pages/RecommendationsFeed.tsx` (full refactor)
- `spendsense/ui/src/components/recommendations/RecommendationCard.tsx` (update props)

### Testing with Real Data
```bash
# Start backend server
python -m uvicorn spendsense.api.main:app --reload

# Test API endpoint
curl http://localhost:8000/api/recommendations/user_MASKED_000?time_window=30d

# Start frontend
cd spendsense/ui
npm run dev

# Navigate to http://localhost:5173/dashboard
```

## Definition of Done

- ✅ All hardcoded recommendations removed from codebase
- ✅ Dashboard calls `/api/recommendations/{user_id}` API
- ✅ Recommendations feed calls same API
- ✅ Time window (30d/180d) correctly passed to API
- ✅ Loading, error, and empty states implemented
- ✅ Disclaimer displayed prominently
- ✅ Manual testing with real user data confirms accuracy
- ✅ Grep search confirms no "mock" comments in recommendations files
- ✅ No console errors or warnings
- ✅ Code review completed
- ✅ TypeScript compiles without errors
- ✅ All tests pass (if tests exist)

## Change Log

**2025-11-08 - v1.0 - Story Created**
- Story 9.1 created for recommendations data integration
- Replaces hardcoded mock recommendations with real API data
- Critical priority - enables personalized recommendations
- Estimated effort: 2-3 hours
