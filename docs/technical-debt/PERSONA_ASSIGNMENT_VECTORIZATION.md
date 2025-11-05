# Technical Debt: Persona Assignment Vectorization

**Priority**: Medium (optimize when scale requires it)
**Estimated Effort**: 2-3 days
**Estimated Performance Gain**: 8-12x faster (120s → 10-15s for 100 users)

---

## Current Performance Baseline

### Test Case: 100 Users × 2 Time Windows
- **Current Time**: ~120 seconds (2 minutes)
- **Operations**: 200 individual assignments
- **Database Queries**: ~800 queries (4 signal queries + 1 write per user per window)

### Bottlenecks Identified

1. **Loop-based user processing** (Python iteration anti-pattern)
2. **Individual SQL queries per user** (N+1 query problem)
3. **Individual database INSERTs** (no bulk operations)
4. **Redundant signal calculations** (same signals calculated multiple times)

---

## Optimization Strategy: PSA Vectorization

**PSA = Batch Processing with Vectorized Operations**

### 1. Vectorize Behavioral Signal Generation

#### Current (Slow)
```python
# spendsense/features/behavioral_summary.py
for user_id in user_ids:
    summary = self.generate_summary(user_id, reference_date)
    # → 4 separate SQL queries per user:
    #   - subscriptions
    #   - savings
    #   - credit
    #   - income
```

#### Optimized (Fast)
```python
def generate_summaries_batch(
    self,
    user_ids: List[str],
    reference_date: date
) -> List[BehavioralSummary]:
    """Generate summaries for multiple users in batch."""

    # Single query for all users' subscriptions
    subscriptions_df = self._get_subscriptions_batch(user_ids, reference_date)

    # Single query for all users' savings
    savings_df = self._get_savings_batch(user_ids, reference_date)

    # Single query for all users' credit
    credit_df = self._get_credit_batch(user_ids, reference_date)

    # Single query for all users' income
    income_df = self._get_income_batch(user_ids, reference_date)

    # Merge and create summaries
    return self._merge_to_summaries(
        user_ids, subscriptions_df, savings_df, credit_df, income_df
    )
```

**Benefit**: 4 queries instead of 400 queries (for 100 users)

### 2. Vectorize Persona Matching

#### Current (Slow)
```python
# spendsense/personas/matcher.py
for persona in self.registry.personas:  # Loop through 6 personas
    match_result = self._evaluate_persona(persona, signals, time_window)
    matches.append(match_result)
```

#### Optimized (Fast)
```python
def match_personas_vectorized(
    self,
    signals_df: pd.DataFrame,  # DataFrame of user signals
    reference_date: date,
    time_window: str
) -> pd.DataFrame:
    """
    Vectorized persona matching for multiple users.

    Args:
        signals_df: DataFrame with columns for each signal, rows per user

    Returns:
        DataFrame with columns: user_id, persona_id, matched, evidence
    """
    results = []

    for persona in self.registry.personas:
        # Vectorized evaluation across all users at once
        matched_mask = self._evaluate_criteria_vectorized(
            persona.criteria,
            signals_df
        )

        results.append({
            'persona_id': persona.id,
            'matched': matched_mask,  # Boolean array for all users
            'priority': persona.priority
        })

    return pd.DataFrame(results)
```

**Benefit**: 6 vectorized operations instead of 600 loop iterations (100 users × 6 personas)

### 3. Vectorize Condition Evaluation

#### Current (Slow)
```python
def _evaluate_condition(self, condition: Dict, signals: ExtendedSignals) -> bool:
    signal_value = getattr(signals, condition['signal'], None)
    if signal_value is None:
        return False
    return self._compare_values(signal_value, condition['operator'], condition['value'])
```

#### Optimized (Fast)
```python
def _evaluate_condition_vectorized(
    self,
    condition: Dict,
    signals_df: pd.DataFrame
) -> pd.Series:
    """Vectorized condition evaluation using pandas."""
    signal_col = condition['signal']
    operator = condition['operator']
    threshold = condition['value']

    # Vectorized comparison (operates on entire column at once)
    if operator == '>=':
        return signals_df[signal_col] >= threshold
    elif operator == '<':
        return signals_df[signal_col] < threshold
    # ... etc
```

**Benefit**: Single operation on entire column vs loop through each value

### 4. Bulk Database Operations

