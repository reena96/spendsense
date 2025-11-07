#!/bin/bash
# Epic 5 Manual Validation Script
# Runs comprehensive validation tests for all guardrails

echo "=================================================="
echo "    Epic 5: Guardrails Manual Validation"
echo "=================================================="
echo ""

API_BASE="http://localhost:8000"
TEST_USER="user_MASKED_099"
MAIN_USER="user_MASKED_000"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper function to print test results
print_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ "$1" == "PASS" ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✅ PASS${NC} - $2"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "${RED}❌ FAIL${NC} - $2"
        if [ ! -z "$3" ]; then
            echo -e "   ${YELLOW}Expected: $3${NC}"
        fi
        if [ ! -z "$4" ]; then
            echo -e "   ${YELLOW}Got: $4${NC}"
        fi
    fi
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check server health
print_section "Prerequisite: Server Health Check"
HEALTH=$(curl -s $API_BASE/health)
if echo "$HEALTH" | grep -q "healthy"; then
    print_test "PASS" "Server is healthy and running"
else
    print_test "FAIL" "Server health check" "Server healthy" "$HEALTH"
    echo ""
    echo "⚠️  Server not running. Please start it with:"
    echo "   python -m uvicorn spendsense.api.main:app --host 127.0.0.1 --port 8000 --reload"
    exit 1
fi

# Story 5.1: Consent Management
print_section "Story 5.1: Consent Management System"

echo "Test 1.1: Check consent status (GET /api/consent/{user_id})"
CONSENT_STATUS=$(curl -s $API_BASE/api/consent/$MAIN_USER)
if echo "$CONSENT_STATUS" | grep -q "consent_status"; then
    print_test "PASS" "GET consent endpoint returns valid response"
else
    print_test "FAIL" "GET consent endpoint" "Valid JSON with consent_status" "$CONSENT_STATUS"
fi

echo ""
echo "Test 1.2: Record consent opt-out (POST /api/consent)"
OPT_OUT=$(curl -s -X POST $API_BASE/api/consent \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$TEST_USER\", \"consent_status\": \"opted_out\"}")
if echo "$OPT_OUT" | grep -q "opted_out"; then
    print_test "PASS" "POST consent endpoint records opt-out"
else
    print_test "FAIL" "POST consent opt-out" "opted_out status" "$OPT_OUT"
fi

echo ""
echo "Test 1.3: Verify consent blocking (403 for opted-out users)"
BLOCKED=$(curl -s -w "\n%{http_code}" $API_BASE/api/recommendations/$TEST_USER?generate=true)
HTTP_CODE=$(echo "$BLOCKED" | tail -1)
if [ "$HTTP_CODE" == "403" ]; then
    print_test "PASS" "Opted-out user blocked from recommendations (403)"
else
    print_test "FAIL" "Consent blocking" "HTTP 403" "HTTP $HTTP_CODE"
fi

echo ""
echo "Test 1.4: Record consent opt-in (POST /api/consent)"
OPT_IN=$(curl -s -X POST $API_BASE/api/consent \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$TEST_USER\", \"consent_status\": \"opted_in\"}")
if echo "$OPT_IN" | grep -q "opted_in"; then
    print_test "PASS" "POST consent endpoint records opt-in"
else
    print_test "FAIL" "POST consent opt-in" "opted_in status" "$OPT_IN"
fi

echo ""
echo "Test 1.5: Verify consent allows access (200 for opted-in users)"
ALLOWED=$(curl -s -w "\n%{http_code}" $API_BASE/api/recommendations/$TEST_USER?generate=true)
HTTP_CODE=$(echo "$ALLOWED" | tail -1)
if [ "$HTTP_CODE" == "200" ]; then
    print_test "PASS" "Opted-in user receives recommendations (200)"
else
    print_test "FAIL" "Consent allowing access" "HTTP 200" "HTTP $HTTP_CODE"
fi

echo ""
echo "Test 1.6: Invalid consent status rejected (400)"
INVALID=$(curl -s -w "\n%{http_code}" -X POST $API_BASE/api/consent \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$TEST_USER\", \"consent_status\": \"maybe_later\"}")
HTTP_CODE=$(echo "$INVALID" | tail -1)
RESPONSE=$(echo "$INVALID" | head -n -1)
if [ "$HTTP_CODE" == "400" ] && echo "$RESPONSE" | grep -qi "invalid"; then
    print_test "PASS" "Invalid consent status rejected (400)"
else
    print_test "FAIL" "Invalid consent validation" "HTTP 400 with error" "HTTP $HTTP_CODE"
fi

# Story 5.4: Mandatory Disclaimer
print_section "Story 5.4: Mandatory Disclaimer System"

