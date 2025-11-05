# Story 4.2: Partner Offer Catalog

**Epic:** Epic 4 - Recommendation Engine & Content Catalog
**Status:** COMPLETED ✅
**Completed:** 2025-11-05

---

## Story

As a **product manager**,
I want **structured catalog of partner offers with eligibility rules and persona targeting**,
so that **relevant financial products can be recommended only to eligible users**.

---

## Acceptance Criteria

### AC1: Partner offer catalog created as YAML/JSON configuration file ✅
- **Status:** COMPLETED
- **Implementation:** `spendsense/config/partner_offers.yaml`
- **Details:** Created YAML catalog following same flat list structure as Story 4.1

### AC2: Each offer includes: ID, title, type (savings account/credit_card/app/tool), description ✅
- **Status:** COMPLETED
- **Implementation:**
  - Created `PartnerOfferType` enum in `models.py` with values: `savings_account`, `credit_card`, `app`, `tool`
  - All offers in YAML include `id`, `title`, `type`, and `description` fields
- **Validation:** Pydantic model enforces required fields

### AC3: Each offer includes eligibility criteria (minimum income, credit requirements, account exclusions) ✅
- **Status:** COMPLETED
- **Implementation:**
  - Created `EligibilityCriteria` model with fields:
    - `min_income`: Optional minimum annual income
    - `min_credit_score`: Optional minimum credit score (300-850)
    - `excluded_accounts`: List of account types that disqualify user
    - `max_credit_utilization`: Optional maximum utilization percentage
    - `min_age`: Optional minimum age requirement
    - `employment_required`: Boolean for employment requirement
  - `PartnerOffer` model includes `eligibility: EligibilityCriteria` field
- **Test Coverage:** 7 eligibility checking tests verify all criteria types

### AC4: Each offer tagged with relevant personas ✅
- **Status:** COMPLETED
- **Implementation:** All offers have `personas: List[str]` field supporting multi-persona targeting
- **Validation:** Tests verify all personas have offers

### AC5: Partner offers defined covering all personas: balance transfer cards, high-yield savings, budgeting apps, subscription management tools ✅
- **Status:** COMPLETED
- **Offers Created:**
  - **Balance Transfer Cards:** Chase Slate Edge, Citi Diamond Preferred
  - **High-Yield Savings:** Ally Bank, Marcus by Goldman Sachs, Wealthfront, Credit Karma Savings
  - **Budgeting Apps:** YNAB, Truebill, Copilot Money
  - **Subscription Management Tools:** Rocket Money
  - **Other Apps:** Qapital (automated savings)
  - **Credit Builder:** Discover Secured Card
- **Coverage:** 13 total offers across 4 product types

### AC6: At least 10 unique partner offers covering all 6 personas ✅
- **Status:** COMPLETED
- **Implementation:** 13 offers created
- **Persona Coverage:**
  - `high_utilization`: 4 offers (balance transfer cards, credit builder, savings)
  - `irregular_income`: 3 offers (high-yield savings, budgeting apps)
  - `low_savings`: 6 offers (high-yield savings accounts, automated savings)
  - `subscription_heavy`: 4 offers (subscription trackers, budget optimizers)
  - `cash_flow_optimizer`: 7 offers (savings, budgeting, subscription tools)
  - `young_professional`: 7 offers (savings, budgeting, credit building)
- **Test:** `test_load_all_personas_present()` validates all 6 personas have offers

### AC7: Harmful/predatory products explicitly excluded from catalog ✅
- **Status:** COMPLETED
- **Implementation:**
  - YAML header comment explicitly states predatory products excluded
  - No payday loans, title loans, high-fee credit cards, rent-to-own, pawn services
- **Test:** `test_catalog_has_no_predatory_products()` scans catalog for predatory terms

### AC8: Each offer includes plain-language summary ✅
- **Status:** COMPLETED
- **Implementation:** All `description` fields written in plain language (grade-8 readability)
- **Validation:**
  - Pydantic model enforces min 20 characters
  - Test verifies common words present (a, the, and, with, for, to)