#### Current (Slow)
```python
# Individual INSERTs
for assignment in assignments:
    session.add(PersonaAssignmentRecord(**assignment))
    session.commit()  # 200 commits!
```

#### Optimized (Fast)
```python
def store_assignments_batch(
    self,
    assignments: List[Dict]
) -> List[str]:
    """Bulk insert persona assignments."""
    records = [
        PersonaAssignmentRecord(**assignment)
        for assignment in assignments
    ]

    with self.Session() as session:
        session.bulk_insert_mappings(PersonaAssignmentRecord, assignments)
        session.commit()  # Single commit

    return [r.assignment_id for r in records]
```

**Benefit**: Single transaction instead of 200 transactions

---

## Implementation Plan

### Phase 1: Batch Signal Generation (Highest Impact)
**Effort**: 1 day
**Gain**: 5-6x speedup

- [ ] Add `generate_summaries_batch()` to BehavioralSummaryGenerator
- [ ] Implement batch SQL queries with `WHERE user_id IN (...)`
- [ ] Use pandas to merge results
- [ ] Add tests for batch operations

### Phase 2: Vectorized Matching (Medium Impact)
**Effort**: 1 day
**Gain**: 2x additional speedup

- [ ] Convert signals to pandas DataFrame structure
- [ ] Implement `_evaluate_condition_vectorized()`
- [ ] Implement `_evaluate_criteria_vectorized()` for AND/OR logic
- [ ] Maintain backward compatibility with single-user API

### Phase 3: Bulk Database Operations (Lower Impact)
**Effort**: 0.5 days
**Gain**: 1.5x additional speedup

- [ ] Add `store_assignments_batch()` to PersonaAssigner
- [ ] Use SQLAlchemy bulk operations
- [ ] Add batch retrieval methods

### Phase 4: Testing & Validation
**Effort**: 0.5 days

- [ ] Add performance benchmarks
- [ ] Verify results match non-vectorized version
- [ ] Test with various batch sizes (10, 100, 1000 users)
- [ ] Profile to find remaining bottlenecks

**Total Effort**: ~3 days
**Expected Result**: 120s → 10-15s (8-12x faster)

---

## Code Examples

### Example 1: Batch Signal Query

```python
def _get_subscriptions_batch(
    self,
    user_ids: List[str],
    reference_date: date,
    window_days: int = 180
) -> pd.DataFrame:
    """Get subscription signals for multiple users."""
    start_date = reference_date - timedelta(days=window_days)

    # Single query for all users
    query = """
    SELECT
        a.user_id,
        COUNT(DISTINCT t.merchant_name) as subscription_count,
        SUM(CASE WHEN t.amount < 0 THEN ABS(t.amount) ELSE 0 END) as subscription_spend,
        (SELECT SUM(ABS(amount)) FROM transactions t2
         JOIN accounts a2 ON t2.account_id = a2.account_id
         WHERE a2.user_id = a.user_id
         AND t2.date >= :start_date
         AND t2.date <= :end_date
         AND t2.amount < 0) as total_spend
    FROM transactions t
    JOIN accounts a ON t.account_id = a.account_id
    WHERE a.user_id IN :user_ids
      AND t.date >= :start_date
      AND t.date <= :end_date
      AND t.payment_channel = 'recurring'
    GROUP BY a.user_id
    """

    with self.Session() as session:
        result = session.execute(
            query,
            {
                'user_ids': tuple(user_ids),
                'start_date': start_date,
                'end_date': reference_date
            }
        )
        return pd.DataFrame(result.fetchall())
```

### Example 2: Vectorized Condition Evaluation

```python
def _evaluate_criteria_vectorized(
    self,
    criteria: Dict,
    signals_df: pd.DataFrame
) -> pd.Series:
    """
    Evaluate criteria for all users at once.

    Returns:
        Boolean Series indicating match for each user
    """
    operator = criteria['operator']
    conditions = criteria['conditions']

    # Evaluate each condition vectorized
    condition_results = []
    for condition in conditions:
        signal_col = condition['signal']
        comp_op = condition['operator']
        threshold = condition['value']

        # Handle missing values
        has_signal = signals_df[signal_col].notna()

        # Vectorized comparison
        if comp_op == '>=':
            result = (signals_df[signal_col] >= threshold) & has_signal
        elif comp_op == '<':
            result = (signals_df[signal_col] < threshold) & has_signal
        elif comp_op == '==':
            result = (signals_df[signal_col] == threshold) & has_signal

        condition_results.append(result)

    # Combine with AND/OR
    if operator == 'AND':
        return pd.concat(condition_results, axis=1).all(axis=1)
    else:  # OR
        return pd.concat(condition_results, axis=1).any(axis=1)
```

