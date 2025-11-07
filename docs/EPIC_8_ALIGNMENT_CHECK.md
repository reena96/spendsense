# Epic 8 Alignment Check

**Date:** 2025-11-07
**Status:** ✅ ALIGNED - Epic 8 fully compatible with existing implementation

---

## Executive Summary

Epic 8 (End-User Dashboard & Experience) has been created to implement the consumer-facing interface documented in `docs/ux/ux-journey-*.md` files. This document verifies that Epic 8:

1. ✅ **Aligns with existing backend APIs** (no conflicts)
2. ✅ **Leverages completed Epics 1-6** (reuses infrastructure)
3. ✅ **Follows established patterns** (React + TypeScript + TailwindCSS)
4. ✅ **Complements Epic 6** (operator dashboard) without overlap
5. ✅ **Requires minimal new backend work** (only Story 8.5 chat endpoints)

**Verdict:** Epic 8 is ready to implement. All dependencies are satisfied.

---

## Backend API Alignment

### APIs Epic 8 Requires

| Epic 8 Story | Required API | Status | Notes |
|---|---|---|---|
| **8.1 Onboarding** | `POST /api/consent` | ✅ Exists | Line 1299, main.py |
| | `GET /api/profile/{user_id}` | ✅ Exists | Line 1011, main.py |
| **8.2 Dashboard** | `GET /api/profile/{user_id}` | ✅ Exists | Returns persona |
| | `GET /api/signals/{user_id}` | ✅ Exists | Line 839, main.py |
| **8.3 Signals** | `GET /api/signals/{user_id}` | ✅ Exists | Overview |
| | `GET /api/signals/{user_id}/subscriptions` | ✅ Exists | Line 876, main.py |
| | `GET /api/signals/{user_id}/savings` | ✅ Exists | Line 908, main.py |
| | `GET /api/signals/{user_id}/credit` | ✅ Exists | Line 942, main.py |
| | `GET /api/signals/{user_id}/income` | ✅ Exists | Line 976, main.py |
| **8.4 Recommendations** | `GET /api/recommendations/{user_id}` | ✅ Exists | Line 1089, main.py |
| **8.5 Chat** | `POST /api/chat/message` | ❌ **NEW** | Requires implementation |
| | `GET /api/chat/history/{user_id}` | ❌ **NEW** | Requires implementation |
| **8.6 Settings** | `GET /api/consent/{user_id}` | ✅ Exists | Line 1367, main.py |
| | `POST /api/consent` (revoke) | ✅ Exists | Supports revocation |

### Verification

**Existing Endpoints (from `spendsense/api/main.py`):**

```python
# Profile & Persona
@app.get("/api/profile/{user_id}")  # Line 1011 - Returns persona with rationale

# Behavioral Signals
@app.get("/api/signals/{user_id}")  # Line 839 - Comprehensive signals
@app.get("/api/signals/{user_id}/subscriptions")  # Line 876
@app.get("/api/signals/{user_id}/savings")  # Line 908
@app.get("/api/signals/{user_id}/credit")  # Line 942
@app.get("/api/signals/{user_id}/income")  # Line 976

# Recommendations
@app.get("/api/recommendations/{user_id}")  # Line 1089 - Personalized recs

# Consent Management
@app.post("/api/consent")  # Line 1299 - Grant/revoke consent
@app.get("/api/consent/{user_id}")  # Line 1367 - Check consent status
```

**Conclusion:** 10/12 required endpoints exist. Only chat endpoints (Story 8.5) need implementation.

---

## Data Model Alignment

### What Existing APIs Return

**1. Profile/Persona Endpoint (`GET /api/profile/{user_id}`):**
```json
{
  "user_id": "user_MASKED_042",
  "persona_30d": "High Utilization",
  "persona_180d": "Savings Builder",
  "audit_log_30d": {
    "qualifying_personas": [...],
    "assigned_persona": "High Utilization",
    "assignment_reason": "Priority 1 (highest)...",
    "evidence": { "credit_max_utilization_pct": 68.0, ... }
  },
  "computed_at": "2025-11-07T..."
}
```

**Epic 8 Usage:**
- Story 8.1 (Onboarding): Display persona name + evidence in Persona Reveal screen
- Story 8.2 (Dashboard): Show persona card with primary metric
- Story 8.3 (Signals): Link persona to specific signals (credit util = 68%)

