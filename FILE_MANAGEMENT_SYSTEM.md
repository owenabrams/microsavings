# Comprehensive File Management System

## Overview

This document describes the professional file management system implemented for the microsavings platform. The system provides enterprise-grade file handling with compression, preview generation, versioning, cascading deletes, and storage quota management.

## Features

### 1. **File Upload & Storage**
- **Multiple file uploads** - Upload multiple files simultaneously
- **Secure storage** - Files stored with UUID-based filenames to prevent conflicts
- **Organized structure** - Files organized by entity type (activities, groups, members, meetings)
- **File validation** - Type and size validation before upload
- **Metadata extraction** - Automatic extraction of file metadata (dimensions, page count, etc.)

### 2. **Automatic Compression**
- **Smart compression** - Files larger than 5MB are automatically compressed
- **Selective compression** - Already compressed formats (ZIP, JPG, MP4) are skipped
- **Compression ratio tracking** - System tracks space saved by compression
- **On-demand compression** - Manual compression endpoint for existing files
- **Transparent decompression** - Files automatically decompressed on download

### 3. **Preview Generation**
- **Image thumbnails** - Automatic thumbnail generation for images (300x300px)
- **PDF previews** - First page preview for PDF documents
- **Preview caching** - Previews stored separately for fast access
- **Multiple formats** - Support for JPG, PNG, GIF, BMP, WEBP, SVG

### 4. **File Versioning**
- **Version tracking** - Complete history of file versions
- **Parent-child relationships** - Track which file replaced which
- **Version numbers** - Automatic version numbering
- **Current version flag** - Easy identification of current version
- **Version history** - Query all versions of a document

### 5. **Cascading Deletes**
- **Soft delete** - Documents marked as deleted but not immediately removed
- **Hard delete** - Permanent deletion with file cleanup
- **Entity cascade** - Delete all files when parent entity is deleted
- **Related file cleanup** - Thumbnails and previews deleted with main file
- **Storage reclamation** - Track space freed by deletions

### 6. **Storage Management**
- **Usage tracking** - Real-time storage usage per entity
- **Quota management** - Track and enforce storage limits
- **Category breakdown** - Usage statistics by file category
- **Duplicate detection** - SHA256 hash-based duplicate detection
- **Orphan cleanup** - Identify and remove orphaned files

### 7. **Metadata Management**
- **Editable metadata** - Update description, type, category without re-uploading
- **Access control** - GROUP, ADMIN, PUBLIC access levels
- **Download tracking** - Track download count and last access time
- **Proof documents** - Flag important documents as proof/evidence
- **File categories** - Automatic categorization (documents, images, videos, archives, audio)

## Architecture

### File Storage Service (`file_storage_service.py`)

The core service layer that handles all file operations:

```python
from project.api.file_storage_service import get_file_storage_service

storage_service = get_file_storage_service()

# Save uploaded file
file_info = storage_service.save_uploaded_file(
    file, 
    entity_type='activity',
    entity_id=123,
    auto_compress=True,
    generate_preview=True
)

# Delete entity files
result = storage_service.delete_entity_files('activity', 123)

# Get storage usage
usage = storage_service.get_storage_usage('group', 456)
```

### Database Models

**ActivityDocument** - Files attached to meeting activities
- Compression fields: `is_compressed`, `compressed_size`, `compression_ratio`
- Preview fields: `thumbnail_path`, `preview_path`, `has_preview`
- Versioning fields: `version`, `parent_document_id`, `is_current_version`
- Metadata fields: `file_hash`, `file_category`, `download_count`, `last_accessed`
- Soft delete: `is_deleted`, `deleted_date`, `deleted_by`

**GroupDocument** - Files attached to groups
- Same enhanced fields as ActivityDocument
- Additional approval workflow: `approval_status`, `approved_by`, `approval_date`

**StorageUsage** - Tracks storage usage per entity
- `entity_type`, `entity_id` - Entity identification
- `total_files`, `total_size`, `compressed_size` - Usage metrics
- Automatically updated via database triggers

**FileVersions** - Tracks file version history
- `document_type`, `document_id` - Document identification
- `version_number`, `file_path`, `file_hash` - Version details
- `is_current` - Current version flag

### API Endpoints

#### Upload & Retrieval
- `POST /api/activities/{activity_id}/documents` - Upload documents
- `GET /api/activities/{activity_id}/documents` - List documents
- `GET /api/documents/{document_id}` - Get document info
- `GET /api/documents/{document_id}/download` - Download document
- `GET /api/documents/{document_id}/preview` - Get preview/thumbnail

#### Management
- `PUT /api/documents/{document_id}` - Update metadata
- `POST /api/documents/{document_id}/compress` - Compress document
- `DELETE /api/documents/{document_id}` - Soft delete
- `DELETE /api/documents/{document_id}/permanent-delete` - Hard delete

#### Storage & Statistics
- `GET /api/activities/{activity_id}/storage-usage` - Activity storage usage
- `GET /api/groups/{group_id}/storage-usage` - Group storage usage
- `GET /api/storage-usage` - Overall storage usage

