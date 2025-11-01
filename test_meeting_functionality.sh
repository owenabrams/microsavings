#!/bin/bash

# Comprehensive Meeting Functionality Test Script
# Tests all meeting-related endpoints and functionality

set -e

BASE_URL="http://localhost:5001"
FRONTEND_URL="http://localhost:3001"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print test results
print_test() {
    local test_name=$1
    local status=$2
    local message=$3
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}✓ PASS${NC} - $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAIL${NC} - $test_name"
        echo -e "  ${RED}Error: $message${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Function to print section header
print_section() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# Function to check if service is running
check_service() {
    local url=$1
    local service_name=$2
    
    if curl -s -f -o /dev/null "$url"; then
        print_test "$service_name is running" "PASS"
        return 0
    else
        print_test "$service_name is running" "FAIL" "Service not accessible at $url"
        return 1
    fi
}

# Function to login and get token
login() {
    local response=$(curl -s -X POST "$BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@savingsgroup.com","password":"admin123"}')

    local token=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('auth_token', ''))" 2>/dev/null)

    if [ -n "$token" ] && [ "$token" != "None" ]; then
        print_test "Admin login" "PASS"
        echo "$token"
        return 0
    else
        print_test "Admin login" "FAIL" "Could not get auth token: $response"
        echo ""
        return 1
    fi
}

# Function to make authenticated API call
api_call() {
    local method=$1
    local endpoint=$2
    local token=$3
    local data=$4
    
    if [ -n "$data" ]; then
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data"
    else
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token"
    fi
}

print_section "MEETING FUNCTIONALITY TEST SUITE"

# Test 1: Check if services are running
print_section "1. SERVICE HEALTH CHECKS"
check_service "$BASE_URL/api/ping" "Backend API" || exit 1
check_service "$FRONTEND_URL" "Frontend" || exit 1

# Test 2: Authentication
print_section "2. AUTHENTICATION"
TOKEN=$(login)
if [ -z "$TOKEN" ]; then
    echo -e "${RED}Cannot proceed without authentication token${NC}"
    exit 1
fi

# Test 3: Get groups
print_section "3. GET GROUPS"
GROUPS_RESPONSE=$(api_call "GET" "/api/savings-groups" "$TOKEN")
echo "$GROUPS_RESPONSE" > /tmp/groups_response.json
GROUP_COUNT=$(echo "$GROUPS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('groups', [])))" 2>/dev/null || echo "0")

if [ "$GROUP_COUNT" -gt 0 ]; then
    print_test "Get groups list" "PASS"
    GROUP_ID=$(echo "$GROUPS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('groups', [{}])[0].get('id', ''))" 2>/dev/null)
    echo -e "  ${YELLOW}Found $GROUP_COUNT groups, using group ID: $GROUP_ID${NC}"
else
    print_test "Get groups list" "FAIL" "No groups found. Response: $(cat /tmp/groups_response.json)"
    exit 1
fi

# Test 4: Get meetings for group
print_section "4. GET MEETINGS FOR GROUP"
MEETINGS_RESPONSE=$(api_call "GET" "/api/groups/$GROUP_ID/meetings" "$TOKEN")
MEETING_COUNT=$(echo $MEETINGS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('meetings', [])))" 2>/dev/null)

if [ "$MEETING_COUNT" -gt 0 ]; then
    print_test "Get meetings for group $GROUP_ID" "PASS"
    MEETING_ID=$(echo $MEETINGS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('meetings', [{}])[0].get('id', ''))" 2>/dev/null)
    echo -e "  ${YELLOW}Found $MEETING_COUNT meetings, using meeting ID: $MEETING_ID${NC}"
else
    print_test "Get meetings for group $GROUP_ID" "FAIL" "No meetings found"
fi

# Test 5: Get meeting detail
if [ -n "$MEETING_ID" ]; then
    print_section "5. GET MEETING DETAIL"
    MEETING_DETAIL=$(api_call "GET" "/api/meetings/$MEETING_ID" "$TOKEN")
    MEETING_STATUS=$(echo $MEETING_DETAIL | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('meeting', {}).get('status', ''))" 2>/dev/null)
    
    if [ -n "$MEETING_STATUS" ]; then
        print_test "Get meeting detail for meeting $MEETING_ID" "PASS"
        echo -e "  ${YELLOW}Meeting status: $MEETING_STATUS${NC}"
    else
        print_test "Get meeting detail for meeting $MEETING_ID" "FAIL" "Could not get meeting status"
    fi
