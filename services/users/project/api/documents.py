"""Document management API endpoints."""
import os
import datetime
import uuid
from flask import Blueprint, jsonify, request, current_app, send_file
from werkzeug.utils import secure_filename
from functools import wraps
import jwt
from project import db
from project.api.models import (
    ActivityDocument, MeetingActivity, GroupDocument, SavingsGroup,
    User, MemberActivityParticipation
)

documents_blueprint = Blueprint('documents', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv',
    'jpg', 'jpeg', 'png', 'gif', 'bmp',
    'mp4', 'avi', 'mov', 'wmv',
    'zip', 'rar', '7z'
}

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


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """Get file extension."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_mime_type(filename):
    """Get MIME type based on file extension."""
    ext = get_file_extension(filename)
    mime_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'txt': 'text/plain',
        'csv': 'text/csv',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        '7z': 'application/x-7z-compressed'
    }
    return mime_types.get(ext, 'application/octet-stream')


@documents_blueprint.route('/activities/<int:activity_id>/documents', methods=['POST'])
@authenticate
def upload_activity_documents(user_id, activity_id):
    """Upload multiple documents for a meeting activity."""
    activity = MeetingActivity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400
    
    # Get additional metadata from form data
    document_type = request.form.get('document_type', 'OTHER')
    document_category = request.form.get('document_category', 'GENERAL')
    description = request.form.get('description', '')
    is_proof_document = request.form.get('is_proof_document', 'false').lower() == 'true'
    
    uploaded_documents = []
    errors = []
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', '/uploads'), 'activities', str(activity_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    for file in files:
        if file and file.filename:
            # Validate file
            if not allowed_file(file.filename):
                errors.append(f'{file.filename}: File type not allowed')
                continue
            
            # Check file size
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                errors.append(f'{file.filename}: File size exceeds 50MB limit')
                continue
            
            # Generate unique filename
            original_filename = secure_filename(file.filename)
            file_extension = get_file_extension(original_filename)
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            try:
                # Save file
                file.save(file_path)
                
                # Create database record
                document = ActivityDocument(
                    activity_id=activity_id,
                    document_name=original_filename,
                    document_type=document_type,
                    file_path=file_path,
                    file_size=file_size,
                    mime_type=get_mime_type(original_filename),
                    description=description,
                    is_proof_document=is_proof_document,
                    document_category=document_category,
                    uploaded_by=user_id,
                    upload_date=datetime.datetime.utcnow()
                )
                db.session.add(document)
                db.session.flush()
                
                uploaded_documents.append({
                    'id': document.id,
                    'document_name': document.document_name,
                    'document_type': document.document_type,
                    'file_size': document.file_size,
                    'mime_type': document.mime_type,
                    'upload_date': document.upload_date.isoformat()
                })
                
            except Exception as e:
                errors.append(f'{file.filename}: {str(e)}')
                if os.path.exists(file_path):
                    os.remove(file_path)
    
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
        # Clean up uploaded files
        for doc in uploaded_documents:
            file_path = os.path.join(upload_dir, doc['document_name'])
            if os.path.exists(file_path):
                os.remove(file_path)
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_blueprint.route('/activities/<int:activity_id>/documents', methods=['GET'])
@authenticate
def get_activity_documents(user_id, activity_id):
    """Get all documents for a meeting activity."""
    activity = MeetingActivity.query.get(activity_id)
    if not activity:
        return jsonify({'status': 'error', 'message': 'Activity not found'}), 404
    
    documents = ActivityDocument.query.filter_by(activity_id=activity_id).all()
    
    return jsonify({
        'status': 'success',
        'data': {
            'documents': [{
                'id': doc.id,
                'document_name': doc.document_name,
                'document_type': doc.document_type,
                'file_size': doc.file_size,
                'mime_type': doc.mime_type,
                'description': doc.description,
                'is_proof_document': doc.is_proof_document,
                'document_category': doc.document_category,
                'uploaded_by': doc.uploaded_by,
                'upload_date': doc.upload_date.isoformat() if doc.upload_date else None
            } for doc in documents]
        }
    }), 200


@documents_blueprint.route('/documents/<int:document_id>', methods=['DELETE'])
@authenticate
def delete_document(user_id, document_id):
    """Delete a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    
    # Check if user has permission (uploaded by user or user is admin)
    user = User.query.get(user_id)
    if document.uploaded_by != user_id and not user.admin:
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403
    
    try:
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete database record
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Document deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@documents_blueprint.route('/documents/<int:document_id>/download', methods=['GET'])
@authenticate
def download_document(user_id, document_id):
    """Download a document."""
    document = ActivityDocument.query.get(document_id)
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    
    if not os.path.exists(document.file_path):
        return jsonify({'status': 'error', 'message': 'File not found on server'}), 404
    
    return send_file(
        document.file_path,
        as_attachment=True,
        download_name=document.document_name,
        mimetype=document.mime_type
    )

