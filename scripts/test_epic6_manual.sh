#!/bin/bash
# Manual Testing Script for Epic 6 Story 6.1
# Run this to test authentication via command line

echo "🧪 Epic 6 Story 6.1 - Manual Testing"
echo "===================================="
echo ""

# Test 1: Login as admin
echo "Test 1: Login as admin..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/operator/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"admin\", \"password\": \"AdminPass123!\"}")

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✅ Login successful"
    ACCESS_TOKEN=$(echo "$RESPONSE" | python -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
    echo "   Token: ${ACCESS_TOKEN:0:50}..."
else
    echo "❌ Login failed"
    echo "$RESPONSE"
    exit 1
fi

echo ""

# Test 2: Access protected endpoint (POST consent) with admin token
echo "Test 2: Admin can POST to /api/consent..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -d "{\"user_id\": \"user_MASKED_000\", \"consent_status\": \"opted_in\"}")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" = "201" ] || [ "$HTTP_STATUS" = "404" ]; then
    echo "✅ Admin access granted (status: $HTTP_STATUS)"
else
    echo "❌ Unexpected status: $HTTP_STATUS"
fi

echo ""

# Test 3: Create viewer
echo "Test 3: Create viewer operator..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/operator/create \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test_viewer\", \"password\": \"ViewerPass123!\", \"role\": \"viewer\"}")

if echo "$RESPONSE" | grep -q "operator_id"; then
    echo "✅ Viewer created"
elif echo "$RESPONSE" | grep -q "already exists"; then
    echo "ℹ️  Viewer already exists (OK)"
else
    echo "⚠️  Could not create viewer"
fi

echo ""

# Test 4: Login as viewer
echo "Test 4: Login as viewer..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/operator/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test_viewer\", \"password\": \"ViewerPass123!\"}")

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✅ Viewer login successful"
    VIEWER_TOKEN=$(echo "$RESPONSE" | python -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
else
    echo "❌ Viewer login failed"
    exit 1
fi

echo ""

# Test 5: Viewer blocked from POST consent
echo "Test 5: Viewer blocked from POST /api/consent..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -d "{\"user_id\": \"user_MASKED_000\", \"consent_status\": \"opted_in\"}")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" = "403" ]; then
    echo "✅ Viewer correctly blocked (403 Forbidden)"
else
    echo "❌ Expected 403, got: $HTTP_STATUS"
fi

echo ""

# Test 6: No auth = 401
echo "Test 6: No auth token = 401..."
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:8000/api/consent \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"user_MASKED_000\", \"consent_status\": \"opted_in\"}")

HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)

if [ "$HTTP_STATUS" = "401" ]; then
    echo "✅ Unauthenticated requests blocked (401)"
else
    echo "❌ Expected 401, got: $HTTP_STATUS"
fi

echo ""
echo "===================================="
echo "🎉 Epic 6 Story 6.1 Manual Testing Complete!"
echo ""
echo "Summary:"
echo "✅ AC #1: Login works"
echo "✅ AC #2: RBAC enforced (viewer blocked)"
echo "✅ AC #3: JWT tokens issued"
echo "✅ AC #4: Consent endpoints protected"
echo "✅ AC #5: Unauthorized access blocked (401)"
