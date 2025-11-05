# Story 4.2: Recommendation Engine

**Epic**: 4 - Personalized Recommendations
**Story**: 4.2
**Effort**: 5-7 days
**Status**: In Progress
**Dependencies**: Story 4.1 (Content Library), Epic 2 (Behavioral Signals), Epic 3 (Persona Assignment)

---

## Goal

Build an intelligent recommendation engine that generates personalized financial recommendations by combining persona assignments, behavioral signals, and curated content from the content library.

---

## User Story

> As a **user with assigned persona and behavioral signals**,
> I want **personalized recommendations that reflect my specific financial situation**,
> so that **I receive actionable, relevant guidance tailored to my unique circumstances** (not generic advice).

---

## Context

- Story 4.1 complete: 44 curated recommendations in content library
- Epic 3 complete: Persona assignments with match evidence
- Epic 2 complete: Behavioral signals (subscriptions, savings, credit, income)
- Need to bridge: Static content → Dynamic, personalized recommendations

**Key Insight:** Same persona can have different needs. For example:
- Two "Low Savings" users may have different subscription patterns
- Need to personalize based on **actual signal values**, not just persona ID

---

## Requirements

### Functional Requirements

1. **Recommendation Generation Pipeline**
   - Input: user_id, persona_assignment, behavioral_signals
   - Output: List of personalized Recommended items (5-10)
   - Steps: Load → Filter → Personalize → Rank → Return top N

2. **Filtering Logic**
   - **Context-aware filtering**: Skip irrelevant recommendations
   - Example: If user has 6+ months emergency fund, skip "build emergency fund" recs
   - Example: If user has no credit cards, skip credit utilization recs
   - Use behavioral signals to determine relevance

3. **Personalization Engine**
   - **Template substitution**: Replace placeholders with actual signal values
   - Example: "{credit_max_utilization_pct}" → "65"
   - Example: "{subscription_count}" → "23"
   - **Fallback**: If signal missing or no template, use original description
   - **Formatting**: Numbers formatted appropriately (%, $, etc.)

4. **Ranking Algorithm**
   - **Multi-factor ranking**:
     - Priority (from content library): 1=highest urgency
     - Relevance score: How well rec matches user's signals
     - Impact: High impact recommendations ranked higher
   - **Output**: Sorted list with most valuable recommendations first

5. **Performance**
   - Generate recommendations in <100ms
   - Cache-friendly design
   - Efficient signal lookups

### Non-Functional Requirements

1. **Extensibility**
   - Easy to add new filtering rules
   - Easy to modify ranking algorithm
   - Support A/B testing different strategies

2. **Observability**
   - Log why recommendations were filtered/included
   - Track personalization success/failures
   - Debug-friendly

3. **Type Safety**
   - Pydantic models for inputs/outputs
   - Type hints throughout
   - Validation

---

## Technical Design

### Architecture

```
User Request
    ↓
RecommendationEngine.generate()
    ↓
1. Load persona's base recommendations (ContentLibrary)
    ↓
2. Filter by user context (FilterEngine)
    ├─ Check signal availability
    ├─ Apply relevance rules
    └─ Remove redundant recs
    ↓
3. Personalize with signals (PersonalizationEngine)
    ├─ Parse templates
    ├─ Substitute signal values
    ├─ Format numbers
    └─ Fallback to original if needed
    ↓
4. Rank by relevance (RankingEngine)
    ├─ Calculate relevance scores
    ├─ Combine with priority/impact
    └─ Sort descending
    ↓
5. Return top N (default 10)
```

### Module Structure

