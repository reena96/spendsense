# Story 4.1: Recommendation Content Library

**Epic**: 4 - Personalized Recommendations
**Story**: 4.1
**Effort**: 3-4 days
**Status**: In Progress

---

## Goal

Build a structured content library with educational recommendations for each persona, providing the foundation for personalized financial guidance.

---

## User Story

> As a **recommendation engine**,
> I want **a curated content library with categorized recommendations per persona**,
> so that **I can provide relevant, actionable financial guidance to users based on their behavioral profile**.

---

## Context

- Epic 3 completed: 6 personas defined and validated
- Each persona has distinct financial challenges and focus areas
- Recommendations need to be:
  - **Relevant** to the persona's specific situation
  - **Actionable** with clear next steps
  - **Prioritized** by impact and urgency
  - **Categorized** for easy filtering and display

---

## Requirements

### Functional Requirements

1. **Content Structure**
   - YAML configuration file for easy maintenance
   - One section per persona (6 total)
   - 5-10 recommendations per persona
   - Minimum 36 total recommendations across all personas

2. **Recommendation Categories**
   - **Education**: Learn about financial concepts
   - **Action**: Take specific steps to improve finances
   - **Tip**: Quick wins and optimization strategies
   - **Insight**: Understand your current situation

3. **Metadata Fields**
   - `id`: Unique identifier (kebab-case)
   - `category`: One of the 4 categories above
   - `title`: Short, action-oriented title (5-10 words)
   - `description`: Detailed explanation (1-3 sentences)
   - `priority`: Integer ranking (1=highest, 10=lowest)
   - `difficulty`: Skill level (beginner, intermediate, advanced)
   - `time_commitment`: Effort required (one-time, daily, weekly, monthly, ongoing)
   - `estimated_impact`: Expected benefit (low, medium, high)
   - `content_url`: Link to detailed content (optional)
   - `personalization_template`: Template string for signal substitution (optional)

4. **Persona Coverage**
   - High Utilization (Priority 1)
   - Irregular Income (Priority 2)
   - Low Savings (Priority 3)
   - Subscription Heavy (Priority 4)
   - Cash Flow Optimizer (Priority 5)
   - Young Professional (Priority 6)

### Non-Functional Requirements

1. **Validation**
   - Pydantic models for type safety
   - Schema validation on load
   - Required field enforcement

2. **Maintainability**
   - YAML format for easy editing
   - Clear documentation
   - Version control friendly

3. **Performance**
   - Load once, cache in memory
   - Fast lookup by persona ID
   - <10ms to retrieve recommendations

---

## Technical Design

### File Structure

```
spendsense/
├── config/
│   └── recommendations.yaml    # Content library
├── recommendations/
│   ├── __init__.py
│   ├── models.py               # Pydantic models
│   └── content_library.py      # Loader and accessor
```

### Data Models

```python
class Recommendation(BaseModel):
    """Individual recommendation model."""
    id: str
    category: Literal["education", "action", "tip", "insight"]
    title: str
    description: str
    priority: int
    difficulty: Literal["beginner", "intermediate", "advanced"]
    time_commitment: Literal["one-time", "daily", "weekly", "monthly", "ongoing"]
    estimated_impact: Literal["low", "medium", "high"]
    content_url: Optional[str] = None
    personalization_template: Optional[str] = None

class ContentLibrary:
    """Content library loader and accessor."""
    def __init__(self, config_path: str):
        self.recommendations: Dict[str, List[Recommendation]] = {}
        self._load_from_yaml(config_path)

    def get_by_persona(self, persona_id: str) -> List[Recommendation]:
        """Get all recommendations for a persona, sorted by priority."""
        ...

    def get_by_id(self, recommendation_id: str) -> Optional[Recommendation]:
        """Get a specific recommendation by ID."""
        ...

    def get_all_personas(self) -> List[str]:
        """Get list of all personas with recommendations."""
        ...
```

### YAML Schema

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
      personalization_template: "You have ${credit_total_balance} in credit card debt. Focus on your {highest_rate_card} card with {highest_rate}% APR first."
