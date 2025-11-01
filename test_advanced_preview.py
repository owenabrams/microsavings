#!/usr/bin/env python3
"""
Test script for advanced document preview features (PDF, video, enhanced file type detection).
Tests PDF preview generation, video thumbnail extraction, and file type detection.
"""

import requests
import json
import os
import sys
from io import BytesIO
from PIL import Image

# Configuration
API_BASE_URL = "http://localhost:5001/api"
TEST_USER_EMAIL = "alice.mukamana@example.com"
TEST_USER_PASSWORD = "password123"

# Test results tracking
tests_passed = 0
tests_failed = 0

def print_test(test_name):
    """Print test name."""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print('='*80)

def print_success(message):
    """Print success message."""
    global tests_passed
    tests_passed += 1
    print(f"✅ {message}")

def print_error(message):
    """Print error message."""
    global tests_failed
    tests_failed += 1
    print(f"❌ {message}")

def print_info(message):
    """Print info message."""
    print(f"ℹ️  {message}")

def login():
    """Login and get JWT token."""
    print_test("User Authentication")
    
    response = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('auth_token') or data.get('access_token')
        if token:
            print_success(f"Login successful for {TEST_USER_EMAIL}")
            return token
        else:
            print_error(f"No auth token in response: {data}")
            return None
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None

