"""
Remote Mobile Money Payment API
Handles remote savings contributions submitted via mobile money with verification workflow.
"""
import datetime
from flask import Blueprint, jsonify, request
from functools import wraps
import jwt
from flask import current_app
from project import db
from project.api.models import (
    SavingTransaction, Meeting, GroupMember, MemberSaving,
    SavingType, MeetingAttendance, TransactionDocument, MeetingSummary
)

remote_payments_blueprint = Blueprint('remote_payments', __name__)


def authenticate(f):
    """Decorator to authenticate requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }), 401
        
        try:
            auth_token = auth_header.split(' ')[1]
            payload = jwt.decode(
                auth_token,
                current_app.config.get('SECRET_KEY'),
                algorithms=['HS256']
            )
            user_id = payload['sub']
            return f(user_id, *args, **kwargs)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, IndexError):
            return jsonify({
                'status': 'fail',
                'message': 'Invalid token.'
            }), 401
    
    return decorated_function


def is_officer_or_admin(user_id, group_id):
    """Check if user is an officer or admin in the group."""
    member = GroupMember.query.filter_by(user_id=user_id, group_id=group_id).first()
    if not member:
        return False
    return member.role in ['ADMIN', 'OFFICER', 'CHAIRPERSON', 'TREASURER', 'SECRETARY']


@remote_payments_blueprint.route('/meetings/<int:meeting_id>/remote-payment', methods=['POST'])
@authenticate
def submit_remote_payment(user_id, meeting_id):
    """
    Allow members to submit remote mobile money payments for a meeting.
    
    Request Body:
    {
        "saving_type_id": 1,
        "amount": 10000,
        "mobile_money_reference": "MTN-ABC123456",
        "mobile_money_phone": "+256700123456",
        "description": "Personal savings contribution"
    }
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404
    
    # Check meeting status - must be SCHEDULED or IN_PROGRESS
    if meeting.status not in ['SCHEDULED', 'IN_PROGRESS']:
        return jsonify({
            'status': 'error',
            'message': 'Can only submit remote payments for scheduled or in-progress meetings'
        }), 400
    
    post_data = request.get_json()
    saving_type_id = post_data.get('saving_type_id')
    amount = post_data.get('amount')
    mobile_money_reference = post_data.get('mobile_money_reference')
    mobile_money_phone = post_data.get('mobile_money_phone')
    description = post_data.get('description', '')
    
    # Validate required fields
    if not all([saving_type_id, amount, mobile_money_reference, mobile_money_phone]):
        return jsonify({
            'status': 'error',
            'message': 'Missing required fields: saving_type_id, amount, mobile_money_reference, mobile_money_phone'
        }), 400
    
    # Validate amount
    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'status': 'error', 'message': 'Amount must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid amount'}), 400
    
    try:
        # Get member from user_id
        member = GroupMember.query.filter_by(user_id=user_id, group_id=meeting.group_id).first()
        if not member:
            return jsonify({
                'status': 'error',
                'message': 'You are not a member of this group'
            }), 403
        
        # Check if member is marked as present (cannot be both present and remote)
        attendance = MeetingAttendance.query.filter_by(
            meeting_id=meeting_id,
            member_id=member.id
        ).first()
        
        if attendance and attendance.is_present:
            return jsonify({
                'status': 'error',
                'message': 'You are marked as present. Cannot submit remote payment.'
            }), 400
        
        # Verify saving type exists and belongs to group
        saving_type = SavingType.query.filter_by(
            id=saving_type_id,
            group_id=meeting.group_id
        ).first()
        
        if not saving_type:
            return jsonify({
                'status': 'error',
                'message': 'Invalid saving type for this group'
            }), 400
        
        # Get or create member_saving record
        member_saving = MemberSaving.query.filter_by(
            member_id=member.id,
            saving_type_id=saving_type_id
        ).first()
        
        if not member_saving:
            # Create new member_saving record
            member_saving = MemberSaving(
                member_id=member.id,
                saving_type_id=saving_type_id,
                current_balance=0.00,
                total_deposits=0.00,
                total_withdrawals=0.00
            )
            db.session.add(member_saving)
            db.session.flush()  # Get the ID
        
        # Create savings transaction with PENDING status
        transaction = SavingTransaction(
            member_saving_id=member_saving.id,
            amount=amount,
            transaction_type='DEPOSIT',  # Remote payments are always deposits
            transaction_date=meeting.meeting_date,
            description=description,
            meeting_id=meeting_id,
            is_mobile_money=True,
            mobile_money_reference=mobile_money_reference,
            mobile_money_phone=mobile_money_phone,
            verification_status='PENDING',  # Requires verification
            notes=f'Remote payment submitted by {member.first_name} {member.last_name}'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Remote payment submitted successfully. Awaiting verification.',
            'data': {
                'transaction_id': transaction.id,
                'amount': float(amount),
                'status': 'PENDING',
                'requires_verification': True,
                'mobile_money_reference': mobile_money_reference
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@remote_payments_blueprint.route('/savings-transactions/<int:transaction_id>/verify', methods=['PUT'])
@authenticate
def verify_remote_payment(user_id, transaction_id):
    """
    Verify or reject a remote payment (officers/admins only).
    
    Request Body:
    {
        "action": "VERIFY",  // or "REJECT"
        "notes": "Confirmed with MTN statement"
    }
    """
    transaction = SavingTransaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'status': 'error', 'message': 'Transaction not found'}), 404
    
    # Check if transaction is a remote payment
    if not transaction.is_mobile_money:
        return jsonify({
            'status': 'error',
            'message': 'This is not a remote payment transaction'
        }), 400
    
    # Check if already verified or rejected
    if transaction.verification_status in ['VERIFIED', 'REJECTED']:
        return jsonify({
            'status': 'error',
            'message': f'Transaction already {transaction.verification_status.lower()}'
        }), 400
    
    # Get meeting and group
    meeting = Meeting.query.get(transaction.meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404
    
    # Check if user is officer/admin
    if not is_officer_or_admin(user_id, meeting.group_id):
        return jsonify({
            'status': 'error',
            'message': 'Only officers and admins can verify payments'
        }), 403
    
    # Get member who submitted the payment
    member_saving = MemberSaving.query.get(transaction.member_saving_id)
    if not member_saving:
        return jsonify({'status': 'error', 'message': 'Member saving record not found'}), 404
    
    # Check if user is trying to verify their own payment
    verifier_member = GroupMember.query.filter_by(user_id=user_id, group_id=meeting.group_id).first()
    if verifier_member and verifier_member.id == member_saving.member_id:
        return jsonify({
            'status': 'error',
            'message': 'You cannot verify your own payment'
        }), 403
    
    post_data = request.get_json()
    action = post_data.get('action', '').upper()
    notes = post_data.get('notes', '')
    
    if action not in ['VERIFY', 'REJECT']:
        return jsonify({
            'status': 'error',
            'message': 'Invalid action. Must be VERIFY or REJECT'
        }), 400
    
    try:
        if action == 'VERIFY':
            # Verify the payment
            transaction.verification_status = 'VERIFIED'
            transaction.verified_by = user_id
            transaction.verified_date = datetime.datetime.utcnow()
            transaction.notes = notes or transaction.notes
            
            # Update member_saving balance (now that it's verified)
            member_saving.current_balance = float(member_saving.current_balance or 0) + float(transaction.amount)
            member_saving.total_deposits = float(member_saving.total_deposits or 0) + float(transaction.amount)

            # If meeting is already completed, update the meeting summary
            if meeting.status == 'COMPLETED':
                summary = MeetingSummary.query.filter_by(meeting_id=meeting.id).first()
                if summary:
                    # Recalculate totals including this newly verified payment
                    all_verified_transactions = SavingTransaction.query.filter_by(
                        meeting_id=meeting.id,
                        verification_status='VERIFIED'
                    ).all()

                    total_deposits = sum(float(t.amount) for t in all_verified_transactions if t.transaction_type == 'DEPOSIT')
                    total_withdrawals = sum(float(t.amount) for t in all_verified_transactions if t.transaction_type == 'WITHDRAWAL')

                    summary.total_deposits = total_deposits
                    summary.total_withdrawals = total_withdrawals
                    summary.net_savings = total_deposits - total_withdrawals

                    # Also update meeting totals
                    meeting.total_savings_collected = total_deposits

            message = 'Payment verified successfully'
            
        else:  # REJECT
            # Reject the payment
            transaction.verification_status = 'REJECTED'
            transaction.verified_by = user_id
            transaction.verified_date = datetime.datetime.utcnow()
            transaction.notes = notes or 'Payment rejected'
            
            # Do NOT update balances for rejected payments
            
            message = 'Payment rejected'
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'transaction_id': transaction.id,
                'verification_status': transaction.verification_status,
                'verified_by': transaction.verified_by,
                'verified_date': transaction.verified_date.isoformat() if transaction.verified_date else None,
                'notes': transaction.notes
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@remote_payments_blueprint.route('/meetings/<int:meeting_id>/pending-payments', methods=['GET'])
@authenticate
def get_pending_payments(user_id, meeting_id):
    """
    Get all pending remote payments for a meeting (officers/admins only).
    
    Returns list of pending payments with member details.
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404
    
    # Check if user is officer/admin
    if not is_officer_or_admin(user_id, meeting.group_id):
        return jsonify({
            'status': 'error',
            'message': 'Only officers and admins can view pending payments'
        }), 403
    
    try:
        # Get all remote payments for this meeting
        remote_payments = SavingTransaction.query.filter_by(
            meeting_id=meeting_id,
            is_mobile_money=True
        ).order_by(SavingTransaction.created_date.asc()).all()
        
        # Separate by status
        pending_payments = []
        verified_payments = []
        rejected_payments = []
        
        for transaction in remote_payments:
            member_saving = MemberSaving.query.get(transaction.member_saving_id)
            if not member_saving:
                continue
            
            member = GroupMember.query.get(member_saving.member_id)
            if not member:
                continue
            
            saving_type = SavingType.query.get(member_saving.saving_type_id)
            
            # Get documents
            documents = TransactionDocument.get_for_entity('savings', transaction.id)
            
            payment_data = {
                'id': transaction.id,
                'member_id': member.id,
                'member_name': f"{member.first_name} {member.last_name}",
                'saving_type_id': member_saving.saving_type_id,
                'saving_type_name': saving_type.name if saving_type else 'Unknown',
                'amount': float(transaction.amount),
                'mobile_money_reference': transaction.mobile_money_reference,
                'mobile_money_phone': transaction.mobile_money_phone,
                'description': transaction.description,
                'submitted_date': transaction.created_date.isoformat() if transaction.created_date else None,
                'verification_status': transaction.verification_status,
                'verified_by': transaction.verified_by,
                'verified_date': transaction.verified_date.isoformat() if transaction.verified_date else None,
                'notes': transaction.notes,
                'documents': [doc.to_dict() for doc in documents]
            }
            
            if transaction.verification_status == 'PENDING':
                pending_payments.append(payment_data)
            elif transaction.verification_status == 'VERIFIED':
                verified_payments.append(payment_data)
            elif transaction.verification_status == 'REJECTED':
                rejected_payments.append(payment_data)
        
        # Calculate totals
        pending_amount = sum([p['amount'] for p in pending_payments])
        verified_amount = sum([p['amount'] for p in verified_payments])
        
        return jsonify({
            'status': 'success',
            'data': {
                'pending_count': len(pending_payments),
                'verified_count': len(verified_payments),
                'rejected_count': len(rejected_payments),
                'total_pending_amount': float(pending_amount),
                'total_verified_amount': float(verified_amount),
                'pending_payments': pending_payments,
                'verified_payments': verified_payments,
                'rejected_payments': rejected_payments
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