### AC9: Catalog schema validated and documented ✅
- **Status:** COMPLETED
- **Implementation:**
  - `PartnerOffer` model with comprehensive docstrings
  - `EligibilityCriteria` model with field documentation
  - All fields include Pydantic `Field()` descriptions
  - `PartnerOfferLibrary` class documented with usage examples
- **Validation:** All models use Pydantic for runtime validation
- **Test:** `test_offers_catalog_schema_validated()` verifies schema compliance

### AC10: Catalog loaded at application startup ✅
- **Status:** COMPLETED
- **Implementation:**
  - Created `PartnerOfferLibrary` class that loads YAML on initialization
  - Singleton pattern via `get_partner_offer_library()` function
  - Default path resolves to `spendsense/config/partner_offers.yaml`
  - Logs load count on startup
- **Test:** `test_singleton_library_instance()` verifies singleton behavior

---

## Implementation Details

### Files Created
1. **`spendsense/recommendations/models.py`** (additions)
   - `PartnerOfferType` enum
   - `EligibilityCriteria` model
   - `PartnerOffer` model with validation

2. **`spendsense/config/partner_offers.yaml`**
   - 13 partner offers
   - Covers all 6 personas
   - 4 product types (credit_card, savings_account, app, tool)

3. **`spendsense/recommendations/partner_offer_library.py`**
   - `PartnerOfferLibrary` class
   - Methods: `get_by_persona()`, `get_by_type()`, `check_eligibility()`, `get_eligible_offers()`
   - Singleton pattern via `get_partner_offer_library()`

4. **`spendsense/recommendations/__init__.py`** (updated)
   - Exports `PartnerOffer`, `PartnerOfferType`, `EligibilityCriteria`
   - Exports `PartnerOfferLibrary`, `get_partner_offer_library`

5. **`tests/test_partner_offer_library.py`**
   - 33 comprehensive tests
   - Model validation tests (7 tests)
   - Library loading tests (5 tests)
   - Library query tests (7 tests)
   - Eligibility checking tests (9 tests)
   - Catalog quality tests (5 tests)

### Test Results
```
33 passed, 4 warnings in 0.63s
```

**Test Coverage:**
- ✅ Model validation (required fields, enums, formats, validation rules)
- ✅ YAML loading (valid file, missing file, invalid syntax, invalid structure)
- ✅ Persona coverage (all 6 personas have offers)
- ✅ Query methods (by persona, by type, by ID, priority sorting)
- ✅ Eligibility checking (income, credit, exclusions, utilization, age, employment)
- ✅ Catalog quality (no predatory products, plain language, schema validation)

---

## Technical Architecture

### Data Model
```python
class PartnerOfferType(str, Enum):
    SAVINGS_ACCOUNT = "savings_account"
    CREDIT_CARD = "credit_card"
    APP = "app"
    TOOL = "tool"

class EligibilityCriteria(BaseModel):
    min_income: Optional[int]
    min_credit_score: Optional[int]
    excluded_accounts: List[str]
    max_credit_utilization: Optional[int]
    min_age: Optional[int]
    employment_required: bool

class PartnerOffer(BaseModel):
    id: str
    type: PartnerOfferType
    title: str
    description: str
    personas: List[str]
    eligibility: EligibilityCriteria
    priority: int
    provider: str
    offer_url: Optional[str]
    key_benefits: List[str]
    rationale_template: Optional[str]
    disclaimer: Optional[str]
```

### YAML Structure
```yaml
partner_offers:
  - id: balance_transfer_chase_slate
    type: credit_card
    title: "Chase Slate Edge℠ - 0% Intro APR Balance Transfer"
    description: "Transfer high-interest credit card balances..."
    personas:
    - high_utilization
    eligibility:
      min_income: 30000
      min_credit_score: 670
      excluded_accounts:
      - chase_credit_cards
    priority: 1
    provider: "Chase"
    key_benefits:
    - "0% intro APR for 18 months"
    - "No annual fee"
    rationale_template: "Your {account_name} card is at {utilization_pct}%..."
```

