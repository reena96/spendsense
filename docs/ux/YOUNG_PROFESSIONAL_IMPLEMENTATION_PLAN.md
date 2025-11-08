# Young Professional Persona - Complete Implementation Plan

**Status**: Partially Implemented (Enum added, characteristics pending)
**Priority**: HIGH - Persona page currently broken due to incomplete implementation
**Estimated Time**: 30 minutes total

---

## 🚨 CRITICAL ISSUE

**Current State**: The Personas page shows error: "Error loading personas: The string did not match the expected pattern."

**Root Cause**: We added `YOUNG_PROFESSIONAL` to the `PersonaType` enum but did NOT complete the implementation in `spendsense/personas/definitions.py`. This broke the persona loading.

**Fix Required**: Complete all 4 steps below to restore functionality and add young_professional support.

---

## 📋 IMPLEMENTATION CHECKLIST

### Phase 1: Fix Persona Definitions (CRITICAL - 10 min)

**File**: `spendsense/personas/definitions.py`

- [ ] **Step 1.1**: Add `PERSONA_YOUNG_PROFESSIONAL` characteristics after `PERSONA_CONTROL` (around line 230)
- [ ] **Step 1.2**: Add `YOUNG_PROFESSIONAL` to `PERSONA_REGISTRY` dict (line 233)
- [ ] **Step 1.3**: Add `YOUNG_PROFESSIONAL` to `PERSONA_DESCRIPTIONS` dict (line 259)
- [ ] **Step 1.4**: Verify personas page loads without error

### Phase 2: Generate Test Users (OPTIONAL - 15 min)

**Goal**: Create 17 young_professional users in database

- [ ] **Step 2.1**: Create `scripts/add_young_professional_users.py`
- [ ] **Step 2.2**: Run script to generate users with transactions and accounts
- [ ] **Step 2.3**: Verify database has young_professional users

### Phase 3: Validation (5 min)

- [ ] **Step 3.1**: Check personas page displays all 6 personas
- [ ] **Step 3.2**: Test young_professional user in signal dashboard
- [ ] **Step 3.3**: Generate recommendations for young_professional user
- [ ] **Step 3.4**: Run persona-related tests

---

## 📝 DETAILED IMPLEMENTATION STEPS

### STEP 1.1: Add PERSONA_YOUNG_PROFESSIONAL Characteristics

**File**: `spendsense/personas/definitions.py`
**Location**: After `PERSONA_CONTROL` definition (around line 230)

```python
PERSONA_YOUNG_PROFESSIONAL = PersonaCharacteristics(
    # Entry-level to early career income
    min_annual_income=Decimal("25000"),
    max_annual_income=Decimal("55000"),
    income_stability="regular",
    median_pay_gap_days=None,  # Regular paycheck

    # Low credit limits (< $3000 per Epic 3 Story 3.5 criteria)
    min_credit_limit=Decimal("500"),
    max_credit_limit=Decimal("2800"),
    target_credit_utilization_min=Decimal("0.10"),
    target_credit_utilization_max=Decimal("0.30"),

    # Building savings habit
    target_savings_monthly_min=Decimal("50"),
    target_savings_monthly_max=Decimal("250"),

    # Few subscriptions (budget-conscious)
    subscription_count_min=1,
    subscription_count_max=4,

    # Basic account structure
    has_checking=True,
    has_savings=True,
    credit_card_count_min=0,  # May not have credit yet
    credit_card_count_max=1,  # Max 1 starter card

    # Low balances (building from scratch)
    checking_balance_months=Decimal("0.4"),
    savings_balance_months=Decimal("0.6"),
)
```

**Rationale for Values**:
- **Income**: $25K-$55K reflects entry-level salaries (Epic 3 criteria: early career)
- **Credit Limits**: Max $2800 (below $3000 threshold from Epic 3 Story 3.5)
- **Utilization**: 10-30% (learning healthy credit habits)
- **Savings**: $50-$250/month (modest but building)
- **Subscriptions**: 1-4 (budget-conscious, fewer than other personas)
- **Credit Cards**: 0-1 (may not have credit yet or just starter card)
- **Balances**: Low (0.4 months checking, 0.6 months savings - building from scratch)

---