**Alignment:** ✅ Perfect match. API provides all data needed for persona reveal and rationale.

---

**2. Signals Endpoints (`GET /api/signals/{user_id}`):**
```json
{
  "user_id": "user_MASKED_042",
  "subscription": {
    "recurring_merchants": ["Netflix", "Spotify", "Adobe"],
    "subscription_count": 7,
    "monthly_subscription_spend": 124.50,
    "subscription_share_of_spend_pct": 3.2
  },
  "credit": {
    "max_utilization_pct": 68.0,
    "cards": [
      {
        "account_id": "acc_card_visa_4523",
        "utilization_pct": 68.0,
        "balance": 3400.0,
        "limit": 5000.0
      }
    ],
    "interest_charges": 87.0
  },
  "savings": {
    "growth_rate_pct": 2.5,
    "net_inflow_monthly": 800.0,
    "emergency_fund_months": 2.5
  },
  "income": {
    "average_monthly": 5000.0,
    "stability": "consistent",
    "pattern": "biweekly"
  }
}
```

**Epic 8 Usage:**
- Story 8.2 (Dashboard): Display 4 signal cards with summary metrics
- Story 8.3 (Signals): Show detailed breakdowns, per-card data, trend charts

**Alignment:** ✅ Perfect match. All signal types covered with rich detail.

---

**3. Recommendations Endpoint (`GET /api/recommendations/{user_id}`):**
```json
{
  "user_id": "user_MASKED_042",
  "recommendations": [
    {
      "id": "rec_001",
      "type": "educational",
      "title": "Credit Utilization Guide",
      "description": "Learn strategies to lower your balance below 30%",
      "rationale": "We noticed your Visa ****4523 is at 68% utilization ($3,400 of $5,000 limit). Bringing this below 30% could improve your credit score and reduce interest charges of $87/month.",
      "category": "credit",
      "format": "article",
      "content_url": "https://..."
    },
    {
      "id": "rec_002",
      "type": "partner_offer",
      "title": "Balance Transfer Credit Card",
      "description": "0% APR for 18 months on balance transfers",
      "rationale": "Based on your $3,400 balance at 18.99% APR, this could save you $1,464 in interest over 18 months.",
      "eligibility": ["income_check_passed", "credit_score_qualified"],
      "savings_estimate": 1464.0,
      "disclaimer": "This is educational content, not financial advice..."
    }
  ],
  "generated_at": "2025-11-07T..."
}
```

**Epic 8 Usage:**
- Story 8.4 (Recommendations): Display cards with type badges, rationales, CTAs

**Alignment:** ✅ Perfect match. Includes educational content + partner offers with transparent rationales.

---

**4. Consent Endpoint (`POST /api/consent`, `GET /api/consent/{user_id}`):**
```json
// POST /api/consent request
{
  "user_id": "user_MASKED_042",
  "consent_given": true,
  "consent_version": "1.0"
}

// Response / GET response
{
  "user_id": "user_MASKED_042",
  "consent_status": "active",
  "consent_given_at": "2025-11-07T10:30:00Z",
  "consent_version": "1.0"
}
```

**Epic 8 Usage:**
- Story 8.1 (Onboarding): Call `POST /api/consent` when user checks consent box
- Story 8.6 (Settings): Show consent status, handle revocation

**Alignment:** ✅ Perfect match. Supports grant/revoke workflows.

---

## Frontend Stack Alignment

### Existing Frontend (Epic 6 - Operator Dashboard)

**Technology Stack:**
- ✅ React 18
- ✅ TypeScript
- ✅ Vite (dev server + build)
- ✅ TailwindCSS (styling)
- ✅ React Router (navigation)
- ✅ React Query (API data fetching/caching)

**Location:** `spendsense/ui/src/`

**Component Examples (from Epic 6):**
- `<UserSearch />` - Search with autocomplete
- `<TimeWindowToggle />` - 30d/180d/both selector
- `<SignalCard />` variants - Credit, Subscriptions, Savings, Income
- `<SignalComparison />` - Side-by-side metric comparison
- `<SignalExport />` - CSV/JSON export