```
spendsense/recommendations/
├── __init__.py
├── models.py                  # Story 4.1 (existing)
├── content_library.py         # Story 4.1 (existing)
├── engine.py                  # NEW - Main engine orchestration
├── filtering.py               # NEW - Context-based filtering
├── personalization.py         # NEW - Template substitution
├── ranking.py                 # NEW - Relevance scoring
└── generated_models.py        # NEW - Generated recommendation model

tests/
├── test_content_library.py    # Story 4.1 (existing)
├── test_recommendation_engine.py      # NEW - Engine tests
├── test_filtering.py                  # NEW - Filtering tests
├── test_personalization.py            # NEW - Personalization tests
└── test_ranking.py                    # NEW - Ranking tests
```

### Data Models

```python
class PersonalizedRecommendation(BaseModel):
    """Personalized recommendation for a specific user."""
    # Original recommendation fields
    recommendation_id: str
    category: RecommendationCategory
    title: str
    description: str
    original_description: str  # Before personalization
    priority: int
    difficulty: DifficultyLevel
    time_commitment: TimeCommitment
    estimated_impact: EstimatedImpact
    content_url: Optional[str]

    # Personalization metadata
    personalized: bool  # Was template substitution performed?
    substitutions: Dict[str, Any]  # Signal values used
    relevance_score: float  # 0.0-1.0
    rank: int  # Final ranking position (1=top)

    # User context
    user_id: str
    persona_id: str
    generated_at: datetime

class RecommendationRequest(BaseModel):
    """Request for generating recommendations."""
    user_id: str
    persona_id: str
    time_window: str  # "30d" or "180d"
    limit: int = 10
    include_metadata: bool = False

class RecommendationResponse(BaseModel):
    """Response with generated recommendations."""
    user_id: str
    persona_id: str
    time_window: str
    recommendations: List[PersonalizedRecommendation]
    generated_at: datetime
    generation_time_ms: float
```

---

## Implementation Plan

### Phase 1: Core Engine (2-3 hours)
1. Create `generated_models.py` with PersonalizedRecommendation, Request, Response
2. Create `engine.py` with RecommendationEngine class
3. Implement basic pipeline: load → return (no filtering/personalization yet)
4. Test: Get base recommendations for a persona

### Phase 2: Filtering Logic (3-4 hours)
1. Create `filtering.py` with FilterEngine class
2. Implement filtering rules:
   - Emergency fund: Skip if savings_emergency_fund_months >= 3.0
   - Credit recommendations: Skip if no credit accounts
   - Subscription recommendations: Skip if subscription_count < 5
   - Income recommendations: Only if income_payment_frequency is irregular
3. Add `filter_reason` logging
4. Test: Verify correct recommendations filtered

### Phase 3: Personalization Engine (4-5 hours)
1. Create `personalization.py` with PersonalizationEngine class
2. Implement template parser:
   - Regex to find `{signal_name}` placeholders
   - Map signal names to BehavioralSummary fields
   - Handle nested fields (e.g., `{savings_30d_emergency_fund_months}`)
3. Implement formatters:
   - Percentages: `{credit_max_utilization_pct}` → "65%"
   - Currency: `{savings_total_balance}` → "$1,234.56"
   - Counts: `{subscription_count}` → "23"
4. Implement fallback logic
5. Track substitutions for metadata
6. Test: Template substitution correctness

### Phase 4: Ranking Algorithm (2-3 hours)
1. Create `ranking.py` with RankingEngine class
2. Implement relevance scoring:
   - Base score from content priority (1-10)
   - Boost for high impact (+0.2)
   - Boost for personalized (+0.1)
   - Boost for quick wins (+0.1)
   - Signal-based relevance (custom rules per persona)
3. Sort by combined score
4. Test: Verify correct ranking

### Phase 5: Integration & Testing (4-6 hours)
1. Wire all components together in engine.py
2. Create comprehensive tests (20-25 tests):
   - Engine orchestration tests
   - Filtering tests (per rule)
   - Personalization tests (per template type)
   - Ranking tests (score calculation)
   - End-to-end tests (with real data)
3. Performance testing (<100ms requirement)
4. Edge case testing (missing signals, no templates, etc.)

### Phase 6: Documentation & Review (1-2 hours)
1. Update docstrings
2. Create usage examples
3. Document filtering/ranking rules
4. Code review

