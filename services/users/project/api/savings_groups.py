"""Savings groups blueprint."""
from flask import Blueprint, request, jsonify
from sqlalchemy import exc, func
from project import db
from project.api.models import (
    SavingsGroup, GroupMember, User, MemberSaving, MemberFine,
    GroupLoan, Meeting, MeetingAttendance, TrainingRecord,
    TrainingAttendance, VotingRecord, MemberVote, SavingType
)
from functools import wraps


savings_groups_blueprint = Blueprint('savings_groups', __name__)


def authenticate(f):
    """Decorator to check authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'status': 'fail', 'message': 'Provide a valid auth token.'}), 401
        
        try:
            auth_token = auth_header.split(' ')[1]
            user_id = User.decode_token(auth_token)
            if isinstance(user_id, str):
                return jsonify({'status': 'fail', 'message': user_id}), 401
        except IndexError:
            return jsonify({'status': 'fail', 'message': 'Invalid token format.'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


@savings_groups_blueprint.route('', methods=['GET'])
@authenticate
def get_all_groups():
    """Get all savings groups."""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        groups = SavingsGroup.query.limit(limit).offset(offset).all()
        total = SavingsGroup.query.count()
        
        groups_list = []
        for group in groups:
            # Calculate actual member count
            actual_member_count = GroupMember.query.filter_by(group_id=group.id).count()

            groups_list.append({
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'status': group.status or group.state,
                'country': group.country,
                'region': group.region,
                'district': group.district,
                'parish': group.parish,
                'village': group.village,
                'meeting_location': group.meeting_location,
                'meeting_day': group.meeting_day,
                'meeting_frequency': group.meeting_frequency,
                'meeting_time': group.meeting_time.isoformat() if group.meeting_time else None,
                'formation_date': group.formation_date.isoformat() if group.formation_date else None,
                'currency': group.currency,
                'share_value': str(group.share_value or 0),
                'total_members': actual_member_count,
                'max_members': group.max_members,
                'total_savings': str(group.savings_balance or 0),
                'created_date': group.created_date.isoformat() if group.created_date else None
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'groups': groups_list,
                'count': len(groups_list),
                'total': total
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@savings_groups_blueprint.route('/<int:group_id>', methods=['GET'])
@authenticate
def get_single_group(group_id):
    """Get a single savings group with members."""
    try:
        group = SavingsGroup.query.filter_by(id=group_id).first()
        if not group:
            return jsonify({
                'status': 'fail',
                'message': 'Group not found.'
            }), 404
        
        # Get members
        members = GroupMember.query.filter_by(group_id=group_id).all()
        members_list = []
        for member in members:
            members_list.append({
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'email': member.email,
                'phone_number': member.phone_number,
                'role': member.role,
                'status': member.status,
                'share_balance': str(member.share_balance or 0),
                'total_contributions': str(member.total_contributions or 0),
                'attendance_percentage': float(member.attendance_percentage or 0),
                'is_eligible_for_loans': member.is_eligible_for_loans
            })
        
        # Calculate financial summary
        total_savings = db.session.query(func.sum(GroupMember.total_contributions)).filter_by(group_id=group_id).scalar() or 0
        avg_attendance = db.session.query(func.avg(GroupMember.attendance_percentage)).filter_by(group_id=group_id).scalar() or 0
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'status': group.status or group.state,
                'country': group.country,
                'region': group.region,
                'district': group.district,
                'parish': group.parish,
                'village': group.village,
                'meeting_location': group.meeting_location,
                'meeting_day': group.meeting_day,
                'meeting_frequency': group.meeting_frequency,
                'meeting_time': group.meeting_time.isoformat() if group.meeting_time else None,
                'formation_date': group.formation_date.isoformat() if group.formation_date else None,
                'currency': group.currency,
                'share_value': str(group.share_value or 0),
                'standard_fine_amount': str(group.standard_fine_amount or 0),
                'loan_interest_rate': str(group.loan_interest_rate or 0),
                'max_members': group.max_members,
                'saving_cycle_months': group.saving_cycle_months,
                'registration_authority': group.registration_authority,
                'certificate_number': group.certificate_number,
                'is_registered': group.is_registered,
                'members': members_list,
                'financial_summary': {
                    'total_savings': str(total_savings),
                    'total_loans': '0',
                    'total_fines': '0',
                    'average_attendance': float(avg_attendance)
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@savings_groups_blueprint.route('', methods=['POST'])
@authenticate
def create_group():
    """Create a new savings group."""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    
    if not post_data:
        return jsonify(response_object), 400
    
    name = post_data.get('name')
    if not name:
        response_object['message'] = 'Group name is required.'
        return jsonify(response_object), 400
    
    try:
        # Check if group exists
        group = SavingsGroup.query.filter_by(name=name).first()
        if group:
            response_object['message'] = 'Group with that name already exists.'
            return jsonify(response_object), 400
        
        # Create new group
        new_group = SavingsGroup(
            name=name,
            description=post_data.get('description'),
            country=post_data.get('country'),
            district=post_data.get('district'),
            parish=post_data.get('parish'),
            village=post_data.get('village'),
            created_by=1  # TODO: Get from auth token
        )
        new_group.state = 'ACTIVE'
        new_group.status = 'ACTIVE'
        
        db.session.add(new_group)
        db.session.commit()
        
        response_object['status'] = 'success'
        response_object['message'] = 'Group created successfully.'
        response_object['data'] = {
            'id': new_group.id,
            'name': new_group.name
        }
        return jsonify(response_object), 201
        
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object['message'] = str(e)
        return jsonify(response_object), 400


@savings_groups_blueprint.route('/<int:group_id>/members', methods=['GET'])
@authenticate
def get_group_members(group_id):
    """Get all members of a group."""
    try:
        members = GroupMember.query.filter_by(group_id=group_id).all()
        members_list = []
        for member in members:
            members_list.append({
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'email': member.email,
                'phone_number': member.phone_number,
                'role': member.role,
                'status': member.status,
                'share_balance': str(member.share_balance or 0),
                'total_contributions': str(member.total_contributions or 0),
                'attendance_percentage': float(member.attendance_percentage or 0),
                'is_eligible_for_loans': member.is_eligible_for_loans
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'members': members_list,
                'count': len(members_list)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@savings_groups_blueprint.route('/<int:group_id>/members', methods=['POST'])
@authenticate
def add_group_member(user_id, group_id):
    """Add a new member to a group."""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }

    if not post_data:
        return jsonify(response_object), 400

    first_name = post_data.get('first_name')
    last_name = post_data.get('last_name')

    if not first_name or not last_name:
        response_object['message'] = 'First name and last name are required.'
        return jsonify(response_object), 400

    try:
        # Verify group exists
        group = SavingsGroup.query.filter_by(id=group_id).first()
        if not group:
            response_object['message'] = 'Group not found.'
            return jsonify(response_object), 404

        # Check if group is at max capacity
        current_members = GroupMember.query.filter_by(group_id=group_id).count()
        if group.max_members and current_members >= group.max_members:
            response_object['message'] = f'Group has reached maximum capacity of {group.max_members} members.'
            return jsonify(response_object), 400

        # Create new member
        new_member = GroupMember(
            group_id=group_id,
            first_name=first_name,
            last_name=last_name,
            email=post_data.get('email'),
            phone_number=post_data.get('phone_number'),
            id_number=post_data.get('id_number'),
            date_of_birth=post_data.get('date_of_birth'),
            gender=post_data.get('gender'),
            occupation=post_data.get('occupation'),
            role=post_data.get('role', 'MEMBER'),
            status=post_data.get('status', 'ACTIVE'),
            is_active=True
        )

        # Use raw SQL to set address field (not in ORM model)
        db.session.add(new_member)
        db.session.flush()  # Get the ID

        if post_data.get('address'):
            db.session.execute(
                db.text("UPDATE group_members SET address = :address WHERE id = :id"),
                {'address': post_data.get('address'), 'id': new_member.id}
            )

        # Update group members_count
        db.session.execute(
            db.text("UPDATE savings_groups SET members_count = members_count + 1 WHERE id = :group_id"),
            {'group_id': group_id}
        )

        db.session.commit()

        response_object['status'] = 'success'
        response_object['message'] = 'Member added successfully.'
        response_object['data'] = {
            'id': new_member.id,
            'first_name': new_member.first_name,
            'last_name': new_member.last_name,
            'role': new_member.role
        }
        return jsonify(response_object), 201

    except exc.IntegrityError as e:
        db.session.rollback()
        response_object['message'] = 'Member with this email or phone number already exists in this group.'
        return jsonify(response_object), 400
    except Exception as e:
        db.session.rollback()
        response_object['message'] = str(e)
        return jsonify(response_object), 500


@savings_groups_blueprint.route('/<int:group_id>/dashboard', methods=['GET'])
@authenticate
def get_group_dashboard(group_id):
    """Get aggregated dashboard data for a group."""
    try:
        # Verify group exists
        group = SavingsGroup.query.filter_by(id=group_id).first()
        if not group:
            return jsonify({'status': 'error', 'message': 'Group not found'}), 404

        # Get all active saving types (saving types are global, not per-group)
        saving_types = SavingType.query.filter_by(is_active=True).all()

        # Calculate total savings by fund type using aggregated data from member_savings
        savings_by_fund = {}
        total_savings = 0

        for saving_type in saving_types:
            # Sum up all member savings for this saving type in this group
            member_savings_records = db.session.query(
                func.sum(MemberSaving.total_deposits).label('deposits'),
                func.sum(MemberSaving.total_withdrawals).label('withdrawals'),
                func.sum(MemberSaving.current_balance).label('balance')
            ).join(
                GroupMember, MemberSaving.member_id == GroupMember.id
            ).filter(
                GroupMember.group_id == group_id,
                MemberSaving.saving_type_id == saving_type.id,
                MemberSaving.is_active == True
            ).first()

            deposits = float(member_savings_records.deposits or 0)
            withdrawals = float(member_savings_records.withdrawals or 0)
            net_savings = float(member_savings_records.balance or 0)

            savings_by_fund[saving_type.name] = {
                'total': net_savings,
                'deposits': deposits,
                'withdrawals': withdrawals
            }
            total_savings += net_savings

        # Calculate total fines (join through GroupMember to filter by group)
        total_fines_issued = db.session.query(func.sum(MemberFine.amount)).join(
            GroupMember, MemberFine.member_id == GroupMember.id
        ).filter(
            GroupMember.group_id == group_id
        ).scalar() or 0

        total_fines_paid = db.session.query(func.sum(MemberFine.paid_amount)).join(
            GroupMember, MemberFine.member_id == GroupMember.id
        ).filter(
            GroupMember.group_id == group_id,
            MemberFine.is_paid == True
        ).scalar() or 0

        # Calculate loan statistics
        total_loans_disbursed = db.session.query(func.sum(GroupLoan.principal)).filter(
            GroupLoan.group_id == group_id,
            GroupLoan.status.in_(['ACTIVE', 'DISBURSED', 'COMPLETED'])
        ).scalar() or 0

        total_loans_outstanding = db.session.query(func.sum(GroupLoan.outstanding_balance)).filter(
            GroupLoan.group_id == group_id,
            GroupLoan.status == 'ACTIVE'
        ).scalar() or 0

        active_loans_count = GroupLoan.query.filter_by(
            group_id=group_id,
            status='ACTIVE'
        ).count()

        # Calculate meeting statistics
        total_meetings = Meeting.query.filter_by(group_id=group_id).count()
        completed_meetings = Meeting.query.filter_by(
            group_id=group_id,
            status='COMPLETED'
        ).count()

        # Calculate average attendance rate across all completed meetings
        attendance_rates = []
        completed_meetings_list = Meeting.query.filter_by(
            group_id=group_id,
            status='COMPLETED'
        ).all()

        for meeting in completed_meetings_list:
            total_members = GroupMember.query.filter_by(group_id=group_id).count()
            present_count = MeetingAttendance.query.filter_by(
                meeting_id=meeting.id,
                is_present=True
            ).count()
            if total_members > 0:
                attendance_rates.append((present_count / total_members) * 100)

        avg_attendance_rate = sum(attendance_rates) / len(attendance_rates) if attendance_rates else 0

        # Calculate training statistics
        total_trainings = TrainingRecord.query.join(Meeting).filter(
            Meeting.group_id == group_id
        ).count()

        total_training_attendances = db.session.query(func.count(TrainingAttendance.id)).join(
            TrainingRecord
        ).join(Meeting).filter(
            Meeting.group_id == group_id,
            TrainingAttendance.attended == True
        ).scalar() or 0

        # Calculate training participation rate
        total_members = GroupMember.query.filter_by(group_id=group_id).count()
        expected_training_attendances = total_trainings * total_members
        training_participation_rate = (total_training_attendances / expected_training_attendances * 100) if expected_training_attendances > 0 else 0

        # Calculate voting statistics
        total_voting_sessions = VotingRecord.query.join(Meeting).filter(
            Meeting.group_id == group_id
        ).count()

        total_votes_cast = db.session.query(func.count(MemberVote.id)).join(
            VotingRecord
        ).join(Meeting).filter(
            Meeting.group_id == group_id,
            MemberVote.vote_cast.in_(['YES', 'NO', 'ABSTAIN'])
        ).scalar() or 0

        # Calculate voting participation rate
        expected_votes = total_voting_sessions * total_members
        voting_participation_rate = (total_votes_cast / expected_votes * 100) if expected_votes > 0 else 0

        # Get group targets
        group_target = float(group.target_amount or 0)

        # Calculate sum of all member targets from member_savings (join through group_members)
        total_member_targets = db.session.query(func.sum(MemberSaving.target_amount)).join(
            GroupMember, MemberSaving.member_id == GroupMember.id
        ).filter(
            GroupMember.group_id == group_id,
            MemberSaving.is_active == True
        ).scalar() or 0

        # Calculate progress towards target
        target_progress = (total_savings / group_target * 100) if group_target > 0 else 0

        return jsonify({
            'status': 'success',
            'data': {
                'group_info': {
                    'id': group.id,
                    'name': group.name,
                    'currency': group.currency,
                    'total_members': total_members,
                    'formation_date': group.formation_date.isoformat() if group.formation_date else None
                },
                'financial_summary': {
                    'total_savings': total_savings,
                    'savings_by_fund': savings_by_fund,
                    'total_fines_issued': float(total_fines_issued),
                    'total_fines_paid': float(total_fines_paid),
                    'total_loans_disbursed': float(total_loans_disbursed),
                    'total_loans_outstanding': float(total_loans_outstanding),
                    'active_loans_count': active_loans_count
                },
                'targets': {
                    'group_target': group_target,
                    'total_member_targets': float(total_member_targets),
                    'current_savings': total_savings,
                    'progress_percentage': target_progress
                },
                'meeting_statistics': {
                    'total_meetings': total_meetings,
                    'completed_meetings': completed_meetings,
                    'average_attendance_rate': avg_attendance_rate
                },
                'participation_statistics': {
                    'total_trainings': total_trainings,
                    'training_participation_rate': training_participation_rate,
                    'total_voting_sessions': total_voting_sessions,
                    'voting_participation_rate': voting_participation_rate
                }
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
