# Pattern Comparison Report: Real vs Synthetic Data

**Date**: 2025-11-04
**Real Data Source**: transactions_formatted.csv (191 customers, 5000 transactions)
**Synthetic Data Source**: spendsense.db (100 users, 19,821 transactions)

---

## Executive Summary

Comprehensive pattern analysis reveals **significant structural differences** between real and synthetic data, with some fundamental misalignments that affect behavioral signal detection accuracy.

### Critical Findings:
- ✅ **Day of week distribution**: Nearly identical (evenly distributed)
- ❌ **Transaction volume**: 7.5x higher in synthetic (198 tx/user vs 26 tx/user)
- ❌ **Transaction amounts**: Negative mean in synthetic due to accounting conventions
- ❌ **Payment methods**: Different taxonomies (payment_method vs payment_channel)
- ⚠️ **Account balances**: Synthetic 4.3x higher ($21,874 vs $5,088 mean)
- ⚠️ **Date range**: Real 2024 full year, Synthetic 6 months (May-Nov 2025)

---

## Detailed Comparison

### 1. Transaction Volume

| Metric | Real Data | Synthetic Data | Ratio |
|--------|-----------|----------------|-------|
| **Total transactions** | 5,000 | 19,821 | 3.96x |
| **Total users/customers** | 191 | 100 | 0.52x |
| **Transactions per user** | 26.2 | 198.2 | **7.57x** ❌ |
| **Median tx per user** | 19.0 | 194.5 | 10.24x |
| **Min tx per user** | 1 | 150 | - |
| **Max tx per user** | 240 | 264 | 1.10x |

**Analysis:**
- Synthetic data has **7.5x more transactions per user** than real data
- Real data shows high variability (1-240), synthetic is more uniform (150-264)
- **This indicates synthetic data generation is over-active**

**Impact on Behavioral Signals:**
- Subscription detection may find MORE subscriptions (more data = more patterns)
- Income detection benefits from more data points (more accurate frequency)
- Credit/savings patterns appear more stable (less variability)

**Recommendation:** ⚠️ Consider reducing synthetic transaction volume to 30-50 tx/user to match real-world patterns

---

### 2. Transaction Amounts

| Metric | Real Data | Synthetic Data | Observation |
|--------|-----------|----------------|-------------|
| **Mean** | $59.14 | $-3.85 | ❌ Negative due to accounting |
| **Median** | $30.56 | $-97.59 | ❌ Negative |
| **Min** | $-291.89 | $-7,144.75 | Much larger in synthetic |
| **Max** | $1,923.29 | $23,970.29 | 12x larger in synthetic |
| **Std Dev** | $113.99 | $1,193.71 | 10x higher variability |

**Analysis:**
- **Negative means**: Synthetic uses debit accounting (negative = expense, positive = income)
- **Real data uses credit accounting** (positive = expense)
- Synthetic has much larger transaction amounts (max $23K vs $1.9K)
- Synthetic has 10x higher variability

**Impact on Behavioral Signals:**
- Amount-based thresholds need adjustment for synthetic data
- Subscription detection (cadence-based) less affected
- Income detection affected by large payroll amounts ($23K salary deposit!)
- Credit utilization calculations use account balances (not tx amounts), so minimal impact

**Recommendation:** ⚠️ Normalize synthetic amounts to real-world ranges ($10-500 typical, max $2K)

---

### 3. Payment Methods vs Payment Channels

#### Real Data - Payment Methods
| Method | Count | Percentage |
|--------|-------|------------|
| credit_card | 2,074 | **41.5%** |
| debit_card | 1,516 | **30.3%** |
| digital_wallet | 718 | 14.4% |
| cash | 474 | 9.5% |
| bank_transfer | 218 | 4.4% |

#### Synthetic Data - Payment Channels
| Channel | Count | Percentage |
|---------|-------|------------|
| in store | 14,639 | **73.9%** |
| online | 3,483 | **17.6%** |
| other | 1,699 | 8.6% |

**Analysis:**
- **Different taxonomies**: Real uses "how you paid", synthetic uses "where you paid"
- Real: 41.5% credit card, but synthetic doesn't track credit vs debit
- Synthetic's "in store" could be credit, debit, or cash
- **Cannot directly compare** - different dimensions

**Impact on Behavioral Signals:**
- Credit utilization relies on accounts table (not payment method) ✅ No impact
- Subscription patterns rely on merchant + cadence ✅ No impact
- Payment method preferences cannot be analyzed in synthetic data

**Recommendation:** ✅ Accept difference - payment_channel serves different purpose (Plaid standard)

---

### 4. Account Balance Distribution

| Metric | Real Data | Synthetic Data | Ratio |
|--------|-----------|----------------|-------|
| **Mean** | $5,087.90 | $21,874.31 | **4.30x** ❌ |
| **Median** | $5,109.32 | $23,112.17 | 4.52x |
| **Min** | $100.08 | $1,064.80 | 10.6x |
| **Max** | $9,999.40 | $50,953.53 | 5.10x |

#### Percentile Comparison