**Epic 8 Reuse Potential:**
- ✅ TimeWindowToggle → Reuse in Story 8.2 (Dashboard Layout)
- ✅ SignalCard patterns → Adapt for Story 8.3 (Signal Exploration)
- ✅ Metric display patterns → Reuse for signal details
- ✅ React Query hooks (`useSignalData`) → Adapt for end-user context

**Alignment:** ✅ Epic 8 uses identical stack. Can reuse patterns and some components.

---

### Tailwind Theme Alignment

**Defined Theme (from `docs/ux/ux-design-specification.md`):**
```css
Primary: #0891b2 (Cyan-600)
Primary Hover: #0e7490 (Cyan-700)
Accent: #06b6d4 (Cyan-500)
Success: #10b981 (Emerald-500)
Warning: #f59e0b (Amber-500)
Error: #ef4444 (Red-500)
Background: #ecfeff (Cyan-50)
Surface: #ffffff (White)
Text Primary: #0f172a (Slate-900)
Text Muted: #64748b (Slate-500)
Border: #cffafe (Cyan-100)
```

**Current Implementation (from `spendsense/ui/src/index.css`):**
- Uses Tailwind base classes
- Has tooltip system already defined
- Font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'`

**Epic 8 Requirements:**
- Extend `tailwind.config.js` with "Balanced Calm" color palette
- Add spacing/shadow tokens if needed
- Maintain consistency with Epic 6 (operator dashboard)

**Alignment:** ✅ Compatible. Just need to extend Tailwind config with Epic 8 theme colors.

---

## UX Journey to Epic 8 Story Mapping

### Journey 1: Onboarding → Story 8.1 ✅

**UX Doc:** `docs/ux/ux-journey-1-onboarding.md` (31KB)

**Coverage:**
- Step 1: Welcome Screen → AC #1 in Story 8.1
- Step 2: Consent → AC #2 in Story 8.1
- Step 3: Processing → AC #3 in Story 8.1
- Step 4: Persona Reveal → AC #4 in Story 8.1
- Step 5: Dashboard Tour → AC #5 in Story 8.1

**Backend Needs:** ✅ All APIs exist (`POST /api/consent`, `GET /api/profile`)

---

### Journey 2: Signal Exploration → Story 8.3 ✅

**UX Doc:** `docs/ux/ux-journey-2-signal-exploration.md` (34KB)

**Coverage:**
- Step 1: Signal Card Selection → AC #1 in Story 8.3
- Step 2: Signal Detail View → AC #2-5 in Story 8.3 (4 signal types)
- Step 3: Contextual Chat → Links to Story 8.5
- Step 4: Deep Dive Actions → AC #7 (related recommendations)

**Backend Needs:** ✅ All APIs exist (`GET /api/signals/{user_id}/*`)

---

### Journey 3: Recommendation Flow → Story 8.4 ✅

**UX Doc:** `docs/ux/ux-journey-3-recommendation-flow.md` (9.6KB summary)

**Coverage:**
- Recommendation feed → AC #1-2 in Story 8.4
- Detail views → AC #3-5 in Story 8.4
- Rationales → AC #4 in Story 8.4
- Actions → AC #5 in Story 8.4

**Backend Needs:** ✅ All APIs exist (`GET /api/recommendations/{user_id}`)

---

### Journey 4: Chat Interaction → Story 8.5 ⚠️

**UX Doc:** `docs/ux/ux-journey-4-chat-interaction.md` (16KB)

**Coverage:**
- 5 conversation patterns → AC #4 in Story 8.5
- Context awareness → AC #5 in Story 8.5
- Quick replies → AC #7 in Story 8.5
- Guardrails → AC #8 in Story 8.5

**Backend Needs:** ❌ NEW - Requires `POST /api/chat/message`, `GET /api/chat/history/{user_id}`

**Implementation Note:** Story 8.5 is the only story requiring new backend work (LLM integration).

---

## Gap Analysis

### What Epic 8 Requires That Doesn't Exist Yet

**1. Chat Backend (Story 8.5 only)**

