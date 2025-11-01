"""
Group Documents API
Handles Constitution, Financial, and Registration documents for savings groups.
"""
import os
import datetime
from flask import Blueprint, jsonify, request, send_file
from functools import wraps
from werkzeug.utils import secure_filename
from project import db
from project.api.models import GroupDocument, SavingsGroup, User, GroupMember
from project.api.file_storage_service import get_file_storage_service

group_documents_blueprint = Blueprint('group_documents', __name__)

# Allowed document types
ALLOWED_DOCUMENT_TYPES = ['CONSTITUTION', 'FINANCIAL_RECORD', 'REGISTRATION']

# Only PDF files allowed
ALLOWED_EXTENSIONS = {'pdf'}

# Maximum file size (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024


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


def is_group_admin(user_id, group_id):
    """Check if user is admin or leader of the group."""
    # Check if user is super admin first
    user = User.query.get(user_id)
    if user and (user.is_super_admin or user.admin):
        return True

    member = GroupMember.query.filter_by(
        user_id=user_id,
        group_id=group_id,
        is_active=True
    ).first()

    if not member:
        return False

    # Check if member has leader role
    return member.role in ['ADMIN', 'LEADER', 'CHAIRPERSON', 'SECRETARY', 'TREASURER']


def allowed_file(filename):
    """Check if file extension is allowed (PDF only)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@group_documents_blueprint.route('/groups/<int:group_id>/documents', methods=['GET'])
@authenticate
def get_group_documents(user_id, group_id):
    """Get all documents for a group."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404

    # Check if user is super admin (bypass membership check)
    user = User.query.get(user_id)
    if not (user and (user.is_super_admin or user.admin)):
        # Check if user is member of the group
        member = GroupMember.query.filter_by(
            user_id=user_id,
            group_id=group_id,
            is_active=True
        ).first()

        if not member:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
    
    # Get document type filter from query params
    document_type = request.args.get('type')
    
    query = GroupDocument.query.filter_by(
        group_id=group_id,
        is_deleted=False
    )
    
    if document_type and document_type in ALLOWED_DOCUMENT_TYPES:
        query = query.filter_by(document_type=document_type)
    
    documents = query.order_by(GroupDocument.upload_date.desc()).all()
    
    documents_data = []
    for doc in documents:
        uploader = User.query.get(doc.uploaded_by) if doc.uploaded_by else None
        documents_data.append({
            'id': doc.id,
            'document_title': doc.document_title,
            'document_type': doc.document_type,
            'file_name': doc.file_name,
            'file_size': doc.file_size,
            'mime_type': doc.mime_type,
            'upload_date': doc.upload_date.isoformat() if doc.upload_date else None,
            'uploaded_by': uploader.username if uploader else 'Unknown',
            'uploader_id': doc.uploaded_by,
            'version': doc.version,
            'version_number': doc.version_number,
            'description': doc.description,
            'is_compressed': doc.is_compressed,
            'compression_ratio': float(doc.compression_ratio) if doc.compression_ratio else None,
            'has_preview': doc.has_preview,
            'download_count': doc.download_count or 0
        })
    
    return jsonify({
        'status': 'success',
        'data': documents_data
    }), 200


