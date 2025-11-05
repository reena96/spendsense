# Epic 3: Persona Assignment Testing Guide

## Quick Start

1. **Start the server** (if not already running):
   ```bash
   source venv/bin/activate
   python -m uvicorn spendsense.api.main:app --reload
   ```

2. **Open the UI**:
   - Navigate to: http://127.0.0.1:8000
   - Click on the "**Persona Assignment**" tab

3. **Test with these user IDs** to see different personas:

---

## Example Users by Persona

All 100 users have been assigned personas for both 30d and 180d windows!

### Persona Distribution (30-day window)

| Persona | Priority | Count | Example User IDs |
|---------|----------|-------|------------------|
| **Irregular Income** | 2 | 21 users | `user_MASKED_001`, `user_MASKED_006`, `user_MASKED_011` |
| **Low Savings** | 3 | 76 users | `user_MASKED_000`, `user_MASKED_002`, `user_MASKED_003` |
| **Subscription Heavy** | 4 | 8 users | `user_MASKED_019`, `user_MASKED_024`, `user_MASKED_034` |

### What You'll See

When you enter a user ID and click "Get Assignment", you'll see:

#### ✨ Beautiful Gradient Card
- **Priority 1** (High Utilization): Pink/red gradient
- **Priority 2** (Irregular Income): Pink/yellow gradient
- **Priority 3** (Low Savings): Blue gradient
- **Priority 4** (Subscription Heavy): Green gradient
- **Priority 5** (Cash Flow Optimizer): Teal gradient
- **Priority 6** (Young Professional): Light blue/pink gradient

#### 🏷️ Priority Badge
- Color-coded badge in the top-right showing priority level
- Example: "Priority 2" or "Priority 3"

#### 📋 All Qualifying Personas
- Shows ALL personas that matched (not just the assigned one)
- Assigned persona highlighted in blue
- Other qualifying personas in gray
- Example: User matches both "Low Savings" AND "Subscription Heavy", but "Low Savings" (priority 3) wins

#### 🧠 Prioritization Reasoning
- Clear explanation of WHY this persona was selected
- Example: "Highest priority match among 2 qualifying personas (priority 3)"

#### 🔍 Expandable Match Evidence
- Click "View all 6 persona evaluations" to expand
- Shows evaluation for ALL 6 personas (not just matches)
- Each persona shows:
  - ✓ Matched or ✗ No Match status
  - Matched conditions (for successful matches)
  - Signal values that were evaluated
  - Color-coded: Green background for matches, gray for non-matches

---

## Testing Scenarios

### Scenario 1: Basic Assignment (Low Savings)
```
User ID: user_MASKED_000
Time Window: 30d (or leave blank for both)

Expected:
- Assigned: Low Savings (Priority 3)
- Qualifying: Low Savings + Subscription Heavy
- Reasoning: "Highest priority match among 2 qualifying personas"
- Evidence: savings_emergency_fund_months = 0.0 (< 3.0 ✓)
```

### Scenario 2: Higher Priority (Irregular Income)
```
User ID: user_MASKED_001
Time Window: 30d

Expected:
- Assigned: Irregular Income (Priority 2)
- Qualifying: Irregular Income + Subscription Heavy
- Reasoning: "Highest priority match among 2 qualifying personas"
- Evidence: income_payroll_count = 0 (< 2.0 ✓)
```

### Scenario 3: Different Window Results
```
User ID: user_MASKED_001
Time Window: (leave blank for both windows)

Expected:
- 30d: Irregular Income (Priority 2)
- 180d: Subscription Heavy (Priority 4)
- Shows how personas can differ between time windows!
```

### Scenario 4: Subscription Heavy
```
User ID: user_MASKED_019
Time Window: 30d

Expected:
- Assigned: Subscription Heavy (Priority 4)
- Evidence: subscription_share_pct ≥ 0.2 (20%)
```

---

## API Testing

You can also test the API directly:

### Get Both Windows
```bash
curl http://127.0.0.1:8000/api/profile/user_MASKED_000 | python -m json.tool
```

### Get Specific Window
```bash
curl "http://127.0.0.1:8000/api/profile/user_MASKED_001?time_window=30d" | python -m json.tool
```

### Response Structure
```json
{
  "user_id": "user_MASKED_000",
  "assignments": {
    "30d": {
      "assignment_id": "uuid",
      "assigned_persona_id": "low_savings",
      "priority": 3,
      "assigned_at": "2025-11-05T...",
      "all_qualifying_personas": ["low_savings", "subscription_heavy"],
      "prioritization_reason": "...",
      "match_evidence": {
        "high_utilization": { "matched": false, ... },
        "irregular_income": { "matched": false, ... },
        "low_savings": { "matched": true, ... },
        "subscription_heavy": { "matched": true, ... },
        "cash_flow_optimizer": { "matched": false, ... },
        "young_professional": { "matched": false, ... }
      }
    },
    "180d": { ... }
  }
}
```

---

## What Makes This Special

### Complete Transparency
- Unlike typical "black box" algorithms, you can see:
  - WHY a persona was assigned
  - WHAT other personas qualified
  - WHICH signal values triggered matches
  - HOW all 6 personas were evaluated

### Audit Trail
- Every assignment stored in database with:
  - Unique assignment ID
  - Timestamp
  - Complete evidence
  - Reasoning explanation

### Time Window Comparison
- See how user behavior differs:
  - 30d = recent patterns
  - 180d = longer-term trends
  - Users can qualify for different personas in different windows!

### Priority-Based Selection
- Highest urgency wins:
  - Priority 1 (High Utilization) = Immediate debt crisis
  - Priority 2 (Irregular Income) = Cash flow instability
  - Priority 3 (Low Savings) = Financial vulnerability
  - Priority 4 (Subscription Heavy) = Optimization opportunity
  - Priority 5 (Cash Flow Optimizer) = Growth opportunity
  - Priority 6 (Young Professional) = Foundation building

---

## Troubleshooting

### "No Assignments Found"
- Run: `python test_persona_assignments_sample.py`
- This will assign personas to the first 5 users

### Server Not Running
```bash
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --reload
```

### Wrong User ID Format
- Format: `user_MASKED_###` (e.g., `user_MASKED_000`)
- Valid range: 000-099 (100 users total)

### Want More Users?
```bash
python test_persona_assignments.py
# Assigns personas to all 100 users (takes ~2 minutes)
```

---

## Fun Things to Try

1. **Compare Time Windows**: Enter a user ID without selecting a window to see both 30d and 180d assignments side-by-side

2. **Explore Evidence**: Click to expand match evidence and see how close users were to matching other personas

3. **Find Edge Cases**: Look for users with many qualifying personas (shows how prioritization works)

4. **Test Different Personas**: Try users from different persona groups to see how the UI adapts (different gradient colors!)

5. **Check Unmatched Personas**: Look at the evidence for personas that didn't match to understand the criteria

---

## Next Steps

After testing the UI:

1. **Run Full Test Suite**:
   ```bash
   pytest tests/test_persona_*.py -v
   # Should show: 91 tests passing ✅
   ```

2. **Review Documentation**:
   - `/EPIC_3_COMPLETE.md` - Comprehensive completion doc
   - `/docs/stories/3-5-custom-personas-validation.md` - Story 3.5 details

3. **Ready for Production**: The system is production-ready!

---

**Happy Testing!** 🎉

If you find any issues or have questions, all the code is well-documented and tested!