#### Cascading Deletes
- `DELETE /api/meetings/{meeting_id}/cascade-delete-files` - Delete meeting files
- `DELETE /api/groups/{group_id}/cascade-delete-files` - Delete group files
- `DELETE /api/members/{member_id}/cascade-delete-files` - Delete member files

## Supported File Types

### Documents
- PDF, DOC, DOCX, XLS, XLSX, TXT, CSV, ODT, ODS

### Images
- JPG, JPEG, PNG, GIF, BMP, WEBP, SVG

### Videos
- MP4, AVI, MOV, WMV, FLV, MKV

### Archives
- ZIP, RAR, 7Z, TAR, GZ

### Audio
- MP3, WAV, OGG, FLAC

## File Size Limits

- **Maximum file size**: 50MB per file
- **Compression threshold**: 5MB (files larger than this are auto-compressed)
- **Thumbnail size**: 300x300 pixels
- **Preview size**: 800x600 pixels

## Storage Structure

```
/app/uploads/
├── activities/
│   ├── {activity_id}/
│   │   ├── {uuid}.pdf
│   │   ├── {uuid}.jpg.gz
│   │   └── ...
├── groups/
│   ├── {group_id}/
│   │   └── ...
├── members/
│   ├── {member_id}/
│   │   └── ...
├── meetings/
│   ├── {meeting_id}/
│   │   └── ...
├── thumbnails/
│   ├── thumb_{uuid}.jpg
│   └── ...
├── previews/
│   ├── preview_{uuid}.jpg
│   └── ...
└── temp/
    └── (temporary decompressed files)
```

## Usage Examples

### Upload Documents with Compression

```bash
curl -X POST \
  http://localhost:5001/api/activities/123/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@receipt1.pdf" \
  -F "files=@receipt2.jpg" \
  -F "document_type=RECEIPT" \
  -F "document_category=FINANCIAL" \
  -F "description=Payment receipts" \
  -F "is_proof_document=true" \
  -F "auto_compress=true" \
  -F "generate_preview=true"
```

### Get Storage Usage

```bash
curl -X GET \
  http://localhost:5001/api/groups/2/storage-usage \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "status": "success",
  "data": {
    "total_files": 45,
    "total_size": 125829120,
    "total_size_mb": 120.0,
    "by_category": {
      "documents": {"count": 30, "size": 85000000},
      "images": {"count": 15, "size": 40829120}
    }
  }
}
```

### Compress Existing Document

```bash
curl -X POST \
  http://localhost:5001/api/documents/456/compress \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "status": "success",
  "message": "Document compressed successfully",
  "data": {
    "id": 456,
    "original_size": 10485760,
    "compressed_size": 3145728,
    "compression_ratio": 70.0,
    "space_saved": 7340032,
    "space_saved_mb": 7.0
  }
}
```

### Cascade Delete Group Files

```bash
curl -X DELETE \
  http://localhost:5001/api/groups/2/cascade-delete-files \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "status": "success",
  "message": "Deleted 45 files",
  "data": {
    "deleted_count": 45,
    "total_size_freed": 125829120,
    "size_freed_mb": 120.0
  }
}
```

## Database Migration

Run the migration to add enhanced file management fields:

```bash
docker exec testdriven_db psql -U postgres -d users_dev -f /migrations/005_enhanced_file_management.sql
```

## Best Practices

1. **Always enable auto-compression** for large files to save storage
2. **Generate previews** for user-facing documents to improve UX
3. **Use soft delete** initially to allow recovery if needed
4. **Track download counts** to identify frequently accessed files
5. **Monitor storage usage** per group to enforce quotas
6. **Run orphan cleanup** periodically to remove unused files
7. **Use file hashes** to detect and prevent duplicate uploads
8. **Implement access control** based on user roles and document sensitivity

## Security Considerations

1. **File validation** - Only allowed file types can be uploaded
2. **Size limits** - Prevents storage exhaustion attacks
3. **Secure filenames** - UUID-based names prevent path traversal
4. **Access control** - GROUP/ADMIN/PUBLIC levels
5. **Soft delete** - Allows audit trail and recovery
6. **Authentication required** - All endpoints require valid JWT token

## Performance Optimizations

1. **Compression** - Reduces storage and transfer costs
2. **Preview caching** - Thumbnails generated once and reused
3. **Database indexes** - Fast queries on file_hash, entity_id, etc.
4. **Lazy loading** - Previews loaded on demand
5. **Batch operations** - Cascade deletes process multiple files efficiently

## Future Enhancements

1. **Cloud storage integration** - S3, Azure Blob, Google Cloud Storage
2. **CDN integration** - Faster file delivery
3. **Virus scanning** - Malware detection on upload
4. **OCR** - Text extraction from images and PDFs
5. **Video transcoding** - Convert videos to web-friendly formats
6. **Watermarking** - Add watermarks to sensitive documents
7. **Encryption** - Encrypt files at rest
8. **Backup automation** - Automatic backup to secondary storage