**Total Estimated Time**: 16-23 hours (~2-3 days focused work)

---

## Acceptance Criteria

- [ ] **AC1**: RecommendationEngine.generate() returns 5-10 personalized recommendations per user
- [ ] **AC2**: Filtering logic implemented with at least 4 filtering rules
- [ ] **AC3**: Signal values substituted into templates (6+ templates from Story 4.1)
- [ ] **AC4**: Fallback to original description when template fails or signal missing
- [ ] **AC5**: Ranking algorithm combines priority, relevance, and impact
- [ ] **AC6**: PersonalizedRecommendation model includes metadata (substitutions, relevance_score, rank)
- [ ] **AC7**: Performance <100ms for generating 10 recommendations
- [ ] **AC8**: 20+ unit tests covering all components
- [ ] **AC9**: Integration tests with real persona assignments and signals
- [ ] **AC10**: All tests passing (100% pass rate)
- [ ] **AC11**: Code review approved

---

## Filtering Rules

### Rule 1: Emergency Fund Built
**Logic**: Skip emergency fund recommendations if user has 3+ months saved
```python
if behavioral_signals.savings.emergency_fund_months >= 3.0:
    filter_out(["emergency_fund_start", "automate_savings_transfers"])
```

### Rule 2: No Credit Accounts
**Logic**: Skip credit-related recommendations if user has no credit cards
```python
if behavioral_signals.credit.high_utilization_count == 0:
    filter_out(["debt_payoff_avalanche", "reduce_credit_utilization", ...])
```

### Rule 3: Low Subscription Count
**Logic**: Skip subscription optimization if user has <5 subscriptions
```python
if behavioral_signals.subscriptions.subscription_count < 5:
    filter_out(["audit_all_subscriptions", "cancel_unused_services", ...])
```

### Rule 4: Stable Income
**Logic**: Skip irregular income recommendations if income is stable (biweekly/monthly)
```python
if behavioral_signals.income.payment_frequency in ["biweekly", "monthly"]:
    filter_out(["variable_income_budgeting", "income_averaging_strategy", ...])
```

### Rule 5: Already Investing
**Logic**: Skip basic investing recommendations if user has investment accounts
```python
if user_has_investment_accounts():  # Inferred from account types
    filter_out(["start_investing_robo_advisor"])
```

---

## Personalization Templates

### Template Syntax
- Placeholders: `{signal_name}`
- Nested fields: `{savings_30d_emergency_fund_months}`
- Formatting: `{credit_max_utilization_pct}%` (formatter detects % suffix)

### Template Examples (from Story 4.1)

**High Utilization:**
```yaml
personalization_template: "You're currently at {credit_max_utilization_pct}% credit utilization. Learn why this matters and how to improve it."
# Result: "You're currently at 65% credit utilization. Learn why this matters and how to improve it."
```

**Low Savings:**
```yaml
personalization_template: "You currently have ${savings_total_balance} saved and spend ${monthly_expenses} per month. Start with a $1,000 mini emergency fund."
# Result: "You currently have $125.50 saved and spend $3,894.32 per month. Start with a $1,000 mini emergency fund."
```

**Subscription Heavy:**
```yaml
personalization_template: "With {subscription_count} active subscriptions consuming {subscription_share}% of your spending, there may be opportunities to cut back and redirect funds to savings."
# Result: "With 23 active subscriptions consuming 82.7% of your spending, there may be opportunities to cut back and redirect funds to savings."
```

### Signal Mapping

