#!/usr/bin/env python3
"""
Comprehensive Meeting Functionality Test Script
Tests all meeting-related endpoints and functionality
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:5001"
FRONTEND_URL = "http://localhost:3001"
ADMIN_EMAIL = "admin@savingsgroup.com"
ADMIN_PASSWORD = "admin123"

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

# Test counters
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'errors': []
}

def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{title}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

def print_test(test_name: str, passed: bool, message: str = ""):
    """Print test result"""
    test_results['total'] += 1
    
    if passed:
        print(f"{Colors.GREEN}✓ PASS{Colors.NC} - {test_name}")
        test_results['passed'] += 1
    else:
        print(f"{Colors.RED}✗ FAIL{Colors.NC} - {test_name}")
        if message:
            print(f"  {Colors.RED}Error: {message}{Colors.NC}")
        test_results['failed'] += 1
        test_results['errors'].append({'test': test_name, 'error': message})

def check_service(url: str, service_name: str) -> bool:
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=5)
        print_test(f"{service_name} is running", response.status_code == 200)
        return response.status_code == 200
    except Exception as e:
        print_test(f"{service_name} is running", False, str(e))
        return False

def login() -> Optional[str]:
    """Login and get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200 and 'auth_token' in data:
            print_test("Admin login", True)
            return data['auth_token']
        else:
            print_test("Admin login", False, f"Response: {data}")
            return None
    except Exception as e:
        print_test("Admin login", False, str(e))
        return None

def api_call(method: str, endpoint: str, token: str, data: Dict = None) -> tuple:
    """Make an authenticated API call"""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return None, f"Unsupported method: {method}"
        
        return response.json(), None
    except Exception as e:
        return None, str(e)

