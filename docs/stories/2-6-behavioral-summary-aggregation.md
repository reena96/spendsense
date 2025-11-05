# Story 2.6: Behavioral Summary Aggregation

**Epic:** 2 - Behavioral Signal Detection Pipeline
**Story ID:** 2.6
**Status:** completed

## Story

As a **data scientist**,
I want **aggregated behavioral summaries per user combining all detected signals**,
so that **persona classification has complete feature set available for decision logic**.

## Acceptance Criteria

1. User behavioral summary created combining subscription, savings, credit, and income signals
2. Summary includes all metrics computed for both time windows
3. Summary includes metadata: calculation timestamp, data completeness flags
4. Missing data indicators added where signals could not be computed
5. Summary stored in structured format (JSON) for recommendation engine access
6. Summary accessible via API endpoint GET /profile/{user_id}
7. Fallback defaults applied consistently for incomplete data
8. Summary generation logged for audit trail
9. Unit tests verify summary completeness and data structure

## Tasks/Subtasks

### Core Behavioral Summary Module
- [ ] Create `spendsense/features/behavioral_summary.py` (AC: 1-4)
  - [ ] Implement `BehavioralSummaryGenerator` class
  - [ ] Implement `generate_summary()` method
  - [ ] Use all 4 detectors (Subscription, Savings, Credit, Income)

### Summary Aggregation
- [ ] Combine all signals (AC: 1, 2)
  - [ ] Call SubscriptionDetector for 30 and 180 days
  - [ ] Call SavingsDetector for 30 and 180 days
  - [ ] Call CreditDetector for 30 and 180 days
  - [ ] Call IncomeDetector for 30 and 180 days
  - [ ] Combine into single summary structure

### Metadata & Completeness
- [ ] Add metadata (AC: 3, 4)
  - [ ] Calculation timestamp
  - [ ] Data completeness flags per detector
  - [ ] Missing data indicators
  - [ ] Fallback value tracking

### Data Storage
- [ ] Structured format (AC: 5)
  - [ ] Create BehavioralSummary dataclass
  - [ ] Support JSON serialization
  - [ ] Include all metrics from all detectors

### API Integration
- [ ] API endpoint (AC: 6)
  - [ ] Add GET /api/signals/{user_id} endpoint
  - [ ] Return complete behavioral summary
  - [ ] Handle errors gracefully

### Fallback Handling
- [ ] Consistent defaults (AC: 7)
  - [ ] Use time_windows.get_default_fallback_values()
  - [ ] Apply defaults when detectors return empty
  - [ ] Document fallback logic

### Logging & Audit
- [ ] Audit trail (AC: 8)
  - [ ] Log summary generation events
  - [ ] Log which detectors succeeded/failed
  - [ ] Track processing time

### Testing
- [ ] Comprehensive tests (AC: 9)
  - [ ] Test full summary generation
  - [ ] Test with missing data scenarios
  - [ ] Test fallback values applied
  - [ ] Test JSON serialization
  - [ ] Test data structure completeness
  - [ ] Test both time windows included

## Dev Notes

**Tech Stack:**
- All 4 detectors from Stories 2.2-2.5
- TimeWindowCalculator
- dataclass with to_dict() for JSON
- logging module

**Data Structure:**
```python
@dataclass
class BehavioralSummary:
    user_id: str
    generated_at: datetime
    reference_date: date

    # Subscription signals
    subscriptions_30d: SubscriptionMetrics
    subscriptions_180d: SubscriptionMetrics

    # Savings signals
    savings_30d: SavingsMetrics
    savings_180d: SavingsMetrics

    # Credit signals
    credit_30d: CreditMetrics
    credit_180d: CreditMetrics

    # Income signals
    income_30d: IncomeMetrics
    income_180d: IncomeMetrics

    # Metadata
    data_completeness: Dict[str, bool]
    fallbacks_applied: List[str]

    def to_dict(self) -> dict:
        \"\"\"Convert to dictionary for JSON serialization.\"\"\"
        pass
```

### Learnings from Previous Stories

**From Stories 2.1-2.5:**
- All detectors follow same pattern
- All support 30 and 180 day windows
- All handle empty data gracefully
- All return dataclass metrics

### References

- [Epic 2: Story 2.6](docs/prd/epic-2-behavioral-signal-detection-pipeline.md#Story-2.6)
- [All previous Epic 2 stories](docs/stories/)
- [Architecture: Features Module](docs/architecture.md#features-module)

## Dev Agent Record

### Context Reference

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-04: Story created for Epic 2 behavioral summary aggregation
