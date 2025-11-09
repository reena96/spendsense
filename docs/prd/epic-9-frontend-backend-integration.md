# Epic 9: Frontend-Backend Data Integration

**Goal:** Replace all hardcoded mock data in the end-user dashboard with real-time data from database APIs, ensuring the frontend displays actual user financial data, personalized recommendations, and behavioral insights.

**Context:** Epic 8 built the end-user dashboard UI/UX with mock data to validate design and user flows. Now we need to connect the frontend to the existing backend APIs (from Epics 1-5) to display real user data. This epic removes all hardcoded values and implements proper data fetching, state management, and error handling.

**Dependencies:**
- Epic 8 (End-User Dashboard) ✅ Complete - UI/UX built with mock data
- Epic 4 (Recommendations) ✅ Complete - API endpoints ready
- Epic 2 (Behavioral Signals) ✅ Complete - Signal detection APIs ready
- Epic 3 (Persona Assignment) ✅ Complete - Persona APIs ready
- Backend APIs: All endpoints exist and tested

**Impact:**
- Users see their ACTUAL financial data, not mock data
- Recommendations are personalized based on real behavioral signals
- Dashboard reflects true 30d vs 180d time windows
- Signal detail pages show real transactions and patterns
- System ready for production deployment

---

## Backend APIs Available (Already Implemented)

All required APIs exist and are tested:

| API Endpoint | Purpose | Returns |
|--------------|---------|---------|
| `GET /api/profile/{user_id}` | Persona with evidence | Persona assignments (30d/180d), match_evidence |
| `GET /api/recommendations/{user_id}?time_window=30d` | Personalized recs | Education + partner offers with rationales |
| `GET /api/signals/{user_id}/subscriptions` | Subscription details | Detected subscriptions, monthly costs, trends |
| `GET /api/signals/{user_id}/credit` | Credit utilization | Credit cards, balances, utilization rates |
| `GET /api/signals/{user_id}/savings` | Savings patterns | Savings accounts, balances, emergency fund |
| `GET /api/signals/{user_id}/income` | Income stability | Income transactions, frequency, stability |
| `GET /api/consent/{user_id}` | Consent status | Consent granted/revoked, timestamp |

---

## Story 9.1: Recommendations Data Integration

**Priority:** 🔴 **CRITICAL** - Users currently see fake recommendations

As an **end user**,
I want **to see real personalized recommendations based on my actual financial behavior**,
so that **I receive relevant advice tailored to my situation, not generic mock data**.

### Acceptance Criteria

1. **Dashboard Recommendations Section** (`EndUserDashboard.tsx`)
   - Remove hardcoded recommendations array (lines 195-199)
   - Call `GET /api/recommendations/{user_id}?time_window={timeWindow}` on mount
   - Display first 4 recommendations (education + partner offers mixed)
   - Show "View All" link to `/recommendations` page
   - Update when time window changes (30d ↔ 180d toggle)
   - Loading state while fetching
   - Error state with retry button
   - Empty state if no recommendations available

2. **Recommendations Feed Page** (`RecommendationsFeed.tsx`)
   - Remove hardcoded `allRecommendations` array (lines 19-66)
   - Fetch from API on mount: `GET /api/recommendations/{user_id}?time_window=30d`
   - Display all recommendations with filtering
   - Filter by type: All | Education | Tools | Partner Offers
   - Search functionality across title and description
   - Respect time window from user preference
   - Show recommendation count: "Showing X recommendations"
   - Loading skeleton during fetch
   - Error handling with retry

3. **Recommendation Card Display**
   - Extract data from API response structure:
     - `item_type`: "education" or "partner_offer"
     - `content.title`: Display title
     - `content.description`: Display description
     - `content.type`: Article, guide, calculator, etc.
     - `content.key_benefits`: Display bullet list
     - `rationale`: Why this recommendation
     - `persona_match_reason`: Persona-specific explanation
     - `signal_citations`: Data points used
   - Map `item_type` to icon (📘 education, 🏦 partner offer, 🧮 tool)
   - Show partner offer savings estimate if available
   - Display eligibility status for partner offers

