# Story 3.1: Persona Definition Registry

Status: drafted

## Story

As a **product manager**,
I want **structured persona definitions with clear criteria, focus areas, and prioritization rules**,
so that **persona assignment logic is maintainable, extensible, and auditable**.

## Acceptance Criteria

1. Persona registry created as YAML configuration file
2. Each persona defined with: ID, name, description, priority rank, match criteria
3. Persona 1 (High Utilization) defined with priority 1 and criteria documented
4. Persona 2 (Variable Income Budgeter) defined with priority 2 and criteria documented
5. Persona 3 (Subscription-Heavy) defined with priority 3 and criteria documented
6. Persona 4 (Savings Builder) defined with priority 4 and criteria documented
7. Persona 5 (Cash Flow Optimizer) defined with priority 5, criteria, and rationale documented
8. Persona 6 (Young Professional) defined with priority 6, criteria, and rationale documented
9. Each persona includes educational focus areas and recommended content types
10. Registry schema validated and documented
11. Registry loaded at application startup

## Tasks / Subtasks

- [ ] Task 1: Create persona registry YAML file (AC: 1, 2, 9, 10)
  - [ ] Create `spendsense/config/personas.yaml` with structured schema
  - [ ] Define YAML schema with fields: id, name, description, priority, criteria, focus_areas, content_types
  - [ ] Document schema structure in file header comments
  - [ ] Add validation rules for required fields

- [ ] Task 2: Define Persona 1 - High Credit Utilization (AC: 3)
  - [ ] Set priority: 1 (highest)
  - [ ] Define criteria: `credit_max_utilization_pct >= 50.0`
  - [ ] Add description: Focus on debt reduction, interest costs
  - [ ] List focus areas: debt management, credit utilization, interest savings
  - [ ] Specify content types: education (debt paydown strategies, balance transfer)

- [ ] Task 3: Define Persona 2 - Variable Income Budgeter (AC: 4)
  - [ ] Set priority: 2
  - [ ] Define criteria: `income_median_pay_gap_days > 45` OR `income_payroll_count < 2` in 30-day window
  - [ ] Add description: Irregular income, cash flow challenges
  - [ ] List focus areas: cash flow budgeting, emergency fund, income smoothing
  - [ ] Specify content types: education (irregular income budgeting, gig economy finance)

- [ ] Task 4: Define Persona 3 - Low Savings / Emergency Fund (AC: 6)
  - [ ] Set priority: 3
  - [ ] Define criteria: `savings_emergency_fund_months < 3.0`
  - [ ] Add description: Minimal savings buffer, building financial resilience
  - [ ] List focus areas: emergency fund, savings strategies, financial resilience
  - [ ] Specify content types: education (emergency fund building, automated savings)

- [ ] Task 5: Define Persona 4 - Subscription-Heavy (AC: 5)
  - [ ] Set priority: 4
  - [ ] Define criteria: `subscription_share_pct >= 0.20` (20% of total spending)
  - [ ] Add description: High recurring spend, subscription optimization opportunity
  - [ ] List focus areas: subscription audit, spending optimization, recurring costs
  - [ ] Specify content types: education (subscription management, cost optimization)

- [ ] Task 6: Define Persona 5 - Cash Flow Optimizer (AC: 7)
  - [ ] Set priority: 5
  - [ ] Define criteria: `savings_emergency_fund_months >= 6.0` AND `credit_max_utilization_pct < 0.10`
  - [ ] Add description: High liquidity, low debt, opportunity for better allocation
  - [ ] List focus areas: investment basics, high-yield savings, goal planning, wealth optimization
  - [ ] Specify content types: education (investment intro, HYSA, financial goals), partner offers (investment platforms, HYSA accounts)
  - [ ] Document rationale: Serves users with financial stability seeking optimization

- [ ] Task 7: Define Persona 6 - Young Professional / Credit Builder (AC: 8)
  - [ ] Set priority: 6 (lowest)
  - [ ] Define criteria: Transaction history < 180 days OR credit limits < $3000 (if credit accounts exist)
  - [ ] Add description: Limited transaction history, early career, building financial foundation
  - [ ] List focus areas: credit building, budgeting basics, financial literacy, starter accounts
  - [ ] Specify content types: education (credit 101, budgeting fundamentals, account types)
  - [ ] Document rationale: Serves early-career users establishing financial habits

