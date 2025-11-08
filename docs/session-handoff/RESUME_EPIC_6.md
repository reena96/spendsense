# 🚀 Resume Epic 6 - Stories 6.2 through 6.6

**Session Context:** Epic 6 Story 6.1 Complete - Ready for Stories 6.2-6.6
**Branch:** `epic-6-operator-view`
**Last Updated:** 2025-11-06

---

## 📋 Quick Start - Resume Development

### **Step 1: Read the Handoff Document**

```bash
cat docs/session-handoff/EPIC_6_SESSION_HANDOFF.md
```

This contains:
- Complete Story 6.1 summary (what was implemented)
- Remaining stories overview (6.2-6.6)
- Technical environment setup
- Testing validation results

---

### **Step 2: Verify Environment**

```bash
# Check branch
git branch

# Start API server (if not running)
source venv/bin/activate
python -m uvicorn spendsense.api.main:app --reload --port 8000

# Verify auth database initialized
ls -la data/processed/spendsense.db

# Run tests to confirm everything works
python -m pytest tests/test_operator_auth.py -v
# Expected: 24 passed
```

---

### **Step 3: Start Story 6.2 (User Signal Dashboard)**

**Recommended first story because:**
- ✅ Context file ready: `docs/stories/6-2-user-signal-dashboard.context.xml`
- ✅ Story file ready: `docs/stories/6-2-user-signal-dashboard.md`
- ✅ Dependencies met: Story 6.1 (auth) complete
- 🟢 Medium complexity
- 🎯 Builds on existing Epic 3 signal infrastructure

**Execute with:**
```bash
/BMad:bmm:workflows:dev-story docs/stories/6-2-user-signal-dashboard.md
```

---

## 🎯 Story Execution Pattern (Repeat for Each Story)

### **Pattern for Stories 6.2 through 6.6:**

```bash
# 1. Start story development
/BMad:bmm:workflows:dev-story docs/stories/6-{N}-story-name.md

# 2. Implementation happens (AI + developer collaboration)
# - Read context file
# - Review story requirements
# - Implement endpoints and logic
# - Write tests
# - Update documentation

# 3. Run code review
/BMad:bmm:workflows:code-review docs/stories/6-{N}-story-name.md

# 4. Fix any issues identified in review

# 5. Mark story complete
/BMad:bmm:workflows:story-done docs/stories/6-{N}-story-name.md

# 6. Update sprint-status.yaml (workflow handles this)

# 7. Move to next story
```

---

## 📚 Story Order Recommendation

### **Suggested Sequence:**

1. **Story 6.2: User Signal Dashboard** (Start here)
   - File: `docs/stories/6-2-user-signal-dashboard.md`
   - Complexity: Medium
   - Dependencies: Epic 3 signals ✅
   - Estimated: 2-3 hours

2. **Story 6.3: Persona Assignment Review Interface**
   - File: `docs/stories/6-3-persona-assignment-review-interface.md`
   - Complexity: Medium
   - Dependencies: Epic 3 personas ✅
   - Estimated: 2-3 hours

3. **Story 6.6: Consent Management Interface**
   - File: `docs/stories/6-6-consent-management-interface.md`
   - Complexity: Low-Medium
   - Dependencies: Epic 5 consent ✅
   - Estimated: 1-2 hours

4. **Story 6.4: Recommendation Review & Approval Queue**
   - File: `docs/stories/6-4-recommendation-review-approval-queue.md`
   - Complexity: High
   - Dependencies: Epic 4 recommendations ✅
   - Estimated: 3-4 hours

5. **Story 6.5: Audit Trail & Compliance Reporting**
   - File: `docs/stories/6-5-audit-trail-compliance-reporting.md`
   - Complexity: Medium-High
   - Dependencies: All Epic 5 audit logs ✅
   - Estimated: 2-3 hours

---

## 🔑 Key Information from Story 6.1

### **Authentication System (Available for All Stories):**

**RBAC Helper:**
```python
from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData
from fastapi import Depends

# Use this pattern for protected endpoints:
@app.get("/api/operator/some-endpoint")
async def my_endpoint(
    current_operator: TokenData = Depends(require_role("reviewer"))
):
    # current_operator.operator_id
    # current_operator.username
    # current_operator.role
    ...
```

**Role Requirements:**
- `viewer` - Read-only access (currently no endpoints)
- `reviewer` - Can view and review data
- `admin` - Full access

**Testing Credentials:**
```
Admin:    admin / AdminPass123!
Reviewer: test_reviewer / ReviewerPass123!
Viewer:   test_viewer / ViewerPass123!
```

---

## 📊 Current Progress

### **Epic 6 Status:**

| Story | Status | Files |
|-------|--------|-------|
| 6.1 - Authentication | ✅ **DONE** | Implemented, tested, validated |
| 6.2 - User Signal Dashboard | 🟡 Ready | Context + story ready |
| 6.3 - Persona Assignment Review | 🟡 Ready | Context + story ready |
| 6.4 - Recommendation Review Queue | 📝 Drafted | Context created |
| 6.5 - Audit Trail & Compliance | 📝 Drafted | Context created |
| 6.6 - Consent Management | 📝 Drafted | Context created |

**Progress:** 1/6 stories complete (17%)
**Remaining:** 5 stories (~10-15 hours estimated)

---

## 🧪 Testing & Validation

### **Test Story 6.1 Auth (Verify Setup):**