4. **Mandatory Disclaimer**
   - Display `disclaimer` from API response
   - Show on dashboard and recommendations feed
   - Use warning icon (⚠️) with yellow background
   - Clear, prominent placement

5. **Time Window Integration**
   - Fetch recommendations for current time window (30d or 180d)
   - Re-fetch when user changes time window toggle
   - Show time window indicator: "Recommendations based on last X days"
   - Cache recommendations per time window to avoid redundant fetches

6. **Error Handling**
   - Network error: "Unable to load recommendations. Try again?"
   - 403 Consent error: "You need to grant consent to see recommendations"
   - 404 User not found: Redirect to onboarding
   - Empty state: "No recommendations available yet. Check back after more transactions."

7. **Performance**
   - Implement loading states (skeleton or spinner)
   - Cache API response in component state
   - Don't re-fetch on every render
   - Debounce search input (300ms)

### Technical Implementation

**File:** `spendsense/ui/src/services/api.ts`
```typescript
export interface RecommendationContent {
  id: string;
  type: string;
  title: string;
  description: string;
  category?: string;
  priority: number;
  content_url?: string;
  offer_url?: string;
  key_benefits?: string[];
  provider?: string;
}

export interface Recommendation {
  item_type: 'education' | 'partner_offer';
  item_id: string;
  content: RecommendationContent;
  rationale: string;
  persona_match_reason: string;
  signal_citations: string[];
}

export interface RecommendationsResponse {
  user_id: string;
  persona_id: string;
  time_window: string;
  recommendations: Recommendation[];
  disclaimer: string;
  metadata: {
    total_recommendations: number;
    education_count: number;
    partner_offer_count: number;
  };
}

export async function fetchRecommendations(
  userId: string,
  timeWindow: '30d' | '180d' = '30d'
): Promise<RecommendationsResponse> {
  const response = await fetch(
    `/api/recommendations/${userId}?time_window=${timeWindow}`
  );

  if (!response.ok) {
    if (response.status === 403) {
      throw new Error('Consent required to view recommendations');
    }
    throw new Error('Failed to load recommendations');
  }

  return response.json();
}
```

**File:** `spendsense/ui/src/pages/EndUserDashboard.tsx`
```typescript
const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
const [recsLoading, setRecsLoading] = useState(true);
const [recsError, setRecsError] = useState<string | null>(null);

useEffect(() => {
  const loadRecommendations = async () => {
    if (!userId) return;

    setRecsLoading(true);
    try {
      const data = await fetchRecommendations(userId, timeWindow);
      setRecommendations(data.recommendations.slice(0, 4)); // First 4 for dashboard
    } catch (err) {
      setRecsError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setRecsLoading(false);
    }
  };

  loadRecommendations();
}, [userId, timeWindow]);
```

### Testing Checklist

- [ ] Dashboard shows first 4 real recommendations from API
- [ ] Recommendations change when time window toggles
- [ ] RecommendationsFeed shows all recommendations from API
- [ ] Filter by type works (All, Education, Partner Offers)
- [ ] Search filters recommendations correctly
- [ ] Loading states display properly
- [ ] Error states show with retry button
- [ ] Disclaimer displays on both dashboard and feed
- [ ] No mock data remains in code
- [ ] API errors handled gracefully (403, 404, 500)
- [ ] Time window indicator shows correct period

### Definition of Done

- ✅ All hardcoded recommendations removed from codebase
- ✅ Dashboard calls `/api/recommendations/{user_id}` API
- ✅ Recommendations feed calls same API
- ✅ Time window (30d/180d) correctly passed to API
- ✅ Loading, error, and empty states implemented
- ✅ Disclaimer displayed prominently
- ✅ Manual testing with real user data confirms accuracy
- ✅ No console errors or warnings
- ✅ Code review completed
- ✅ Grep search confirms no "mock" or "hardcoded" comments remain

---

## Story 9.2: Subscriptions Signal Data Integration

**Priority:** 🔴 **CRITICAL** - Subscription page shows fake data

As an **end user**,
I want **to see my actual recurring subscriptions and spending patterns**,
so that **I can identify real opportunities to reduce subscription costs**.