- [ ] Task 8: Implement registry loader module (AC: 11)
  - [ ] Create `spendsense/personas/registry.py` with `load_persona_registry()` function
  - [ ] Implement YAML parsing with pyyaml
  - [ ] Add Pydantic models for type validation: `Persona`, `PersonaCriteria`, `PersonaRegistry`
  - [ ] Validate all required fields present on load
  - [ ] Cache loaded registry (singleton pattern or app startup)
  - [ ] Add error handling for missing/malformed YAML

- [ ] Task 9: Write unit tests for registry (AC: 10, 11)
  - [ ] Test registry file loads successfully
  - [ ] Test all 6 personas present with correct priorities
  - [ ] Test schema validation catches missing required fields
  - [ ] Test criteria parsing for each persona
  - [ ] Test registry singleton/caching behavior

## Dev Notes

### Architecture Alignment

**From architecture.md (lines 912-947):**
- Personas module key interfaces: `load_persona_registry() -> PersonaRegistry`
- 6 personas defined with prioritization order
- Match criteria use behavioral signals from Epic 2

**Persona Prioritization Order (from architecture):**
1. `high_utilization` (≥50% credit utilization)
2. `irregular_income` (high variance or <2 paychecks/30d)
3. `low_savings` (<3 months emergency fund)
4. `subscription_heavy` (≥20% recurring spend)
5. `cash_flow_optimizer` (≥6 months savings AND <10% utilization)
6. `young_professional` (<180 days history OR <$3000 credit limits)

### Project Structure Notes

**Module Location:** `spendsense/personas/`
- Registry file: `spendsense/config/personas.yaml`
- Loader module: `spendsense/personas/registry.py`

**Existing Code:**
- `spendsense/personas/definitions.py` exists but is for *synthetic data generation*
- This story creates the *detection/assignment* registry (different purpose)

### Dependencies

**Consumes:** Nothing (first story in Epic 3)
**Produces:** Persona registry YAML, loader module
**Depends On:** Epic 2 signal names (subscription_share_pct, credit_max_utilization_pct, etc.)

### Testing Strategy

**Unit Tests:**
- Test YAML loads without errors
- Test all 6 personas defined
- Test priority ordering correct
- Test criteria field structure valid
- Test Pydantic validation catches errors

**Test File:** `tests/test_persona_registry.py`

### References

- [Source: docs/prd/epic-3-persona-assignment-system.md#Story-3.1]
- [Source: docs/architecture.md#Personas-Module (lines 912-947)]
- [Source: docs/architecture.md#Key-Design-Decisions (lines 26-30)]

## Dev Agent Record

### Context Reference

N/A - First story in Epic 3

### Agent Model Used

Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Debug Log References

No issues encountered during implementation.

### Completion Notes List

**✅ Story 3.1 Complete - All acceptance criteria satisfied**

**Created Files:**
- `spendsense/config/personas.yaml` - Comprehensive 6-persona registry with criteria, focus areas, and content types
- `spendsense/personas/registry.py` - Registry loader with Pydantic models and validation
- `tests/test_persona_registry.py` - 24 unit tests (all passing)

**Key Implementation Details:**
1. **YAML Schema**: Defined clear structure with operator (AND/OR) and conditions (signal, operator, value)
2. **6 Personas Defined**:
   - Priority 1: High Credit Utilization (≥50% utilization)
   - Priority 2: Variable Income Budgeter (>45 day gap OR <2 paychecks)
   - Priority 3: Low Savings (<3 months emergency fund)
   - Priority 4: Subscription-Heavy (≥20% recurring spend)
   - Priority 5: Cash Flow Optimizer (≥6 months savings AND <10% utilization)
   - Priority 6: Young Professional (<180 days history OR <$3000 credit limits)
3. **Pydantic Models**: Strong typing with validation for PersonaCondition, PersonaCriteria, Persona, PersonaRegistry
4. **Caching**: Singleton pattern for registry loading (loaded once at startup)
5. **Validation**: Ensures unique IDs, unique priorities, lowercase IDs, non-empty fields

**For Next Story (3.2 - Persona Matching Engine):**
- Registry is ready to be consumed
- Use `load_persona_registry()` to get all personas
- Match logic should evaluate `PersonaCriteria` against `BehavioralSignal` data
- Criteria format: `operator` (AND/OR) with list of `conditions`
- Each condition has: `signal` (field name), `operator` (>=, <=, etc.), `value` (threshold)

**Testing:**
- All 24 unit tests pass
- Registry loads successfully
- All 6 personas present with correct priorities
- Criteria structure validated
- Caching works correctly

### File List

**NEW:**
- `spendsense/config/personas.yaml`
- `spendsense/personas/registry.py`
- `tests/test_persona_registry.py`