fi

# Test 6: Get meeting attendance
if [ -n "$MEETING_ID" ]; then
    print_section "6. GET MEETING ATTENDANCE"
    ATTENDANCE_RESPONSE=$(api_call "GET" "/api/meetings/$MEETING_ID/attendance" "$TOKEN")
    ATTENDANCE_COUNT=$(echo $ATTENDANCE_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('attendance', [])))" 2>/dev/null)
    
    if [ "$ATTENDANCE_COUNT" -ge 0 ]; then
        print_test "Get meeting attendance" "PASS"
        echo -e "  ${YELLOW}Found $ATTENDANCE_COUNT attendance records${NC}"
    else
        print_test "Get meeting attendance" "FAIL" "Could not get attendance records"
    fi
fi

# Test 7: Get savings transactions
if [ -n "$MEETING_ID" ]; then
    print_section "7. GET SAVINGS TRANSACTIONS"
    SAVINGS_RESPONSE=$(api_call "GET" "/api/meetings/$MEETING_ID/savings-transactions" "$TOKEN")
    SAVINGS_COUNT=$(echo $SAVINGS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('transactions', [])))" 2>/dev/null)
    
    if [ "$SAVINGS_COUNT" -ge 0 ]; then
        print_test "Get savings transactions" "PASS"
        echo -e "  ${YELLOW}Found $SAVINGS_COUNT savings transactions${NC}"
    else
        print_test "Get savings transactions" "FAIL" "Could not get savings transactions"
    fi
fi

# Test 8: Get fines
if [ -n "$MEETING_ID" ]; then
    print_section "8. GET FINES"
    FINES_RESPONSE=$(api_call "GET" "/api/meetings/$MEETING_ID/fines" "$TOKEN")
    FINES_COUNT=$(echo $FINES_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('fines', [])))" 2>/dev/null)
    
    if [ "$FINES_COUNT" -ge 0 ]; then
        print_test "Get fines" "PASS"
        echo -e "  ${YELLOW}Found $FINES_COUNT fines${NC}"
        
        if [ "$FINES_COUNT" -gt 0 ]; then
            FINE_ID=$(echo $FINES_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('fines', [{}])[0].get('id', ''))" 2>/dev/null)
            echo -e "  ${YELLOW}Sample fine ID: $FINE_ID${NC}"
        fi
    else
        print_test "Get fines" "FAIL" "Could not get fines"
    fi
fi

# Test 9: Get loan repayments
if [ -n "$MEETING_ID" ]; then
    print_section "9. GET LOAN REPAYMENTS"
    LOANS_RESPONSE=$(api_call "GET" "/api/meetings/$MEETING_ID/loan-repayments" "$TOKEN")
    LOANS_COUNT=$(echo $LOANS_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('repayments', [])))" 2>/dev/null)
    
    if [ "$LOANS_COUNT" -ge 0 ]; then
        print_test "Get loan repayments" "PASS"
        echo -e "  ${YELLOW}Found $LOANS_COUNT loan repayments${NC}"
    else
        print_test "Get loan repayments" "FAIL" "Could not get loan repayments"
    fi
fi

# Test 10: Get training activities
if [ -n "$MEETING_ID" ]; then
    print_section "10. GET TRAINING ACTIVITIES"
    TRAINING_RESPONSE=$(api_call "GET" "/api/meetings/$MEETING_ID/trainings" "$TOKEN")
    TRAINING_COUNT=$(echo $TRAINING_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('trainings', [])))" 2>/dev/null)
    
    if [ "$TRAINING_COUNT" -ge 0 ]; then
        print_test "Get training activities" "PASS"
        echo -e "  ${YELLOW}Found $TRAINING_COUNT training activities${NC}"
        
        if [ "$TRAINING_COUNT" -gt 0 ]; then
            TRAINING_ID=$(echo $TRAINING_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('trainings', [{}])[0].get('id', ''))" 2>/dev/null)
            echo -e "  ${YELLOW}Sample training ID: $TRAINING_ID${NC}"
        fi
    else
        print_test "Get training activities" "FAIL" "Could not get training activities"
    fi
fi

