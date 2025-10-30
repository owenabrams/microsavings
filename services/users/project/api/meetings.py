"""Meeting management API endpoints."""
import datetime
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import func, and_, or_
from functools import wraps
import jwt
from project import db
from project.api.models import (
    Meeting, MeetingAttendance, SavingsGroup, GroupMember,
    MemberSaving, SavingTransaction, MemberFine, GroupLoan, LoanRepayment,
    TrainingRecord, TrainingAttendance, VotingRecord, MemberVote,
    MeetingSummary, GroupSettings, SavingType, MeetingActivity,
    ActivityDocument, MemberActivityParticipation
)

meetings_blueprint = Blueprint('meetings', __name__)


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


@meetings_blueprint.route('/groups/<int:group_id>/meetings', methods=['POST'])
@authenticate
def create_meeting(user_id, group_id):
    """Create a new meeting for a group."""
    post_data = request.get_json()
    
    # Validate group exists
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404
    
    # Get next meeting number
    last_meeting = Meeting.query.filter_by(group_id=group_id).order_by(Meeting.meeting_number.desc()).first()
    next_meeting_number = (last_meeting.meeting_number + 1) if last_meeting else 1
    
    try:
        # Create meeting
        meeting = Meeting(
            group_id=group_id,
            meeting_number=next_meeting_number,
            meeting_date=datetime.datetime.strptime(post_data.get('meeting_date'), '%Y-%m-%d').date(),
            meeting_time=datetime.datetime.strptime(post_data.get('meeting_time', '14:00'), '%H:%M').time() if post_data.get('meeting_time') else None,
            meeting_type=post_data.get('meeting_type', 'REGULAR'),
            status='SCHEDULED',
            chairperson_id=post_data.get('chairperson_id'),
            secretary_id=post_data.get('secretary_id'),
            treasurer_id=post_data.get('treasurer_id'),
            agenda=post_data.get('agenda'),
            location=post_data.get('location'),
            latitude=post_data.get('latitude'),
            longitude=post_data.get('longitude'),
            total_members=group.members_count
        )
        
        db.session.add(meeting)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Meeting created successfully',
            'meeting': {
                'id': meeting.id,
                'meeting_number': meeting.meeting_number,
                'meeting_date': meeting.meeting_date.isoformat(),
                'meeting_time': meeting.meeting_time.isoformat() if meeting.meeting_time else None,
                'status': meeting.status,
                'location': meeting.location
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/groups/<int:group_id>/meetings', methods=['GET'])
@authenticate
def get_group_meetings(user_id, group_id):
    """Get all meetings for a group."""
    # Validate group exists
    group = SavingsGroup.query.get(group_id)
    if not group:
        return jsonify({'status': 'error', 'message': 'Group not found'}), 404
    
    # Get query parameters
    status = request.args.get('status')
    limit = request.args.get('limit', type=int)
    
    # Build query
    query = Meeting.query.filter_by(group_id=group_id).order_by(Meeting.meeting_date.desc())
    
    if status:
        query = query.filter_by(status=status)
    
    if limit:
        query = query.limit(limit)
    
    meetings = query.all()
    
    return jsonify({
        'status': 'success',
        'meetings': [{
            'id': m.id,
            'meeting_number': m.meeting_number,
            'meeting_date': m.meeting_date.isoformat(),
            'meeting_time': m.meeting_time.isoformat() if m.meeting_time else None,
            'meeting_type': m.meeting_type,
            'status': m.status,
            'location': m.location,
            'total_members': m.total_members,
            'members_present': m.members_present,
            'attendance_rate': float(m.members_present / m.total_members * 100) if m.total_members > 0 else 0,
            'quorum_met': m.quorum_met,
            'total_savings_collected': float(m.total_savings_collected or 0),
            'total_fines_collected': float(m.total_fines_collected or 0),
            'total_loan_repayments': float(m.total_loan_repayments or 0),
            'agenda': m.agenda,
            'created_date': m.created_date.isoformat()
        } for m in meetings]
    }), 200


@meetings_blueprint.route('/meetings/<int:meeting_id>', methods=['GET'])
@authenticate
def get_meeting_detail(user_id, meeting_id):
    """Get detailed information about a specific meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    # Get group settings to check what's enabled
    group_settings = GroupSettings.query.filter_by(group_id=meeting.group_id).first()

    # Get attendance records
    attendance = MeetingAttendance.query.filter_by(meeting_id=meeting_id).all()

    # Get savings transactions
    savings_transactions = SavingTransaction.query.filter_by(meeting_id=meeting_id).all()

    # Get fines
    fines = MemberFine.query.filter_by(meeting_id=meeting_id).all()

    # Get loan repayments
    loan_repayments = LoanRepayment.query.filter_by(meeting_id=meeting_id).all()

    # Get training records
    trainings = TrainingRecord.query.filter_by(meeting_id=meeting_id).all()

    # Get voting records
    votings = VotingRecord.query.filter_by(meeting_id=meeting_id).all()

    # Get meeting summary if exists
    summary = MeetingSummary.query.filter_by(meeting_id=meeting_id).first()
    
    return jsonify({
        'status': 'success',
        'meeting': {
            'id': meeting.id,
            'group_id': meeting.group_id,
            'meeting_number': meeting.meeting_number,
            'meeting_date': meeting.meeting_date.isoformat(),
            'meeting_time': meeting.meeting_time.isoformat() if meeting.meeting_time else None,
            'meeting_type': meeting.meeting_type,
            'status': meeting.status,
            'location': meeting.location,
            'latitude': float(meeting.latitude) if meeting.latitude else None,
            'longitude': float(meeting.longitude) if meeting.longitude else None,
            'total_members': meeting.total_members,
            'members_present': meeting.members_present,
            'quorum_met': meeting.quorum_met,
            'agenda': meeting.agenda,
            'minutes': meeting.minutes,
            'decisions_made': meeting.decisions_made,
            'action_items': meeting.action_items,
            'chairperson_id': meeting.chairperson_id,
            'secretary_id': meeting.secretary_id,
            'treasurer_id': meeting.treasurer_id,
            'created_date': meeting.created_date.isoformat(),
            'updated_date': meeting.updated_date.isoformat()
        },
        'group_settings': {
            'attendance_tracking_enabled': group_settings.attendance_tracking_enabled if group_settings else True,
            'loan_disbursement_enabled': group_settings.loan_disbursement_enabled if group_settings else True,
            'loan_repayment_enabled': group_settings.loan_repayment_enabled if group_settings else True,
            'voting_session_enabled': group_settings.voting_session_enabled if group_settings else True,
            'training_session_enabled': group_settings.training_session_enabled if group_settings else True,
            'fine_collection_enabled': group_settings.fine_collection_enabled if group_settings else True
        },
        'attendance': [{
            'id': a.id,
            'member_id': a.member_id,
            'member_name': f"{a.member.first_name} {a.member.last_name}" if a.member else 'Unknown',
            'is_present': a.is_present,
            'status': 'present' if a.is_present else 'absent',
            'arrival_time': a.arrival_time.isoformat() if a.arrival_time else None,
            'excuse_reason': a.excuse_reason
        } for a in attendance],
        'savings_transactions': [{
            'id': st.id,
            'member_id': st.member_saving.member_id if st.member_saving else None,
            'member_name': f"{st.member_saving.member.first_name} {st.member_saving.member.last_name}" if st.member_saving and st.member_saving.member else 'Unknown',
            'saving_type_id': st.member_saving.saving_type_id if st.member_saving else None,
            'saving_type_name': st.member_saving.saving_type.name if st.member_saving and st.member_saving.saving_type else 'Unknown',
            'transaction_type': st.transaction_type,
            'amount': float(st.amount),
            'transaction_date': st.transaction_date.isoformat() if st.transaction_date else None,
            'description': st.description,
            'reference_number': st.reference_number,
            'verification_status': st.verification_status
        } for st in savings_transactions],
        'fines': [{
            'id': f.id,
            'member_id': f.member_id,
            'member_name': f"{f.member.first_name} {f.member.last_name}" if f.member else 'Unknown',
            'fine_type': f.fine_type,
            'amount': float(f.amount),
            'reason': f.reason,
            'fine_date': f.fine_date.isoformat() if f.fine_date else None,
            'is_paid': f.is_paid,
            'paid_amount': float(f.paid_amount) if f.paid_amount else 0,
            'payment_date': f.payment_date.isoformat() if f.payment_date else None,
            'verification_status': f.verification_status
        } for f in fines],
        'loan_repayments': [{
            'id': lr.id,
            'loan_id': lr.loan_id,
            'member_id': lr.member_id,
            'member_name': f"{lr.member.first_name} {lr.member.last_name}" if lr.member else 'Unknown',
            'repayment_amount': float(lr.repayment_amount),
            'principal_amount': float(lr.principal_amount),
            'interest_amount': float(lr.interest_amount),
            'outstanding_balance': float(lr.outstanding_balance),
            'repayment_date': lr.repayment_date.isoformat() if lr.repayment_date else None,
            'payment_method': lr.payment_method
        } for lr in loan_repayments],
        'trainings': [{
            'id': t.id,
            'training_topic': t.training_topic,
            'training_description': t.training_description,
            'trainer_name': t.trainer_name,
            'duration_minutes': t.duration_minutes,
            'total_attendees': t.total_attendees
        } for t in trainings],
        'votings': [{
            'id': v.id,
            'vote_topic': v.vote_topic,
            'vote_description': v.vote_description,
            'vote_type': v.vote_type,
            'result': v.result,
            'yes_count': v.yes_count,
            'no_count': v.no_count,
            'abstain_count': v.abstain_count,
            'absent_count': v.absent_count
        } for v in votings],
        'summary': {
            'total_deposits': float(summary.total_deposits) if summary else 0,
            'total_withdrawals': float(summary.total_withdrawals) if summary else 0,
            'net_savings': float(summary.net_savings) if summary else 0,
            'total_fines_issued': float(summary.total_fines_issued) if summary else 0,
            'total_fines_paid': float(summary.total_fines_paid) if summary else 0,
            'total_loans_disbursed': float(summary.total_loans_disbursed) if summary else 0,
            'total_loan_repayments': float(summary.total_loan_repayments) if summary else 0,
            'trainings_held': summary.trainings_held if summary else 0,
            'voting_sessions_held': summary.voting_sessions_held if summary else 0,
            'net_cash_flow': float(summary.net_cash_flow) if summary else 0
        } if summary else None
    }), 200


@meetings_blueprint.route('/meetings/<int:meeting_id>', methods=['PUT'])
@authenticate
def update_meeting(user_id, meeting_id):
    """Update meeting details."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404
    
    post_data = request.get_json()
    
    try:
        # Update allowed fields
        if 'meeting_date' in post_data:
            meeting.meeting_date = datetime.datetime.strptime(post_data['meeting_date'], '%Y-%m-%d').date()
        if 'meeting_time' in post_data:
            meeting.meeting_time = datetime.datetime.strptime(post_data['meeting_time'], '%H:%M').time()
        if 'meeting_type' in post_data:
            meeting.meeting_type = post_data['meeting_type']
        if 'status' in post_data:
            meeting.status = post_data['status']
        if 'location' in post_data:
            meeting.location = post_data['location']
        if 'latitude' in post_data:
            meeting.latitude = post_data['latitude']
        if 'longitude' in post_data:
            meeting.longitude = post_data['longitude']
        if 'agenda' in post_data:
            meeting.agenda = post_data['agenda']
        if 'minutes' in post_data:
            meeting.minutes = post_data['minutes']
        if 'decisions_made' in post_data:
            meeting.decisions_made = post_data['decisions_made']
        if 'action_items' in post_data:
            meeting.action_items = post_data['action_items']
        if 'chairperson_id' in post_data:
            meeting.chairperson_id = post_data['chairperson_id']
        if 'secretary_id' in post_data:
            meeting.secretary_id = post_data['secretary_id']
        if 'treasurer_id' in post_data:
            meeting.treasurer_id = post_data['treasurer_id']
        
        meeting.updated_date = datetime.datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Meeting updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>', methods=['DELETE'])
@authenticate
def delete_meeting(user_id, meeting_id):
    """Delete a meeting and all associated records (cascading delete)."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    try:
        # Delete all associated records manually to ensure data integrity
        # 1. Delete attendance records
        MeetingAttendance.query.filter_by(meeting_id=meeting_id).delete()

        # 2. Delete savings transactions
        SavingTransaction.query.filter_by(meeting_id=meeting_id).delete()

        # 3. Delete fines
        MemberFine.query.filter_by(meeting_id=meeting_id).delete()

        # 4. Delete loan repayments
        LoanRepayment.query.filter_by(meeting_id=meeting_id).delete()

        # 5. Delete training attendance records first
        trainings = TrainingRecord.query.filter_by(meeting_id=meeting_id).all()
        for training in trainings:
            TrainingAttendance.query.filter_by(training_id=training.id).delete()

        # 6. Delete training records
        TrainingRecord.query.filter_by(meeting_id=meeting_id).delete()

        # 7. Delete member votes first
        votings = VotingRecord.query.filter_by(meeting_id=meeting_id).all()
        for voting in votings:
            MemberVote.query.filter_by(voting_record_id=voting.id).delete()

        # 8. Delete voting records
        VotingRecord.query.filter_by(meeting_id=meeting_id).delete()

        # 9. Delete meeting summary
        MeetingSummary.query.filter_by(meeting_id=meeting_id).delete()

        # 10. Finally delete the meeting itself
        db.session.delete(meeting)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Meeting and all associated records deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/start', methods=['POST'])
@authenticate
def start_meeting(user_id, meeting_id):
    """Start a meeting (change status to IN_PROGRESS)."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status != 'SCHEDULED':
        return jsonify({'status': 'error', 'message': f'Cannot start meeting with status {meeting.status}'}), 400

    try:
        meeting.status = 'IN_PROGRESS'
        meeting.updated_date = datetime.datetime.utcnow()
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Meeting started successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/complete', methods=['POST'])
@authenticate
def complete_meeting(user_id, meeting_id):
    """Complete a meeting and generate summary."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status not in ['IN_PROGRESS', 'SCHEDULED']:
        return jsonify({'status': 'error', 'message': f'Cannot complete meeting with status {meeting.status}'}), 400

    try:
        # Calculate attendance
        attendance_records = MeetingAttendance.query.filter_by(meeting_id=meeting_id).all()
        members_present = sum(1 for a in attendance_records if a.is_present)
        members_absent = len(attendance_records) - members_present
        attendance_rate = (members_present / len(attendance_records) * 100) if attendance_records else 0

        # Calculate savings
        savings_transactions = SavingTransaction.query.filter_by(meeting_id=meeting_id).all()
        total_deposits = sum(float(s.amount) for s in savings_transactions if s.transaction_type == 'DEPOSIT')
        total_withdrawals = sum(float(s.amount) for s in savings_transactions if s.transaction_type == 'WITHDRAWAL')
        net_savings = total_deposits - total_withdrawals

        # Calculate fines
        fines = MemberFine.query.filter_by(meeting_id=meeting_id).all()
        total_fines_issued = sum(float(f.amount) for f in fines)
        total_fines_paid = sum(float(f.paid_amount or 0) for f in fines)
        outstanding_fines = total_fines_issued - total_fines_paid

        # Calculate loan repayments
        repayments = LoanRepayment.query.filter_by(meeting_id=meeting_id).all()
        total_loan_repayments = sum(float(r.repayment_amount) for r in repayments)
        loan_repayments_count = len(repayments)

        # Calculate training stats
        trainings = TrainingRecord.query.filter_by(meeting_id=meeting_id).all()
        trainings_held = len(trainings)
        training_attendance_count = sum(t.total_attendees for t in trainings)
        training_participation_rate = (training_attendance_count / (trainings_held * meeting.total_members) * 100) if trainings_held > 0 and meeting.total_members > 0 else 0

        # Calculate voting stats
        votings = VotingRecord.query.filter_by(meeting_id=meeting_id).all()
        voting_sessions_held = len(votings)
        votes_cast_count = sum(v.yes_count + v.no_count + v.abstain_count for v in votings)
        voting_participation_rate = (votes_cast_count / (voting_sessions_held * meeting.total_members) * 100) if voting_sessions_held > 0 and meeting.total_members > 0 else 0

        # Calculate net cash flow
        net_cash_flow = total_deposits + total_loan_repayments + total_fines_paid - total_withdrawals

        # Update meeting
        meeting.status = 'COMPLETED'
        meeting.members_present = members_present
        meeting.attendance_count = members_present
        meeting.total_savings_collected = total_deposits
        meeting.total_fines_collected = total_fines_paid
        meeting.total_loan_repayments = total_loan_repayments
        meeting.updated_date = datetime.datetime.utcnow()

        # Check if quorum met (default 66.67%)
        group_settings = GroupSettings.query.filter_by(group_id=meeting.group_id).first()
        quorum_percentage = float(group_settings.quorum_percentage) if group_settings and group_settings.quorum_percentage else 66.67
        meeting.quorum_met = attendance_rate >= quorum_percentage

        # Create or update meeting summary
        summary = MeetingSummary.query.filter_by(meeting_id=meeting_id).first()
        if not summary:
            summary = MeetingSummary(meeting_id=meeting_id)
            db.session.add(summary)

        summary.total_members = meeting.total_members
        summary.members_present = members_present
        summary.members_absent = members_absent
        summary.attendance_rate = attendance_rate
        summary.total_deposits = total_deposits
        summary.total_withdrawals = total_withdrawals
        summary.net_savings = net_savings
        summary.total_fines_issued = total_fines_issued
        summary.total_fines_paid = total_fines_paid
        summary.outstanding_fines = outstanding_fines
        summary.total_loan_repayments = total_loan_repayments
        summary.loan_repayments_count = loan_repayments_count
        summary.trainings_held = trainings_held
        summary.training_attendance_count = training_attendance_count
        summary.training_participation_rate = training_participation_rate
        summary.voting_sessions_held = voting_sessions_held
        summary.votes_cast_count = votes_cast_count
        summary.voting_participation_rate = voting_participation_rate
        summary.net_cash_flow = net_cash_flow
        summary.updated_date = datetime.datetime.utcnow()

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Meeting completed successfully',
            'summary': {
                'attendance_rate': float(attendance_rate),
                'total_deposits': float(total_deposits),
                'total_withdrawals': float(total_withdrawals),
                'net_savings': float(net_savings),
                'total_fines_collected': float(total_fines_paid),
                'total_loan_repayments': float(total_loan_repayments),
                'trainings_held': trainings_held,
                'voting_sessions_held': voting_sessions_held,
                'net_cash_flow': float(net_cash_flow),
                'quorum_met': meeting.quorum_met
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/attendance', methods=['POST'])
@authenticate
def record_attendance(user_id, meeting_id):
    """Record attendance for a meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    post_data = request.get_json()
    attendance_records = post_data.get('attendance', [])

    if not attendance_records:
        return jsonify({'status': 'error', 'message': 'No attendance records provided'}), 400

    try:
        for record in attendance_records:
            member_id = record.get('member_id')
            is_present = record.get('is_present', False)
            arrival_time = record.get('arrival_time')
            excuse_reason = record.get('excuse_reason')

            # Check if attendance already exists
            attendance = MeetingAttendance.query.filter_by(
                meeting_id=meeting_id,
                member_id=member_id
            ).first()

            if attendance:
                # Update existing
                attendance.is_present = is_present
                if arrival_time:
                    attendance.arrival_time = datetime.datetime.strptime(arrival_time, '%H:%M').time()
                attendance.excuse_reason = excuse_reason
            else:
                # Create new
                attendance = MeetingAttendance(
                    meeting_id=meeting_id,
                    group_id=meeting.group_id,
                    member_id=member_id,
                    meeting_date=meeting.meeting_date,
                    meeting_number=meeting.meeting_number,
                    is_present=is_present,
                    arrival_time=datetime.datetime.strptime(arrival_time, '%H:%M').time() if arrival_time else None,
                    excuse_reason=excuse_reason
                )
                db.session.add(attendance)

        db.session.commit()

        # Calculate attendance stats
        all_attendance = MeetingAttendance.query.filter_by(meeting_id=meeting_id).all()
        members_present = sum(1 for a in all_attendance if a.is_present)

        return jsonify({
            'status': 'success',
            'message': 'Attendance recorded successfully',
            'stats': {
                'total_members': len(all_attendance),
                'members_present': members_present,
                'attendance_rate': float(members_present / len(all_attendance) * 100) if all_attendance else 0
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/savings', methods=['POST'])
@authenticate
def record_savings_transaction(user_id, meeting_id):
    """Record a savings transaction during a meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status != 'IN_PROGRESS':
        return jsonify({'status': 'error', 'message': 'Meeting must be in progress to record transactions'}), 400

    post_data = request.get_json()
    member_id = post_data.get('member_id')
    saving_type_id = post_data.get('saving_type_id')
    transaction_type = post_data.get('transaction_type')  # 'DEPOSIT' or 'WITHDRAWAL'
    amount = post_data.get('amount')
    description = post_data.get('description', '')

    if not all([member_id, saving_type_id, transaction_type, amount]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        # Verify member belongs to the group
        member = GroupMember.query.filter_by(id=member_id, group_id=meeting.group_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found in this group'}), 404

        # Get or create member_saving record
        member_saving = MemberSaving.query.filter_by(
            member_id=member_id,
            saving_type_id=saving_type_id
        ).first()

        if not member_saving:
            # Create new member_saving record
            member_saving = MemberSaving(
                member_id=member_id,
                saving_type_id=saving_type_id,
                current_balance=0.00,
                total_deposits=0.00,
                total_withdrawals=0.00
            )
            db.session.add(member_saving)
            db.session.flush()  # Get the ID

        # Create savings transaction
        transaction = SavingTransaction(
            member_saving_id=member_saving.id,
            amount=amount,
            transaction_type=transaction_type,
            transaction_date=meeting.meeting_date,
            description=description,
            meeting_id=meeting_id,
            verification_status='VERIFIED'
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Savings transaction recorded successfully',
            'data': {
                'transaction_id': transaction.id,
                'member_id': member_id,
                'amount': float(amount),
                'transaction_type': transaction_type
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/fines', methods=['POST'])
@authenticate
def record_fine(user_id, meeting_id):
    """Record a fine during a meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status != 'IN_PROGRESS':
        return jsonify({'status': 'error', 'message': 'Meeting must be in progress to record fines'}), 400

    post_data = request.get_json()
    member_id = post_data.get('member_id')
    fine_type = post_data.get('fine_type')
    amount = post_data.get('amount')
    reason = post_data.get('reason')

    if not all([member_id, fine_type, amount]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        # Verify member belongs to the group
        member = GroupMember.query.filter_by(id=member_id, group_id=meeting.group_id).first()
        if not member:
            return jsonify({'status': 'error', 'message': 'Member not found in this group'}), 404

        # Create fine record
        fine = MemberFine(
            member_id=member_id,
            fine_type=fine_type,
            amount=amount,
            reason=reason or '',
            meeting_id=meeting_id,
            fine_date=meeting.meeting_date,
            is_paid=False,
            verification_status='VERIFIED',
            imposed_by=user_id
        )

        db.session.add(fine)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Fine recorded successfully',
            'data': {
                'fine_id': fine.id,
                'member_id': member_id,
                'amount': float(amount),
                'fine_type': fine_type
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/loan-repayments', methods=['POST'])
@authenticate
def record_loan_repayment(user_id, meeting_id):
    """Record a loan repayment during a meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status != 'IN_PROGRESS':
        return jsonify({'status': 'error', 'message': 'Meeting must be in progress to record repayments'}), 400

    post_data = request.get_json()
    loan_id = post_data.get('loan_id')
    repayment_amount = post_data.get('repayment_amount')
    principal_amount = post_data.get('principal_amount')
    interest_amount = post_data.get('interest_amount')

    if not all([loan_id, repayment_amount, principal_amount, interest_amount]):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    try:
        # Verify loan exists and belongs to the group
        loan = GroupLoan.query.filter_by(id=loan_id, group_id=meeting.group_id).first()
        if not loan:
            return jsonify({'status': 'error', 'message': 'Loan not found in this group'}), 404

        # Calculate new outstanding balance
        outstanding_balance = float(loan.outstanding_balance or loan.loan_amount) - float(repayment_amount)

        # Create repayment record
        repayment = LoanRepayment(
            loan_id=loan_id,
            meeting_id=meeting_id,
            repayment_amount=repayment_amount,
            principal_amount=principal_amount,
            interest_amount=interest_amount,
            outstanding_balance=outstanding_balance,
            repayment_date=meeting.meeting_date
        )

        # Update loan outstanding balance
        loan.outstanding_balance = outstanding_balance
        if outstanding_balance <= 0:
            loan.status = 'PAID'

        db.session.add(repayment)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Loan repayment recorded successfully',
            'data': {
                'repayment_id': repayment.id,
                'loan_id': loan_id,
                'repayment_amount': float(repayment_amount),
                'outstanding_balance': float(outstanding_balance)
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/trainings', methods=['POST'])
@authenticate
def create_training_session(user_id, meeting_id):
    """Create a training session during a meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status != 'IN_PROGRESS':
        return jsonify({'status': 'error', 'message': 'Meeting must be in progress to create training sessions'}), 400

    post_data = request.get_json()
    training_topic = post_data.get('training_topic')
    training_description = post_data.get('training_description')
    trainer_name = post_data.get('trainer_name')
    duration_minutes = post_data.get('duration_minutes')

    if not training_topic:
        return jsonify({'status': 'error', 'message': 'Training topic is required'}), 400

    try:
        # Create training record
        training = TrainingRecord(
            meeting_id=meeting_id,
            training_topic=training_topic,
            training_description=training_description,
            trainer_name=trainer_name,
            duration_minutes=duration_minutes,
            total_attendees=0
        )

        db.session.add(training)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Training session created successfully',
            'data': {
                'training_id': training.id,
                'training_topic': training_topic,
                'meeting_id': meeting_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/trainings/<int:training_id>/attendance', methods=['POST'])
@authenticate
def record_training_attendance(user_id, training_id):
    """Record member attendance for a training session."""
    training = TrainingRecord.query.get(training_id)
    if not training:
        return jsonify({'status': 'error', 'message': 'Training session not found'}), 404

    post_data = request.get_json()
    attendance_records = post_data.get('attendance', [])

    if not attendance_records:
        return jsonify({'status': 'error', 'message': 'No attendance records provided'}), 400

    try:
        total_attended = 0
        for record in attendance_records:
            member_id = record.get('member_id')
            attended = record.get('attended', False)

            # Check if attendance already exists
            attendance = TrainingAttendance.query.filter_by(
                training_id=training_id,
                member_id=member_id
            ).first()

            if attendance:
                # Update existing
                attendance.attended = attended
            else:
                # Create new
                attendance = TrainingAttendance(
                    training_id=training_id,
                    member_id=member_id,
                    attended=attended
                )
                db.session.add(attendance)

            if attended:
                total_attended += 1

        # Update total attendees count
        training.total_attendees = total_attended

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Training attendance recorded successfully',
            'data': {
                'training_id': training_id,
                'total_attended': total_attended,
                'total_members': len(attendance_records)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/meetings/<int:meeting_id>/votings', methods=['POST'])
@authenticate
def create_voting_session(user_id, meeting_id):
    """Create a voting session during a meeting."""
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        return jsonify({'status': 'error', 'message': 'Meeting not found'}), 404

    if meeting.status != 'IN_PROGRESS':
        return jsonify({'status': 'error', 'message': 'Meeting must be in progress to create voting sessions'}), 400

    post_data = request.get_json()
    vote_topic = post_data.get('vote_topic')
    vote_description = post_data.get('vote_description')
    vote_type = post_data.get('vote_type', 'SIMPLE_MAJORITY')

    if not vote_topic:
        return jsonify({'status': 'error', 'message': 'Vote topic is required'}), 400

    try:
        # Create voting record
        voting = VotingRecord(
            meeting_id=meeting_id,
            vote_topic=vote_topic,
            vote_description=vote_description,
            vote_type=vote_type,
            yes_count=0,
            no_count=0,
            abstain_count=0,
            absent_count=0
        )

        db.session.add(voting)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Voting session created successfully',
            'data': {
                'voting_id': voting.id,
                'vote_topic': vote_topic,
                'meeting_id': meeting_id
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/votings/<int:voting_id>/votes', methods=['POST'])
@authenticate
def record_member_votes(user_id, voting_id):
    """Record member votes for a voting session."""
    voting = VotingRecord.query.get(voting_id)
    if not voting:
        return jsonify({'status': 'error', 'message': 'Voting session not found'}), 404

    post_data = request.get_json()
    vote_records = post_data.get('votes', [])

    if not vote_records:
        return jsonify({'status': 'error', 'message': 'No vote records provided'}), 400

    try:
        yes_count = 0
        no_count = 0
        abstain_count = 0
        absent_count = 0

        for record in vote_records:
            member_id = record.get('member_id')
            vote_cast = record.get('vote_cast')  # 'YES', 'NO', 'ABSTAIN', 'ABSENT'

            if vote_cast not in ['YES', 'NO', 'ABSTAIN', 'ABSENT']:
                continue

            # Check if vote already exists
            vote = MemberVote.query.filter_by(
                voting_record_id=voting_id,
                member_id=member_id
            ).first()

            if vote:
                # Update existing
                vote.vote_cast = vote_cast
            else:
                # Create new
                vote = MemberVote(
                    voting_record_id=voting_id,
                    member_id=member_id,
                    vote_cast=vote_cast
                )
                db.session.add(vote)

            # Count votes
            if vote_cast == 'YES':
                yes_count += 1
            elif vote_cast == 'NO':
                no_count += 1
            elif vote_cast == 'ABSTAIN':
                abstain_count += 1
            elif vote_cast == 'ABSENT':
                absent_count += 1

        # Update vote counts
        voting.yes_count = yes_count
        voting.no_count = no_count
        voting.abstain_count = abstain_count
        voting.absent_count = absent_count

        # Determine result based on vote type
        if voting.vote_type == 'SIMPLE_MAJORITY':
            if yes_count > no_count:
                voting.result = 'PASSED'
            elif no_count > yes_count:
                voting.result = 'FAILED'
            else:
                voting.result = 'TIE'
        elif voting.vote_type == 'TWO_THIRDS_MAJORITY':
            total_votes = yes_count + no_count + abstain_count
            if total_votes > 0 and (yes_count / total_votes) >= 0.67:
                voting.result = 'PASSED'
            else:
                voting.result = 'FAILED'
        else:
            voting.result = 'PENDING'

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Votes recorded successfully',
            'data': {
                'voting_id': voting_id,
                'yes_count': yes_count,
                'no_count': no_count,
                'abstain_count': abstain_count,
                'absent_count': absent_count,
                'result': voting.result
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


# ==================== EDIT TRANSACTION ENDPOINTS ====================

@meetings_blueprint.route('/savings-transactions/<int:transaction_id>', methods=['PUT'])
@authenticate
def update_savings_transaction(user_id, transaction_id):
    """Update a savings transaction."""
    transaction = SavingTransaction.query.get(transaction_id)
    if not transaction:
        return jsonify({'status': 'error', 'message': 'Transaction not found'}), 404

    data = request.get_json()

    try:
        # Store old amount for balance adjustment
        old_amount = float(transaction.amount)

        # Update transaction fields
        if 'amount' in data:
            transaction.amount = data['amount']
        if 'transaction_type' in data:
            transaction.transaction_type = data['transaction_type']
        if 'description' in data:
            transaction.description = data['description']
        if 'notes' in data:
            transaction.notes = data['notes']
        if 'verification_status' in data:
            transaction.verification_status = data['verification_status']

        # Update member_saving balance if amount changed
        if 'amount' in data and old_amount != float(data['amount']):
            member_saving = MemberSaving.query.get(transaction.member_saving_id)
            if member_saving:
                amount_diff = float(data['amount']) - old_amount
                if transaction.transaction_type == 'DEPOSIT':
                    member_saving.current_balance += amount_diff
                    member_saving.total_deposits += amount_diff
                elif transaction.transaction_type == 'WITHDRAWAL':
                    member_saving.current_balance -= amount_diff
                    member_saving.total_withdrawals += amount_diff

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Transaction updated successfully',
            'data': {
                'id': transaction.id,
                'amount': float(transaction.amount),
                'transaction_type': transaction.transaction_type,
                'description': transaction.description,
                'notes': transaction.notes
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/fines/<int:fine_id>', methods=['PUT'])
@authenticate
def update_fine(user_id, fine_id):
    """Update a fine record."""
    fine = MemberFine.query.get(fine_id)
    if not fine:
        return jsonify({'status': 'error', 'message': 'Fine not found'}), 404

    data = request.get_json()

    try:
        if 'fine_type' in data:
            fine.fine_type = data['fine_type']
        if 'reason' in data:
            fine.reason = data['reason']
        if 'amount' in data:
            fine.amount = data['amount']
        if 'paid_amount' in data:
            fine.paid_amount = data['paid_amount']
        if 'is_paid' in data:
            fine.is_paid = data['is_paid']
        if 'notes' in data:
            fine.notes = data['notes']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Fine updated successfully',
            'data': {
                'id': fine.id,
                'fine_type': fine.fine_type,
                'reason': fine.reason,
                'amount': float(fine.amount),
                'paid_amount': float(fine.paid_amount or 0),
                'is_paid': fine.is_paid,
                'notes': fine.notes
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/loan-repayments/<int:repayment_id>', methods=['PUT'])
@authenticate
def update_loan_repayment(user_id, repayment_id):
    """Update a loan repayment record."""
    repayment = LoanRepayment.query.get(repayment_id)
    if not repayment:
        return jsonify({'status': 'error', 'message': 'Repayment not found'}), 404

    data = request.get_json()

    try:
        if 'repayment_amount' in data:
            repayment.repayment_amount = data['repayment_amount']
        if 'principal_amount' in data:
            repayment.principal_amount = data['principal_amount']
        if 'interest_amount' in data:
            repayment.interest_amount = data['interest_amount']
        if 'outstanding_balance' in data:
            repayment.outstanding_balance = data['outstanding_balance']
        if 'payment_method' in data:
            repayment.payment_method = data['payment_method']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Loan repayment updated successfully',
            'data': {
                'id': repayment.id,
                'repayment_amount': float(repayment.repayment_amount),
                'principal_amount': float(repayment.principal_amount),
                'interest_amount': float(repayment.interest_amount),
                'outstanding_balance': float(repayment.outstanding_balance)
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/trainings/<int:training_id>', methods=['PUT'])
@authenticate
def update_training(user_id, training_id):
    """Update a training record."""
    training = TrainingRecord.query.get(training_id)
    if not training:
        return jsonify({'status': 'error', 'message': 'Training not found'}), 404

    data = request.get_json()

    try:
        if 'training_topic' in data:
            training.training_topic = data['training_topic']
        if 'training_description' in data:
            training.training_description = data['training_description']
        if 'trainer_name' in data:
            training.trainer_name = data['trainer_name']
        if 'trainer_type' in data:
            training.trainer_type = data['trainer_type']
        if 'duration_minutes' in data:
            training.duration_minutes = data['duration_minutes']
        if 'materials_provided' in data:
            training.materials_provided = data['materials_provided']
        if 'notes' in data:
            training.notes = data['notes']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Training updated successfully',
            'data': {
                'id': training.id,
                'training_topic': training.training_topic,
                'training_description': training.training_description,
                'trainer_name': training.trainer_name,
                'duration_minutes': training.duration_minutes,
                'notes': training.notes
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400


@meetings_blueprint.route('/votings/<int:voting_id>', methods=['PUT'])
@authenticate
def update_voting(user_id, voting_id):
    """Update a voting record."""
    voting = VotingRecord.query.get(voting_id)
    if not voting:
        return jsonify({'status': 'error', 'message': 'Voting not found'}), 404

    data = request.get_json()

    try:
        if 'vote_topic' in data:
            voting.vote_topic = data['vote_topic']
        if 'vote_description' in data:
            voting.vote_description = data['vote_description']
        if 'vote_type' in data:
            voting.vote_type = data['vote_type']
        if 'result' in data:
            voting.result = data['result']
        if 'notes' in data:
            voting.notes = data['notes']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Voting updated successfully',
            'data': {
                'id': voting.id,
                'vote_topic': voting.vote_topic,
                'vote_description': voting.vote_description,
                'vote_type': voting.vote_type,
                'result': voting.result,
                'notes': voting.notes
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 400
