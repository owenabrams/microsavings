#!/usr/bin/env python3
"""
Phase 3.5 Testing Script - Document Upload Integration
Tests document upload during transaction recording in MeetingWorkspace
"""

import requests
import json
import os
import sys

BASE_URL = "http://localhost:5001/api"

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def login():
    """Login and get JWT token"""
    print_header("TEST 1: Login")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "alice.mukamana@example.com", "password": "password123"}
    )

    if response.status_code == 200:
        token = response.json()['auth_token']
        print_success(f"Login successful. Token: {token[:20]}...")
        return token
    else:
        print_error(f"Login failed: {response.text}")
        sys.exit(1)

def get_meeting_detail(token, meeting_id):
    """Get meeting details"""
    print_header(f"TEST 2: Get Meeting {meeting_id} Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/meetings/{meeting_id}", headers=headers)

    if response.status_code == 200:
        data = response.json()
        meeting = data.get('meeting', {})
        print_success(f"Meeting: {meeting.get('meeting_type', 'N/A')} - {data.get('status', 'N/A')}")
        print_info(f"Savings transactions: {len(data.get('savings_transactions', []))}")
        print_info(f"Fines: {len(data.get('fines', []))}")
        print_info(f"Trainings: {len(data.get('trainings', []))}")
        print_info(f"Votings: {len(data.get('votings', []))}")
        return data
    else:
        print_error(f"Failed to get meeting: {response.text}")
        return None