# Test 11: Get voting sessions
if [ -n "$MEETING_ID" ]; then
    print_section "11. GET VOTING SESSIONS"
    VOTING_RESPONSE=$(api_call "GET" "/api/meetings/$MEETING_ID/votings" "$TOKEN")
    VOTING_COUNT=$(echo $VOTING_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('data', {}).get('votings', [])))" 2>/dev/null)
    
    if [ "$VOTING_COUNT" -ge 0 ]; then
        print_test "Get voting sessions" "PASS"
        echo -e "  ${YELLOW}Found $VOTING_COUNT voting sessions${NC}"
        
        if [ "$VOTING_COUNT" -gt 0 ]; then
            VOTING_ID=$(echo $VOTING_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('votings', [{}])[0].get('id', ''))" 2>/dev/null)
            echo -e "  ${YELLOW}Sample voting ID: $VOTING_ID${NC}"
        fi
    else
        print_test "Get voting sessions" "FAIL" "Could not get voting sessions"
    fi
fi

# Test 12: Test fine edit endpoint (if fine exists)
if [ -n "$FINE_ID" ]; then
    print_section "12. TEST FINE EDIT ENDPOINT"
    FINE_EDIT_DATA='{"amount": 2000, "reason": "Updated test fine", "is_paid": true, "notes": "Test note"}'
    FINE_EDIT_RESPONSE=$(api_call "PUT" "/api/fines/$FINE_ID" "$TOKEN" "$FINE_EDIT_DATA")
    FINE_EDIT_STATUS=$(echo "$FINE_EDIT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', ''))" 2>/dev/null)

    if [ "$FINE_EDIT_STATUS" = "success" ]; then
        print_test "Edit fine endpoint" "PASS"
    else
        print_test "Edit fine endpoint" "FAIL" "Response: $FINE_EDIT_RESPONSE"
    fi
fi

# Test 13: Test training edit endpoint (if training exists)
if [ -n "$TRAINING_ID" ]; then
    print_section "13. TEST TRAINING EDIT ENDPOINT"
    TRAINING_EDIT_DATA='{"activity_name": "Updated Training", "description": "Updated description", "notes": "Test note"}'
    TRAINING_EDIT_RESPONSE=$(api_call "PUT" "/api/trainings/$TRAINING_ID" "$TOKEN" "$TRAINING_EDIT_DATA")
    TRAINING_EDIT_STATUS=$(echo "$TRAINING_EDIT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', ''))" 2>/dev/null)

    if [ "$TRAINING_EDIT_STATUS" = "success" ]; then
        print_test "Edit training endpoint" "PASS"
    else
        print_test "Edit training endpoint" "FAIL" "Response: $TRAINING_EDIT_RESPONSE"
    fi
fi

# Test 14: Test voting edit endpoint (if voting exists)
if [ -n "$VOTING_ID" ]; then
    print_section "14. TEST VOTING EDIT ENDPOINT"
    VOTING_EDIT_DATA='{"vote_topic": "Updated Topic", "vote_description": "Updated description", "vote_type": "DECISION", "notes": "Test note"}'
    VOTING_EDIT_RESPONSE=$(api_call "PUT" "/api/votings/$VOTING_ID" "$TOKEN" "$VOTING_EDIT_DATA")
    VOTING_EDIT_STATUS=$(echo "$VOTING_EDIT_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', ''))" 2>/dev/null)

    if [ "$VOTING_EDIT_STATUS" = "success" ]; then
        print_test "Edit voting endpoint" "PASS"
    else
        print_test "Edit voting endpoint" "FAIL" "Response: $VOTING_EDIT_RESPONSE"
    fi
fi

# Test 15: Check backend logs for errors
print_section "15. CHECK BACKEND LOGS FOR ERRORS"
BACKEND_ERRORS=$(docker logs testdriven_backend 2>&1 | tail -100 | grep -i "error\|exception\|traceback" | wc -l)
if [ "$BACKEND_ERRORS" -eq 0 ]; then
    print_test "Backend logs clean (no errors)" "PASS"
else
    print_test "Backend logs clean (no errors)" "FAIL" "Found $BACKEND_ERRORS error lines in logs"
    echo -e "${YELLOW}Recent backend errors:${NC}"
    docker logs testdriven_backend 2>&1 | tail -100 | grep -i "error\|exception\|traceback" | head -10
fi

print_section "TEST SUMMARY"
echo -e "${BLUE}Total Tests:${NC} $TOTAL_TESTS"
echo -e "${GREEN}Passed:${NC} $PASSED_TESTS"
echo -e "${RED}Failed:${NC} $FAILED_TESTS"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}✓ ALL TESTS PASSED!${NC}\n"
    exit 0
else
    echo -e "\n${RED}✗ SOME TESTS FAILED${NC}\n"
    exit 1
fi

