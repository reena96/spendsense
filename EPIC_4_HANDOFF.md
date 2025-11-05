# Epic 4: Personalized Recommendations - Handoff Document

**Date**: 2025-11-05
**Status**: Ready to Start
**Prerequisites**: Epic 3 Complete ✅
**Estimated Effort**: 3-4 weeks

---

## Executive Summary

**Epic 4** builds personalized financial recommendations powered by the persona assignments from Epic 3. Each user will receive tailored educational content, actionable insights, and partner offers based on their assigned persona and behavioral signals.

**Key Deliverable**: Users see recommendations that address their specific financial situation (high utilization → debt payoff strategies, low savings → emergency fund building, etc.)

---

## What's Complete (Epic 3 Foundation)

### ✅ Persona Assignment System
- **6 personas** defined with priorities, criteria, and educational focus areas
- **91 tests passing** across all persona assignment functionality
- **API endpoint**: GET `/api/profile/{user_id}` returns complete persona assignments
- **Beautiful UI**: Interactive Persona Assignment tab showing full audit trail
- **100 users** with assignments for both 30d and 180d windows
- **Database**: Complete audit trail stored in `persona_assignments` table

### ✅ Behavioral Signals (Epic 2)
- Subscription detection and analysis
- Savings and emergency fund metrics
- Credit utilization tracking
- Income pattern analysis
- All signals available via API: GET `/api/signals/{user_id}`

### ✅ Infrastructure
- FastAPI backend with database integration
- Pydantic models for type safety
- Comprehensive test framework
- Interactive web UI

---

## Epic 4 Overview

**Goal**: Generate personalized financial recommendations based on persona assignments and behavioral signals.

### User Story
> As a **user with assigned persona**,
> I want **personalized financial recommendations relevant to my situation**,
> so that **I receive actionable guidance to improve my financial health**.

---

## Epic 4 Stories (From PRD)

### Story 4.1: Recommendation Content Library
**Effort**: 3-4 days

**Goal**: Build structured content library with educational recommendations for each persona.

**Deliverables**:
- Content database/YAML file with recommendations per persona
- Recommendation categories: Education, Actions, Tips, Insights
- Priority ordering (most important recommendations first)
- Metadata: difficulty level, time commitment, estimated impact

**Example Structure**:
```yaml
recommendations:
  high_utilization:
    - id: "debt_payoff_avalanche"
      category: "education"
      title: "Debt Payoff: Avalanche Method"
      description: "Pay off highest-interest debt first to minimize interest costs"
      priority: 1
      difficulty: "intermediate"
      time_commitment: "ongoing"
      estimated_impact: "high"
      content_url: "/content/debt-avalanche"

    - id: "reduce_credit_utilization"
      category: "action"
      title: "Lower Your Credit Utilization"
      description: "Pay down balances to under 30% to improve credit score"
      priority: 2
      ...
```

**Acceptance Criteria**:
- [ ] Content library created with 5-10 recommendations per persona
- [ ] Recommendations categorized (education, action, tip, insight)
- [ ] Priority ordering defined
- [ ] Metadata complete (difficulty, time, impact)
- [ ] Content accessible via API or module

---

### Story 4.2: Recommendation Engine
**Effort**: 5-7 days

**Goal**: Build engine that selects and personalizes recommendations based on persona and signals.

**Deliverables**:
- `RecommendationEngine` class that generates recommendations
- Personalization using behavioral signals (not just persona)
- Filtering logic (exclude irrelevant recommendations)
- Ranking algorithm (most relevant first)
- A/B test support (optional: multiple recommendation strategies)

**Example Logic**:
```python
def generate_recommendations(user_id: str, persona_assignment: PersonaAssignment,
                            behavioral_signals: BehavioralSummary) -> List[Recommendation]:
    # 1. Get base recommendations for assigned persona
    base_recommendations = content_library.get_by_persona(persona_assignment.persona_id)

    # 2. Filter based on user context
    # Example: If user already has emergency fund, skip emergency fund recommendations
    filtered = filter_by_user_context(base_recommendations, behavioral_signals)

    # 3. Personalize with specific signal values
    # Example: "You're at 65% utilization" instead of generic "high utilization"
    personalized = personalize_with_signals(filtered, behavioral_signals)

    # 4. Rank by relevance and priority
    ranked = rank_recommendations(personalized, behavioral_signals)

    return ranked[:10]  # Top 10
```

