"""
Enhanced Document Management API with comprehensive file management features.
Includes compression, preview generation, versioning, and cascading deletes.
"""
import os
import datetime
from flask import Blueprint, jsonify, request, current_app, send_file
from functools import wraps
from sqlalchemy import and_, or_
from project import db
from project.api.models import (
    ActivityDocument, MeetingActivity, GroupDocument, SavingsGroup,
    User, Meeting, GroupMember
)
from project.api.file_storage_service import get_file_storage_service

documents_enhanced_blueprint = Blueprint('documents_enhanced', __name__)


def authenticate(f):
    """Decorator to authenticate requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'status': 'error', 'message': 'Authorization header required'}), 401
        
        try:
            auth_token = auth_header.split(' ')[1]
            user_id = User.decode_token(auth_token)
            if isinstance(user_id, str):
                return jsonify({'status': 'error', 'message': user_id}), 401
            return f(user_id, *args, **kwargs)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 401
    
    return decorated_function


@documents_enhanced_blueprint.route('/activities/<int:activity_id>/documents', methods=['POST'])
@authenticate
def upload_activity_documents(user_id, activity_id):
    """Upload multiple documents for a meeting activity with compression and preview generation."""
    activity = MeetingActivity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400
    
    # Get metadata from form
    document_type = request.form.get('document_type', 'OTHER')
    document_category = request.form.get('document_category', 'GENERAL')
    description = request.form.get('description', '')
    is_proof_document = request.form.get('is_proof_document', 'false').lower() == 'true'
    auto_compress = request.form.get('auto_compress', 'true').lower() == 'true'
    generate_preview = request.form.get('generate_preview', 'true').lower() == 'true'
    
    storage_service = get_file_storage_service()
    uploaded_documents = []
    errors = []
    
    for file in files:
        if file and file.filename:
            # Validate file
            if not storage_service.is_allowed_file(file.filename):
                errors.append(f'{file.filename}: File type not allowed')
                continue
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > storage_service.MAX_FILE_SIZE:
                errors.append(f'{file.filename}: File size exceeds 50MB limit')
                continue
            
            try:
                # Save file with compression and preview generation
                file_info = storage_service.save_uploaded_file(
                    file, 
                    'activity', 
                    activity_id,
                    auto_compress=auto_compress,
                    generate_preview=generate_preview
                )
                
                # Create database record
                document = ActivityDocument(
                    activity_id=activity_id,
                    document_name=file_info['original_filename'],
                    original_filename=file_info['original_filename'],
                    document_type=document_type,
                    file_path=file_info['file_path'],
                    file_size=file_info['file_size'],
                    mime_type=file_info['metadata']['mime_type'],
                    description=description,
                    is_proof_document=is_proof_document,
                    document_category=document_category,
                    uploaded_by=user_id,
                    upload_date=datetime.datetime.utcnow(),
                    # Compression fields
                    is_compressed=file_info['is_compressed'],
                    compressed_size=file_info['compressed_size'],
                    compression_ratio=file_info['compression_ratio'],
                    file_hash=file_info['metadata']['file_hash'],
                    # Preview fields
                    thumbnail_path=file_info['thumbnail_path'],
                    preview_path=file_info['preview_path'],
                    has_preview=file_info['thumbnail_path'] is not None or file_info['preview_path'] is not None,
                    # Metadata
                    file_category=file_info['metadata']['file_category']
                )
                db.session.add(document)
                db.session.flush()
                
                uploaded_documents.append({
                    'id': document.id,
                    'document_name': document.document_name,
                    'document_type': document.document_type,
                    'file_size': document.file_size,
                    'compressed_size': document.compressed_size,
                    'is_compressed': document.is_compressed,
                    'compression_ratio': float(document.compression_ratio) if document.compression_ratio else 0,
                    'has_preview': document.has_preview,
                    'mime_type': document.mime_type,
                    'upload_date': document.upload_date.isoformat()
                })
                
            except Exception as e:
                errors.append(f'{file.filename}: {str(e)}')
    
    try:
        db.session.commit()
        
        response = {
            'status': 'success',
            'message': f'Uploaded {len(uploaded_documents)} document(s)',
            'data': {
                'uploaded': uploaded_documents,
                'errors': errors
            }
        }
        
        return jsonify(response), 201 if uploaded_documents else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/activities/<int:activity_id>/documents', methods=['GET'])
@authenticate
def get_activity_documents(user_id, activity_id):
    """Get all documents for an activity."""
    activity = MeetingActivity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    documents = ActivityDocument.query.filter_by(
        activity_id=activity_id,
        is_deleted=False
    ).order_by(ActivityDocument.upload_date.desc()).all()
    
    storage_service = get_file_storage_service()
    
    documents_data = []
    for doc in documents:
        documents_data.append({
            'id': doc.id,
            'document_name': doc.document_name,
            'original_filename': doc.original_filename,
            'document_type': doc.document_type,
            'document_category': doc.document_category,
            'file_size': doc.file_size,
            'compressed_size': doc.compressed_size,
            'is_compressed': doc.is_compressed,
            'compression_ratio': float(doc.compression_ratio) if doc.compression_ratio else 0,
            'has_preview': doc.has_preview,
            'mime_type': doc.mime_type,
            'file_category': doc.file_category,
            'description': doc.description,
            'is_proof_document': doc.is_proof_document,
            'upload_date': doc.upload_date.isoformat() if doc.upload_date else None,
            'uploaded_by': doc.uploaded_by,
            'download_count': doc.download_count or 0,
            'last_accessed': doc.last_accessed.isoformat() if doc.last_accessed else None,
            'version': doc.version,
            'is_current_version': doc.is_current_version
        })
    
    return jsonify({
        'status': 'success',
        'data': {
            'documents': documents_data,
            'total_count': len(documents_data)
        }
    }), 200


@documents_enhanced_blueprint.route('/documents/<int:document_id>', methods=['GET'])
@authenticate
def get_document_info(user_id, document_id):
    """Get detailed information about a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    
    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404
    
    storage_service = get_file_storage_service()
    
    # Get file metadata if file exists
    file_metadata = None
    if os.path.exists(document.file_path):
        file_metadata = storage_service.extract_file_metadata(document.file_path)
    
    return jsonify({
        'status': 'success',
        'data': {
            'id': document.id,
            'document_name': document.document_name,
            'original_filename': document.original_filename,
            'document_type': document.document_type,
            'document_category': document.document_category,
            'file_size': document.file_size,
            'compressed_size': document.compressed_size,
            'is_compressed': document.is_compressed,
            'compression_ratio': float(document.compression_ratio) if document.compression_ratio else 0,
            'has_preview': document.has_preview,
            'mime_type': document.mime_type,
            'file_category': document.file_category,
            'description': document.description,
            'is_proof_document': document.is_proof_document,
            'upload_date': document.upload_date.isoformat() if document.upload_date else None,
            'uploaded_by': document.uploaded_by,
            'download_count': document.download_count or 0,
            'last_accessed': document.last_accessed.isoformat() if document.last_accessed else None,
            'version': document.version,
            'is_current_version': document.is_current_version,
            'parent_document_id': document.parent_document_id,
            'file_hash': document.file_hash,
            'file_metadata': file_metadata
        }
    }), 200


