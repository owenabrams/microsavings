#!/bin/bash

# Backend API Testing Script
# Tests all transaction edit endpoints

BASE_URL="http://localhost:5001"
echo "🧪 COMPREHENSIVE BACKEND API TESTING"
echo "===================================="
echo ""

# Step 1: Login and get token
echo "1️⃣ Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@savingsgroup.com","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"auth_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed! Response:"
  echo "$LOGIN_RESPONSE"
  exit 1
fi

echo "✅ Login successful! Token: ${TOKEN:0:20}..."
echo ""

# Step 2: Get groups
echo "2️⃣ Testing Get Groups..."
GROUPS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/groups" \
  -H "Authorization: Bearer $TOKEN")

echo "$GROUPS_RESPONSE" | head -c 200
echo "..."
echo ""

# Step 3: Get meetings for a group
echo "3️⃣ Testing Get Meetings..."
MEETINGS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/groups/2/meetings" \
  -H "Authorization: Bearer $TOKEN")

echo "$MEETINGS_RESPONSE" | head -c 200
echo "..."
echo ""

# Step 4: Get meeting detail
echo "4️⃣ Testing Get Meeting Detail..."
MEETING_DETAIL=$(curl -s -X GET "$BASE_URL/api/meetings/24" \
  -H "Authorization: Bearer $TOKEN")

echo "$MEETING_DETAIL" | head -c 300
echo "..."
echo ""

# Step 5: Test UPDATE endpoints
echo "5️⃣ Testing UPDATE Savings Transaction Endpoint..."
UPDATE_SAVINGS=$(curl -s -X PUT "$BASE_URL/api/savings-transactions/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":15000,"notes":"Updated via API test"}')

echo "Response: $UPDATE_SAVINGS"
echo ""

echo "6️⃣ Testing UPDATE Fine Endpoint..."
UPDATE_FINE=$(curl -s -X PUT "$BASE_URL/api/fines/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":5000,"notes":"Updated fine via API test"}')

echo "Response: $UPDATE_FINE"
echo ""

echo "7️⃣ Testing UPDATE Loan Repayment Endpoint..."
UPDATE_LOAN=$(curl -s -X PUT "$BASE_URL/api/loan-repayments/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"principal_amount":20000,"notes":"Updated loan via API test"}')

echo "Response: $UPDATE_LOAN"
echo ""

echo "8️⃣ Testing UPDATE Training Endpoint..."
UPDATE_TRAINING=$(curl -s -X PUT "$BASE_URL/api/trainings/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Updated Training Topic","notes":"Updated via API test"}')

echo "Response: $UPDATE_TRAINING"
echo ""

echo "9️⃣ Testing UPDATE Voting Endpoint..."
UPDATE_VOTING=$(curl -s -X PUT "$BASE_URL/api/votings/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic":"Updated Voting Topic","notes":"Updated via API test"}')

echo "Response: $UPDATE_VOTING"
echo ""

# Step 6: Check backend logs for errors
echo "🔟 Checking Backend Logs for Errors..."
docker logs testdriven_backend --tail 50 | grep -i "error\|exception\|traceback" || echo "✅ No errors found in logs"
echo ""

echo "===================================="
echo "✅ BACKEND TESTING COMPLETE!"
echo "===================================="