**Acceptance Criteria**:
- [ ] Engine generates 5-10 personalized recommendations per user
- [ ] Recommendations filtered based on user context
- [ ] Signal values inserted into recommendation text
- [ ] Ranking algorithm implemented (priority + relevance)
- [ ] Unit tests cover filtering and personalization logic
- [ ] Performance: <100ms to generate recommendations

---

### Story 4.3: Recommendation Storage & Tracking
**Effort**: 3-4 days

**Goal**: Store generated recommendations and track user interactions.

**Deliverables**:
- Database table: `recommendations`
- Database table: `recommendation_interactions` (views, clicks, dismissals)
- API endpoints:
  - GET `/api/recommendations/{user_id}` - Get current recommendations
  - POST `/api/recommendations/{recommendation_id}/view` - Track view
  - POST `/api/recommendations/{recommendation_id}/click` - Track click
  - POST `/api/recommendations/{recommendation_id}/dismiss` - Track dismissal
- Recommendation versioning (track changes over time)

**Database Schema**:
```sql
CREATE TABLE recommendations (
    recommendation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    persona_id TEXT NOT NULL,
    content_id TEXT NOT NULL,  -- Reference to content library
    generated_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    priority INTEGER,
    personalized_title TEXT,
    personalized_description TEXT,
    metadata JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE recommendation_interactions (
    interaction_id TEXT PRIMARY KEY,
    recommendation_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    interaction_type TEXT NOT NULL,  -- 'view', 'click', 'dismiss'
    interaction_at TIMESTAMP NOT NULL,
    metadata JSON,
    FOREIGN KEY (recommendation_id) REFERENCES recommendations(recommendation_id)
);
```

**Acceptance Criteria**:
- [ ] Recommendations stored in database with versioning
- [ ] API endpoints for retrieval and tracking
- [ ] Interaction tracking (view, click, dismiss)
- [ ] Unit tests for storage and retrieval
- [ ] Database indexes for performance

---

### Story 4.4: Recommendation UI Components
**Effort**: 4-5 days

**Goal**: Display personalized recommendations in web UI.

**Deliverables**:
- New "Recommendations" tab in dashboard
- Recommendation cards with:
  - Title and description
  - Category badge (Education, Action, Tip, Insight)
  - Priority/importance indicator
  - "Learn More" and "Dismiss" actions
- Filtering by category
- Sort by priority/relevance
- Real-time updates (when new recommendations generated)

**UI Design**:
```
┌─────────────────────────────────────────────┐
│ 💡 Your Personalized Recommendations       │
│                                              │
│ Based on: Low Savings (Priority 3)          │
│ Updated: 11/5/2025, 10:30 AM                │
├─────────────────────────────────────────────┤
│                                              │
│ ┌──────────────────────────────┐            │
│ │ 🎯 Build Your Emergency Fund  │ EDUCATION  │
│ │                               │            │
│ │ You currently have 0 months   │            │
│ │ of expenses saved. Start with │            │
│ │ a goal of $1,000.             │            │
│ │                               │            │
│ │ [Learn More]  [Dismiss]       │            │
│ └──────────────────────────────┘            │
│                                              │
│ ┌──────────────────────────────┐            │
│ │ 💰 Automate Your Savings      │ ACTION     │
│ │                               │            │
│ │ Set up automatic transfers of │            │
│ │ $50/week to savings.          │            │
│ │                               │            │
│ │ [Learn More]  [Dismiss]       │            │
│ └──────────────────────────────┘            │
└─────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] Recommendations tab added to dashboard
- [ ] Recommendation cards display with all metadata
- [ ] Category filtering working
- [ ] Sort by priority/relevance
- [ ] View tracking on card display
- [ ] Click tracking on "Learn More"
- [ ] Dismiss functionality
- [ ] Responsive design
- [ ] Loading states and error handling

---

### Story 4.5: Partner Offers Integration (Optional)
**Effort**: 3-4 days

**Goal**: Integrate partner offers relevant to user's persona.

**Deliverables**:
- Partner offer content library
- Partner offer recommendation logic
- Disclosure/disclaimer UI
- Tracking for partner offer views/clicks
- Compliance with advertising guidelines

**Example Partner Offers**:
- High Utilization → Balance transfer credit cards
- Low Savings → High-yield savings accounts
- Subscription Heavy → Subscription management tools
- Cash Flow Optimizer → Investment platforms (robo-advisors)

**Acceptance Criteria**:
- [ ] Partner offers defined in content library
- [ ] Mapped to relevant personas
- [ ] Displayed separately from educational content
- [ ] Clear disclaimers and disclosures
- [ ] Opt-out mechanism
- [ ] Tracking for attribution/revenue share

---

## Technical Architecture

### Recommendation Flow

```
User visits Dashboard
    ↓