| Percentile | Real Data | Synthetic Data | Synthetic/Real |
|------------|-----------|----------------|----------------|
| 10th | $1,067.35 | $4,698.89 | 4.40x |
| 25th | $2,657.17 | $14,636.87 | **5.51x** |
| 50th (Median) | $5,109.64 | $23,167.32 | 4.53x |
| 75th | $7,590.68 | $29,559.11 | 3.89x |
| 90th | $8,981.66 | $36,320.29 | 4.04x |
| 95th | $9,503.53 | $40,005.00 | 4.21x |
| 99th | $9,901.98 | $49,285.67 | 4.98x |

**Low Balance Frequency:**
- Real: 9.3% have balances <$1K
- Synthetic: 0% (minimum is $1,064.80)

**Analysis:**
- Synthetic balances are **4-5x higher across all percentiles**
- Synthetic has NO low-balance accounts (<$1K)
- This suggests **synthetic users are wealthier** than real population

**Impact on Behavioral Signals:**
- ❌ **Savings detection**: Emergency fund calculations assume higher income
- ❌ **Credit utilization**: Higher balances may mask financial stress
- ❌ **Income stability**: Higher buffers hide cash flow problems
- ❌ **Subscription burden**: $100/month subscription looks smaller with $20K balance

**Recommendation:** ⚠️ **CRITICAL** - Scale down synthetic balances by 4-5x to match real-world distribution

---

### 5. Merchant Categories

#### Real Data - Top 10 Categories
| Category | Count | Percentage |
|----------|-------|------------|
| other | 560 | 11.2% |
| retail | 535 | 10.7% |
| utilities | 520 | 10.4% |
| healthcare | 512 | 10.2% |
| restaurant | 498 | 10.0% |
| entertainment | 497 | 9.9% |
| groceries | 483 | 9.7% |
| transportation | 476 | 9.5% |
| online_shopping | 460 | 9.2% |
| gas_station | 459 | 9.2% |

**Real data: Evenly distributed** (9-11% each)

#### Synthetic Data - Personal Finance Categories
| Category | Count | Percentage |
|----------|-------|------------|
| FOOD_AND_DRINK_RESTAURANTS | 6,267 | **31.6%** ❌ |
| FOOD_AND_DRINK_GROCERIES | 5,123 | **25.8%** ❌ |
| TRANSPORTATION_GAS | 2,533 | 12.8% |
| GENERAL_SERVICES_SUBSCRIPTION | 2,067 | 10.4% |
| HOME_UTILITIES | 1,232 | 6.2% |
| INCOME_WAGES | 1,114 | 5.6% |
| GENERAL_MERCHANDISE_GENERAL | 900 | 4.5% |
| LOAN_PAYMENTS_CREDIT_CARD_PAYMENT | 461 | 2.3% |
| TRANSFER_OUT_SAVINGS | 124 | 0.6% |

**Synthetic data: Heavily skewed** (57% food!)

**Analysis:**
- Real data: Balanced spending across categories
- Synthetic data: **57% of spending is food** (restaurants 32% + groceries 26%)
- This is **unrealistic** - typical food spending is 10-15% of budget
- Healthcare, entertainment, online shopping underrepresented in synthetic

**Impact on Behavioral Signals:**
- ✅ Subscription detection works (10.4% subscriptions realistic)
- ❌ Category-based insights skewed (food dominates)
- ❌ Lifestyle profiling inaccurate (everyone appears to eat out constantly)

**Recommendation:** ⚠️ **HIGH PRIORITY** - Rebalance synthetic category distribution to match real data (10-11% per category)

---

### 6. Temporal Patterns

#### Day of Week Distribution

| Day | Real % | Synthetic % | Difference |
|-----|--------|-------------|------------|
| Monday | 13.6% | 14.5% | +0.9% ✅ |
| Tuesday | 14.2% | 14.3% | +0.1% ✅ |
| Wednesday | 14.1% | 14.0% | -0.1% ✅ |
| Thursday | 14.9% | 13.6% | -1.3% ✅ |
| Friday | 14.0% | 14.6% | +0.6% ✅ |
| Saturday | 14.8% | 14.2% | -0.6% ✅ |
| Sunday | 14.5% | 14.7% | +0.2% ✅ |

**Analysis:** ✅ **EXCELLENT MATCH** - Both datasets show evenly distributed transactions across days

#### Hour of Day Distribution

**Real Data:**
- Peak: 6am (5.2%) - morning coffee/commute
- Trough: Multiple hours ~3.7-3.9%
- Relatively flat distribution (3.7-5.2%)
- No strong hourly pattern

**Synthetic Data:**
- Not analyzed (no hour column in transactions table)
- Would need to enhance synthetic data generation

**Recommendation:** ⚠️ Add hourly timestamps to synthetic data for more realistic patterns

---

### 7. Transaction Types

#### Real Data Transaction Types
| Type | Count | Percentage |
|------|-------|------------|
| purchase | 3,190 | **63.8%** |
| refund | 515 | 10.3% |
| transfer | 504 | 10.1% |
| fee | 279 | 5.6% |
| deposit | 270 | 5.4% |
| withdrawal | 242 | 4.8% |