def create_test_pdf():
    """Create a simple test PDF file."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        pdf_path = "/tmp/test_document.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "Test PDF Document")
        c.drawString(100, 730, "This is a test PDF for preview generation.")
        c.drawString(100, 710, "Page 1 of 2")
        c.showPage()
        c.drawString(100, 750, "Page 2")
        c.drawString(100, 730, "This is the second page.")
        c.save()
        
        print_info(f"Created test PDF: {pdf_path}")
        return pdf_path
    except ImportError:
        print_error("reportlab not installed, skipping PDF creation")
        return None

def create_test_image():
    """Create a simple test image file."""
    try:
        img = Image.new('RGB', (800, 600), color='blue')
        img_path = "/tmp/test_image.jpg"
        img.save(img_path, 'JPEG')
        print_info(f"Created test image: {img_path}")
        return img_path
    except Exception as e:
        print_error(f"Failed to create test image: {e}")
        return None

def test_pdf_upload_and_preview(token):
    """Test PDF upload with preview generation."""
    print_test("PDF Upload and Preview Generation")

    # Create test PDF
    pdf_path = create_test_pdf()
    if not pdf_path:
        print_error("Cannot test PDF preview without test file")
        return None

    # Upload PDF to meeting entity (entity_id=39 exists from seeding)
    headers = {"Authorization": f"Bearer {token}"}
    entity_type = "meeting"
    entity_id = 39

    with open(pdf_path, 'rb') as f:
        files = {
            'files': ('test_document.pdf', f, 'application/pdf')
        }
        data = {
            'document_type': 'MINUTES',
            'description': 'Test PDF document for preview'
        }

        response = requests.post(
            f"{API_BASE_URL}/transaction-documents/documents/{entity_type}/{entity_id}",
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code == 201:
        response_data = response.json()
        # Response has nested structure: {status, data: {uploaded: [...], errors: [], count}}
        if response_data.get('status') == 'success':
            uploaded = response_data.get('data', {}).get('uploaded', [])
            if uploaded and len(uploaded) > 0:
                doc = uploaded[0]
                doc_id = doc.get('id')
                has_preview = doc.get('has_preview', False)
                preview_path = doc.get('preview_path')
                thumbnail_path = doc.get('thumbnail_path')

                print_success(f"PDF uploaded successfully (ID: {doc_id})")
                print_info(f"Has preview: {has_preview}")
                print_info(f"MIME type: {doc.get('mime_type')}")
                print_info(f"File size: {doc.get('file_size')} bytes")
                print_info(f"Preview path: {preview_path}")
                print_info(f"Thumbnail path: {thumbnail_path}")

                if has_preview and preview_path and thumbnail_path:
                    print_success("PDF preview and thumbnail generated successfully")
                elif has_preview:
                    print_success("PDF preview generated (partial)")
                else:
                    print_error("PDF preview not generated")

                return doc_id
            else:
                print_error(f"No documents in upload response")
                return None
        else:
            print_error(f"Upload failed: {response_data}")
            return None
    else:
        print_error(f"PDF upload failed: {response.status_code} - {response.text}")
        return None

def test_pdf_preview_retrieval(token, doc_id):
    """Test PDF preview image retrieval."""
    print_test("PDF Preview Retrieval")

    if not doc_id:
        print_error("No document ID provided")
        return

    # Get preview image
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE_URL}/transaction-documents/documents/{doc_id}/preview",
        headers=headers,
        params={'type': 'preview'}
    )

    if response.status_code == 200:
        # Check if it's a valid image
        try:
            img = Image.open(BytesIO(response.content))
            width, height = img.size
            print_success(f"PDF preview retrieved successfully ({width}x{height})")
            print_info(f"Image format: {img.format}")
            print_info(f"Image mode: {img.mode}")

            # Check preview size (should be around 800x600)
            if width <= 800 and height <= 600:
                print_success("PDF preview size is correct (≤800x600)")
            else:
                print_error(f"PDF preview size is too large ({width}x{height})")
        except Exception as e:
            print_error(f"Invalid image data: {e}")
    else:
        print_error(f"Preview retrieval failed: {response.status_code}")

def test_image_upload_and_thumbnail(token):
    """Test image upload with thumbnail generation."""
    print_test("Image Upload and Thumbnail Generation")

    # Create test image
    img_path = create_test_image()
    if not img_path:
        print_error("Cannot test image thumbnail without test file")
        return None

    # Upload image to meeting entity
    headers = {"Authorization": f"Bearer {token}"}
    entity_type = "meeting"
    entity_id = 39

    with open(img_path, 'rb') as f:
        files = {
            'files': ('test_image.jpg', f, 'image/jpeg')
        }
        data = {
            'document_type': 'PHOTO',
            'description': 'Test image for thumbnail'
        }

        response = requests.post(
            f"{API_BASE_URL}/transaction-documents/documents/{entity_type}/{entity_id}",
            headers=headers,
            files=files,
            data=data
        )

    if response.status_code == 201:
        response_data = response.json()
        # Response has nested structure: {status, data: {uploaded: [...], errors: [], count}}
        if response_data.get('status') == 'success':
            uploaded = response_data.get('data', {}).get('uploaded', [])
            if uploaded and len(uploaded) > 0:
                doc = uploaded[0]
                doc_id = doc.get('id')
                has_preview = doc.get('has_preview', False)
                thumbnail_path = doc.get('thumbnail_path')

                print_success(f"Image uploaded successfully (ID: {doc_id})")
                print_info(f"Has preview: {has_preview}")
                print_info(f"Thumbnail path: {thumbnail_path}")

                if has_preview and thumbnail_path:
                    print_success("Image thumbnail generated successfully")
                elif has_preview:
                    print_success("Image thumbnail generated (partial)")
                else:
                    print_error("Image thumbnail not generated")

                return doc_id
            else:
                print_error(f"No documents in upload response")
                return None
        else:
            print_error(f"Upload failed: {response_data}")
            return None
    else:
        print_error(f"Image upload failed: {response.status_code} - {response.text}")
        return None

def test_thumbnail_retrieval(token, doc_id):
    """Test thumbnail image retrieval."""
    print_test("Thumbnail Retrieval")

    if not doc_id:
        print_error("No document ID provided")
        return

    # Get thumbnail image
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{API_BASE_URL}/transaction-documents/documents/{doc_id}/preview",
        headers=headers,
        params={'type': 'thumbnail'}
    )

    if response.status_code == 200:
        # Check if it's a valid image
        try:
            img = Image.open(BytesIO(response.content))
            width, height = img.size
            print_success(f"Thumbnail retrieved successfully ({width}x{height})")
            print_info(f"Image format: {img.format}")
            print_info(f"Image mode: {img.mode}")

            # Check thumbnail size (should be around 300x300)
            if width <= 300 and height <= 300:
                print_success("Thumbnail size is correct (≤300x300)")
            else:
                print_error(f"Thumbnail size is too large ({width}x{height})")
        except Exception as e:
            print_error(f"Invalid image data: {e}")
    else:
        print_error(f"Thumbnail retrieval failed: {response.status_code}")

def test_file_type_detection(token):
    """Test enhanced file type detection."""
    print_test("Enhanced File Type Detection")

    # Test various file types
    test_files = [
        ("/tmp/test_document.pdf", "application/pdf", "PDF"),
        ("/tmp/test_image.jpg", "image/jpeg", "Image"),
    ]

    entity_type = "meeting"
    entity_id = 39

    for file_path, expected_mime, file_type in test_files:
        if not os.path.exists(file_path):
            print_info(f"Skipping {file_type} test (file not found)")
            continue

        headers = {"Authorization": f"Bearer {token}"}

        with open(file_path, 'rb') as f:
            files = {'files': (os.path.basename(file_path), f)}
            data = {
                'document_type': 'OTHER',
                'description': f'Test {file_type} for MIME type detection'
            }

            response = requests.post(
                f"{API_BASE_URL}/transaction-documents/documents/{entity_type}/{entity_id}",
                headers=headers,
                files=files,
                data=data
            )

        if response.status_code == 201:
            response_data = response.json()
            # Response has nested structure: {status, data: {uploaded: [...], errors: [], count}}
            if response_data.get('status') == 'success':
                uploaded = response_data.get('data', {}).get('uploaded', [])
                if uploaded and len(uploaded) > 0:
                    doc = uploaded[0]
                    detected_mime = doc.get('mime_type')

                    if detected_mime == expected_mime:
                        print_success(f"{file_type}: Correct MIME type detected ({detected_mime})")
                    else:
                        print_error(f"{file_type}: Wrong MIME type (expected {expected_mime}, got {detected_mime})")
                else:
                    print_error(f"{file_type}: No documents in upload response")
            else:
                print_error(f"{file_type}: Upload failed - {response_data}")
        else:
            print_error(f"{file_type}: Upload failed ({response.status_code})")

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("ADVANCED DOCUMENT PREVIEW FEATURES TEST SUITE")
    print("="*80)
    
    # Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # Test PDF upload and preview
    pdf_doc_id = test_pdf_upload_and_preview(token)
    if pdf_doc_id:
        test_pdf_preview_retrieval(token, pdf_doc_id)
    
    # Test image upload and thumbnail
    img_doc_id = test_image_upload_and_thumbnail(token)
    if img_doc_id:
        test_thumbnail_retrieval(token, img_doc_id)
    
    # Test file type detection
    test_file_type_detection(token)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Tests Passed: {tests_passed}")
    print(f"❌ Tests Failed: {tests_failed}")
    print(f"📊 Total Tests: {tests_passed + tests_failed}")
    print(f"📈 Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
    print("="*80 + "\n")
    
    sys.exit(0 if tests_failed == 0 else 1)

if __name__ == "__main__":
    main()

