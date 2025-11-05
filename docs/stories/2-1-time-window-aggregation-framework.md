# Story 2.1: Time Window Aggregation Framework

**Epic:** 2 - Behavioral Signal Detection Pipeline
**Story ID:** 2.1
**Status:** drafted

## Story

As a **data scientist**,
I want **standardized time window calculation framework supporting 30-day and 180-day analysis periods**,
so that **all behavioral signals can be computed consistently across different time horizons**.

## Acceptance Criteria

1. Time window utility function created accepting reference date and window size (30/180 days)
2. Function returns filtered dataset for specified window
3. Function handles edge cases (insufficient historical data)
4. Window calculations use consistent date arithmetic across all modules
5. Default fallback values defined for users with insufficient data
6. Window framework documented with usage examples
7. Unit tests verify correct date filtering and edge case handling

## Tasks/Subtasks

### Core Time Window Module
- [ ] Create `spendsense/features/__init__.py` module (AC: 1)
- [ ] Create `spendsense/features/time_windows.py` with TimeWindow class (AC: 1, 4)
  - [ ] Implement `get_window_transactions(user_id, reference_date, days)` function
  - [ ] Implement `get_window_accounts(user_id, reference_date, days)` function
  - [ ] Support both 30-day and 180-day windows
  - [ ] Use consistent date arithmetic (datetime.timedelta)

### Edge Case Handling
- [ ] Handle insufficient historical data (AC: 3, 5)
  - [ ] Return empty dataset if no data in window
  - [ ] Flag data completeness in results
  - [ ] Define default fallback values for missing data
  - [ ] Document minimum data requirements

### Testing & Documentation
- [ ] Write comprehensive unit tests (AC: 7)
  - [ ] Test 30-day window filtering
  - [ ] Test 180-day window filtering
  - [ ] Test edge case: new user with <30 days history
  - [ ] Test edge case: user with no transactions
  - [ ] Test date boundary conditions
- [ ] Document usage with examples (AC: 6)
  - [ ] Add docstrings to all functions
  - [ ] Create usage examples in module docstring
  - [ ] Document return value structures

## Dev Notes

**Tech Stack:**
- pandas for date filtering and DataFrame operations
- datetime/timedelta for date arithmetic
- SQLite database access via existing DatabaseWriter
- Pydantic models from Story 1.2 for data validation

**Module Design:**
```python
# Core time window utilities
class TimeWindowCalculator:
    def __init__(self, db_path: str):
        self.db = DatabaseWriter(db_path)

    def get_transactions_in_window(
        self,
        user_id: str,
        reference_date: date,
        window_days: int
    ) -> pd.DataFrame:
        """Get all transactions within specified window."""
        pass

    def get_accounts_snapshot(
        self,
        user_id: str,
        reference_date: date
    ) -> List[Account]:
        """Get account balances as of reference date."""
        pass
```

**Date Arithmetic:**
- Use `datetime.timedelta(days=window_days)` for consistency
- Window start = `reference_date - timedelta(days=window_days)`
- Window end = `reference_date` (inclusive)
- All dates stored as `YYYY-MM-DD` strings in SQLite

**Edge Cases:**
1. **New user (<30 days):** Return available data, set `data_complete=False`
2. **No transactions:** Return empty DataFrame with proper schema
3. **Reference date in future:** Raise ValueError
4. **Window extends before account creation:** Filter to available data

**Integration:**
- Story 2.2-2.5 will use this module for all time-based filtering
- Story 2.6 will aggregate results across both window sizes

### References

- [Epic 2: Story 2.1](docs/prd/epic-2-behavioral-signal-detection-pipeline.md#Story-2.1)
- [Architecture: Features Module](docs/architecture.md#features-module)

## Dev Agent Record

### Context Reference

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2025-11-04: Story created for Epic 2 time window framework
