"""Member Profile API blueprint."""
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import exc, func, text, or_
from project import db
from project.api.models import GroupMember, SavingsGroup, User
from datetime import datetime
from functools import wraps
import json
import jwt

member_profile_blueprint = Blueprint('member_profile', __name__)


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


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/profile', methods=['GET'])
@authenticate
def get_member_profile(user_id, group_id, member_id):
    """Get comprehensive member profile."""
    try:
        # Use raw SQL to get complete profile with all new fields
        query = text("""
            SELECT * FROM member_profile_complete
            WHERE id = :member_id AND group_id = :group_id
        """)
        
        result = db.session.execute(query, {'member_id': member_id, 'group_id': group_id})
        row = result.fetchone()
        
        if not row:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404
        
        # Convert row to dict
        profile = dict(row._mapping)
        
        # Convert date/datetime objects to strings
        for key, value in profile.items():
            if isinstance(value, datetime):
                profile[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):  # date objects
                profile[key] = value.isoformat()
        
        return jsonify({
            'status': 'success',
            'data': profile
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching member profile: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/profile', methods=['PUT'])
@authenticate
def update_member_profile(user_id, group_id, member_id):
    """Update member profile."""
    try:
        data = request.get_json()

        # Verify member exists and belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404

        # Check permissions: user can update their own profile, or super admin can update any profile
        user = User.query.get(user_id)
        is_own_profile = (member.user_id == user_id)
        is_super_admin = (user and (user.is_super_admin or user.admin))
        is_group_admin = (member.role in ['ADMIN', 'CHAIRPERSON', 'SECRETARY', 'TREASURER'])

        if not (is_own_profile or is_super_admin or is_group_admin):
            return jsonify({
                'status': 'fail',
                'message': 'You do not have permission to update this profile.'
            }), 403

        # Update allowed fields
        allowed_fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'id_number',
            'date_of_birth', 'gender', 'occupation', 'address',
            'emergency_contact_name', 'emergency_contact_phone', 'notes',
            'profile_photo_url'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(member, field, data[field])
        
        # Update timestamp
        member.updated_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Member profile updated successfully.',
            'data': {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'email': member.email,
                'phone_number': member.phone_number
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error updating member profile: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/settings', methods=['GET'])
@authenticate
def get_member_settings(user_id, group_id, member_id):
    """Get member settings (membership details, permissions)."""
    try:
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404
        
        # Use raw SQL to get all fields including new ones
        query = text("""
            SELECT 
                id, group_id, status, role, joined_date, is_active,
                can_view_finances, can_apply_for_loans, can_vote,
                notification_preferences, exit_date, exit_reason,
                suspended_date, suspended_reason, suspended_by,
                is_eligible_for_loans, share_balance, total_contributions,
                attendance_percentage
            FROM group_members
            WHERE id = :member_id AND group_id = :group_id
        """)
        
        result = db.session.execute(query, {'member_id': member_id, 'group_id': group_id})
        row = result.fetchone()
        
        if not row:
            return jsonify({
                'status': 'fail',
                'message': 'Member settings not found.'
            }), 404
        
        settings = dict(row._mapping)
        
        # Convert date/datetime objects to strings
        for key, value in settings.items():
            if isinstance(value, datetime):
                settings[key] = value.isoformat()
            elif hasattr(value, 'isoformat'):
                settings[key] = value.isoformat()
        
        return jsonify({
            'status': 'success',
            'data': settings
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching member settings: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/settings', methods=['PUT'])
@authenticate
def update_member_settings(user_id, group_id, member_id):
    """Update member settings (membership details, permissions)."""
    try:
        data = request.get_json()
        
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404
        
        # Update membership fields
        if 'status' in data:
            old_status = member.status
            member.status = data['status']
            
            # Log status change
            if old_status != data['status']:
                if data['status'] == 'SUSPENDED':
                    member.suspended_date = datetime.utcnow()
                    member.suspended_by = user_id
                    if 'suspended_reason' in data:
                        member.suspended_reason = data['suspended_reason']
                elif data['status'] == 'INACTIVE':
                    member.exit_date = datetime.utcnow()
                    if 'exit_reason' in data:
                        member.exit_reason = data['exit_reason']
        
        if 'role' in data:
            member.role = data['role']
        
        if 'is_active' in data:
            member.is_active = data['is_active']
        
        # Update permission fields
        if 'can_view_finances' in data:
            member.can_view_finances = data['can_view_finances']
        
        if 'can_apply_for_loans' in data:
            member.can_apply_for_loans = data['can_apply_for_loans']
        
        if 'can_vote' in data:
            member.can_vote = data['can_vote']
        
        # Update notification preferences
        if 'notification_preferences' in data:
            # Use raw SQL to update JSONB field
            query = text("""
                UPDATE group_members 
                SET notification_preferences = :prefs::jsonb
                WHERE id = :member_id
            """)
            db.session.execute(query, {
                'prefs': json.dumps(data['notification_preferences']),
                'member_id': member_id
            })
        
        member.updated_date = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Member settings updated successfully.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error updating member settings: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/activity-log', methods=['GET'])
@authenticate
def get_member_activity_log(user_id, group_id, member_id):
    """Get member activity log."""
    try:
        # Verify member belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        activity_type = request.args.get('type', None)
        category = request.args.get('category', None)
        
        # Build query
        query = text("""
            SELECT 
                mal.*,
                u.username as performed_by_username
            FROM member_activity_log mal
            LEFT JOIN users u ON mal.performed_by = u.id
            WHERE mal.member_id = :member_id
            """ + (f" AND mal.activity_type = :activity_type" if activity_type else "") +
            (f" AND mal.activity_category = :category" if category else "") + """
            ORDER BY mal.activity_date DESC
            LIMIT :limit OFFSET :offset
        """)
        
        params = {
            'member_id': member_id,
            'limit': per_page,
            'offset': (page - 1) * per_page
        }
        
        if activity_type:
            params['activity_type'] = activity_type
        if category:
            params['category'] = category
        
        result = db.session.execute(query, params)
        rows = result.fetchall()
        
        activities = []
        for row in rows:
            activity = dict(row._mapping)
            # Convert datetime to string
            if isinstance(activity.get('activity_date'), datetime):
                activity['activity_date'] = activity['activity_date'].isoformat()
            activities.append(activity)
        
        # Get total count
        count_query = text("""
            SELECT COUNT(*) as total
            FROM member_activity_log
            WHERE member_id = :member_id
            """ + (f" AND activity_type = :activity_type" if activity_type else "") +
            (f" AND activity_category = :category" if category else ""))
        
        count_result = db.session.execute(count_query, {
            'member_id': member_id,
            'activity_type': activity_type if activity_type else None,
            'category': category if category else None
        })
        total = count_result.fetchone()[0]
        
        return jsonify({
            'status': 'success',
            'data': {
                'activities': activities,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching activity log: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/documents', methods=['GET'])
@authenticate
def get_member_documents(user_id, group_id, member_id):
    """Get member documents."""
    try:
        # Verify member belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404

        # Get documents
        query = text("""
            SELECT * FROM member_documents_detailed
            WHERE member_id = :member_id
            ORDER BY uploaded_date DESC
        """)

        result = db.session.execute(query, {'member_id': member_id})
        rows = result.fetchall()

        documents = []
        for row in rows:
            doc = dict(row._mapping)
            # Convert datetime to string
            for key, value in doc.items():
                if isinstance(value, datetime):
                    doc[key] = value.isoformat()
                elif hasattr(value, 'isoformat'):
                    doc[key] = value.isoformat()
            documents.append(doc)

        return jsonify({
            'status': 'success',
            'data': documents
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching documents: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/documents', methods=['POST'])
@authenticate
def add_member_document(user_id, group_id, member_id):
    """Add a document for a member."""
    try:
        data = request.get_json()

        # Verify member belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404

        # Validate required fields
        required_fields = ['document_type', 'document_name', 'file_name', 'file_url']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'fail',
                    'message': f'Missing required field: {field}'
                }), 400

        # Insert document
        query = text("""
            INSERT INTO member_documents (
                member_id, document_type, document_name, file_name, file_url,
                file_size, mime_type, uploaded_by, expiry_date, notes
            ) VALUES (
                :member_id, :document_type, :document_name, :file_name, :file_url,
                :file_size, :mime_type, :uploaded_by, :expiry_date, :notes
            ) RETURNING id
        """)

        result = db.session.execute(query, {
            'member_id': member_id,
            'document_type': data['document_type'],
            'document_name': data['document_name'],
            'file_name': data['file_name'],
            'file_url': data['file_url'],
            'file_size': data.get('file_size'),
            'mime_type': data.get('mime_type'),
            'uploaded_by': user_id,
            'expiry_date': data.get('expiry_date'),
            'notes': data.get('notes')
        })

        document_id = result.fetchone()[0]
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Document uploaded successfully.',
            'data': {'id': document_id}
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error uploading document: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/documents/<int:document_id>', methods=['DELETE'])
@authenticate
def delete_member_document(user_id, group_id, member_id, document_id):
    """Delete a member document."""
    try:
        # Verify member belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404

        # Delete document
        query = text("""
            DELETE FROM member_documents
            WHERE id = :document_id AND member_id = :member_id
            RETURNING id
        """)

        result = db.session.execute(query, {
            'document_id': document_id,
            'member_id': member_id
        })

        if result.rowcount == 0:
            return jsonify({
                'status': 'fail',
                'message': 'Document not found.'
            }), 404

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Document deleted successfully.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'Error deleting document: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members', methods=['GET'])
@authenticate
def get_group_members_enhanced(user_id, group_id):
    """Get group members with search, filter, and sort."""
    try:
        # Get query parameters
        search = request.args.get('search', '').strip()
        role = request.args.get('role', None)
        status = request.args.get('status', None)
        gender = request.args.get('gender', None)
        sort_by = request.args.get('sort', 'name')  # name, joined_date, contributions, attendance
        sort_order = request.args.get('order', 'asc')  # asc, desc
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        # Build WHERE clause
        where_clauses = ['group_id = :group_id']
        params = {'group_id': group_id}

        if search:
            where_clauses.append("(first_name ILIKE :search OR last_name ILIKE :search OR phone_number ILIKE :search OR email ILIKE :search)")
            params['search'] = f'%{search}%'

        if role:
            where_clauses.append('role = :role')
            params['role'] = role

        if status:
            where_clauses.append('status = :status')
            params['status'] = status

        if gender:
            where_clauses.append('gender = :gender')
            params['gender'] = gender

        where_clause = ' AND '.join(where_clauses)

        # Build ORDER BY clause
        order_map = {
            'name': 'first_name, last_name',
            'joined_date': 'joined_date',
            'contributions': 'total_contributions',
            'attendance': 'attendance_percentage'
        }
        order_by = order_map.get(sort_by, 'first_name, last_name')
        order_direction = 'DESC' if sort_order.lower() == 'desc' else 'ASC'

        # Get members
        query = text(f"""
            SELECT
                id, first_name, last_name, email, phone_number, gender,
                role, status, joined_date, is_active, occupation,
                share_balance, total_contributions, attendance_percentage,
                is_eligible_for_loans, profile_photo_url
            FROM group_members
            WHERE {where_clause}
            ORDER BY {order_by} {order_direction}
            LIMIT :limit OFFSET :offset
        """)

        params['limit'] = per_page
        params['offset'] = (page - 1) * per_page

        result = db.session.execute(query, params)
        rows = result.fetchall()

        members = []
        for row in rows:
            member = dict(row._mapping)
            # Convert date/datetime to string
            for key, value in member.items():
                if isinstance(value, datetime):
                    member[key] = value.isoformat()
                elif hasattr(value, 'isoformat'):
                    member[key] = value.isoformat()
            members.append(member)

        # Get total count
        count_query = text(f"""
            SELECT COUNT(*) as total
            FROM group_members
            WHERE {where_clause}
        """)

        count_result = db.session.execute(count_query, {k: v for k, v in params.items() if k not in ['limit', 'offset']})
        total = count_result.fetchone()[0]

        return jsonify({
            'status': 'success',
            'data': {
                'members': members,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'pages': (total + per_page - 1) // per_page
                },
                'filters': {
                    'search': search,
                    'role': role,
                    'status': status,
                    'gender': gender,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching members: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/financial', methods=['GET'])
@authenticate
def get_member_financial(user_id, group_id, member_id):
    """Get member financial data (savings, loans, fines)."""
    try:
        # Verify member belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404

        # Get savings by fund type
        savings_query = text("""
            SELECT
                st.name as fund_name,
                st.description as fund_description,
                COALESCE(SUM(CASE WHEN sav_t.transaction_type = 'DEPOSIT' THEN sav_t.amount ELSE 0 END), 0) as total_deposits,
                COALESCE(SUM(CASE WHEN sav_t.transaction_type = 'WITHDRAWAL' THEN sav_t.amount ELSE 0 END), 0) as total_withdrawals,
                COALESCE(SUM(CASE WHEN sav_t.transaction_type = 'DEPOSIT' THEN sav_t.amount ELSE -sav_t.amount END), 0) as balance
            FROM member_savings ms
            LEFT JOIN saving_types st ON ms.saving_type_id = st.id
            LEFT JOIN saving_transactions sav_t ON sav_t.member_saving_id = ms.id
            WHERE ms.member_id = :member_id
            GROUP BY st.id, st.name, st.description
            ORDER BY st.name
        """)

        savings_result = db.session.execute(savings_query, {'member_id': member_id})
        savings_by_fund = []
        total_savings = 0

        for row in savings_result:
            fund_data = dict(row._mapping)
            fund_data['total_deposits'] = float(fund_data['total_deposits'])
            fund_data['total_withdrawals'] = float(fund_data['total_withdrawals'])
            fund_data['balance'] = float(fund_data['balance'])
            total_savings += fund_data['balance']
            savings_by_fund.append(fund_data)

        # Get loans
        loans_query = text("""
            SELECT
                id,
                principal,
                interest_rate,
                term_months,
                monthly_payment,
                status,
                application_date,
                approval_date,
                disbursement_date,
                maturity_date,
                total_amount_due,
                amount_paid,
                outstanding_balance,
                payments_made,
                payments_missed,
                days_overdue
            FROM group_loans
            WHERE member_id = :member_id
            ORDER BY application_date DESC
        """)

        loans_result = db.session.execute(loans_query, {'member_id': member_id})
        loans = []

        for row in loans_result:
            loan_data = dict(row._mapping)
            # Convert dates to strings
            for key, value in loan_data.items():
                if isinstance(value, datetime):
                    loan_data[key] = value.isoformat()
                elif hasattr(value, 'isoformat'):
                    loan_data[key] = value.isoformat()
                elif isinstance(value, (int, float)):
                    loan_data[key] = float(value) if '.' in str(value) or isinstance(value, float) else value
            loans.append(loan_data)

        # Get fines
        fines_query = text("""
            SELECT
                id,
                fine_type,
                reason,
                amount,
                is_paid,
                paid_amount,
                paid_date,
                created_date
            FROM member_fines
            WHERE member_id = :member_id
            ORDER BY created_date DESC
        """)

        fines_result = db.session.execute(fines_query, {'member_id': member_id})
        fines = []
        total_fines = 0
        paid_fines = 0

        for row in fines_result:
            fine_data = dict(row._mapping)
            # Convert dates to strings
            for key, value in fine_data.items():
                if isinstance(value, datetime):
                    fine_data[key] = value.isoformat()
                elif hasattr(value, 'isoformat'):
                    fine_data[key] = value.isoformat()

            fine_data['amount'] = float(fine_data['amount'])
            fine_data['paid_amount'] = float(fine_data.get('paid_amount') or 0)
            total_fines += fine_data['amount']
            paid_fines += fine_data['paid_amount']
            fines.append(fine_data)

        return jsonify({
            'status': 'success',
            'data': {
                'savings': {
                    'total': total_savings,
                    'by_fund': savings_by_fund
                },
                'loans': loans,
                'fines': {
                    'total': total_fines,
                    'paid': paid_fines,
                    'outstanding': total_fines - paid_fines,
                    'items': fines
                }
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching financial data: {str(e)}'
        }), 500


@member_profile_blueprint.route('/groups/<int:group_id>/members/<int:member_id>/attendance', methods=['GET'])
@authenticate
def get_member_attendance(user_id, group_id, member_id):
    """Get member attendance history."""
    try:
        # Verify member belongs to group
        member = GroupMember.query.filter_by(id=member_id, group_id=group_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404

        # Get attendance records
        attendance_query = text("""
            SELECT
                ma.id,
                ma.meeting_id,
                m.meeting_date,
                m.meeting_type,
                ma.is_present,
                ma.arrival_time,
                ma.excuse_reason,
                ma.fine_applied,
                ma.fine_amount,
                ma.created_date
            FROM meeting_attendance ma
            LEFT JOIN meetings m ON ma.meeting_id = m.id
            WHERE ma.member_id = :member_id
            ORDER BY m.meeting_date DESC
        """)

        attendance_result = db.session.execute(attendance_query, {'member_id': member_id})
        attendance_records = []
        total_meetings = 0
        attended_meetings = 0

        for row in attendance_result:
            record = dict(row._mapping)
            # Convert dates to strings
            for key, value in record.items():
                if isinstance(value, datetime):
                    record[key] = value.isoformat()
                elif hasattr(value, 'isoformat'):
                    record[key] = value.isoformat()

            if record.get('fine_amount'):
                record['fine_amount'] = float(record['fine_amount'])

            total_meetings += 1
            if record.get('is_present'):
                attended_meetings += 1

            attendance_records.append(record)

        attendance_rate = (attended_meetings / total_meetings * 100) if total_meetings > 0 else 0

        return jsonify({
            'status': 'success',
            'data': {
                'summary': {
                    'total_meetings': total_meetings,
                    'attended': attended_meetings,
                    'absent': total_meetings - attended_meetings,
                    'attendance_rate': round(attendance_rate, 2)
                },
                'records': attendance_records
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error fetching attendance data: {str(e)}'
        }), 500

