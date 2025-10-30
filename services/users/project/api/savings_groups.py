"""Savings groups blueprint."""
from flask import Blueprint, request, jsonify
from sqlalchemy import exc, func
from project import db
from project.api.models import SavingsGroup, GroupMember, User
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
                'total_members': group.members_count,
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