---

## Performance Testing

### Benchmark Script

```python
import time
from datetime import date
from pathlib import Path

def benchmark_current_approach(user_ids, reference_date):
    """Benchmark current loop-based approach."""
    from spendsense.personas.assigner import PersonaAssigner

    assigner = PersonaAssigner("data/processed/spendsense.db")

    start = time.time()
    for user_id in user_ids:
        assigner.assign_persona(user_id, reference_date, "30d")
        assigner.assign_persona(user_id, reference_date, "180d")
    end = time.time()

    return end - start

def benchmark_vectorized_approach(user_ids, reference_date):
    """Benchmark vectorized batch approach."""
    from spendsense.personas.assigner_vectorized import PersonaAssignerVectorized

    assigner = PersonaAssignerVectorized("data/processed/spendsense.db")

    start = time.time()
    assigner.assign_personas_batch(user_ids, reference_date, ["30d", "180d"])
    end = time.time()

    return end - start

# Run benchmarks
user_ids = [f"user_MASKED_{i:03d}" for i in range(100)]
reference_date = date(2025, 11, 5)

current_time = benchmark_current_approach(user_ids, reference_date)
vectorized_time = benchmark_vectorized_approach(user_ids, reference_date)

print(f"Current approach: {current_time:.2f}s")
print(f"Vectorized approach: {vectorized_time:.2f}s")
print(f"Speedup: {current_time / vectorized_time:.1f}x")
```

---

## Trade-offs

### Advantages of Vectorization
✅ **8-12x faster** for batch operations
✅ **More scalable** (handles 1000s of users efficiently)
✅ **Better resource utilization** (fewer DB connections)
✅ **Lower latency** for batch jobs

### Disadvantages
❌ **More complex code** (pandas/numpy required)
❌ **Higher memory usage** (loads more data at once)
❌ **Less readable** (vectorized code harder to debug)
❌ **Overkill for small batches** (<10 users)

---

## When to Implement

### Triggers for Optimization

Implement vectorization when:

1. **User count grows** beyond 1000 users
2. **Assignment time** exceeds 5 minutes for full batch
3. **Real-time requirements** need <1s per user
4. **Scheduled jobs** run daily/hourly at scale
5. **API endpoints** need batch assignment capability

### Current Recommendation

**DO NOT OPTIMIZE YET** because:
- Current scale: 100 users
- Current time: 2 minutes (acceptable)
- Epic 3 just completed (prioritize new features)
- Epic 4-6 have higher priority
- Code clarity > performance at this stage

**REVISIT** during:
- Epic 6 (Operator View) - if real-time updates needed
- Production deployment planning
- Scale testing with real user base

---

## References

- **Discussion**: PSA Vectorization (Alexis Manyrath, Aaron Gallant)
- **Key Insight**: "If you see a for loop in mathy code, it's probably an anti-pattern"
- **Tools**: pandas, numpy for vectorization
- **SQLAlchemy**: `bulk_insert_mappings()` for batch DB operations

---

**Status**: Documented as technical debt
**Next Action**: Implement when scale requires (see triggers above)
**Owner**: Future developer (Epic 6 or production prep)

---

## Appendix: Quick Wins (If Needed Today)

If you need immediate improvement without full vectorization:

### Quick Win 1: Batch DB Writes (5 min)
```python
# In store_assignments loop:
session.add(record)
# Don't commit inside loop!

# After loop:
session.commit()  # Single commit
```
**Gain**: 2x faster writes

### Quick Win 2: Connection Pooling
```python
# In database_writer.py:
engine = create_engine(
    f'sqlite:///{db_path}',
    pool_size=10,  # Add connection pool
    max_overflow=20
)
```
**Gain**: 20-30% faster

### Quick Win 3: Parallel Processing
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(assigner.assign_persona, user_id, date, window)
        for user_id in user_ids
        for window in ["30d", "180d"]
    ]
```
**Gain**: 2-4x faster (limited by SQLite locking)