UI requests recommendations: GET /api/recommendations/{user_id}
    ↓
API checks cache (Redis/memory)
    ↓ (if miss)
Recommendation Engine generates:
    1. Load persona assignment (Epic 3)
    2. Load behavioral signals (Epic 2)
    3. Get base content for persona
    4. Filter based on user context
    5. Personalize with signal values
    6. Rank by relevance
    7. Store in database
    8. Return to API
    ↓
API returns recommendations to UI
    ↓
UI displays cards
    ↓
User interacts (view/click/dismiss)
    ↓
Tracking logged to database
```

### Module Structure

```
spendsense/
├── recommendations/
│   ├── __init__.py
│   ├── content_library.py      # Story 4.1 - Content definitions
│   ├── engine.py                # Story 4.2 - Generation logic
│   ├── personalizer.py          # Story 4.2 - Personalization
│   ├── ranker.py                # Story 4.2 - Ranking algorithm
│   ├── storage.py               # Story 4.3 - Database operations
│   └── models.py                # Pydantic models
│
├── api/
│   └── main.py                  # Story 4.3 & 4.4 - API endpoints
│
├── config/
│   └── recommendations.yaml     # Story 4.1 - Content library
│
└── ingestion/
    └── database_writer.py       # Story 4.3 - Add recommendation tables

