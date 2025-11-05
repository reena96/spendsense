# Story 4.1: Educational Content Catalog

**Epic:** 4 - Recommendation Engine & Content Catalog
**Story ID:** 4.1
**Status:** in-progress

## Story

As a **product manager**,
I want **structured catalog of educational content items with metadata linking them to personas and signals**,
so that **relevant education can be programmatically matched to user needs**.

## Acceptance Criteria

- [ ] 1. Content catalog created as YAML/JSON configuration file
- [ ] 2. Each content item includes: ID, title, type (article/template/calculator/video), description
- [ ] 3. Each item tagged with relevant personas (can apply to multiple personas)
- [ ] 4. Each item tagged with triggering signals (subscription, savings, credit, income patterns)
- [ ] 5. Content items defined for all persona educational focus areas
- [ ] 6. At least 15 unique educational items covering all 6 personas
- [ ] 7. Content includes: debt paydown strategies, budget templates, subscription audit checklists, emergency fund calculators, credit utilization explainers
- [ ] 8. Each item includes plain-language summary (grade-8 readability)
- [ ] 9. Catalog schema validated and documented
- [ ] 10. Catalog loaded at application startup

## Implementation Notes

### Current Implementation Review

**What We Have:**
- ✅ YAML configuration file (`spendsense/config/recommendations.yaml`)
- ✅ 44 recommendations (exceeds 15 minimum)
- ✅ All have: ID, title, description
- ✅ Schema validated with Pydantic models
- ✅ Loaded at application startup via ContentLibrary
- ✅ Plain-language descriptions

**Gaps Identified:**

**GAP 1 - AC2: Missing "type" field**
- Current: Has "category" field (education/action/tip/insight)
- Required: "type" field (article/template/calculator/video)
- Impact: Field name and enum values don't match PRD

**GAP 2 - AC3: Single persona per item**
- Current: Recommendations organized by single persona
- Required: Items can apply to multiple personas
- Impact: Cannot tag one recommendation as applicable to multiple personas

**GAP 3 - AC4: No explicit signal tags**
- Current: No "triggering_signals" field
- Required: Each item tagged with signals (subscription, savings, credit, income)
- Impact: Cannot query "show me all recommendations for users with high credit utilization"

### Required Schema Changes

```yaml
# Current schema (what we have)
recommendations:
  high_utilization:  # Single persona organization
    - id: "understand_credit_utilization"
      category: "education"  # Not "type"
      title: "Understanding Credit Utilization"
      description: "..."
      # Missing: type, personas[], triggering_signals[]

# PRD-compliant schema (what we need)
educational_content:
  - id: "understand_credit_utilization"
    type: "article"  # article/template/calculator/video
    title: "Understanding Credit Utilization"
    description: "..."
    personas: ["high_utilization", "young_professional"]  # Multiple personas
    triggering_signals: ["credit_utilization", "credit_score"]  # Explicit signals
    category: "education"  # Keep for backward compatibility
    priority: 1
    difficulty: "beginner"
    time_commitment: "one-time"
    estimated_impact: "high"
```

### Implementation Plan

**Phase 1: Update Data Models**
1. Add `type` field to Recommendation model (enum: article/template/calculator/video)
2. Add `personas` field (List[str]) - replaces single-persona organization
3. Add `triggering_signals` field (List[str])
4. Keep `category` for backward compatibility

**Phase 2: Update YAML File**
1. Restructure from persona-based to flat list
2. Add `type` field to all 44 recommendations
3. Add `personas` array to each (map from current organization)
4. Add `triggering_signals` array based on personalization templates and filtering logic

**Phase 3: Update ContentLibrary**
1. Update YAML loading to handle new structure
2. Maintain `get_by_persona()` method (filter by personas array)
3. Add `get_by_signal()` method for signal-based querying
4. Update tests

## Tasks/Subtasks

### Phase 1: Update Data Models
- [ ] Add `type: Literal["article", "template", "calculator", "video"]` field to Recommendation model
- [ ] Add `personas: List[str]` field
- [ ] Add `triggering_signals: List[str]` field
- [ ] Update model validators
- [ ] Update tests for new fields

### Phase 2: Update YAML Structure
- [ ] Convert persona-based structure to flat list under `educational_content:`
- [ ] Add `type` field to all 44 items (map category → type)
- [ ] Add `personas` array to all items
- [ ] Add `triggering_signals` array to all items
- [ ] Validate YAML loads successfully

### Phase 3: Update ContentLibrary
- [ ] Update `_load_yaml()` to handle new structure
- [ ] Ensure `get_by_persona()` still works (filter by personas array)
- [ ] Add `get_by_signal()` method
- [ ] Add `get_by_type()` method
- [ ] Update all tests
- [ ] Verify backward compatibility

## Definition of Done

- [ ] All 10 acceptance criteria met
- [ ] Schema matches PRD specification exactly
- [ ] All existing tests passing
- [ ] New tests added for new fields/methods
- [ ] Documentation updated
- [ ] Code review approved

---

**Created:** 2025-11-05
**Status:** In Progress - PRD Alignment