**Synthetic Data:**
- No "transaction_type" field in schema
- All transactions treated as purchases/expenses
- Income detected by category (INCOME_WAGES)

**Analysis:**
- Real data explicitly tags transaction types
- Synthetic infers type from amount sign and category
- Missing: refunds, fees, withdrawals in synthetic

**Impact on Behavioral Signals:**
- ✅ Income detection works (uses category)
- ❌ Cannot analyze refund patterns
- ❌ Cannot analyze fee burden (overdraft fees, ATM fees)
- ❌ Cannot distinguish withdrawals from purchases

**Recommendation:** ⚠️ Add transaction_type field to synthetic schema

---

### 8. Fraud Detection

| Metric | Real Data | Synthetic Data |
|--------|-----------|----------------|
| **Fraud transactions** | 87 (1.74%) | Not tracked |
| **Fraud flag** | Yes (is_fraud column) | No |

**Recommendation:** ⚠️ Add fraud simulation to synthetic data (2% fraud rate) for testing fraud detection features

---

## Impact Assessment on Epic 2 Features

### Story 2.1: Time Window Aggregation ✅
**Status:** Minimal impact
**Reason:** Works with any transaction volume, date range handled correctly

### Story 2.2: Subscription Detection ⚠️
**Status:** Moderate impact
**Issues:**
- Higher transaction volume = more false positives possible
- Food spending dominance may mask other subscriptions
**Accuracy:** Likely **overstates** subscription count due to high transaction volume

### Story 2.3: Savings Behavior ❌
**Status:** HIGH impact
**Issues:**
- Balances 4-5x too high → emergency fund calculations unrealistic
- Emergency fund of "2 months" with $20K balance looks good
- But that same user spending $200/month on subscriptions is only 1% of balance
**Accuracy:** **Significantly overstates** financial health

### Story 2.4: Credit Utilization ✅
**Status:** Low impact
**Reason:** Uses credit limits and balances (already fixed), not transaction amounts

### Story 2.5: Income Stability ⚠️
**Status:** Moderate impact
**Issues:**
- Huge income deposits ($23K max) vs real ($1.9K max)
- May indicate annual bonuses vs biweekly paychecks
- More transactions = more accurate frequency detection (benefit)
**Accuracy:** Frequency detection MORE accurate, amount-based analysis LESS accurate

### Story 2.6: Behavioral Summary ⚠️
**Status:** Moderate impact
**Reason:** Aggregates issues from all stories above

---

## Priority Recommendations

### P0 - CRITICAL (Data Generation Bugs)
1. **Reduce transaction volume** from 198 tx/user to 30-50 tx/user
2. **Scale down account balances** by 4-5x (currently 4.5x too high)
3. **Rebalance category distribution** (food is 57%, should be 15%)

### P1 - HIGH (Realism Improvements)
4. **Normalize transaction amounts** to real ranges ($10-500 typical, max $2K)
5. **Fix negative amount accounting** or document convention clearly
6. **Add transaction_type field** (purchase, refund, fee, etc.)

### P2 - MEDIUM (Feature Completeness)
7. **Add hourly timestamps** for intraday pattern analysis
8. **Add fraud simulation** (2% fraud rate)
9. **Add amount variability** (currently too uniform at high end)

### P3 - LOW (Nice to Have)
10. Accept payment_channel vs payment_method difference (Plaid standard)
11. Document accounting conventions (negative = expense)
12. Add more merchant diversity (top merchant has 1000+ transactions)

---

## Validation Checklist

After implementing recommendations, validate:

- [ ] Mean balance: $4K-6K (currently $21K ❌)
- [ ] Transactions per user: 25-50 (currently 198 ❌)
- [ ] Food spending: 10-15% (currently 57% ❌)
- [ ] Low balance accounts: 5-10% <$1K (currently 0% ❌)
- [ ] Mean transaction: $40-70 (currently negative ❌)
- [ ] Day of week: Even distribution ✅
- [ ] Date range: 6-12 months ✅
- [ ] Credit card coverage: 90%+ ✅ (fixed)
- [ ] Savings account coverage: 35-45% ✅ (fixed)

---

## Conclusion

### Matches ✅
- Day of week distribution
- Credit account coverage (after fix)
- Savings account coverage (after fix)
- Date range (acceptable)

### Critical Misses ❌
1. **Account balances 4.5x too high** → Savings behavior analysis unrealistic
2. **Transaction volume 7.5x too high** → Subscription detection may overstate
3. **Category skew (57% food)** → Spending pattern analysis inaccurate

### Recommendation Priority
**Focus on P0 fixes first** - These three issues fundamentally affect the accuracy of Epic 2's behavioral signal detection. Without these fixes, demos will show:
- Users with $20K balances but "financial stress"
- 200+ transactions creating noise in pattern detection
- Everyone appearing to eat out constantly

**Timeline:** P0 fixes should be implemented before production deployment. Current data suitable for feature development and testing, but needs calibration for realistic demos.

---

**Analysis Date:** 2025-11-04
**Analyst:** Claude
**Tools:** scripts/analyze_patterns.py
**Datasets:** transactions_formatted.csv (real), spendsense.db (synthetic)