| Placeholder | Source | Format |
|-------------|--------|--------|
| `{credit_max_utilization_pct}` | `behavioral_signals.credit.aggregate_utilization * 100` | `65.0` → `"65"` |
| `{credit_total_balance}` | `Sum of credit balances` | `8250.75` → `"$8,250.75"` |
| `{savings_total_balance}` | `behavioral_signals.savings.total_savings_balance` | `125.50` → `"$125.50"` |
| `{savings_emergency_fund_months}` | `behavioral_signals.savings.emergency_fund_months` | `0.5` → `"0.5"` |
| `{subscription_count}` | `behavioral_signals.subscriptions.subscription_count` | `23` → `"23"` |
| `{subscription_share}` | `behavioral_signals.subscriptions.subscription_share * 100` | `0.827` → `"82.7"` |
| `{monthly_expenses}` | `Calculated from transactions` | `3894.32` → `"$3,894.32"` |
| `{income_payment_frequency}` | `behavioral_signals.income.payment_frequency` | `"biweekly"` → `"biweekly"` |

---

## Ranking Algorithm

### Relevance Score Calculation

```python
def calculate_relevance_score(
    recommendation: Recommendation,
    behavioral_signals: BehavioralSummary,
    persona_id: str
) -> float:
    """
    Calculate relevance score (0.0-1.0).

    Formula:
    base_score = (11 - priority) / 10  # Priority 1 = 1.0, Priority 10 = 0.1

    Boosts:
    - High impact: +0.2
    - Personalized (template used): +0.1
    - Quick win: +0.1
    - Signal-specific relevance: +0.0 to +0.3

    Final score capped at 1.0
    """
    base_score = (11 - recommendation.priority) / 10

    boosts = 0.0
    if recommendation.estimated_impact == EstimatedImpact.HIGH:
        boosts += 0.2
    if recommendation.personalization_template:
        boosts += 0.1
    if recommendation.is_quick_win:
        boosts += 0.1

    # Signal-based relevance (persona-specific)
    signal_boost = calculate_signal_relevance(recommendation, behavioral_signals, persona_id)

    return min(1.0, base_score + boosts + signal_boost)
```

### Signal-Based Relevance

**Example: Low Savings Persona**
- If `emergency_fund_months < 1.0`: Boost emergency fund recs by +0.3
- If `subscription_share > 0.5`: Boost subscription optimization by +0.2
- If `savings_total_balance == 0`: Boost "start saving" recs by +0.3

**Example: High Utilization Persona**
- If `credit_max_utilization_pct > 0.7`: Boost debt payoff recs by +0.3
- If `high_utilization_count > 2`: Boost balance transfer recs by +0.2

---

## Testing Strategy

### Unit Tests (20-25 tests)

1. **Engine Tests** (5 tests)
   - Generate recommendations for valid user
   - Handle missing persona
   - Handle missing signals
   - Respect limit parameter
   - Performance <100ms

2. **Filtering Tests** (6 tests)
   - Filter emergency fund (has savings)
   - Filter credit recs (no credit cards)
   - Filter subscription recs (low count)
   - Filter income recs (stable income)
   - Don't filter when rules don't apply
   - Log filter reasons

3. **Personalization Tests** (6 tests)
   - Substitute percentage placeholders
   - Substitute currency placeholders
   - Substitute count placeholders
   - Handle missing signals gracefully
   - Fallback to original description
   - Track substitutions in metadata

4. **Ranking Tests** (5 tests)
   - Base score from priority
   - High impact boost
   - Personalized boost
   - Quick win boost
   - Signal relevance boost
   - Final ranking order correct

5. **Integration Tests** (3+ tests)
   - End-to-end with Low Savings persona
   - End-to-end with High Utilization persona
   - End-to-end with Subscription Heavy persona

---

## Dependencies

### Internal
- Story 4.1: ContentLibrary (complete ✅)
- Epic 3: PersonaAssignment (complete ✅)
- Epic 2: BehavioralSummary (complete ✅)

### External
- `string.Template` or regex for template parsing
- `datetime` for timestamps

---

## Risk & Mitigation

### Risk 1: Template Parsing Complexity
**Risk**: Complex templates may fail or produce incorrect output
**Mitigation**:
- Start with simple `{placeholder}` syntax
- Comprehensive tests for each template type
- Fallback to original description on error
- Log all personalization failures