@group_documents_blueprint.route('/groups/<int:group_id>/documents', methods=['POST'])
@authenticate
def upload_group_documents(user_id, group_id):
    """Upload documents for a group (admin/leader only)."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404
    
    # Check if user is admin/leader
    if not is_group_admin(user_id, group_id):
        return jsonify({'status': 'error', 'message': 'Only group admins/leaders can upload documents'}), 403
    
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400
    
    # Get document type from form data
    document_type = request.form.get('document_type', 'OTHER')
    if document_type not in ALLOWED_DOCUMENT_TYPES:
        return jsonify({'status': 'error', 'message': f'Invalid document type. Must be one of: {", ".join(ALLOWED_DOCUMENT_TYPES)}'}), 400
    
    description = request.form.get('description', '')
    version = request.form.get('version', '1.0')
    
    storage_service = get_file_storage_service()
    uploaded_documents = []
    errors = []
    
    for file in files:
        if file and file.filename:
            # Validate file type (PDF only)
            if not allowed_file(file.filename):
                errors.append(f'{file.filename}: Only PDF files are allowed')
                continue
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f'{file.filename}: File size exceeds 50MB limit')
                continue
            
            try:
                # Save file with compression and preview generation
                file_info = storage_service.save_uploaded_file(
                    file,
                    'group',
                    group_id,
                    auto_compress=True,
                    generate_preview=True
                )
                
                # Create database record
                document = GroupDocument(
                    group_id=group_id,
                    document_title=file_info['original_filename'],
                    document_type=document_type,
                    file_path=file_info['file_path'],
                    file_name=file_info['original_filename'],
                    original_filename=file_info['original_filename'],
                    file_size=file_info['file_size'],
                    mime_type=file_info.get('mime_type', 'application/pdf'),
                    uploaded_by=user_id,
                    upload_date=datetime.datetime.utcnow(),
                    version=version,
                    description=description,
                    is_compressed=file_info.get('is_compressed', False),
                    compressed_size=file_info.get('compressed_size'),
                    compression_ratio=file_info.get('compression_ratio'),
                    file_hash=file_info.get('file_hash'),
                    has_preview=file_info.get('has_preview', False),
                    thumbnail_path=file_info.get('thumbnail_path'),
                    preview_path=file_info.get('preview_path'),
                    is_active=True,
                    is_current_version=True
                )
                
                db.session.add(document)
                db.session.commit()
                
                uploader = User.query.get(user_id)
                uploaded_documents.append({
                    'id': document.id,
                    'document_title': document.document_title,
                    'document_type': document.document_type,
                    'file_name': document.file_name,
                    'file_size': document.file_size,
                    'upload_date': document.upload_date.isoformat(),
                    'uploaded_by': uploader.username if uploader else 'Unknown',
                    'is_compressed': document.is_compressed,
                    'compression_ratio': float(document.compression_ratio) if document.compression_ratio else None
                })
                
            except Exception as e:
                db.session.rollback()
                errors.append(f'{file.filename}: {str(e)}')
    
    if not uploaded_documents and errors:
        return jsonify({
            'status': 'error',
            'message': 'Failed to upload documents',
            'errors': errors
        }), 400
    
    response_data = {
        'status': 'success',
        'message': f'Successfully uploaded {len(uploaded_documents)} document(s)',
        'data': uploaded_documents
    }
    
    if errors:
        response_data['warnings'] = errors
    
    return jsonify(response_data), 201


@group_documents_blueprint.route('/groups/<int:group_id>/documents/<int:document_id>', methods=['DELETE'])
@authenticate
def delete_group_document(user_id, group_id, document_id):
    """Delete a group document (admin/leader only)."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404
    
    # Check if user is admin/leader
    if not is_group_admin(user_id, group_id):
        return jsonify({'status': 'error', 'message': 'Only group admins/leaders can delete documents'}), 403
    
    document = GroupDocument.query.filter_by(
        id=document_id,
        group_id=group_id,
        is_deleted=False
    ).first()
    
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    
    try:
        # Soft delete the document
        document.is_deleted = True
        document.deleted_date = datetime.datetime.utcnow()
        document.deleted_by = user_id
        
        # Delete physical file
        storage_service = get_file_storage_service()
        if os.path.exists(document.file_path):
            storage_service.delete_file(document.file_path)
        
        # Delete thumbnail and preview if they exist
        if document.thumbnail_path and os.path.exists(document.thumbnail_path):
            storage_service.delete_file(document.thumbnail_path)
        if document.preview_path and os.path.exists(document.preview_path):
            storage_service.delete_file(document.preview_path)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@group_documents_blueprint.route('/groups/<int:group_id>/documents/<int:document_id>/download', methods=['GET'])
@authenticate
def download_group_document(user_id, group_id, document_id):
    """Download a group document."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404

    # Check if user is super admin (bypass membership check)
    user = User.query.get(user_id)
    if not (user and (user.is_super_admin or user.admin)):
        # Check if user is member of the group
        member = GroupMember.query.filter_by(
            user_id=user_id,
            group_id=group_id,
            is_active=True
        ).first()

        if not member:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

    document = GroupDocument.query.filter_by(
        id=document_id,
        group_id=group_id,
        is_deleted=False
    ).first()

    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if not os.path.exists(document.file_path):
        return jsonify({'status': 'error', 'message': 'File not found on server'}), 404

    # Update download count
    document.download_count = (document.download_count or 0) + 1
    document.last_accessed = datetime.datetime.utcnow()
    db.session.commit()

    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.file_name,
        mimetype=document.mime_type
    )


@group_documents_blueprint.route('/groups/<int:group_id>/documents/<int:document_id>/preview', methods=['GET'])
@authenticate
def preview_group_document(user_id, group_id, document_id):
    """Preview a group document."""
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404

    # Check if user is super admin (bypass membership check)
    user = User.query.get(user_id)
    if not (user and (user.is_super_admin or user.admin)):
        # Check if user is member of the group
        member = GroupMember.query.filter_by(
            user_id=user_id,
            group_id=group_id,
            is_active=True
        ).first()

        if not member:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403

    document = GroupDocument.query.filter_by(
        id=document_id,
        group_id=group_id,
        is_deleted=False
    ).first()

    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    # Try to serve preview if available, otherwise serve original
    preview_path = document.preview_path if document.has_preview and document.preview_path else document.file_path

    if not os.path.exists(preview_path):
        return jsonify({'status': 'error', 'message': 'File not found on server'}), 404

    # Update last accessed
    document.last_accessed = datetime.datetime.utcnow()
    db.session.commit()

    return send_file(
        preview_path,
        mimetype=document.mime_type
    )