```bash
# Run unit tests
pytest tests/test_operator_auth.py -v

# Validate RBAC
./scripts/test_rbac_validation.sh

# Manual test via Swagger UI
open http://localhost:8000/docs
```

### **When Implementing New Stories:**

1. **Write tests first** (TDD approach)
2. **Use existing auth patterns** from Story 6.1
3. **Follow Swagger UI UX patterns** (auto-fill examples, clear descriptions)
4. **Add RBAC protection** to all operator endpoints
5. **Include audit logging** for sensitive operations

---

## 🔗 Integration Points

### **Epic 3 Integration (For Story 6.2):**

**Behavioral Signals:**
```python
from spendsense.signals.behavioral_signals import BehavioralSignalGenerator

# Signals stored in database
# Table: behavioral_signals (if exists) or load from data files
```

### **Epic 3 Integration (For Story 6.3):**

**Persona Assignments:**
```python
from spendsense.ingestion.database_writer import PersonaAssignmentRecord

# Table: persona_assignments
# Fields: assignment_id, user_id, assigned_persona_id, qualifying_personas, match_evidence
```

### **Epic 4 Integration (For Story 6.4):**

**Recommendations:**
```python
from spendsense.recommendations.storage import RecommendationSetStorage

# Stored in: data/synthetic/recommendations/{user_id}/
# Need to add: review_status, reviewer_id, review_timestamp fields
```

### **Epic 5 Integration (For Story 6.5, 6.6):**

**Consent & Audit Logs:**
```python
# Consent: Already integrated in Story 6.1
# POST /api/consent (admin)
# GET /api/consent/{user_id} (reviewer)

# Audit logs: auth_audit_log table
# Need to add: Other operation logs for full compliance reporting
```

---

## 📝 Common Patterns to Follow

### **Endpoint Pattern:**

```python
from fastapi import APIRouter, Depends
from spendsense.auth.rbac import require_role
from spendsense.auth.tokens import TokenData
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/operator", tags=["operator-{feature}"])

class MyRequest(BaseModel):
    field: str = Field(default="example", description="Description")

class MyResponse(BaseModel):
    data: dict

@router.get("/my-endpoint")
async def my_endpoint(
    current_operator: TokenData = Depends(require_role("reviewer"))
) -> MyResponse:
    """
    Endpoint description.

    🔒 **Authentication Required:** Use the 'Authorize' button (top right)
    to provide your JWT token. Once authorized, you can execute this endpoint directly.
    """
    # Implementation here
    return MyResponse(data={"result": "success"})
```

### **Test Pattern:**

```python
def test_my_endpoint_requires_auth():
    """Test endpoint requires authentication."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app

    client = TestClient(app)
    response = client.get("/api/operator/my-endpoint")
    assert response.status_code == 401

def test_my_endpoint_requires_reviewer():
    """Test endpoint requires reviewer role."""
    from fastapi.testclient import TestClient
    from spendsense.api.main import app
    from spendsense.auth.tokens import create_access_token

    client = TestClient(app)
    viewer_token = create_access_token("op_viewer", "viewer", "viewer")

    response = client.get(
        "/api/operator/my-endpoint",
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert response.status_code == 403
```

---

## 🚨 Important Notes

### **Context Usage:**
- Check context before starting new story (don't exceed 70% of 200k)
- If context high, finish current story and start fresh session

### **Story Workflow:**
- Always use `/BMad:bmm:workflows:dev-story` (not manual implementation)
- Always run code review before marking done
- Always update sprint-status.yaml via workflow

### **Git Workflow:**
- All work stays on `epic-6-operator-view` branch
- Commit after each story completion
- Create PR after all 6 stories complete

### **Testing Requirements:**
- Minimum 10 tests per story (aim for 15-20)
- Include auth/RBAC tests
- Include integration tests
- All tests must pass before marking story done

---

## 🎉 When Epic 6 Complete

### **Final Steps:**

1. **Run Epic Retrospective:**
   ```bash
   /BMad:bmm:workflows:retrospective docs/epics/epic-6.md
   ```

2. **Update Sprint Status:**
   ```yaml
   epic-6: done
   all stories: done
   epic-6-retrospective: completed
   ```

3. **Create Pull Request:**
   ```bash
   git push origin epic-6-operator-view
   # Then create PR on GitHub to merge into main
   ```

4. **Celebrate!** 🎉 - Full operator oversight interface complete!

---

## 📞 Need Help?

### **Reference Documents:**
- **Handoff:** `docs/session-handoff/EPIC_6_SESSION_HANDOFF.md` (comprehensive details)
- **Story Files:** `docs/stories/6-*.md`
- **Context Files:** `docs/stories/6-*.context.xml`
- **Sprint Status:** `docs/sprint-status.yaml`

### **Quick Commands:**
```bash
# Check current story status
cat docs/sprint-status.yaml | grep "6-"

# See Story 6.1 implementation as reference
cat docs/stories/6-1-operator-authentication-authorization.md

# Run all Epic 6 tests
pytest tests/test_operator*.py -v

# Validate RBAC
./scripts/test_rbac_validation.sh
```

---

**Ready to resume? Start here:**

```bash
# Read the handoff
cat docs/session-handoff/EPIC_6_SESSION_HANDOFF.md

# Start Story 6.2
/BMad:bmm:workflows:dev-story docs/stories/6-2-user-signal-dashboard.md
```

🚀 **Let's complete Epic 6!**
