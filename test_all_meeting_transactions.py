#!/usr/bin/env python3
"""
Comprehensive test for all meeting transaction types.
Tests all 5 transaction tables across multiple meetings.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5001/api"
FRONTEND_URL = "http://localhost:3001"

def test_all_transactions():
    """Test all meeting transaction types."""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE MEETING TRANSACTIONS TEST")
    print("="*60)
    
    # 1. Login
    print("\n1. Authenticating...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@savingsgroup.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"✗ Login failed: {login_response.status_code}")
        return False
    
    token = login_response.json()['auth_token']
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Authenticated successfully")
    
    # 2. Get groups
    print("\n2. Getting groups...")
    groups_response = requests.get(f"{BASE_URL}/savings-groups", headers=headers)
    
    if groups_response.status_code != 200:
        print(f"✗ Failed to get groups: {groups_response.status_code}")
        return False
    
    groups_data = groups_response.json()
    if 'data' in groups_data and 'groups' in groups_data['data']:
        groups = groups_data['data']['groups']
    elif 'groups' in groups_data:
        groups = groups_data['groups']
    else:
        print(f"✗ Unexpected groups response structure")
        return False
    
    if not groups:
        print("✗ No groups found")
        return False
    
    group_id = groups[0]['id']
    group_name = groups[0]['name']
    print(f"✓ Found {len(groups)} groups, testing with: {group_name} (ID: {group_id})")
    
    # 3. Get meetings for the group
    print("\n3. Getting meetings...")
    meetings_response = requests.get(f"{BASE_URL}/groups/{group_id}/meetings", headers=headers)
    
    if meetings_response.status_code != 200:
        print(f"✗ Failed to get meetings: {meetings_response.status_code}")
        return False
    
    meetings_data = meetings_response.json()
    if 'data' in meetings_data and 'meetings' in meetings_data['data']:
        meetings = meetings_data['data']['meetings']
    elif 'meetings' in meetings_data:
        meetings = meetings_data['meetings']
    else:
        print(f"✗ Unexpected meetings response structure")
        return False
    
    if not meetings:
        print("✗ No meetings found")
        return False
    
    print(f"✓ Found {len(meetings)} meetings")
    
    # 4. Test each meeting and collect transaction statistics
    print("\n4. Testing all meetings and transactions...")
    print("-" * 60)
    
    total_stats = {
        'meetings_tested': 0,
        'attendance_records': 0,
        'savings_transactions': 0,
        'fines': 0,
        'loan_repayments': 0,
        'trainings': 0,
        'votings': 0
    }
    
    for meeting in meetings:
        meeting_id = meeting['id']
        meeting_num = meeting['meeting_number']
        
        # Get meeting detail
        detail_response = requests.get(f"{BASE_URL}/meetings/{meeting_id}", headers=headers)
        
        if detail_response.status_code != 200:
            print(f"✗ Meeting #{meeting_num} (ID: {meeting_id}): Failed to get details")
            continue
        
        detail = detail_response.json()
        
        # Count transactions
        attendance_count = len(detail.get('attendance', []))
        savings_count = len(detail.get('savings_transactions', []))
        fines_count = len(detail.get('fines', []))
        loans_count = len(detail.get('loan_repayments', []))
        trainings_count = len(detail.get('trainings', []))
        votings_count = len(detail.get('votings', []))
        
        total_stats['meetings_tested'] += 1
        total_stats['attendance_records'] += attendance_count
        total_stats['savings_transactions'] += savings_count
        total_stats['fines'] += fines_count
        total_stats['loan_repayments'] += loans_count
        total_stats['trainings'] += trainings_count
        total_stats['votings'] += votings_count
        
        # Print meeting summary
        status_icon = "✓" if detail_response.status_code == 200 else "✗"
        print(f"{status_icon} Meeting #{meeting_num} (ID: {meeting_id}):")
        print(f"    Attendance: {attendance_count}")
        print(f"    Savings: {savings_count}")
        print(f"    Fines: {fines_count}")
        print(f"    Loan Repayments: {loans_count}")
        print(f"    Trainings: {trainings_count}")
        print(f"    Votings: {votings_count}")
        
        # Show details for trainings
        if trainings_count > 0:
            for training in detail.get('trainings', []):
                print(f"      → Training: {training.get('training_topic', 'N/A')}")
                print(f"         Trainer: {training.get('trainer_name', 'N/A')}")
                print(f"         Attendees: {training.get('total_attendees', 0)}")
        
        # Show details for votings
        if votings_count > 0:
            for voting in detail.get('votings', []):
                print(f"      → Voting: {voting.get('vote_topic', 'N/A')}")
                print(f"         Result: {voting.get('result', 'N/A')}")
                print(f"         Yes: {voting.get('yes_count', 0)}, No: {voting.get('no_count', 0)}, Abstain: {voting.get('abstain_count', 0)}")
        
        # Show details for fines
        if fines_count > 0:
            for fine in detail.get('fines', []):
                print(f"      → Fine: {fine.get('fine_reason', 'N/A')}")
                print(f"         Amount: {fine.get('fine_amount', 0)}")
    
    # 5. Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Meetings Tested: {total_stats['meetings_tested']}")
    print(f"Total Attendance Records: {total_stats['attendance_records']}")
    print(f"Total Savings Transactions: {total_stats['savings_transactions']}")
    print(f"Total Fines: {total_stats['fines']}")
    print(f"Total Loan Repayments: {total_stats['loan_repayments']}")
    print(f"Total Trainings: {total_stats['trainings']}")
    print(f"Total Votings: {total_stats['votings']}")
    print("="*60)
    
    # 6. Verify we have data in all transaction types
    success = True
    if total_stats['attendance_records'] == 0:
        print("⚠ WARNING: No attendance records found")
        success = False
    if total_stats['fines'] == 0:
        print("⚠ WARNING: No fines found")
        success = False
    if total_stats['trainings'] == 0:
        print("⚠ WARNING: No trainings found")
        success = False
    if total_stats['votings'] == 0:
        print("⚠ WARNING: No votings found")
        success = False
    
    if success:
        print("\n✓ ALL TRANSACTION TYPES VERIFIED!")
        print(f"\n🌐 View the group at: {FRONTEND_URL}/groups/{group_id}")
        return True
    else:
        print("\n✗ SOME TRANSACTION TYPES ARE MISSING")
        return False

if __name__ == '__main__':
    try:
        success = test_all_transactions()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