def record_savings_with_document(token, meeting_id, member_id):
    """Record savings transaction with document"""
    print_header("TEST 3: Record Savings with Document")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Record savings transaction
    savings_data = {
        "member_id": member_id,
        "saving_type_id": 1,
        "transaction_type": "DEPOSIT",
        "amount": 5000
    }
    
    response = requests.post(
        f"{BASE_URL}/meetings/{meeting_id}/savings",
        headers=headers,
        json=savings_data
    )
    
    if response.status_code != 201:
        print_error(f"Failed to record savings: {response.text}")
        return None
    
    transaction_id = response.json()['data']['transactions'][0]['id']
    print_success(f"Savings transaction recorded. ID: {transaction_id}")
    
    # Upload document
    print_info("Uploading document...")
    
    # Create a test file
    test_file_path = "/tmp/test_savings_receipt.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test savings receipt document for Phase 3.5 testing.\n")
        f.write(f"Transaction ID: {transaction_id}\n")
        f.write(f"Amount: 5000\n")
    
    with open(test_file_path, "rb") as f:
        files = {"files": ("savings_receipt.txt", f, "text/plain")}
        data = {
            "document_type": "RECEIPT",
            "document_category": "FINANCIAL",
            "description": "Savings deposit receipt"
        }
        
        response = requests.post(
            f"{BASE_URL}/transaction-documents/documents/savings/{transaction_id}",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 201:
        doc_data = response.json()['data']
        print_success(f"Document uploaded. Count: {doc_data['uploaded_count']}")
        return transaction_id
    else:
        print_error(f"Failed to upload document: {response.text}")
        return None

def record_fine_with_document(token, meeting_id, member_id):
    """Record fine with document"""
    print_header("TEST 4: Record Fine with Document")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Record fine
    fine_data = {
        "member_id": member_id,
        "fine_type": "LATE_ARRIVAL",
        "amount": 500,
        "reason": "Arrived 15 minutes late"
    }
    
    response = requests.post(
        f"{BASE_URL}/meetings/{meeting_id}/fines",
        headers=headers,
        json=fine_data
    )
    
    if response.status_code != 201:
        print_error(f"Failed to record fine: {response.text}")
        return None
    
    fine_id = response.json()['data']['fines'][0]['id']
    print_success(f"Fine recorded. ID: {fine_id}")
    
    # Upload document
    print_info("Uploading document...")
    
    test_file_path = "/tmp/test_fine_receipt.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test fine payment receipt for Phase 3.5 testing.\n")
        f.write(f"Fine ID: {fine_id}\n")
        f.write(f"Amount: 500\n")
    
    with open(test_file_path, "rb") as f:
        files = {"files": ("fine_receipt.txt", f, "text/plain")}
        data = {
            "document_type": "RECEIPT",
            "document_category": "FINANCIAL",
            "description": "Fine payment receipt"
        }
        
        response = requests.post(
            f"{BASE_URL}/transaction-documents/documents/fine/{fine_id}",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 201:
        doc_data = response.json()['data']
        print_success(f"Document uploaded. Count: {doc_data['uploaded_count']}")
        return fine_id
    else:
        print_error(f"Failed to upload document: {response.text}")
        return None

def create_training_with_document(token, meeting_id):
    """Create training with document"""
    print_header("TEST 5: Create Training with Document")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create training
    training_data = {
        "training_topic": "Financial Literacy Workshop",
        "trainer_name": "John Doe",
        "duration_minutes": 60,
        "training_description": "Workshop on budgeting and savings"
    }
    
    response = requests.post(
        f"{BASE_URL}/meetings/{meeting_id}/training",
        headers=headers,
        json=training_data
    )
    
    if response.status_code != 201:
        print_error(f"Failed to create training: {response.text}")
        return None
    
    training_id = response.json()['data']['training_id']
    print_success(f"Training created. ID: {training_id}")
    
    # Upload document
    print_info("Uploading training materials...")
    
    test_file_path = "/tmp/test_training_materials.txt"
    with open(test_file_path, "w") as f:
        f.write("Financial Literacy Workshop Materials\n")
        f.write("=" * 50 + "\n\n")
        f.write("1. Introduction to Budgeting\n")
        f.write("2. Savings Strategies\n")
        f.write("3. Investment Basics\n")
    
    with open(test_file_path, "rb") as f:
        files = {"files": ("training_materials.txt", f, "text/plain")}
        data = {
            "document_type": "REPORT",
            "document_category": "TRAINING",
            "description": "Training session materials"
        }
        
        response = requests.post(
            f"{BASE_URL}/transaction-documents/documents/training/{training_id}",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 201:
        doc_data = response.json()['data']
        print_success(f"Document uploaded. Count: {doc_data['uploaded_count']}")
        return training_id
    else:
        print_error(f"Failed to upload document: {response.text}")
        return None

def verify_documents_in_meeting(token, meeting_id):
    """Verify all documents appear in meeting detail"""
    print_header("TEST 6: Verify Documents in Meeting Detail")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/meetings/{meeting_id}", headers=headers)

    if response.status_code != 200:
        print_error(f"Failed to get meeting: {response.text}")
        return False

    data = response.json()
    
    # Check savings documents
    savings_with_docs = [s for s in data.get('savings_transactions', []) if s.get('documents')]
    print_info(f"Savings transactions with documents: {len(savings_with_docs)}")
    
    # Check fines documents
    fines_with_docs = [f for f in data.get('fines', []) if f.get('documents')]
    print_info(f"Fines with documents: {len(fines_with_docs)}")
    
    # Check training documents
    trainings_with_docs = [t for t in data.get('trainings', []) if t.get('documents')]
    print_info(f"Trainings with documents: {len(trainings_with_docs)}")
    
    if savings_with_docs or fines_with_docs or trainings_with_docs:
        print_success("Documents found in meeting detail!")
        return True
    else:
        print_error("No documents found in meeting detail")
        return False

def main():
    print_header("PHASE 3.5 - DOCUMENT UPLOAD INTEGRATION TEST")
    print_info("Testing document upload during transaction recording")
    
    # Login
    token = login()
    
    # Get meeting detail
    meeting_id = 37
    meeting = get_meeting_detail(token, meeting_id)
    
    if not meeting:
        print_error("Cannot proceed without meeting data")
        sys.exit(1)
    
    # Get first member ID
    member_id = 1
    
    # Test savings with document
    record_savings_with_document(token, meeting_id, member_id)
    
    # Test fine with document
    record_fine_with_document(token, meeting_id, member_id)
    
    # Test training with document
    create_training_with_document(token, meeting_id)
    
    # Verify documents appear in meeting
    verify_documents_in_meeting(token, meeting_id)
    
    print_header("TEST SUMMARY")
    print_success("All tests completed!")
    print_info("Next steps:")
    print_info("1. Open http://localhost:3001 in browser")
    print_info("2. Login as alice.mukamana@example.com / password123")
    print_info("3. Navigate to meeting 37")
    print_info("4. Check that documents appear with download/delete buttons")
    print_info("5. Test uploading documents from the UI")

if __name__ == "__main__":
    main()

