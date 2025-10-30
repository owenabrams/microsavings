"""Members API blueprint."""
from flask import Blueprint, request, jsonify
from sqlalchemy import exc, func
from project import db
from project.api.models import (
    GroupMember, SavingsGroup, MemberSaving, SavingType,
    MeetingAttendance, MemberFine, GroupLoan, LoanAssessment,
    User
)
from functools import wraps
import jwt
from flask import current_app


members_blueprint = Blueprint('members', __name__)


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


@members_blueprint.route('/<int:member_id>', methods=['GET'])
@authenticate
def get_member(user_id, member_id):
    """Get member basic information."""
    try:
        member = GroupMember.query.filter_by(id=member_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404
        
        # Get group information
        group = SavingsGroup.query.filter_by(id=member.group_id).first()
        
        return jsonify({
            'status': 'success',
            'data': {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'email': member.email,
                'phone_number': member.phone_number,
                'role': member.role,
                'status': member.status,
                'joined_date': member.joined_date.isoformat() if member.joined_date else None,
                'group': {
                    'id': group.id,
                    'name': group.name,
                    'district': group.district,
                    'parish': group.parish,
                    'village': group.village
                } if group else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@members_blueprint.route('/<int:member_id>/dashboard', methods=['GET'])
@authenticate
def get_member_dashboard(user_id, member_id):
    """Get comprehensive member dashboard data."""
    try:
        member = GroupMember.query.filter_by(id=member_id).first()
        if not member:
            return jsonify({
                'status': 'fail',
                'message': 'Member not found.'
            }), 404
        
        group = SavingsGroup.query.filter_by(id=member.group_id).first()
        
        # 1. SAVINGS DATA - Get savings by fund type
        # Get all member savings for this member
        member_savings = MemberSaving.query.filter_by(member_id=member_id).all()

        # Build savings by fund dictionary
        savings_by_fund_dict = {}
        for ms in member_savings:
            saving_type = SavingType.query.filter_by(id=ms.saving_type_id).first()
            if saving_type:
                balance = float(ms.total_deposits or 0) - float(ms.total_withdrawals or 0)
                savings_by_fund_dict[saving_type.name] = {
                    'name': saving_type.name,
                    'description': saving_type.description,
                    'total_deposits': float(ms.total_deposits or 0),
                    'total_withdrawals': float(ms.total_withdrawals or 0),
                    'balance': balance
                }

        funds = list(savings_by_fund_dict.values())
        total_savings = sum([f['balance'] for f in funds])
        
        # 2. LOAN STATUS - Get loan eligibility and current loans
        loan_assessment = LoanAssessment.query.filter_by(
            member_id=member_id
        ).order_by(LoanAssessment.assessment_date.desc()).first()

        # Query loans using raw SQL to avoid ORM mismatch
        active_loans_query = db.session.execute(
            db.text("""
                SELECT principal, outstanding_balance
                FROM group_loans
                WHERE member_id = :member_id
                AND status IN ('PENDING', 'APPROVED', 'DISBURSED', 'REPAYING')
            """),
            {'member_id': member_id}
        )
        active_loans = active_loans_query.fetchall()

        total_loan_amount = sum([float(loan[0] or 0) for loan in active_loans])
        total_outstanding = sum([float(loan[1] or 0) for loan in active_loans])
        
        loan_status = {
            'is_eligible': loan_assessment.is_eligible if loan_assessment else False,
            'max_loan_amount': float(loan_assessment.max_loan_amount or 0) if loan_assessment else 0,
            'overall_score': float(loan_assessment.overall_score or 0) if loan_assessment else 0,
            'risk_level': loan_assessment.risk_level if loan_assessment else 'UNKNOWN',
            'active_loans_count': len(active_loans),
            'total_loan_amount': total_loan_amount,
            'total_outstanding': total_outstanding
        }
        
        # 3. ATTENDANCE & PERFORMANCE
        total_meetings = db.session.query(func.count(MeetingAttendance.id)).filter(
            MeetingAttendance.member_id == member_id
        ).scalar() or 0
        
        attended_meetings = db.session.query(func.count(MeetingAttendance.id)).filter(
            MeetingAttendance.member_id == member_id,
            MeetingAttendance.is_present == True
        ).scalar() or 0
        
        attendance_rate = (attended_meetings / total_meetings * 100) if total_meetings > 0 else 0
        
        # 4. FINES
        total_fines = db.session.query(
            func.coalesce(func.sum(MemberFine.amount), 0)
        ).filter(
            MemberFine.member_id == member_id
        ).scalar() or 0
        
        paid_fines = db.session.query(
            func.coalesce(func.sum(MemberFine.paid_amount), 0)
        ).filter(
            MemberFine.member_id == member_id,
            MemberFine.is_paid == True
        ).scalar() or 0
        
        outstanding_fines = float(total_fines) - float(paid_fines)
        
        # 5. GROUP AVERAGES FOR COMPARISON
        group_avg_savings = db.session.query(
            func.avg(GroupMember.total_contributions)
        ).filter(
            GroupMember.group_id == member.group_id,
            GroupMember.is_active == True
        ).scalar() or 0
        
        group_avg_attendance = db.session.query(
            func.avg(GroupMember.attendance_percentage)
        ).filter(
            GroupMember.group_id == member.group_id,
            GroupMember.is_active == True
        ).scalar() or 0
        
        # 6. IGA PARTICIPATION (placeholder for Phase 1.5)
        iga_participation = {
            'active_campaigns': 0,
            'total_invested': 0,
            'total_returns': 0,
            'roi_percentage': 0
        }
        
        # Compile dashboard data
        dashboard_data = {
            'member': {
                'id': member.id,
                'first_name': member.first_name,
                'last_name': member.last_name,
                'role': member.role,
                'status': member.status,
                'joined_date': member.joined_date.isoformat() if member.joined_date else None
            },
            'group': {
                'id': group.id,
                'name': group.name,
                'district': group.district,
                'parish': group.parish,
                'village': group.village,
                'currency': group.currency or 'UGX',
                'share_value': float(group.share_value or 0),
                'target_amount': float(group.target_amount or 0)
            } if group else None,
            'savings': {
                'total': total_savings,
                'by_fund': funds,
                'target': float(member.share_balance or 0),
                'progress_percentage': (total_savings / float(member.share_balance) * 100) if member.share_balance and member.share_balance > 0 else 0
            },
            'loans': loan_status,
            'performance': {
                'attendance_rate': float(attendance_rate),
                'total_meetings': total_meetings,
                'attended_meetings': attended_meetings,
                'total_contributions': float(member.total_contributions or 0),
                'member_savings': total_savings,
                'group_avg_savings': float(group_avg_savings or 0),
                'group_avg_attendance': float(group_avg_attendance or 0)
            },
            'fines': {
                'total': float(total_fines),
                'paid': float(paid_fines),
                'outstanding': outstanding_fines
            },
            'iga': iga_participation
        }
        
        return jsonify({
            'status': 'success',
            'data': dashboard_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500