@documents_enhanced_blueprint.route('/documents/<int:document_id>/download', methods=['GET'])
@authenticate
def download_document(user_id, document_id):
    """Download a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404

    storage_service = get_file_storage_service()

    # Decompress if needed
    file_path = document.file_path
    if document.is_compressed and file_path.endswith('.gz'):
        temp_path = os.path.join(storage_service.base_upload_folder, 'temp', document.original_filename)
        file_path = storage_service.decompress_file(document.file_path, temp_path)

    if not os.path.exists(file_path):
        return jsonify({'status': 'error', 'message': 'File not found on server'}), 404

    # Update download count and last accessed
    document.download_count = (document.download_count or 0) + 1
    document.last_accessed = datetime.datetime.utcnow()
    db.session.commit()

    return send_file(
        file_path,
        as_attachment=True,
        download_name=document.original_filename or document.document_name,
        mimetype=document.mime_type
    )


@documents_enhanced_blueprint.route('/documents/<int:document_id>/preview', methods=['GET'])
@authenticate
def get_document_preview(user_id, document_id):
    """Get preview/thumbnail for a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404

    # Return thumbnail if available
    if document.thumbnail_path and os.path.exists(document.thumbnail_path):
        return send_file(document.thumbnail_path, mimetype='image/jpeg')

    # Return preview if available
    if document.preview_path and os.path.exists(document.preview_path):
        return send_file(document.preview_path, mimetype='image/jpeg')

    return jsonify({'status': 'error', 'message': 'No preview available for this document'}), 404