### STEP 1.2: Update PERSONA_REGISTRY

**File**: `spendsense/personas/definitions.py`
**Location**: Line ~233

**FIND THIS**:
```python
PERSONA_REGISTRY: dict[PersonaType, PersonaCharacteristics] = {
    PersonaType.HIGH_UTILIZATION: PERSONA_HIGH_UTILIZATION,
    PersonaType.VARIABLE_INCOME: PERSONA_VARIABLE_INCOME,
    PersonaType.SUBSCRIPTION_HEAVY: PERSONA_SUBSCRIPTION_HEAVY,
    PersonaType.SAVINGS_BUILDER: PERSONA_SAVINGS_BUILDER,
    PersonaType.CONTROL: PERSONA_CONTROL,
}
```

**REPLACE WITH**:
```python
PERSONA_REGISTRY: dict[PersonaType, PersonaCharacteristics] = {
    PersonaType.HIGH_UTILIZATION: PERSONA_HIGH_UTILIZATION,
    PersonaType.VARIABLE_INCOME: PERSONA_VARIABLE_INCOME,
    PersonaType.SUBSCRIPTION_HEAVY: PERSONA_SUBSCRIPTION_HEAVY,
    PersonaType.SAVINGS_BUILDER: PERSONA_SAVINGS_BUILDER,
    PersonaType.YOUNG_PROFESSIONAL: PERSONA_YOUNG_PROFESSIONAL,  # <-- ADD THIS LINE
    PersonaType.CONTROL: PERSONA_CONTROL,
}
```

---

### STEP 1.3: Update PERSONA_DESCRIPTIONS

**File**: `spendsense/personas/definitions.py`
**Location**: Line ~259

**FIND THIS**:
```python
PERSONA_DESCRIPTIONS = {
    PersonaType.HIGH_UTILIZATION: (
        "High credit utilization (60-80%). Moderate income but carrying high balances. "
        "Needs guidance on debt management and interest costs."
    ),
    PersonaType.VARIABLE_INCOME: (
        "Irregular income patterns with >45 day median pay gaps. Income volatility creates "
        "cash flow challenges. Needs guidance on budgeting for irregular income."
    ),
    PersonaType.SUBSCRIPTION_HEAVY: (
        "5-10 recurring subscriptions consuming significant monthly budget. May benefit from "
        "subscription audit and optimization recommendations."
    ),
    PersonaType.SAVINGS_BUILDER: (
        "Strong savings habit with >$200/month contributions. Low credit utilization (<30%). "
        "Good financial health, may benefit from investment and optimization guidance."
    ),
    PersonaType.CONTROL: (
        "Mixed financial behaviors that don't strongly align with any single persona. "
        "Represents baseline/average user for comparison."
    ),
}
```

**REPLACE WITH**:
```python
PERSONA_DESCRIPTIONS = {
    PersonaType.HIGH_UTILIZATION: (
        "High credit utilization (60-80%). Moderate income but carrying high balances. "
        "Needs guidance on debt management and interest costs."
    ),
    PersonaType.VARIABLE_INCOME: (
        "Irregular income patterns with >45 day median pay gaps. Income volatility creates "
        "cash flow challenges. Needs guidance on budgeting for irregular income."
    ),
    PersonaType.SUBSCRIPTION_HEAVY: (
        "5-10 recurring subscriptions consuming significant monthly budget. May benefit from "
        "subscription audit and optimization recommendations."
    ),
    PersonaType.SAVINGS_BUILDER: (
        "Strong savings habit with >$200/month contributions. Low credit utilization (<30%). "
        "Good financial health, may benefit from investment and optimization guidance."
    ),
    PersonaType.YOUNG_PROFESSIONAL: (  # <-- ADD THIS ENTRY
        "Limited transaction history (<180 days) or low credit limits (<$3000). "
        "Entry-level income ($25K-$55K), building financial foundation. Needs credit building, "
        "budgeting basics, and financial literacy guidance."
    ),
    PersonaType.CONTROL: (
        "Mixed financial behaviors that don't strongly align with any single persona. "
        "Represents baseline/average user for comparison."
    ),
}
```

---

### STEP 1.4: Verify Fix

**Action**: Refresh the personas page at `http://localhost:8000/` and click "Personas" tab