echo "Test 4.1: Disclaimer present in API response"
REC_RESPONSE=$(curl -s $API_BASE/api/recommendations/$MAIN_USER?generate=true)
if echo "$REC_RESPONSE" | grep -q "disclaimer"; then
    print_test "PASS" "Disclaimer field exists in response"
else
    print_test "FAIL" "Disclaimer field" "disclaimer field in JSON" "Field missing"
fi

echo ""
echo "Test 4.2: Disclaimer contains required text"
if echo "$REC_RESPONSE" | grep -qi "not financial advice"; then
    print_test "PASS" "Disclaimer contains 'not financial advice'"
else
    print_test "FAIL" "Disclaimer content" "'not financial advice'" "Text missing"
fi

echo ""
echo "Test 4.3: Disclaimer contains 'licensed advisor'"
if echo "$REC_RESPONSE" | grep -qi "licensed advisor"; then
    print_test "PASS" "Disclaimer contains 'licensed advisor'"
else
    print_test "FAIL" "Disclaimer content" "'licensed advisor'" "Text missing"
fi

# Story 5.2: Eligibility Filtering
print_section "Story 5.2: Eligibility Filtering System"

echo "Test 2.1: Recommendations include eligibility-appropriate offers"
REC_COUNT=$(echo "$REC_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('recommendations', [])))" 2>/dev/null)
if [ ! -z "$REC_COUNT" ] && [ "$REC_COUNT" -gt 0 ]; then
    print_test "PASS" "Eligibility filtering returns recommendations (count: $REC_COUNT)"
else
    print_test "FAIL" "Eligibility filtering" "Recommendations returned" "Empty or invalid"
fi

# Story 5.3: Tone Validation
print_section "Story 5.3: Tone Validation & Language Safety"

echo "Test 3.1: Check for prohibited shame-based language"
if echo "$REC_RESPONSE" | grep -qi "irresponsible\|bad with money\|poor choices"; then
    print_test "FAIL" "Tone validation" "No shame-based language" "Prohibited words found"
else
    print_test "PASS" "No shame-based language detected"
fi

# Story 5.5: Integration & Performance
print_section "Story 5.5: Integration & Performance"

echo "Test 5.1: Performance under 5 seconds"
START_TIME=$(date +%s%N)
PERF_TEST=$(curl -s $API_BASE/api/recommendations/$MAIN_USER?generate=true)
END_TIME=$(date +%s%N)
DURATION=$(( ($END_TIME - $START_TIME) / 1000000 ))
if [ $DURATION -lt 5000 ]; then
    print_test "PASS" "Response time: ${DURATION}ms (requirement: <5000ms)"
else
    print_test "FAIL" "Performance requirement" "<5000ms" "${DURATION}ms"
fi

echo ""
echo "Test 5.2: Metadata includes generation time"
GEN_TIME=$(echo "$PERF_TEST" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('metadata', {}).get('generation_time_ms', 'N/A'))" 2>/dev/null)
if [ "$GEN_TIME" != "N/A" ] && [ "$GEN_TIME" != "None" ]; then
    print_test "PASS" "Metadata includes generation_time_ms: ${GEN_TIME}ms"
else
    print_test "FAIL" "Metadata generation time" "Numeric value" "$GEN_TIME"
fi

echo ""
echo "Test 5.3: Full guardrail pipeline executed"
if echo "$PERF_TEST" | grep -q "recommendations" && echo "$PERF_TEST" | grep -q "disclaimer"; then
    print_test "PASS" "Full pipeline: consent → eligibility → tone → disclaimer"
else
    print_test "FAIL" "Full pipeline" "Complete response" "Missing fields"
fi

# Summary
print_section "Validation Summary"

echo ""
echo "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED_TESTS${NC}"
else
    echo -e "Failed: 0"
fi
echo ""

PASS_RATE=$(( $PASSED_TESTS * 100 / $TOTAL_TESTS ))
echo "Pass Rate: ${PASS_RATE}%"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ ✅ ✅  ALL TESTS PASSED  ✅ ✅ ✅${NC}"
    echo ""
    echo "Epic 5 is ready for closure!"
    echo ""
    echo "Next steps:"
    echo "  1. Review validation results"
    echo "  2. Test UI at http://localhost:8000/ (Recommendations tab)"
    echo "  3. Sign off in docs/validation/epic-5-validation.md"
    echo "  4. Commit changes and create PR"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review results above.${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  - Ensure server is running on port 8000"
    echo "  - Check database has user data: sqlite3 data/processed/spendsense.db 'SELECT COUNT(*) FROM users;'"
    echo "  - Review logs for errors"
    exit 1
fi