**Required Implementation:**
```python
# New endpoints in spendsense/api/main.py

@app.post("/api/chat/message")
async def send_chat_message(
    user_id: str,
    message: str,
    context: dict  # {current_screen, persona, signals}
):
    # 1. Load user context (persona, signals, recommendations)
    # 2. Build LLM prompt with context + guardrails
    # 3. Call LLM (OpenAI, Anthropic, or local model)
    # 4. Validate response for guardrails (no financial advice)
    # 5. Store message in chat history
    # 6. Return AI response + quick reply buttons
    return {
        "message": "Your credit utilization is at 68%...",
        "quick_replies": ["Show strategies", "How long?", "View breakdown"]
    }

@app.get("/api/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    # Return last N messages from database
    return {
        "messages": [
            {"sender": "user", "content": "Why is my utilization high?", "timestamp": "..."},
            {"sender": "assistant", "content": "Your Visa ****4523...", "timestamp": "..."}
        ]
    }
```

**Estimated Effort:** 2-3 weeks (LLM integration, prompt engineering, guardrails, storage)

**Dependencies:**
- LLM API key (OpenAI, Anthropic, or local model setup)
- Chat message storage (new DB table or extend existing)
- Prompt templates for 5 conversation patterns

**Risk:** Medium - LLM responses need careful guardrail testing to prevent financial advice violations.

---

**2. End-User UI Components (All of Epic 8)**

**What Doesn't Exist:**
- No end-user onboarding flow (Story 8.1)
- No end-user dashboard layout (Story 8.2)
- No end-user signal exploration UI (Story 8.3)
- No end-user recommendation feed (Story 8.4)
- No chat interface (Story 8.5)
- No end-user settings page (Story 8.6)

**What Does Exist:**
- ✅ Operator dashboard (Epic 6) - Separate interface for staff
- ✅ Operator signal views - Similar patterns can be adapted
- ✅ React component patterns - Can be reused

**Key Difference:**
- **Epic 6** = Operator view (search users, review signals, approve recommendations)
- **Epic 8** = End-user view (own data only, educational focus, conversational guidance)

**Alignment:** ✅ No overlap. Both UIs consume same backend APIs but serve different audiences.

---

## Design System Alignment

### Epic 6 (Operator) vs Epic 8 (End-User) UI Differences

