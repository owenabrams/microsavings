#!/usr/bin/env python3
"""
Test script for document preview functionality.
Tests preview generation and retrieval for different file types.
"""

import requests
import json
import os
import sys
from io import BytesIO
from PIL import Image

# Configuration
BASE_URL = "http://localhost:5001/api"
LOGIN_EMAIL = "alice.mukamana@example.com"
LOGIN_PASSWORD = "password123"

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_success(text):
    """Print success message."""
    print(f"✅ {text}")

def print_error(text):
    """Print error message."""
    print(f"❌ {text}")

def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")

def login():
    """Login and get JWT token."""
    print_header("TEST 1: Login")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": LOGIN_EMAIL, "password": LOGIN_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('auth_token')
        print_success(f"Login successful")
        print_info(f"Token: {token[:20]}...")
        return token
    else:
        print_error(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def create_test_image():
    """Create a test image file."""
    print_header("Creating Test Image")
    
    # Create a simple test image
    img = Image.new('RGB', (800, 600), color=(73, 109, 137))
    
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    print_success("Test image created (800x600 JPEG)")
    return img_bytes

def upload_document_with_image(token):
    """Upload a document with an image to test preview generation."""
    print_header("TEST 2: Upload Image Document")

    # Create test image
    img_bytes = create_test_image()

    # Upload to a voting record (entity_type=voting, entity_id=2)
    headers = {"Authorization": f"Bearer {token}"}
    files = {
        'files': ('test_preview_image.jpg', img_bytes, 'image/jpeg')
    }
    data = {
        'document_type': 'PHOTO',
        'document_category': 'VOTING',
        'description': 'Test image for preview functionality'
    }
    
    response = requests.post(
        f"{BASE_URL}/transaction-documents/documents/voting/2",
        headers=headers,
        files=files,
        data=data
    )
    
    if response.status_code == 201:
        result = response.json()
        documents = result.get('data', {}).get('uploaded', [])
        if documents:
            doc = documents[0]
            print_success(f"Document uploaded successfully")
            print_info(f"Document ID: {doc['id']}")
            print_info(f"Has Preview: {doc.get('has_preview', False)}")
            print_info(f"Thumbnail Path: {doc.get('thumbnail_path', 'None')}")
            print_info(f"Preview Path: {doc.get('preview_path', 'None')}")
            return doc['id']
        else:
            print_error("No documents in response")
            print_error(f"Response: {json.dumps(result, indent=2)}")
            return None
    else:
        print_error(f"Upload failed: {response.status_code}")
        print(response.text)
        return None

def get_document_details(token, document_id):
    """Get document details."""
    print_header("TEST 3: Get Document Details")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/transaction-documents/documents/{document_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        doc = data.get('data', {}).get('document', {})
        print_success("Document details retrieved")
        print_info(f"Filename: {doc.get('original_filename')}")
        print_info(f"MIME Type: {doc.get('mime_type')}")
        print_info(f"File Size: {doc.get('file_size')} bytes")
        print_info(f"Has Preview: {doc.get('has_preview', False)}")
        return doc
    else:
        print_error(f"Failed to get document details: {response.status_code}")
        print(response.text)
        return None

def get_thumbnail(token, document_id):
    """Get document thumbnail."""
    print_header("TEST 4: Get Thumbnail")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/transaction-documents/documents/{document_id}/preview",
        headers=headers,
        params={'type': 'thumbnail'}
    )
    
    if response.status_code == 200:
        print_success("Thumbnail retrieved successfully")
        print_info(f"Content-Type: {response.headers.get('Content-Type')}")
        print_info(f"Size: {len(response.content)} bytes")
        
        # Try to load as image
        try:
            img = Image.open(BytesIO(response.content))
            print_info(f"Image dimensions: {img.size[0]}x{img.size[1]}")
            print_success("Thumbnail is a valid image")
            return True
        except Exception as e:
            print_error(f"Failed to load thumbnail as image: {e}")
            return False
    else:
        print_error(f"Failed to get thumbnail: {response.status_code}")
        print(response.text)
        return False

def get_preview(token, document_id):
    """Get document preview."""
    print_header("TEST 5: Get Preview")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/transaction-documents/documents/{document_id}/preview",
        headers=headers,
        params={'type': 'preview'}
    )
    
    if response.status_code == 200:
        print_success("Preview retrieved successfully")
        print_info(f"Content-Type: {response.headers.get('Content-Type')}")
        print_info(f"Size: {len(response.content)} bytes")
        
        # Try to load as image
        try:
            img = Image.open(BytesIO(response.content))
            print_info(f"Image dimensions: {img.size[0]}x{img.size[1]}")
            print_success("Preview is a valid image")
            return True
        except Exception as e:
            print_error(f"Failed to load preview as image: {e}")
            return False
    elif response.status_code == 404:
        print_info("Preview not available (expected for some file types)")
        return True
    else:
        print_error(f"Failed to get preview: {response.status_code}")
        print(response.text)
        return False

def list_documents_with_previews(token):
    """List documents for an entity and check preview availability."""
    print_header("TEST 6: List Documents with Preview Info")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/transaction-documents/documents/voting/2",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get('data', {}).get('documents', [])
        print_success(f"Found {len(documents)} document(s)")
        
        for doc in documents:
            print_info(f"Document: {doc.get('original_filename')}")
            print_info(f"  - Has Preview: {doc.get('has_preview', False)}")
            print_info(f"  - Document Type: {doc.get('document_type')}")
            print_info(f"  - MIME Type: {doc.get('mime_type')}")
        
        return True
    else:
        print_error(f"Failed to list documents: {response.status_code}")
        print(response.text)
        return False

def cleanup_test_document(token, document_id):
    """Delete the test document."""
    print_header("TEST 7: Cleanup - Delete Test Document")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/transaction-documents/documents/{document_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        print_success("Test document deleted successfully")
        return True
    else:
        print_error(f"Failed to delete document: {response.status_code}")
        print(response.text)
        return False

def main():
    """Run all tests."""
    print("\n" + "🚀" * 40)
    print("  DOCUMENT PREVIEW FUNCTIONALITY TEST SUITE")
    print("🚀" * 40)
    
    # Test 1: Login
    token = login()
    if not token:
        print_error("Cannot proceed without authentication")
        sys.exit(1)
    
    # Test 2: Upload image document
    document_id = upload_document_with_image(token)
    if not document_id:
        print_error("Cannot proceed without uploaded document")
        sys.exit(1)
    
    # Test 3: Get document details
    doc_details = get_document_details(token, document_id)
    if not doc_details:
        print_error("Failed to get document details")
    
    # Test 4: Get thumbnail
    thumbnail_success = get_thumbnail(token, document_id)
    
    # Test 5: Get preview
    preview_success = get_preview(token, document_id)
    
    # Test 6: List documents with preview info
    list_success = list_documents_with_previews(token)
    
    # Test 7: Cleanup
    cleanup_success = cleanup_test_document(token, document_id)
    
    # Summary
    print_header("TEST SUMMARY")
    tests = [
        ("Login", token is not None),
        ("Upload Image Document", document_id is not None),
        ("Get Document Details", doc_details is not None),
        ("Get Thumbnail", thumbnail_success),
        ("Get Preview", preview_success),
        ("List Documents", list_success),
        ("Cleanup", cleanup_success),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print("\n" + "=" * 80)
    print(f"  RESULTS: {passed}/{total} tests passed")
    print("=" * 80 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! Document preview functionality is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please review the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