**Expected Result**: Page should display all 6 personas without error:
1. High Credit Utilization
2. Variable Income Budgeter
3. Subscription-Heavy
4. Savings Builder
5. Young Professional / Credit Builder ← NEW
6. Control Group

---

## STEP 2: Generate Young Professional Test Users (OPTIONAL)

### STEP 2.1: Create User Generation Script

**File**: `scripts/add_young_professional_users.py`

```python
#!/usr/bin/env python3
"""
Generate young_professional persona users in the database.

Adds 17 young_professional users to balance the existing 20 of each other persona.
Final distribution: 20 high_util, 20 variable_income, 20 subscription, 20 savings, 17 young_prof, 20 control = 117 total
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from spendsense.generators.profile_generator import ProfileGenerator
from spendsense.generators.account_generator import AccountGenerator
from spendsense.generators.transaction_generator import TransactionGenerator
from spendsense.generators.liability_generator import LiabilityGenerator
from spendsense.personas.definitions import PersonaType
from spendsense.config.database import get_db_session

def main():
    """Generate 17 young_professional users."""

    print("🎯 Generating 17 Young Professional users...")

    session = get_db_session()

    try:
        # Initialize generators
        profile_gen = ProfileGenerator()
        account_gen = AccountGenerator()
        transaction_gen = TransactionGenerator()
        liability_gen = LiabilityGenerator()

        # Generate 17 young_professional users
        for i in range(17):
            user_number = 100 + i  # Start from user_MASKED_100
            user_id = f"user_MASKED_{user_number:03d}"

            print(f"  Creating {user_id}...")

            # Generate profile
            profile = profile_gen.generate_profile(
                user_id=user_id,
                persona_type=PersonaType.YOUNG_PROFESSIONAL
            )

            # Generate accounts
            accounts = account_gen.generate_accounts(profile)

            # Generate transactions
            transactions = transaction_gen.generate_transactions(
                profile=profile,
                accounts=accounts,
                days=365  # Full year of history (but will be limited by persona characteristics)
            )

            # Generate liabilities
            liabilities = liability_gen.generate_liabilities(profile, accounts)

            # Add to session
            session.add(profile)
            for account in accounts:
                session.add(account)
            for txn in transactions:
                session.add(txn)
            for liability in liabilities:
                session.add(liability)

            # Commit every 5 users to avoid huge transactions
            if (i + 1) % 5 == 0:
                session.commit()
                print(f"  ✓ Committed {i + 1}/17 users")

        # Final commit
        session.commit()

        print("\n✅ Successfully generated 17 young_professional users!")
        print(f"   User IDs: user_MASKED_100 through user_MASKED_116")

        # Verify
        from spendsense.ingestion.database_writer import User
        count = session.query(User).filter(User.persona == "young_professional").count()
        print(f"\n📊 Total young_professional users in database: {count}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
```

### STEP 2.2: Run the Script

```bash
cd /Users/reena/gauntletai/spendsense
source venv/bin/activate
python scripts/add_young_professional_users.py
```

**Expected Output**:
```
🎯 Generating 17 Young Professional users...
  Creating user_MASKED_100...
  Creating user_MASKED_101...
  ...
  ✓ Committed 5/17 users
  ...
✅ Successfully generated 17 young_professional users!
   User IDs: user_MASKED_100 through user_MASKED_116
📊 Total young_professional users in database: 17
```

### STEP 2.3: Verify Database

```bash
sqlite3 data/processed/spendsense.db "SELECT persona, COUNT(*) as count FROM users GROUP BY persona ORDER BY count DESC;"
```

**Expected Output**:
```
high_utilization|20
variable_income|20
subscription_heavy|20
savings_builder|20
control|20
young_professional|17
```

---

## STEP 3: Validation & Testing

### STEP 3.1: Check Personas Page

**URL**: `http://localhost:8000/` → Click "Personas" tab

**Expected**: All 6 personas displayed with characteristics

### STEP 3.2: Test Signal Dashboard

**URL**: `http://localhost:3000/signals`

1. Search for user: `user_MASKED_100`
2. Verify persona displayed as "Young Professional / Credit Builder"
3. Check signals show appropriate values (low credit limits, modest income, etc.)