### Acceptance Criteria

1. **Subscriptions Detail Page** (`spendsense/ui/src/pages/signals/SubscriptionsDetail.tsx`)
   - Remove hardcoded subscriptions array (lines 24-32)
   - Remove hardcoded monthlyIncome (line 35)
   - Call `GET /api/signals/{user_id}/subscriptions` on mount
   - Display real detected subscriptions from API

2. **Data Mapping from API**
   - API returns: `detected_subscriptions` array with:
     - `merchant_name`: Display as subscription name
     - `avg_amount`: Display as monthly cost
     - `cadence`: monthly | irregular
     - `transaction_count`: Number of transactions
     - `last_charge_date`: Last charge date
     - `median_gap_days`: Payment frequency
   - Map merchant names to icons (use generic icon if no match)
   - Calculate total from API's `monthly_recurring_spend` field

3. **Key Metrics Display**
   - Active Subscriptions: `subscription_count` from API
   - Total Monthly Cost: `monthly_recurring_spend` from API
   - % of Income: `subscription_share * 100` from API
   - Show as percentage already calculated by backend

4. **Subscription List**
   - Display each subscription with:
     - Icon (merchant-specific or generic)
     - Merchant name
     - Monthly cost
     - Cadence badge (Monthly | Irregular)
     - Last charge date
   - Sort by cost (highest first) by default
   - Allow sorting by name or date

5. **Time Window Support**
   - API accepts `window_days` query param (30 or 180)
   - Update subscriptions when time window changes
   - Show "Last X Days" indicator
   - Note: Some subscriptions may only appear in 180d window

6. **Empty State**
   - If `subscription_count === 0`:
     - "No recurring subscriptions detected"
     - "We haven't detected any recurring charges in this time period."

7. **Error Handling**
   - Network error: Retry button
   - 404 User not found: Redirect to onboarding
   - Loading state: Skeleton or spinner

### Technical Implementation

**File:** `spendsense/ui/src/services/api.ts`
```typescript
export interface DetectedSubscription {
  merchant_name: string;
  cadence: 'monthly' | 'irregular';
  avg_amount: number;
  transaction_count: number;
  last_charge_date: string;
  median_gap_days: number;
}

export interface SubscriptionsData {
  user_id: string;
  window_days: number;
  subscription_count: number;
  monthly_recurring_spend: number;
  total_spend: number;
  subscription_share: number;
  detected_subscriptions: DetectedSubscription[];
}

export async function fetchSubscriptions(
  userId: string,
  windowDays: number = 30
): Promise<SubscriptionsData> {
  const response = await fetch(
    `/api/signals/${userId}/subscriptions?window_days=${windowDays}`
  );

  if (!response.ok) {
    throw new Error('Failed to load subscription data');
  }

  return response.json();
}
```

### Testing Checklist

- [ ] Real subscriptions display from database
- [ ] Monthly cost matches API data
- [ ] Subscription count matches API
- [ ] % of income calculated correctly
- [ ] Time window toggle updates subscriptions
- [ ] Empty state shows when no subscriptions
- [ ] Loading state during fetch
- [ ] Error state with retry
- [ ] No hardcoded subscription data remains

---

## Story 9.3: Credit Utilization Signal Data Integration

**Priority:** 🔴 **CRITICAL**

As an **end user**,
I want **to see my actual credit card balances and utilization rates**,
so that **I understand my real credit situation, not mock data**.

### Acceptance Criteria

1. **Credit Detail Page** (`spendsense/ui/src/pages/signals/CreditUtilizationDetail.tsx`)
   - Remove hardcoded credit card data (line 16+)
   - Call `GET /api/signals/{user_id}/credit` on mount
   - Display real credit cards with actual balances

2. **Data from API** (structure from Epic 2)
   - List of credit card accounts
   - Per-card: name, balance, limit, utilization
   - Aggregate utilization rate
   - High utilization count

3. **Display Requirements**
   - Show each credit card with current balance and limit
   - Highlight high utilization cards (>70%) in red/orange
   - Show aggregate utilization prominently
   - Provide guidance based on actual utilization

