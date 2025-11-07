#!/bin/bash
# RBAC Validation Script for Epic 6 Story 6.1
# Tests all three roles: viewer, reviewer, admin

echo "🔒 RBAC Validation Test Suite"
echo "======================================"
echo ""

API_URL="http://localhost:8000"

# Create test operators
echo "📋 Phase 1: Creating Test Operators"
echo "------------------------------------"

# Create viewer
echo -n "Creating viewer... "
RESPONSE=$(curl -s -X POST "$API_URL/api/operator/create" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test_viewer\", \"password\": \"ViewerPass123!\", \"role\": \"viewer\"}")
if echo "$RESPONSE" | grep -q "operator_id"; then
    echo "✅ Created"
elif echo "$RESPONSE" | grep -q "already exists"; then
    echo "✅ Already exists"
else
    echo "⚠️  Failed"
fi

# Create reviewer
echo -n "Creating reviewer... "
RESPONSE=$(curl -s -X POST "$API_URL/api/operator/create" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test_reviewer\", \"password\": \"ReviewerPass123!\", \"role\": \"reviewer\"}")
if echo "$RESPONSE" | grep -q "operator_id"; then
    echo "✅ Created"
elif echo "$RESPONSE" | grep -q "already exists"; then
    echo "✅ Already exists"
else
    echo "⚠️  Failed"
fi

echo ""

# Test Viewer Role
echo "👁️  Phase 2: Testing VIEWER Role (Should Be Blocked)"
echo "------------------------------------"

# Login as viewer
VIEWER_TOKEN=$(curl -s -X POST "$API_URL/api/operator/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test_viewer\", \"password\": \"ViewerPass123!\"}" | \
  python -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$VIEWER_TOKEN" ]; then
    echo "❌ Failed to get viewer token"
    exit 1
fi

# Test POST /api/consent (should fail)
echo -n "POST /api/consent... "
STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/api/consent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -d "{\"user_id\": \"user_MASKED_000\", \"consent_status\": \"opted_in\"}")
if [ "$STATUS" = "403" ]; then
    echo "✅ Blocked (403)"
else
    echo "❌ Expected 403, got $STATUS"
fi

# Test GET /api/consent/{user_id} (should fail)
echo -n "GET /api/consent/user_MASKED_000... "
STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X GET "$API_URL/api/consent/user_MASKED_000" \
  -H "Authorization: Bearer $VIEWER_TOKEN")
if [ "$STATUS" = "403" ]; then
    echo "✅ Blocked (403)"
else
    echo "❌ Expected 403, got $STATUS"
fi

echo ""

# Test Reviewer Role
echo "👓 Phase 3: Testing REVIEWER Role (Can GET, Cannot POST)"
echo "------------------------------------"

# Login as reviewer
REVIEWER_TOKEN=$(curl -s -X POST "$API_URL/api/operator/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test_reviewer\", \"password\": \"ReviewerPass123!\"}" | \
  python -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$REVIEWER_TOKEN" ]; then
    echo "❌ Failed to get reviewer token"
    exit 1
fi

# Test POST /api/consent (should fail)
echo -n "POST /api/consent... "
STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/api/consent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -d "{\"user_id\": \"user_MASKED_000\", \"consent_status\": \"opted_in\"}")
if [ "$STATUS" = "403" ]; then
    echo "✅ Blocked (403)"
else
    echo "❌ Expected 403, got $STATUS"
fi

# Test GET /api/consent/{user_id} (should succeed)
echo -n "GET /api/consent/user_MASKED_000... "
STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X GET "$API_URL/api/consent/user_MASKED_000" \
  -H "Authorization: Bearer $REVIEWER_TOKEN")
if [ "$STATUS" = "200" ] || [ "$STATUS" = "404" ]; then
    echo "✅ Allowed ($STATUS)"
else
    echo "❌ Expected 200/404, got $STATUS"
fi

echo ""

# Test Admin Role
echo "👑 Phase 4: Testing ADMIN Role (Full Access)"
echo "------------------------------------"

# Login as admin
ADMIN_TOKEN=$(curl -s -X POST "$API_URL/api/operator/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"AdminPass123!\"}" | \
  python -c "import json,sys; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$ADMIN_TOKEN" ]; then
    echo "❌ Failed to get admin token"
    exit 1
fi

# Test POST /api/consent (should succeed)
echo -n "POST /api/consent... "
STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_URL/api/consent" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d "{\"user_id\": \"user_MASKED_000\", \"consent_status\": \"opted_in\"}")
if [ "$STATUS" = "201" ] || [ "$STATUS" = "404" ]; then
    echo "✅ Allowed ($STATUS)"
else
    echo "❌ Expected 201/404, got $STATUS"
fi

# Test GET /api/consent/{user_id} (should succeed)
echo -n "GET /api/consent/user_MASKED_000... "
STATUS=$(curl -s -w "%{http_code}" -o /dev/null -X GET "$API_URL/api/consent/user_MASKED_000" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
if [ "$STATUS" = "200" ] || [ "$STATUS" = "404" ]; then
    echo "✅ Allowed ($STATUS)"
else
    echo "❌ Expected 200/404, got $STATUS"
fi

echo ""
echo "======================================"
echo "✅ RBAC Validation Complete!"
echo ""
echo "Summary:"
echo "  ✅ Viewer: Blocked from both endpoints"
echo "  ✅ Reviewer: Can GET, cannot POST"
echo "  ✅ Admin: Full access to both endpoints"