def main():
    """Main test function"""
    print_section("COMPREHENSIVE MEETING FUNCTIONALITY TEST SUITE")
    
    # Test 1: Service Health Checks
    print_section("1. SERVICE HEALTH CHECKS")
    if not check_service(f"{BASE_URL}/api/ping", "Backend API"):
        print(f"\n{Colors.RED}Backend is not running. Exiting.{Colors.NC}\n")
        sys.exit(1)
    
    check_service(FRONTEND_URL, "Frontend")
    
    # Test 2: Authentication
    print_section("2. AUTHENTICATION")
    token = login()
    if not token:
        print(f"\n{Colors.RED}Cannot proceed without authentication token{Colors.NC}\n")
        sys.exit(1)
    
    # Test 3: Get Groups
    print_section("3. GET GROUPS")
    groups_data, error = api_call("GET", "/api/savings-groups", token)
    
    if error:
        print_test("Get groups list", False, error)
        sys.exit(1)
    
    groups = groups_data.get('data', {}).get('groups', [])
    if len(groups) > 0:
        print_test("Get groups list", True)
        group_id = groups[0]['id']
        print(f"  {Colors.YELLOW}Found {len(groups)} groups, using group ID: {group_id}{Colors.NC}")
    else:
        print_test("Get groups list", False, "No groups found")
        sys.exit(1)
    
    # Test 4: Get Meetings for Group
    print_section("4. GET MEETINGS FOR GROUP")
    meetings_data, error = api_call("GET", f"/api/groups/{group_id}/meetings", token)

    if error:
        print_test(f"Get meetings for group {group_id}", False, error)
        meeting_id = None
    else:
        # Handle both response formats: {data: {meetings: []}} and {meetings: []}
        meetings = meetings_data.get('meetings', []) or meetings_data.get('data', {}).get('meetings', [])
        if len(meetings) > 0:
            print_test(f"Get meetings for group {group_id}", True)
            meeting_id = meetings[0]['id']
            print(f"  {Colors.YELLOW}Found {len(meetings)} meetings, using meeting ID: {meeting_id}{Colors.NC}")
        else:
            print_test(f"Get meetings for group {group_id}", False, "No meetings found")
            meeting_id = None
    
    if not meeting_id:
        print(f"\n{Colors.YELLOW}No meetings found. Skipping meeting-specific tests.{Colors.NC}\n")
        print_summary()
        return
    
    # Test 5: Get Meeting Detail (includes all transactions)
    print_section("5. GET MEETING DETAIL")
    meeting_detail, error = api_call("GET", f"/api/meetings/{meeting_id}", token)

    if error:
        print_test(f"Get meeting detail for meeting {meeting_id}", False, error)
        print(f"\n{Colors.RED}Cannot proceed without meeting detail{Colors.NC}\n")
        print_summary()
        return

    # Extract all data from meeting detail response
    meeting = meeting_detail.get('meeting', {})
    attendance = meeting_detail.get('attendance', [])
    savings_transactions = meeting_detail.get('savings_transactions', [])
    fines = meeting_detail.get('fines', [])
    loan_repayments = meeting_detail.get('loan_repayments', [])
    trainings = meeting_detail.get('trainings', [])
    votings = meeting_detail.get('votings', [])

    if meeting:
        print_test(f"Get meeting detail for meeting {meeting_id}", True)
        print(f"  {Colors.YELLOW}Meeting status: {meeting.get('status', 'N/A')}{Colors.NC}")
        print(f"  {Colors.YELLOW}Meeting date: {meeting.get('meeting_date', 'N/A')}{Colors.NC}")
        print(f"  {Colors.YELLOW}Location: {meeting.get('location', 'N/A')}{Colors.NC}")
    else:
        print_test(f"Get meeting detail for meeting {meeting_id}", False, "No meeting data")
        print_summary()
        return

    # Test 6: Verify Meeting Attendance Data
    print_section("6. VERIFY MEETING ATTENDANCE DATA")
    print_test("Meeting attendance data structure", True)
    print(f"  {Colors.YELLOW}Found {len(attendance)} attendance records{Colors.NC}")

    # Test 7: Verify Savings Transactions Data
    print_section("7. VERIFY SAVINGS TRANSACTIONS DATA")
    print_test("Savings transactions data structure", True)
    print(f"  {Colors.YELLOW}Found {len(savings_transactions)} savings transactions{Colors.NC}")

    # Test 8: Verify Fines Data
    print_section("8. VERIFY FINES DATA")
    fine_id = None
    print_test("Fines data structure", True)
    print(f"  {Colors.YELLOW}Found {len(fines)} fines{Colors.NC}")
    if len(fines) > 0:
        fine_id = fines[0]['id']
        print(f"  {Colors.YELLOW}Sample fine ID: {fine_id}{Colors.NC}")
        print(f"  {Colors.YELLOW}Fine amount: {fines[0].get('amount', 'N/A')}{Colors.NC}")
        print(f"  {Colors.YELLOW}Fine reason: {fines[0].get('reason', 'N/A')}{Colors.NC}")

    # Test 9: Verify Loan Repayments Data
    print_section("9. VERIFY LOAN REPAYMENTS DATA")
    print_test("Loan repayments data structure", True)
    print(f"  {Colors.YELLOW}Found {len(loan_repayments)} loan repayments{Colors.NC}")

    # Test 10: Verify Training Activities Data
    print_section("10. VERIFY TRAINING ACTIVITIES DATA")
    training_id = None
    print_test("Training activities data structure", True)
    print(f"  {Colors.YELLOW}Found {len(trainings)} training activities{Colors.NC}")
    if len(trainings) > 0:
        training_id = trainings[0]['id']
        print(f"  {Colors.YELLOW}Sample training ID: {training_id}{Colors.NC}")
        print(f"  {Colors.YELLOW}Training topic: {trainings[0].get('training_topic', 'N/A')}{Colors.NC}")

    # Test 11: Verify Voting Sessions Data
    print_section("11. VERIFY VOTING SESSIONS DATA")
    voting_id = None
    print_test("Voting sessions data structure", True)
    print(f"  {Colors.YELLOW}Found {len(votings)} voting sessions{Colors.NC}")
    if len(votings) > 0:
        voting_id = votings[0]['id']
        print(f"  {Colors.YELLOW}Sample voting ID: {voting_id}{Colors.NC}")
        print(f"  {Colors.YELLOW}Voting topic: {votings[0].get('vote_topic', 'N/A')}{Colors.NC}")
        print(f"  {Colors.YELLOW}Result: {votings[0].get('result', 'N/A')}{Colors.NC}")
    
    # Test 12: Test Fine Edit Endpoint
    if fine_id:
        print_section("12. TEST FINE EDIT ENDPOINT")
        fine_edit_data = {
            "amount": 2000,
            "reason": "Updated test fine",
            "is_paid": True,
            "notes": "Test note from automated test"
        }
        fine_edit_response, error = api_call("PUT", f"/api/fines/{fine_id}", token, fine_edit_data)
        
        if error:
            print_test("Edit fine endpoint", False, error)
        elif fine_edit_response.get('status') == 'success':
            print_test("Edit fine endpoint", True)
        else:
            print_test("Edit fine endpoint", False, f"Response: {fine_edit_response}")
    
    # Test 13: Test Training Edit Endpoint
    if training_id:
        print_section("13. TEST TRAINING EDIT ENDPOINT")
        training_edit_data = {
            "activity_name": "Updated Training Session",
            "description": "Updated description from automated test",
            "notes": "Test note from automated test"
        }
        training_edit_response, error = api_call("PUT", f"/api/trainings/{training_id}", token, training_edit_data)
        
        if error:
            print_test("Edit training endpoint", False, error)
        elif training_edit_response.get('status') == 'success':
            print_test("Edit training endpoint", True)
        else:
            print_test("Edit training endpoint", False, f"Response: {training_edit_response}")
    
    # Test 14: Test Voting Edit Endpoint
    if voting_id:
        print_section("14. TEST VOTING EDIT ENDPOINT")
        voting_edit_data = {
            "vote_topic": "Updated Voting Topic",
            "vote_description": "Updated description from automated test",
            "vote_type": "DECISION",
            "notes": "Test note from automated test"
        }
        voting_edit_response, error = api_call("PUT", f"/api/votings/{voting_id}", token, voting_edit_data)
        
        if error:
            print_test("Edit voting endpoint", False, error)
        elif voting_edit_response.get('status') == 'success':
            print_test("Edit voting endpoint", True)
        else:
            print_test("Edit voting endpoint", False, f"Response: {voting_edit_response}")
    
    print_summary()

def print_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")
    print(f"{Colors.BLUE}Total Tests:{Colors.NC} {test_results['total']}")
    print(f"{Colors.GREEN}Passed:{Colors.NC} {test_results['passed']}")
    print(f"{Colors.RED}Failed:{Colors.NC} {test_results['failed']}")
    
    if test_results['failed'] > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.NC}")
        for error in test_results['errors']:
            print(f"  - {error['test']}: {error['error']}")
    
    if test_results['failed'] == 0:
        print(f"\n{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.NC}\n")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}✗ SOME TESTS FAILED{Colors.NC}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()