### STEP 3.3: Test Recommendations

**URL**: `http://localhost:8000/recommendations/user_MASKED_100?time_window=30d&generate=true`

**Expected**: Recommendations should include young_professional content:
- Credit building education
- Budgeting basics
- Financial literacy foundations
- Starter credit card offers

### STEP 3.4: Run Tests

```bash
# Test persona registry loads correctly
pytest tests/test_persona_registry.py -v

# Test persona matching with young_professional
pytest tests/test_persona_matcher.py -v

# Test profile generator with young_professional
pytest tests/test_profile_generator.py -k young_professional -v
```

---

## ✅ WHAT'S ALREADY COMPLETE (No Changes Needed)

1. **spendsense/config/personas.yaml** ✅
   - young_professional fully defined (lines 154-185)
   - Priority: 6, Criteria, Focus areas, Content types

2. **spendsense/config/recommendations.yaml** ✅
   - 8 educational content items for young_professional
   - Lines: 654, 671, 690, 709, 726, 743, 761, 777

3. **spendsense/config/partner_offers.yaml** ✅
   - 7 partner offers for young_professional
   - Lines: 76, 156, 183, 208, 234, 261, 289

4. **spendsense/personas/registry.py** ✅
   - Already loads all personas from YAML

5. **spendsense/personas/definitions.py** ⚠️ PARTIALLY COMPLETE
   - ✅ PersonaType enum has YOUNG_PROFESSIONAL
   - ❌ Missing characteristics definition
   - ❌ Missing registry entry
   - ❌ Missing description entry

6. **UI Components** ✅
   - All components use dynamic persona display
   - No hardcoded persona lists

---

## 📊 CURRENT STATE SUMMARY

### What Works:
- ✅ Persona matching/classification (YAML-based)
- ✅ Recommendation content for young_professional
- ✅ Partner offers for young_professional
- ✅ UI persona display (dynamic)

### What's Broken:
- ❌ Personas page (enum/dict mismatch)
- ❌ Cannot generate young_professional test users (missing characteristics)
- ❌ Profile generator fails with young_professional enum

### After Phase 1 (Steps 1.1-1.4):
- ✅ Personas page works
- ✅ Can generate young_professional users
- ⚠️ Still no young_professional users in database

### After Phase 2 (Steps 2.1-2.3):
- ✅ 17 young_professional test users in database
- ✅ Full system coverage for all 6 personas

---

## 🎯 MINIMUM VIABLE FIX

**If time is limited**, complete **ONLY Phase 1** (Steps 1.1-1.4) to:
1. Fix the broken personas page
2. Restore system functionality
3. Enable young_professional support

**Phase 2 is optional** - it adds test users but is not required for basic functionality.

---

## 🔍 VERIFICATION CHECKLIST

After completing implementation, verify:

- [ ] Personas page loads without error
- [ ] All 6 personas displayed in personas page
- [ ] Backend logs show no errors on startup
- [ ] Profile generator accepts PersonaType.YOUNG_PROFESSIONAL
- [ ] (If Phase 2 done) Database has young_professional users
- [ ] (If Phase 2 done) Signal dashboard displays young_professional users correctly
- [ ] (If Phase 2 done) Recommendations generated for young_professional

---

## 📚 REFERENCE DOCUMENTATION

- **Epic 3 PRD**: `/Users/reena/gauntletai/spendsense/docs/prd/epic-3-persona-assignment-system.md`
- **Story 3.1**: `/Users/reena/gauntletai/spendsense/docs/stories/3-1-persona-definition-registry.md`
- **Story 3.5**: Epic 3 Story 3.5 defines Persona 6 (Young Professional) criteria
- **Personas YAML**: `/Users/reena/gauntletai/spendsense/spendsense/config/personas.yaml` (lines 154-185)

---

## 🚀 READY TO IMPLEMENT

This plan is complete and ready for execution. Follow the steps in order, verify after each phase, and the young_professional persona will be fully integrated across the entire SpendSense system.

**Estimated Total Time**:
- Phase 1 (Critical): 10 minutes
- Phase 2 (Optional): 15 minutes
- Phase 3 (Validation): 5 minutes
- **Total**: 30 minutes

Good luck! 🎯
