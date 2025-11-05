---
name: story-validation-guide
description: After completing any story, provide a CONCISE validation guide with minimal essential steps to verify acceptance criteria and test UI/functionality quickly
---

# Story Validation Guide Skill

## When to Use This Skill

**ALWAYS** use this skill immediately after completing implementation of any story.

## What This Skill Does

Provides a **concise, quick-to-execute** validation guide with only the essential steps needed to verify the story is complete and working.

## Validation Guide Template (CONCISE)

```markdown
## ✅ Story [ID]: [Name] - Quick Validation

### 🧪 Run Tests (30 sec)
```bash
[Single command to run all tests for this story]
# Expected: [X/X passed]
```

### 🌐 UI Quick Test (2 min)
[Only if UI exists]

**URL:** [url]

**Test:**
1. [Action 1] → [Expected result] ✓ ACs [numbers]
2. [Action 2] → [Expected result] ✓ ACs [numbers]
3. [Action 3] → [Expected result] ✓ ACs [numbers]

### 📋 Acceptance Criteria Coverage
- ✅ AC 1-3: [Brief summary - covered by above tests]
- ✅ AC 4-6: [Brief summary - covered by above tests]
- ✅ AC 7-9: [Brief summary - covered by above tests]

### 🔄 Regression Check (30 sec)
[Only if existing features were modified]
- [ ] [Quick test for feature X that was touched]

### ✅ Done
- [X/X] ACs validated
- [Tests: X/X passed]
- Story ready for: [next step]
```

## Critical Requirements

1. **Be Concise**: 3-5 minute validation maximum
2. **Be Specific**: Exact commands and UI steps only
3. **Group ACs**: Don't repeat - show which test/UI step covers which ACs
4. **Minimize**: Only essential steps for coverage
5. **Regression**: Only if existing features touched

## Principles

- **Single test command** if possible (not multiple commands)
- **3-5 UI steps max** that cover all ACs
- **Group ACs together** (e.g., "ACs 1-3 validated by test suite")
- **Skip details** - assume user can read test output
- **No troubleshooting** - keep it positive and simple
- **No file lists** - they can see git status

## Example - CONCISE Format

```markdown
## ✅ Story 1.3: Profile Generator - Quick Validation

### 🧪 Run Tests (30 sec)
```bash
pytest tests/test_profile_generator.py -v
# Expected: 58/58 passed
```

### 🌐 UI Quick Test (2 min)
**URL:** http://localhost:8000

**Test:**
1. Generate Profiles tab → Set 100 users, seed 42 → Generate → Success shown ✓ ACs 1,2,6,7,8
2. View Profiles tab → See 10 profiles, try pagination → Works ✓ ACs 3,4,5
3. Statistics tab → See 20% bars, validation ✓ → Confirms AC 2,7

### 📋 Acceptance Criteria Coverage
- ✅ AC 1-8: Covered by tests + UI steps above
- ✅ AC 9: Documentation in spendsense/generators/README.md

### ✅ Done
- 9/9 ACs validated | Tests: 58/58 passed | Ready for: Review
```

That's it! User can validate in ~3 minutes total.
