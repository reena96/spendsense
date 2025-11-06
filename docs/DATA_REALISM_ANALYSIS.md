# Data Realism Analysis: Synthetic vs Real Data

## Executive Summary

**Finding**: Our synthetic data distribution does NOT match real-world patterns. This creates unrealistic demo scenarios where most users show zeros for credit/savings.

### Real Data (transactions_formatted.csv - 191 customers)
- **96% of users have credit cards** (185/191)
- **51% of transactions show balances >$5K** (indicating savings potential)
- **9% have low balances <$1K** (minimal emergency fund)
- **Payment mix**: 41% credit card, 30% debit, 14% digital wallet, 9% cash, 4% bank transfer

### Synthetic Data (100 users)
- **57% of users have credit cards** (57/100) ❌ Should be ~90%
- **20% have savings accounts** (20/100) ❌ Needs validation
- **Persona distribution is too segmented** ❌ Real users have mixed behaviors

## Critical Issues

### Issue 1: Credit Card Coverage Too Low (57% vs 96%)

**Current Distribution by Persona:**
```
Persona              Users  With Credit  With Savings
─────────────────────────────────────────────────────
control                 20      8 (40%)      0 (0%)
high_utilization        20     20 (100%)     0 (0%)
savings_builder         20     13 (65%)     20 (100%)
subscription_heavy      20     13 (65%)      0 (0%)
variable_income         20      3 (15%)      0 (0%)
─────────────────────────────────────────────────────
TOTAL                  100     57 (57%)     20 (20%)
```

**Real-World Expectation:**
- ~90-95% of users should have at least one credit card
- Credit cards are ubiquitous in modern banking

**Impact on Demo:**
- 43% of randomly selected users show "0 credit cards" ❌
- This makes the system look broken
- Demo requires cherry-picking specific user IDs

### Issue 2: Persona Segregation Too Strict

**Current Problem:**
- Each persona has distinct, non-overlapping behaviors
- Real users exhibit multiple behaviors simultaneously
- Example: A high_utilization user can ALSO have savings (paying down debt while building emergency fund)

**Real-World Pattern:**
- Users have credit cards regardless of financial health
- Savings varies by income level and habits, not binary yes/no
- Subscriptions are universal (Netflix, Spotify, utilities)
- Income patterns affect behaviors but don't eliminate others

### Issue 3: Savings Distribution Unclear

**Question**: Is 20% savings account ownership realistic?

**Real Data Insight:**
- 51% of transactions show balances >$5K
- This suggests many users maintain savings buffers
- However, high checking balance ≠ savings account

**Industry Research Needed:**
- What % of Americans have dedicated savings accounts?
- Typical emergency fund amounts by income bracket
- Relationship between income and savings behavior

## Recommendations

### 1. **Increase Credit Card Coverage to 90%** ✅ PRIORITY

```sql
-- Should update to:
control:            18/20 with credit (90%)
high_utilization:   20/20 with credit (100%) ✅ Already correct
savings_builder:    18/20 with credit (90%)
subscription_heavy: 19/20 with credit (95%)
variable_income:    15/20 with credit (75%) -- Lower due to credit access issues
```

**Why these numbers:**
- high_utilization: 100% (they need credit to show high utilization)
- variable_income: 75% (gig workers may have limited credit access)
- Others: 90-95% (standard American banking pattern)

### 2. **Add Multi-Dimensional Behaviors**

Instead of strict personas, users should have **behavior scores**:

```python
Example User Profile:
- user_MASKED_042
- credit_utilization: 0.65 (high)
- has_savings: True
- emergency_fund_months: 2.3
- subscription_spend_ratio: 0.25
- income_stability: "regular"
```

This user would show:
- ✅ Credit utilization signals (65%)
- ✅ Savings signals ($X balance, 2.3 months)
- ✅ Subscription signals (25% of spend)
- ✅ Income signals (biweekly regularity)

### 3. **Validate Savings Rates Against Research**

**Need to verify:**
- What % of Americans have savings accounts vs just checking?
- Is 20% too low or reasonable?
- Should we assume high checking balance = implicit savings?

### 4. **Fix populate_accounts.py to Match Real Patterns**

Current script gives:
- 100 checking accounts (100%)
- 57 credit accounts (57%)
- 20 savings accounts (20%)

Should be:
- 100 checking accounts (100%) ✅
- 90 credit accounts (90%) ⬆️ Increase
- 40-60 savings accounts (40-60%?) ⬆️ Validate & increase

## Impact on User Experience

### Current Demo Flow (BROKEN):
1. User opens UI
2. Tries random user: user_MASKED_005
3. Sees: 0 credit cards, 0 savings, subscriptions work, income works
4. Thinks: "Why is credit/savings broken?" ❌

### Fixed Demo Flow:
1. User opens UI
2. Tries ANY random user
3. Sees: 1-2 credit cards, potentially savings, subscriptions, income all work
4. Thinks: "This looks realistic!" ✅

## Action Items

### Immediate (P0):
1. ✅ Document the issue (this file)
2. ⬜ Update populate_accounts.py to create 90 credit accounts
3. ⬜ Update fix_credit_and_savings.py to link all 90
4. ⬜ Research typical savings account ownership rates
5. ⬜ Update savings account creation to realistic %

### Short-term (P1):
6. ⬜ Add multi-dimensional behavior scoring
7. ⬜ Update demo guide with realistic expectations
8. ⬜ Add "data quality" API endpoint showing coverage

### Long-term (P2):
9. ⬜ Replace rigid personas with behavior profiles
10. ⬜ Generate correlated behaviors (e.g., high income → more likely to have savings)
11. ⬜ Add time-series savings growth patterns

## Technical Debt

**Current Architecture Issue:**
- Personas defined at user creation time
- Account creation happens separately
- No correlation between persona intent and actual account setup

**Better Approach:**
```python
class UserProfile:
    def __init__(self, persona_weights):
        self.credit_score_range = (650, 750)
        self.income_level = "medium"
        self.has_credit_card_probability = 0.90
        self.has_savings_probability = 0.45
        self.subscription_intensity = "medium"

    def generate_accounts(self):
        # Probabilistic account generation
        # Ensures realistic distribution
```

## Conclusion

**The zeros are NOT bugs - they're realistic for users without those account types.**

**The PROBLEM is that too few users have credit/savings accounts, making the demo unconvincing.**

**Fix**: Increase credit card coverage from 57% → 90% and validate/increase savings coverage.

---

**Date**: 2025-11-04
**Analyst**: Claude
**Real Data Source**: /Users/reena/Downloads/transactions_formatted.csv (191 customers, 5000 transactions)