tests/
├── test_content_library.py
├── test_recommendation_engine.py
├── test_recommendation_storage.py
└── test_recommendation_api.py
```

---

## Data Requirements

### Inputs (From Previous Epics)

**From Epic 3: Persona Assignment**
```python
{
  "user_id": "user_MASKED_000",
  "assignments": {
    "30d": {
      "assigned_persona_id": "low_savings",
      "priority": 3,
      "all_qualifying_personas": ["low_savings", "subscription_heavy"]
    }
  }
}
```

**From Epic 2: Behavioral Signals**
```python
{
  "user_id": "user_MASKED_000",
  "subscriptions": {
    "30d": {
      "subscription_count": 23,
      "subscription_share": 0.827
    }
  },
  "savings": {
    "30d": {
      "emergency_fund_months": 0.0,
      "total_savings_balance": 0.0
    }
  },
  "credit": {
    "30d": {
      "aggregate_utilization": 0.005,
      "high_utilization_count": 0
    }
  },
  "income": {
    "30d": {
      "total_income": 2250.0,
      "payment_frequency": "biweekly"
    }
  }
}
```

### Outputs (New in Epic 4)

**Recommendation Object**
```python
{
  "recommendation_id": "rec_uuid",
  "user_id": "user_MASKED_000",
  "persona_id": "low_savings",
  "title": "Build Your Emergency Fund",
  "description": "You currently have 0 months of expenses saved. Start with a goal of $1,000.",
  "category": "education",
  "priority": 1,
  "difficulty": "beginner",
  "time_commitment": "ongoing",
  "estimated_impact": "high",
  "content_url": "/content/emergency-fund-101",
  "generated_at": "2025-11-05T10:30:00Z",
  "personalized_data": {
    "current_savings": 0.0,
    "monthly_expenses": 3894.32,
    "recommended_first_goal": 1000.0
  }
}
```

---

## Testing Strategy

### Unit Tests
- Content library loading and validation
- Recommendation engine filtering logic
- Personalization logic (signal substitution)
- Ranking algorithm
- Database operations
- API endpoint responses

### Integration Tests
- End-to-end recommendation generation
- Persona assignment → Behavioral signals → Recommendations flow
- Recommendation storage and retrieval
- Interaction tracking

### UI Tests
- Recommendation cards display correctly
- Filtering and sorting work
- Interaction tracking fires correctly
- Error states handled gracefully

**Target**: 80+ tests covering all recommendation logic

---

## Performance Considerations

### Caching Strategy
- Cache recommendations per user (TTL: 24 hours)
- Invalidate cache when:
  - New persona assignment generated
  - Behavioral signals updated
  - User dismisses recommendation

### Database Optimization
- Index on `recommendations.user_id`
- Index on `recommendations.generated_at`
- Index on `recommendation_interactions.user_id`
- Consider partitioning by date for interactions table

### Generation Performance
- **Target**: <100ms to generate recommendations
- **Strategy**: Pre-compute recommendations nightly for all users
- **Fallback**: Generate on-demand if cache miss

---

## Dependencies

### Internal Dependencies (Complete)
- ✅ Epic 2: Behavioral Signal Detection
- ✅ Epic 3: Persona Assignment System
- ✅ Database infrastructure
- ✅ API framework (FastAPI)
- ✅ UI framework (HTML/CSS/JS)

### External Dependencies (May Need)
- Content management system (or YAML file for MVP)
- A/B testing framework (optional)
- Analytics tracking (optional)
- Partner API integrations (Story 4.5)

### Python Libraries (May Need)
```python
# requirements.txt additions
jinja2>=3.1.0          # Template engine for personalization
markdown>=3.5.0        # Render markdown content
bleach>=6.1.0          # Sanitize user-generated content (if allowing feedback)
redis>=5.0.0           # Caching (optional)
```

---

## Known Risks & Mitigation

### Risk 1: Content Quality
**Risk**: Generic recommendations feel impersonal
**Mitigation**:
- Use specific signal values in recommendation text
- A/B test different messaging
- Iterate based on user feedback

### Risk 2: Recommendation Staleness
**Risk**: Recommendations become outdated as user behavior changes
**Mitigation**:
- Regenerate recommendations when persona changes
- TTL on cached recommendations (24 hours)
- Show "Updated: [timestamp]" in UI

### Risk 3: Content Overload
**Risk**: Too many recommendations overwhelm users
**Mitigation**:
- Limit to top 5-10 recommendations
- Prioritize ruthlessly (most impactful first)
- Allow dismissal to reduce clutter

### Risk 4: Partner Offer Compliance
**Risk**: Legal/compliance issues with partner offers
**Mitigation**:
- Clear disclaimers
- Separate from educational content
- Opt-out mechanism
- Legal review before launch (Story 4.5)

---

## Success Metrics

### Engagement Metrics
- **Recommendation View Rate**: % of users who view recommendations tab
- **Click-Through Rate**: % of recommendations clicked
- **Dismissal Rate**: % of recommendations dismissed (lower is better)
- **Time on Page**: Average time spent reading recommendations

### Quality Metrics
- **Relevance Score**: User feedback on recommendation quality (survey)
- **Action Rate**: % of users who take recommended action
- **Return Rate**: % of users who come back to recommendations

### Business Metrics
- **Partner Offer CTR**: Click-through rate on partner offers
- **Conversion Rate**: % of clicks that result in sign-ups/purchases
- **Revenue Attribution**: Revenue generated from partner offers

**Target**: 60%+ view rate, 20%+ CTR, <10% dismissal rate

---

## User Stories for Testing

### Story 1: High Utilization User
**Persona**: High Credit Utilization (Priority 1)
**Signals**: 65% credit utilization, $8,000 balance, 18% APR
**Expected Recommendations**:
1. "Pay down high-interest debt first (Avalanche method)"
2. "Consider balance transfer card (0% APR for 18 months)"
3. "Lower utilization to under 30% to improve credit score"
4. "Create debt payoff plan with calculator"

### Story 2: Low Savings User
**Persona**: Low Savings (Priority 3)
**Signals**: $0 savings, $3,900/month expenses
**Expected Recommendations**:
1. "Build emergency fund: Start with $1,000 goal"
2. "Automate savings: Set up $50/week transfer"
3. "Find extra money: Review your subscriptions (82% of spending)"
4. "Open high-yield savings account (5% APY)"

### Story 3: Subscription Heavy User
**Persona**: Subscription Heavy (Priority 4)
**Signals**: 23 subscriptions, 82% of spending
**Expected Recommendations**:
1. "Audit your subscriptions: You have 23 active subscriptions"
2. "Cancel unused services: Save $200+/month"
3. "Try subscription manager tool"
4. "Set spending alerts for recurring charges"

### Story 4: Cash Flow Optimizer
**Persona**: Cash Flow Optimizer (Priority 5)
**Signals**: 8 months emergency fund, 5% utilization, stable income
**Expected Recommendations**:
1. "Start investing: You're ready for robo-advisor"
2. "Optimize idle cash: Move to HYSA (5% vs 0.01%)"
3. "Set financial goals: Home, retirement, etc."
4. "Learn about index funds and diversification"

---

## Out of Scope (For Later Epics)

### Not in Epic 4:
- ❌ Recommendation explanations ("Why this recommendation?")
- ❌ User feedback on recommendations ("Was this helpful?")
- ❌ Historical recommendation tracking over time
- ❌ Recommendation effectiveness measurement
- ❌ Multi-user household recommendations
- ❌ Recommendation scheduling (send at optimal time)
- ❌ Push notifications for new recommendations
- ❌ Gamification (badges, streaks for completing actions)

These features may be added in Epic 5 (Guardrails) or Epic 6 (Operator View).

---

## Getting Started

### Pre-Work Checklist

Before starting Epic 4:

- [ ] **Review Epic 3 completion** (`EPIC_3_COMPLETE.md`)
- [ ] **Understand persona system** (read `personas.yaml`, test API)
- [ ] **Explore behavioral signals** (test `/api/signals/{user_id}`)
- [ ] **Review PRD** (`docs/prd/epic-4-recommendations.md`)
- [ ] **Set up test environment** (verify all 91 Epic 3 tests pass)

### Recommended Story Order

1. **Start with Story 4.1** (Content Library) - Foundation for everything
2. **Then Story 4.2** (Recommendation Engine) - Core logic
3. **Then Story 4.3** (Storage & Tracking) - Persistence layer
4. **Then Story 4.4** (UI Components) - User-facing features
5. **Optional: Story 4.5** (Partner Offers) - Revenue opportunities

**Parallel Work Possible**:
- Story 4.1 and 4.3 can be done in parallel (content + database)
- Story 4.2 and 4.4 depend on 4.1 (need content first)

---

## Reference Links

### Documentation
- Epic 3 Completion: `/EPIC_3_COMPLETE.md`
- Epic 3 Demo Guide: `/EPIC_3_DEMO_CHECKLIST.md`
- Testing Guide: `/TESTING_GUIDE.md`
- Architecture: `/docs/architecture.md`

### Code References
- Persona Registry: `spendsense/personas/registry.py`
- Persona Matcher: `spendsense/personas/matcher.py`
- Behavioral Summary: `spendsense/features/behavioral_summary.py`
- API Endpoints: `spendsense/api/main.py`

### API Endpoints (Available Now)
- GET `/api/profile/{user_id}` - Persona assignments
- GET `/api/signals/{user_id}` - Behavioral signals
- GET `/api/personas` - Persona definitions

---

## Questions for Planning

Before starting implementation, clarify:

1. **Content Authoring**: Who writes recommendation content? PM? Content team? AI-generated?
2. **Content Format**: Markdown? HTML? Plain text? Rich media?
3. **Partner Offers**: Which partners? Revenue share model? Legal approval needed?
4. **A/B Testing**: Required for MVP or later? If now, which framework?
5. **Analytics**: Google Analytics? Custom tracking? Privacy considerations?
6. **Caching**: Redis available? Or in-memory cache sufficient?
7. **Recommendation Refresh**: Daily? Weekly? On-demand?
8. **Content Updates**: How to update recommendations without code deploy?

---

## Current System State

### What's Working (Epic 3)
- ✅ 100 users with persona assignments
- ✅ API returning complete persona data
- ✅ Beautiful UI showing assignments
- ✅ 91 tests passing
- ✅ Database with full audit trail

### What's Needed (Epic 4)
- 🔨 Recommendation content library
- 🔨 Recommendation generation engine
- 🔨 Database tables for recommendations
- 🔨 API endpoints for recommendations
- 🔨 UI components for displaying recommendations

---

## Timeline Estimate

**Total Epic 4 Effort**: 3-4 weeks (assuming 1 developer, full-time)

| Story | Effort | Cumulative |
|-------|--------|------------|
| 4.1: Content Library | 3-4 days | Week 1 |
| 4.2: Recommendation Engine | 5-7 days | Week 1-2 |
| 4.3: Storage & Tracking | 3-4 days | Week 2-3 |
| 4.4: UI Components | 4-5 days | Week 3 |
| 4.5: Partner Offers (Optional) | 3-4 days | Week 4 |
| **Testing & QA** | 2-3 days | Week 4 |
| **Documentation** | 1-2 days | Week 4 |

**Deliverable**: Fully functional recommendation system with UI, ready for user testing

---

## Handoff Checklist

When starting Epic 4, developer should:

- [ ] Read this entire handoff document
- [ ] Review Epic 3 completion doc
- [ ] Test Epic 3 UI (verify it works)
- [ ] Run Epic 3 tests (verify 91 passing)
- [ ] Read Epic 4 PRD (if exists)
- [ ] Review persona definitions (`personas.yaml`)
- [ ] Test persona and signal APIs
- [ ] Set up development environment
- [ ] Create Epic 4 branch
- [ ] Create Story 4.1 markdown file

---

**Handoff Date**: 2025-11-05
**Handed Off By**: Claude (Epic 3 Implementation Team)
**Handed Off To**: Next Developer (Epic 4 Implementation Team)

**Status**: 🚀 **READY TO START EPIC 4!**

All prerequisites complete. System is stable and well-tested. Foundation is solid for building personalized recommendations!

---

## Appendix: Example Recommendations by Persona

### High Utilization (Priority 1)
1. Understand how credit utilization affects your score
2. Pay down highest-interest debt first (Avalanche method)
3. Consider balance transfer to 0% APR card
4. Create debt payoff timeline calculator
5. Set up payment reminders to avoid late fees

### Irregular Income (Priority 2)
1. Create variable income budget (percentage-based)
2. Build larger emergency fund (6+ months)
3. Smooth income with income averaging strategy
4. Set aside taxes for 1099 income
5. Explore gig economy financial planning tools

### Low Savings (Priority 3)
1. Build emergency fund: Start with $1,000
2. Automate savings: Set up recurring transfers
3. Find extra money: Review subscription spending
4. Open high-yield savings account
5. Use "pay yourself first" method

### Subscription Heavy (Priority 4)
1. Audit your subscriptions (you have 23 active)
2. Cancel unused services to save $200+/month
3. Try subscription management tool
4. Negotiate better rates on current services
5. Set spending alerts for recurring charges

### Cash Flow Optimizer (Priority 5)
1. Start investing with robo-advisor
2. Optimize idle cash: HYSA vs checking
3. Set long-term financial goals
4. Learn about index funds and diversification
5. Consider tax-advantaged accounts (IRA, HSA)

### Young Professional (Priority 6)
1. Credit 101: How credit scores work
2. Open your first credit card (secured or starter)
3. Budgeting fundamentals for beginners
4. Understand different account types
5. Build good financial habits early