### Risk 2: Signal Unavailability
**Risk**: Required signals may be missing for some users
**Mitigation**:
- Check signal availability before substitution
- Graceful fallback to generic text
- Don't fail entire generation if one template fails
- Log warnings for debugging

### Risk 3: Ranking Subjectivity
**Risk**: "Best" ranking is subjective and may not satisfy all users
**Mitigation**:
- Start with simple, explainable algorithm
- Make algorithm configurable for A/B testing
- Track user engagement metrics (Story 4.3)
- Iterate based on data

### Risk 4: Performance
**Risk**: Complex personalization may exceed 100ms budget
**Mitigation**:
- Cache content library (already done in Story 4.1)
- Pre-compile regex patterns
- Profile hot paths
- Optimize only if needed

---

## Out of Scope

- A/B testing framework (nice to have, deprioritize)
- Machine learning-based ranking (future enhancement)
- Multi-recommendation strategies (future)
- Recommendation explanations ("Why this rec?") (Epic 5)
- User feedback loop (Epic 5)

---

## Definition of Done

- [ ] Code implemented and passing all tests
- [ ] 20+ unit tests with 100% pass rate
- [ ] Integration tests with real data
- [ ] All 11 acceptance criteria met
- [ ] Performance <100ms verified
- [ ] Code review completed and approved
- [ ] Documentation updated
- [ ] Story marked complete in tracking

---

## Usage Examples

### Example 1: Generate Recommendations

```python
from datetime import date
from spendsense.recommendations.engine import RecommendationEngine
from spendsense.personas.assigner import PersonaAssigner
from spendsense.features.behavioral_summary import BehavioralSummaryGenerator

# Initialize
engine = RecommendationEngine("spendsense/config/recommendations.yaml")
assigner = PersonaAssigner("data/processed/spendsense.db")
signal_gen = BehavioralSummaryGenerator("data/processed/spendsense.db")

# Get user data
user_id = "user_MASKED_000"
reference_date = date(2025, 11, 5)

assignment = assigner.get_assignment(user_id, "30d")
signals = signal_gen.generate_summary(user_id, reference_date, window_days=30)

# Generate recommendations
recommendations = engine.generate(
    user_id=user_id,
    persona_id=assignment.assigned_persona_id,
    behavioral_signals=signals,
    limit=10
)

# Display
for i, rec in enumerate(recommendations, 1):
    print(f"{i}. [{rec.category.value.upper()}] {rec.title}")
    print(f"   {rec.description}")
    print(f"   Relevance: {rec.relevance_score:.2f}, Rank: {rec.rank}")
    if rec.personalized:
        print(f"   Personalized with: {rec.substitutions}")
    print()
```

### Example 2: Filter Only

```python
from spendsense.recommendations.filtering import FilterEngine

filter_engine = FilterEngine()
base_recs = content_library.get_by_persona("low_savings")

filtered_recs, filter_log = filter_engine.filter(
    recommendations=base_recs,
    behavioral_signals=signals,
    persona_id="low_savings"
)

print(f"Filtered {len(base_recs) - len(filtered_recs)} recommendations:")
for reason in filter_log:
    print(f"  - {reason}")
```

### Example 3: Personalize Only

```python
from spendsense.recommendations.personalization import PersonalizationEngine

personalizer = PersonalizationEngine()

for rec in recommendations:
    personalized = personalizer.personalize(
        recommendation=rec,
        behavioral_signals=signals
    )

    if personalized.personalized:
        print(f"Original: {rec.description}")
        print(f"Personalized: {personalized.description}")
        print(f"Substitutions: {personalized.substitutions}")
```

---

**Created**: 2025-11-05
**Author**: Claude (Epic 4 Implementation)
**Status**: Ready for Implementation
**Dependencies**: Story 4.1 (complete ✅), Epic 2 & 3 (complete ✅)