```

---

## Implementation Plan

### Phase 1: Data Models (1-2 hours)
1. Create `spendsense/recommendations/__init__.py`
2. Create `spendsense/recommendations/models.py`
   - Define `Recommendation` Pydantic model
   - Add validation for enums and constraints
   - Add helper methods for display

### Phase 2: Content Library Loader (2-3 hours)
1. Create `spendsense/recommendations/content_library.py`
   - Implement `ContentLibrary` class
   - YAML loading with error handling
   - Caching and singleton pattern
   - Lookup methods

### Phase 3: Content Creation (6-8 hours)
1. Create `spendsense/config/recommendations.yaml`
2. Write 5-10 recommendations per persona:
   - High Utilization: 8 recommendations
   - Irregular Income: 7 recommendations
   - Low Savings: 8 recommendations
   - Subscription Heavy: 7 recommendations
   - Cash Flow Optimizer: 6 recommendations
   - Young Professional: 8 recommendations
3. Total: ~44 recommendations

### Phase 4: Testing (3-4 hours)
1. Create `tests/test_content_library.py`
2. Test cases:
   - YAML loading and validation
   - Model validation (required fields, enums)
   - Lookup by persona (sorted by priority)
   - Lookup by recommendation ID
   - Error handling (missing file, invalid YAML)
   - Edge cases (empty persona, unknown persona)
3. Target: 15-20 tests

---

## Acceptance Criteria

- [ ] **AC1**: Content library YAML file exists at `spendsense/config/recommendations.yaml`
- [ ] **AC2**: Library contains 5-10 recommendations for each of the 6 personas (36+ total)
- [ ] **AC3**: All recommendations have required metadata fields (id, category, title, description, priority, difficulty, time_commitment, estimated_impact)
- [ ] **AC4**: Recommendations are categorized correctly (education, action, tip, insight)
- [ ] **AC5**: Each persona's recommendations are priority-ordered (1=highest)
- [ ] **AC6**: Pydantic models validate recommendation structure
- [ ] **AC7**: ContentLibrary class loads YAML successfully
- [ ] **AC8**: `get_by_persona()` returns sorted recommendations
- [ ] **AC9**: `get_by_id()` retrieves specific recommendations
- [ ] **AC10**: All tests passing (15+ tests)
- [ ] **AC11**: Code review approved

---

## Example Content by Persona

### High Utilization (8 recommendations)
1. **Education**: Understanding credit utilization impact
2. **Action**: Pay down highest-interest debt first
3. **Action**: Make bi-weekly payments instead of monthly
4. **Tip**: Request credit limit increase (don't use it)
5. **Action**: Consider balance transfer to 0% APR card
6. **Education**: Create debt payoff timeline
7. **Tip**: Set up payment reminders
8. **Insight**: How much you're paying in interest monthly

### Irregular Income (7 recommendations)
1. **Education**: Variable income budgeting strategies
2. **Action**: Build 6+ month emergency fund
3. **Action**: Smooth income with averaging strategy
4. **Tip**: Use percentage-based budgeting
5. **Action**: Set aside estimated taxes (1099 income)
6. **Education**: Gig economy financial planning
7. **Insight**: Income variability analysis

### Low Savings (8 recommendations)
1. **Action**: Build emergency fund - Start with $1,000
2. **Action**: Automate savings transfers
3. **Tip**: Review subscription spending for savings
4. **Action**: Open high-yield savings account
5. **Education**: "Pay yourself first" method
6. **Tip**: Round-up savings apps
7. **Education**: Emergency fund importance
8. **Insight**: How much you need for 3-month cushion

### Subscription Heavy (7 recommendations)
1. **Action**: Audit your subscriptions
2. **Action**: Cancel unused services
3. **Tip**: Try subscription management tool
4. **Action**: Negotiate better rates
5. **Tip**: Set spending alerts for recurring charges
6. **Education**: Subscription spending psychology
7. **Insight**: Total monthly subscription cost

### Cash Flow Optimizer (6 recommendations)
1. **Action**: Start investing with robo-advisor
2. **Action**: Optimize idle cash placement
3. **Education**: Index funds and diversification
4. **Action**: Set long-term financial goals
5. **Education**: Tax-advantaged accounts (IRA, HSA)
6. **Insight**: Investment vs savings opportunity cost

### Young Professional (8 recommendations)
1. **Education**: Credit 101 - How scores work
2. **Action**: Open your first credit card
3. **Education**: Budgeting fundamentals
4. **Education**: Different account types
5. **Action**: Build credit history responsibly
6. **Tip**: Start small with savings goals
7. **Education**: Compound interest basics
8. **Insight**: Your financial foundation checklist

---

## Testing Strategy

### Unit Tests (15+ tests)

1. **Model Validation** (5 tests)
   - Valid recommendation model
   - Missing required fields
   - Invalid enum values
   - Priority range validation
   - ID uniqueness

2. **YAML Loading** (5 tests)
   - Load valid YAML file
   - Handle missing file
   - Handle invalid YAML syntax
   - Handle invalid recommendation structure
   - Validate all personas present

3. **Content Access** (5 tests)
   - Get recommendations by persona ID
   - Get recommendations sorted by priority
   - Get recommendation by ID
   - Handle unknown persona ID
   - Handle unknown recommendation ID

4. **Edge Cases** (3+ tests)
   - Empty persona (no recommendations)
   - Duplicate recommendation IDs
   - Mixed priority ordering

---

## Dependencies

### Internal
- None (foundation module)

### External
- `pyyaml`: YAML file parsing
- `pydantic`: Data validation

---

## Risk & Mitigation

### Risk 1: Content Quality
**Risk**: Recommendations may not resonate with users
**Mitigation**:
- Start with research-backed strategies
- Iterate based on user feedback
- A/B test different messaging

### Risk 2: Content Staleness
**Risk**: Financial advice becomes outdated
**Mitigation**:
- Version control for recommendations
- Regular content review cycle
- Easy YAML editing for updates

### Risk 3: Personalization Complexity
**Risk**: Templates may not work for all users
**Mitigation**:
- Start with simple templates
- Graceful fallback to generic text
- Log template errors for debugging

---

## Out of Scope

- Content rendering (HTML/Markdown)
- Content management UI
- User feedback on recommendations
- Recommendation effectiveness tracking
- Multi-language support
- Partner offer integration

These will be addressed in later stories (4.2-4.5).

---

## Definition of Done

- [ ] Code implemented and passing all tests
- [ ] 15+ unit tests with 100% pass rate
- [ ] All 11 acceptance criteria met
- [ ] Code review completed and approved
- [ ] Documentation updated
- [ ] Story marked complete in tracking

---

## Notes

- Content library is the foundation for all recommendation features
- YAML format chosen for ease of editing by non-developers
- Priority system allows future expansion with more recommendations
- Personalization templates are optional (Story 4.2 will use them)

---

**Created**: 2025-11-05
**Author**: Claude (Epic 4 Implementation)
**Status**: Ready for Implementation