@documents_enhanced_blueprint.route('/documents/<int:document_id>', methods=['PUT'])
@authenticate
def update_document_metadata(user_id, document_id):
    """Update document metadata (description, type, category, etc.)."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404

    data = request.get_json()

    try:
        # Update allowed fields
        if 'description' in data:
            document.description = data['description']
        if 'document_type' in data:
            document.document_type = data['document_type']
        if 'document_category' in data:
            document.document_category = data['document_category']
        if 'is_proof_document' in data:
            document.is_proof_document = data['is_proof_document']
        if 'access_level' in data:
            document.access_level = data['access_level']
        if 'is_public' in data:
            document.is_public = data['is_public']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Document metadata updated successfully',
            'data': {
                'id': document.id,
                'document_name': document.document_name,
                'description': document.description,
                'document_type': document.document_type,
                'document_category': document.document_category
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/documents/<int:document_id>/compress', methods=['POST'])
@authenticate
def compress_document(user_id, document_id):
    """Manually compress a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404

    if document.is_compressed:
        return jsonify({'status': 'error', 'message': 'Document is already compressed'}), 400

    storage_service = get_file_storage_service()

    try:
        # Compress file
        compressed_path, original_size, compressed_size = storage_service.compress_file(document.file_path)

        if compressed_path != document.file_path:
            # Update document record
            document.file_path = compressed_path
            document.is_compressed = True
            document.compressed_size = compressed_size
            document.compression_ratio = (1 - compressed_size / original_size) * 100

            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'Document compressed successfully',
                'data': {
                    'id': document.id,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'compression_ratio': float(document.compression_ratio),
                    'space_saved': original_size - compressed_size,
                    'space_saved_mb': round((original_size - compressed_size) / (1024 * 1024), 2)
                }
            }), 200
        else:
            return jsonify({
                'status': 'info',
                'message': 'File is not suitable for compression or already optimally compressed'
            }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/documents/<int:document_id>', methods=['DELETE'])
@authenticate
def delete_document(user_id, document_id):
    """Soft delete a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document already deleted'}), 400

    try:
        # Soft delete
        document.is_deleted = True
        document.deleted_date = datetime.datetime.utcnow()
        document.deleted_by = user_id
        document.is_current_version = False

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Document deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/documents/<int:document_id>/permanent-delete', methods=['DELETE'])
@authenticate
def permanent_delete_document(user_id, document_id):
    """Permanently delete a document and its files."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    storage_service = get_file_storage_service()

    try:
        # Delete physical files
        storage_service.delete_file(document.file_path, delete_related=True)

        # Delete database record
        db.session.delete(document)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Document permanently deleted'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/activities/<int:activity_id>/storage-usage', methods=['GET'])
@authenticate
def get_activity_storage_usage(user_id, activity_id):
    """Get storage usage statistics for an activity."""
    activity = MeetingActivity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404

    storage_service = get_file_storage_service()
    usage = storage_service.get_storage_usage('activity', activity_id)

    return jsonify({
        'status': 'success',
        'data': usage
    }), 200


