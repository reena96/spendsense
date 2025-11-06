# Young Professional Persona - Quick Checklist

## 🚨 CRITICAL (Must Do - 10 min)

### Phase 1: Fix Persona Definitions

**File**: `spendsense/personas/definitions.py`

- [ ] **1.1** Add PERSONA_YOUNG_PROFESSIONAL after PERSONA_CONTROL (~line 230)
- [ ] **1.2** Add to PERSONA_REGISTRY dict (~line 233)
- [ ] **1.3** Add to PERSONA_DESCRIPTIONS dict (~line 259)
- [ ] **1.4** Verify personas page loads (http://localhost:8000/ → Personas tab)

## ⭐ OPTIONAL (Nice to Have - 15 min)

### Phase 2: Generate Test Users

- [ ] **2.1** Create `scripts/add_young_professional_users.py`
- [ ] **2.2** Run script: `python scripts/add_young_professional_users.py`
- [ ] **2.3** Verify: `sqlite3 data/processed/spendsense.db "SELECT persona, COUNT(*) FROM users GROUP BY persona;"`

## ✅ Validation (5 min)

- [ ] **3.1** Personas page shows 6 personas (no error)
- [ ] **3.2** Test young_professional in signal dashboard
- [ ] **3.3** Generate recommendations for young_professional
- [ ] **3.4** Run tests: `pytest tests/test_persona_*.py`

---

**See `YOUNG_PROFESSIONAL_IMPLEMENTATION_PLAN.md` for detailed code snippets and instructions.**