4. **Error Handling**
   - No credit cards: Show empty state
   - API error: Retry button
   - Loading state

---

## Story 9.4: Savings & Income Signal Data Integration

**Priority:** 🔴 **CRITICAL**

Similar structure to Stories 9.2 and 9.3, integrate:

**Savings Detail Page:**
- Call `GET /api/signals/{user_id}/savings`
- Display real savings accounts, balances, emergency fund months
- Replace hardcoded savings data

**Income Detail Page:**
- Call `GET /api/signals/{user_id}/income`
- Display real income transactions, frequency, stability
- Replace hardcoded income data

---

## Story 9.5: Persona Card Real-Time Metrics

**Priority:** 🟡 **MEDIUM**

As an **end user**,
I want **my persona card to show a real primary metric calculated from my data**,
so that **I see meaningful insights, not placeholder values**.

### Acceptance Criteria

1. **PersonaCard.tsx** (line 30)
   - Remove hardcoded "primary metric" mock
   - Calculate from `userProfile.assignments[timeWindow].match_evidence`
   - Display persona-specific metric:
     - High Utilization → Show max credit utilization %
     - Subscription Heavy → Show subscription count
     - Low Savings → Show emergency fund months
     - Irregular Income → Show income stability indicator
     - Young Professional → Show credit score or savings rate

2. **Calculation Logic**
   - Extract from match_evidence in persona assignment
   - Format appropriately for display
   - Update when time window changes

---

## Story 9.6: Settings Page Real Data

**Priority:** 🟢 **LOW**

As an **end user**,
I want **my settings page to show my real consent status and user info**,
so that **I see accurate account information**.

### Acceptance Criteria

1. **SettingsPage.tsx** (line 16)
   - Remove hardcoded user data
   - Call `GET /api/consent/{user_id}` on mount
   - Display real consent granted date
   - Show real consent status (granted/revoked)

2. **Consent Revocation**
   - Implement `POST /api/consent` with revoke action (line 22 TODO)
   - Show confirmation dialog before revoking
   - Clear local storage after revocation
   - Redirect to onboarding

---

## Epic 9 Success Metrics

**Before (Current State):**
- ❌ 100% of dashboard data is hardcoded mock data
- ❌ Recommendations show same content for all users
- ❌ Signal pages show fake subscriptions/credit/savings
- ❌ Time window toggle does nothing
- ❌ Cannot test with real user data

**After (Target State):**
- ✅ 100% of dashboard data from database APIs
- ✅ Recommendations personalized per user and time window
- ✅ Signal pages show real transaction data
- ✅ Time window toggle updates all data correctly
- ✅ System ready for production with real users

**Validation:**
- Grep codebase: No "Mock" or "hardcoded" comments
- Test with 3 different user_ids: See different data
- Toggle time window: Data changes appropriately
- Network tab: Verify API calls to backend
- Console: No errors or warnings

---

## Out of Scope for Epic 9

- AI Chat implementation (Epic 10 candidate)
- New backend APIs (all APIs exist)
- New features beyond data integration
- Performance optimization (can be separate epic)
- Advanced caching strategies
- Offline support

---

## Epic 9 Story Summary

| Story | Description | Priority | Estimated Effort |
|-------|-------------|----------|------------------|
| 9.1 | Recommendations Integration | 🔴 Critical | 2-3 hours |
| 9.2 | Subscriptions Integration | 🔴 Critical | 1-2 hours |
| 9.3 | Credit Utilization Integration | 🔴 Critical | 1-2 hours |
| 9.4 | Savings & Income Integration | 🔴 Critical | 1-2 hours |
| 9.5 | Persona Card Real Metrics | 🟡 Medium | 1 hour |
| 9.6 | Settings Page Real Data | 🟢 Low | 30 min |

**Total Estimated Effort:** 6-10 hours

---

## Change Log

**2025-11-08 - v1.0 - Epic Created**
- Epic 9 created to address frontend-backend data integration gap
- Epic 8 built UI with mock data; Epic 9 replaces with real database APIs
- 6 stories defined covering recommendations, signals, persona, and settings
- All required backend APIs already exist from Epics 1-5
- Critical priority to move from prototype to production-ready