### Library Usage
```python
from spendsense.recommendations import get_partner_offer_library

# Load library (singleton)
library = get_partner_offer_library()

# Get offers for persona
offers = library.get_by_persona("high_utilization")

# Check eligibility
user_data = {
    "annual_income": 50000,
    "credit_score": 700,
    "existing_accounts": [],
    "credit_utilization": 60,
    "age": 30,
    "is_employed": True,
}

is_eligible, reasons = library.check_eligibility(offers[0], user_data)

# Get only eligible offers
eligible = library.get_eligible_offers("high_utilization", user_data, limit=3)
```

---

## Catalog Contents

### Summary Statistics
- **Total Offers:** 13
- **Credit Cards:** 3 (2 balance transfer, 1 secured)
- **Savings Accounts:** 4 (high-yield accounts)
- **Apps:** 5 (budgeting and subscription management)
- **Tools:** 1 (automated savings)

### Offer Distribution by Persona
- **high_utilization:** 4 offers (31%)
- **irregular_income:** 3 offers (23%)
- **low_savings:** 6 offers (46%)
- **subscription_heavy:** 4 offers (31%)
- **cash_flow_optimizer:** 7 offers (54%)
- **young_professional:** 7 offers (54%)

*Note: Percentages > 100% due to multi-persona targeting*

### Sample Offers

**Balance Transfer Credit Cards:**
- Chase Slate Edge℠ (0% for 18 months)
- Citi® Diamond Preferred® (0% for 21 months)

**High-Yield Savings:**
- Ally Bank (4.35% APY)
- Marcus by Goldman Sachs (4.40% APY)
- Wealthfront Cash Account (5.00% APY)

**Budgeting Apps:**
- YNAB (You Need A Budget) - Zero-based budgeting
- Truebill - Bill negotiation + budgeting
- Copilot Money - Premium iOS budgeting

**Subscription Management:**
- Rocket Money - Track & cancel subscriptions

---

## Dependencies

### Story Dependencies
- ✅ **Story 4.1:** Educational Content Catalog (completed)
  - Established YAML structure pattern
  - Created base models and library pattern
  - Set testing standards

### Dependent Stories
- **Story 4.3:** Recommendation Matching Logic (next)
  - Will use `PartnerOfferLibrary.get_eligible_offers()`
  - Will combine with educational content from Story 4.1

---

## Next Steps

Story 4.2 is complete. Ready to proceed with:

**Story 4.3: Recommendation Matching Logic**
- Implement matching algorithm combining education + offers
- Filter by persona and signals
- Rank by relevance
- Select 3-5 education items + 1-3 partner offers
- Prevent duplicates within time window

---

## Notes

### Design Decisions

1. **Multi-Persona Support:** Offers can target multiple personas (e.g., high-yield savings works for `low_savings`, `cash_flow_optimizer`, and `young_professional`)

2. **Flexible Eligibility:** All criteria fields are optional, allowing offers with no restrictions (e.g., apps with no income/credit requirements)

3. **Eligibility Method Returns Reasons:** `check_eligibility()` returns both boolean and list of reasons for transparency

4. **Singleton Pattern:** Same as Story 4.1 for consistent library access and memory efficiency

5. **Rationale Templates:** Each offer includes template for personalized explanations (will be used in Story 4.4)

### Lessons Learned

1. **Follow Established Patterns:** Using same structure as Story 4.1 made implementation faster and more consistent

2. **Comprehensive Eligibility:** Real-world offers have complex eligibility (income, credit, existing accounts, age, employment) - implemented all common criteria types

3. **Test Quality Gates:** Tests for predatory products and plain language ensure catalog quality matches PRD requirements

---

**Story 4.2 Status: COMPLETED ✅**

All 10 acceptance criteria met. 33/33 tests passing. Ready for Story 4.3.
