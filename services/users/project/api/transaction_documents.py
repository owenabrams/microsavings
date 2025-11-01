"""
Transaction Document Management API
Polymorphic document attachments for all transaction types using unified architecture.

Supports entity types:
- training: Training sessions
- voting: Voting sessions
- loan_repayment: Loan repayments
- fine: Member fines
- savings: Savings transactions
- meeting: Meeting-level documents
- member: Member documents
- group: Group documents
"""

import os
import datetime
from flask import Blueprint, jsonify, request, send_file
from functools import wraps
from werkzeug.utils import secure_filename
from project import db
from project.api.models import (
    TransactionDocument, User, TrainingRecord, VotingRecord,
    LoanRepayment, MemberFine, SavingTransaction, Meeting,
    GroupMember, SavingsGroup
)
from project.api.file_storage_service import get_file_storage_service

transaction_documents_blueprint = Blueprint('transaction_documents', __name__)


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


def validate_entity_exists(entity_type, entity_id):
    """
    Validate that the entity exists in the database.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of entity
        
    Returns:
        tuple: (exists: bool, entity: object or None, error_message: str or None)
    """
    entity_map = {
        'training': TrainingRecord,
        'voting': VotingRecord,
        'loan_repayment': LoanRepayment,
        'fine': MemberFine,
        'savings': SavingTransaction,
        'meeting': Meeting,
        'member': GroupMember,
        'group': SavingsGroup
    }
    
    model = entity_map.get(entity_type)
    if not model:
        return False, None, f'Invalid entity type: {entity_type}'
    
    entity = model.query.get(entity_id)
    if not entity:
        return False, None, f'{entity_type.replace("_", " ").title()} not found'
    
    return True, entity, None


@transaction_documents_blueprint.route('/documents/<entity_type>/<int:entity_id>', methods=['GET'])
@authenticate
def get_entity_documents(user_id, entity_type, entity_id):
    """
    Get all documents for a specific entity.
    
    Args:
        entity_type: Type of entity (training, voting, etc.)
        entity_id: ID of the entity
        
    Returns:
        JSON response with list of documents
    """
    # Validate entity type
    if not TransactionDocument.validate_entity_type(entity_type):
        return jsonify({
            'status': 'error',
            'message': f'Invalid entity type: {entity_type}. Valid types: {", ".join(TransactionDocument.get_entity_types())}'
        }), 400
    
    # Validate entity exists
    exists, entity, error_msg = validate_entity_exists(entity_type, entity_id)
    if not exists:
        return jsonify({'status': 'error', 'message': error_msg}), 404
    
    # Get documents
    documents = TransactionDocument.get_for_entity(entity_type, entity_id)
    
    return jsonify({
        'status': 'success',
        'data': {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'documents': [doc.to_dict() for doc in documents],
            'count': len(documents)
        }
    }), 200


@transaction_documents_blueprint.route('/documents/<entity_type>/<int:entity_id>', methods=['POST'])
@authenticate
def upload_entity_documents(user_id, entity_type, entity_id):
    """
    Upload documents for a specific entity.
    
    Supports multiple file upload with automatic compression and preview generation.
    
    Args:
        entity_type: Type of entity
        entity_id: ID of the entity
        
    Form data:
        files: Multiple files to upload
        document_type: Type of document (RECEIPT, INVOICE, PHOTO, REPORT, CERTIFICATE, OTHER)
        document_category: Category (FINANCIAL, TRAINING, VOTING, LEGAL, GENERAL)
        description: Optional description
        is_proof_document: Boolean flag
        
    Returns:
        JSON response with uploaded document details
    """
    # Validate entity type
    if not TransactionDocument.validate_entity_type(entity_type):
        return jsonify({
            'status': 'error',
            'message': f'Invalid entity type: {entity_type}'
        }), 400
    
    # Validate entity exists
    exists, entity, error_msg = validate_entity_exists(entity_type, entity_id)
    if not exists:
        return jsonify({'status': 'error', 'message': error_msg}), 404
    
    # Check for files
    if 'files' not in request.files:
        return jsonify({'status': 'error', 'message': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'status': 'error', 'message': 'No files selected'}), 400
    
    # Get optional metadata
    document_type = request.form.get('document_type', 'OTHER')
    document_category = request.form.get('document_category', 'GENERAL')
    description = request.form.get('description', '')
    is_proof_document = request.form.get('is_proof_document', 'false').lower() == 'true'
    
    # Get file storage service
    storage_service = get_file_storage_service()
    
    uploaded_documents = []
    errors = []
    
    for file in files:
        if file.filename == '':
            continue
        
        try:
            # Save file using storage service
            file_info = storage_service.save_uploaded_file(
                file,
                entity_type=entity_type,
                entity_id=entity_id,
                auto_compress=True,
                generate_preview=True
            )
            
            # Create database record
            document = TransactionDocument(
                entity_type=entity_type,
                entity_id=entity_id,
                document_name=file_info['stored_filename'],
                original_filename=file_info['original_filename'],
                document_type=document_type,
                document_category=document_category,
                description=description,
                file_path=file_info['file_path'],
                file_size=file_info['file_size'],
                mime_type=file_info.get('metadata', {}).get('mime_type'),
                file_hash=file_info.get('metadata', {}).get('file_hash'),
                is_compressed=file_info['is_compressed'],
                compressed_size=file_info.get('compressed_size'),
                compression_ratio=file_info.get('compression_ratio'),
                thumbnail_path=file_info.get('thumbnail_path'),
                preview_path=file_info.get('preview_path'),
                has_preview=file_info.get('thumbnail_path') is not None,
                is_proof_document=is_proof_document,
                uploaded_by=user_id
            )
            
            db.session.add(document)
            db.session.flush()
            
            uploaded_documents.append(document.to_dict())
            
        except Exception as e:
            errors.append({
                'filename': file.filename,
                'error': str(e)
            })
    
    # Commit all successful uploads
    if uploaded_documents:
        db.session.commit()
    else:
        db.session.rollback()
    
    if errors and not uploaded_documents:
        return jsonify({
            'status': 'error',
            'message': 'All uploads failed',
            'errors': errors
        }), 400
    
    return jsonify({
        'status': 'success',
        'data': {
            'uploaded': uploaded_documents,
            'errors': errors,
            'count': len(uploaded_documents)
        }
    }), 201