| Aspect | Epic 6 (Operator) | Epic 8 (End-User) |
|---|---|---|
| **Audience** | Bank staff, compliance officers | Consumers (bank customers) |
| **Navigation** | User search → Select user → View data | Personal dashboard → Explore own data |
| **Tone** | Professional, analytical | Supportive, educational |
| **Layout** | Data tables, metrics, export tools | Cards, charts, conversational guidance |
| **Auth** | JWT with RBAC (viewer/reviewer/admin) | Session-based (user_id from bank SSO) |
| **Features** | Review queue, override decisions, audit logs | Chat coach, recommendations, onboarding |
| **Color Theme** | Default Tailwind (blue-600) | "Balanced Calm" (cyan-600 #0891b2) |

**Alignment:** ✅ Separate UIs with distinct purposes. No conflicts.

---

### Responsive Design Requirements

**Epic 8 Breakpoints:**
- Mobile: <768px (bottom tab navigation)
- Tablet: 768-1023px (floating chat widget)
- Desktop: ≥1024px (split-screen with persistent chat sidebar)

**Epic 6 Breakpoints:**
- Desktop-focused (optimized for 1024px+)
- Tablet support (responsive grid)
- Mobile functional but not primary target

**Alignment:** ✅ Epic 8 is mobile-first (consumer-facing). Epic 6 is desktop-first (internal tool). No conflicts.

---

## Dependency Resolution

### Epic 8 Story Dependencies

**Recommended Sequence:**
1. **Story 8.1 (Onboarding)** → No dependencies, start first
2. **Story 8.2 (Dashboard Layout)** → After 8.1 (needs onboarding to complete)
3. **Stories 8.3, 8.4, 8.6** → After 8.2 (parallel work possible)
4. **Story 8.5 (Chat)** → Can be done in parallel or last (requires new backend)

**Critical Path:**
- 8.1 → 8.2 → (8.3, 8.4, 8.6 in parallel) → 8.5

**Parallel Work Opportunities:**
- Frontend dev team: Stories 8.3, 8.4, 8.6 (after 8.2 done)
- Backend dev team: Story 8.5 backend (can start anytime)

---

### Backend Dependency Check

| Epic 8 Story | Backend Dependency | Status |
|---|---|---|
| 8.1 Onboarding | Epics 1, 2, 3 (profiles, signals, personas) | ✅ Done |
| | Epic 5 (consent management) | ✅ Done |
| 8.2 Dashboard | Epic 3 (persona assignment) | ✅ Done |
| | Epic 2 (signal detection) | ✅ Done |
| 8.3 Signals | Epic 2 (all 4 signal types) | ✅ Done |
| 8.4 Recommendations | Epic 4 (rec engine, content catalog) | ✅ Done |
| | Epic 5 (guardrails, rationales) | ✅ Done |
| 8.5 Chat | **NEW: LLM integration** | ❌ Not started |
| 8.6 Settings | Epic 5 (consent management) | ✅ Done |

**Blocker Analysis:**
- Stories 8.1-8.4, 8.6: ✅ **READY** - All backend dependencies satisfied
- Story 8.5: ⚠️ **REQUIRES BACKEND** - New chat endpoints needed

---

## Risk Assessment

### High Risk: None ✅

### Medium Risk: 1 item

**1. Chat Backend Implementation (Story 8.5)**
- **Risk:** LLM integration complexity, guardrail enforcement, cost
- **Mitigation:**
  - Start with mock chat backend for frontend development
  - Test guardrails extensively before production
  - Consider starting with rule-based responses before full LLM
  - Budget for LLM API costs (OpenAI/Anthropic) or deploy local model

### Low Risk: 2 items

**2. Mobile Responsiveness**
- **Risk:** Complex responsive layouts (split-screen → bottom tabs)
- **Mitigation:** Use Tailwind responsive utilities, test on real devices early

**3. Chart/Visualization Libraries**
- **Risk:** Trend charts for signals need clean implementation
- **Mitigation:** Use established libraries (Recharts, Chart.js), start simple

---

## Success Criteria for Epic 8

**Functional Completeness:**
- ✅ All 6 stories implemented with acceptance criteria met
- ✅ All UX journeys (1-4) functional end-to-end
- ✅ Responsive on mobile, tablet, desktop
- ✅ Accessible (WCAG AA compliance)

**Integration:**
- ✅ Consumes all 10 existing backend APIs correctly
- ✅ Chat backend (Story 8.5) integrated with LLM
- ✅ No conflicts with Epic 6 (operator dashboard)

**User Experience:**
- ✅ Onboarding completion rate >80%
- ✅ Signal exploration engagement >60%
- ✅ Recommendation views >50%
- ✅ Chat interaction >40%
- ✅ Average session time >5 minutes

**Technical:**
- ✅ Page load time <2 seconds
- ✅ API response time <500ms
- ✅ Mobile performance (60fps scrolling)
- ✅ No console errors

---

## Conclusion

### Epic 8 Readiness: ✅ ALIGNED AND READY

**Summary:**
1. **Backend APIs:** 10/12 endpoints exist. Only chat endpoints (Story 8.5) need new implementation.
2. **Data Models:** All existing APIs return data matching Epic 8 requirements exactly.
3. **Frontend Stack:** Identical to Epic 6. Can reuse patterns and some components.
4. **UX Journeys:** All 4 journeys map perfectly to Epic 8 stories.
5. **No Conflicts:** Epic 8 complements Epic 6 (different audiences, no overlap).
6. **Design System:** "Balanced Calm" theme fully specified, just needs Tailwind config extension.

**Recommended Action:**
✅ **Proceed with Epic 8 implementation**

**Suggested Story Order:**
1. Story 8.1 (Onboarding) - 1-2 weeks
2. Story 8.2 (Dashboard Layout) - 1 week
3. Stories 8.3, 8.4, 8.6 (Signals, Recs, Settings) - 3-4 weeks (parallel)
4. Story 8.5 (Chat) - 2-3 weeks (requires backend work)

**Total Estimate:** 8-11 weeks for full Epic 8 completion

---

## Next Steps

1. ✅ **Epic 8 created** - `docs/prd/epic-8-end-user-dashboard-experience.md`
2. ✅ **Sprint status updated** - Epic 8 stories added to `docs/sprint-status.yaml`
3. ⏭️ **Create story files** - Draft individual story .md files in `docs/stories/`
4. ⏭️ **Create story context** - Link stories to UX journeys and API specs
5. ⏭️ **Start implementation** - Begin with Story 8.1 (Onboarding Flow)

---

**End of Alignment Check**