@documents_enhanced_blueprint.route('/groups/<int:group_id>/storage-usage', methods=['GET'])
@authenticate
def get_group_storage_usage(user_id, group_id):
    """Get storage usage statistics for a group."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404

    storage_service = get_file_storage_service()
    usage = storage_service.get_storage_usage('group', group_id)

    return jsonify({
        'status': 'success',
        'data': usage
    }), 200


@documents_enhanced_blueprint.route('/storage-usage', methods=['GET'])
@authenticate
def get_overall_storage_usage(user_id):
    """Get overall storage usage statistics."""
    storage_service = get_file_storage_service()
    usage = storage_service.get_storage_usage()

    return jsonify({
        'status': 'success',
        'data': usage
    }), 200


@documents_enhanced_blueprint.route('/meetings/<int:meeting_id>/cascade-delete-files', methods=['DELETE'])
@authenticate
def cascade_delete_meeting_files(user_id, meeting_id):
    """Delete all files associated with a meeting (when meeting is deleted)."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    storage_service = get_file_storage_service()

    try:
        # Get all activities for this meeting
        activities = MeetingActivity.query.filter_by(meeting_id=meeting_id).all()

        total_deleted = 0
        total_size_freed = 0

        for activity in activities:
            # Delete files for each activity
            result = storage_service.delete_entity_files('activity', activity.id)
            total_deleted += result['deleted_count']
            total_size_freed += result['total_size_freed']

            # Soft delete documents in database
            ActivityDocument.query.filter_by(activity_id=activity.id).update({
                'is_deleted': True,
                'deleted_date': datetime.datetime.utcnow(),
                'deleted_by': user_id
            })

        # Delete meeting-level files
        meeting_result = storage_service.delete_entity_files('meeting', meeting_id)
        total_deleted += meeting_result['deleted_count']
        total_size_freed += meeting_result['total_size_freed']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Deleted {total_deleted} files',
            'data': {
                'deleted_count': total_deleted,
                'total_size_freed': total_size_freed,
                'size_freed_mb': round(total_size_freed / (1024 * 1024), 2)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/groups/<int:group_id>/cascade-delete-files', methods=['DELETE'])
@authenticate
def cascade_delete_group_files(user_id, group_id):
    """Delete all files associated with a group (when group is deleted)."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404

    storage_service = get_file_storage_service()

    try:
        # Delete group-level files
        result = storage_service.delete_entity_files('group', group_id)

        # Soft delete documents in database
        GroupDocument.query.filter_by(group_id=group_id).update({
            'is_deleted': True,
            'deleted_date': datetime.datetime.utcnow(),
            'deleted_by': user_id
        })

        # Delete all meeting files for this group
        meetings = Meeting.query.filter_by(group_id=group_id).all()
        total_deleted = result['deleted_count']
        total_size_freed = result['total_size_freed']

        for meeting in meetings:
            activities = MeetingActivity.query.filter_by(meeting_id=meeting.id).all()
            for activity in activities:
                activity_result = storage_service.delete_entity_files('activity', activity.id)
                total_deleted += activity_result['deleted_count']
                total_size_freed += activity_result['total_size_freed']

                ActivityDocument.query.filter_by(activity_id=activity.id).update({
                    'is_deleted': True,
                    'deleted_date': datetime.datetime.utcnow(),
                    'deleted_by': user_id
                })

            meeting_result = storage_service.delete_entity_files('meeting', meeting.id)
            total_deleted += meeting_result['deleted_count']
            total_size_freed += meeting_result['total_size_freed']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Deleted {total_deleted} files',
            'data': {
                'deleted_count': total_deleted,
                'total_size_freed': total_size_freed,
                'size_freed_mb': round(total_size_freed / (1024 * 1024), 2)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_enhanced_blueprint.route('/members/<int:member_id>/cascade-delete-files', methods=['DELETE'])
@authenticate
def cascade_delete_member_files(user_id, member_id):
    """Delete all files associated with a member (when member is deleted)."""
    member = GroupMember.query.get(member_id)
    if not member:
        return jsonify({'status': 'error', 'message': 'Member not found'}), 404

    storage_service = get_file_storage_service()

    try:
        # Delete member-level files
        result = storage_service.delete_entity_files('member', member_id)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': f'Deleted {result["deleted_count"]} files',
            'data': result
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400