@transaction_documents_blueprint.route('/documents/<int:document_id>', methods=['GET'])
@authenticate
def get_document_details(user_id, document_id):
    """
    Get details of a specific document.
    
    Args:
        document_id: ID of the document
        
    Returns:
        JSON response with document details
    """
    document = TransactionDocument.query.get(document_id)
    
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    
    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404
    
    return jsonify({
        'status': 'success',
        'data': document.to_dict()
    }), 200


@transaction_documents_blueprint.route('/documents/<int:document_id>/download', methods=['GET'])
@authenticate
def download_document(user_id, document_id):
    """
    Download a document file.
    
    Args:
        document_id: ID of the document
        
    Returns:
        File download response
    """
    document = TransactionDocument.query.get(document_id)
    
    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    
    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404
    
    # Check if file exists
    if not os.path.exists(document.file_path):
        return jsonify({'status': 'error', 'message': 'File not found on server'}), 404
    
    try:
        return send_file(
            document.file_path,
            as_attachment=True,
            download_name=document.original_filename,
            mimetype=document.mime_type
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error downloading file: {str(e)}'}), 500


@transaction_documents_blueprint.route('/documents/<int:document_id>/preview', methods=['GET'])
@authenticate
def get_document_preview(user_id, document_id):
    """
    Get document preview/thumbnail.

    Args:
        document_id: ID of the document

    Query params:
        type: 'thumbnail' or 'preview' (default: thumbnail)

    Returns:
        Preview image file or error
    """
    document = TransactionDocument.query.get(document_id)

    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document has been deleted'}), 404

    # Get preview type
    preview_type = request.args.get('type', 'thumbnail')

    # Get preview path
    if preview_type == 'thumbnail' and document.thumbnail_path:
        preview_path = document.thumbnail_path
    elif preview_type == 'preview' and document.preview_path:
        preview_path = document.preview_path
    else:
        return jsonify({'status': 'error', 'message': 'Preview not available for this document'}), 404

    # Check if preview file exists
    if not os.path.exists(preview_path):
        return jsonify({'status': 'error', 'message': 'Preview file not found on server'}), 404

    try:
        return send_file(
            preview_path,
            mimetype='image/jpeg'
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error loading preview: {str(e)}'}), 500


@transaction_documents_blueprint.route('/documents/<int:document_id>', methods=['DELETE'])
@authenticate
def delete_document(user_id, document_id):
    """
    Soft delete a document.

    Args:
        document_id: ID of the document

    Returns:
        JSON response confirming deletion
    """
    document = TransactionDocument.query.get(document_id)

    if not document:
        return jsonify({'status': 'error', 'message': 'Document not found'}), 404

    if document.is_deleted:
        return jsonify({'status': 'error', 'message': 'Document already deleted'}), 400

    # Soft delete
    document.soft_delete(deleted_by_user_id=user_id)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'message': 'Document deleted successfully',
        'data': {
            'document_id': document_id,
            'deleted_at': document.deleted_at.isoformat() if document.deleted_at else None
        }
    }), 200

