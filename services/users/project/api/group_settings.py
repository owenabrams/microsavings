"""Group settings API endpoints."""

import datetime
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import exc
from functools import wraps
import jwt

from project import db
from project.api.models import SavingsGroup, GroupSettings, GroupDocument


group_settings_blueprint = Blueprint('group_settings', __name__)


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


@group_settings_blueprint.route('/<int:group_id>/settings', methods=['GET'])
@authenticate
def get_group_settings(user_id, group_id):
    """Get complete group settings including all configuration."""
    try:
        group = SavingsGroup.query.filter_by(id=group_id).first()
        if not group:
            return jsonify({
                'status': 'fail',
                'message': 'Group not found.'
            }), 404

        # Get or create group settings
        settings = GroupSettings.query.filter_by(group_id=group_id).first()
        if not settings:
            settings = GroupSettings(group_id=group_id)
            db.session.add(settings)
            db.session.commit()

        # Get mobile money account
        mobile_money_query = db.text("""
            SELECT provider, account_number, account_holder
            FROM group_mobile_money_accounts
            WHERE group_id = :group_id AND is_primary = TRUE
            LIMIT 1
        """)
        mobile_money_result = db.session.execute(mobile_money_query, {'group_id': group_id}).fetchone()

        mobile_money = None
        if mobile_money_result:
            mobile_money = {
                'provider': mobile_money_result[0],
                'account_number': mobile_money_result[1],
                'account_holder': mobile_money_result[2]
            }

        response_data = {
            'group_id': group.id,
            'group_name': group.name,
            
            # Basic Information
            'basic_info': {
                'name': group.name,
                'description': group.description,
                'formation_date': group.formation_date.isoformat() if group.formation_date else None,
                'max_members': group.max_members,
                'saving_cycle_months': group.saving_cycle_months,
                'status': group.status,
            },
            
            # Location
            'location': {
                'country': group.country,
                'region': group.region,
                'district': group.district,
                'parish': group.parish,
                'village': group.village,
                'meeting_location': group.meeting_location,
                'latitude': float(group.latitude) if group.latitude else None,
                'longitude': float(group.longitude) if group.longitude else None,
            },
            
            # Meeting Schedule
            'meeting_schedule': {
                'meeting_day': group.meeting_day,
                'meeting_frequency': group.meeting_frequency,
                'meeting_time': group.meeting_time.isoformat() if group.meeting_time else None,
                'meeting_location': group.meeting_location,
            },
            
            # Registration
            'registration': {
                'is_registered': group.is_registered,
                'registration_number': group.registration_number,
                'registration_date': group.registration_date.isoformat() if group.registration_date else None,
                'registration_authority': group.registration_authority,
                'certificate_number': group.certificate_number,
            },
            
            # Constitution
            'constitution': {
                'document_url': group.constitution_document_url,
                'version': group.constitution_version,
                'description': group.constitution_description,
            },
            
            # Financial Settings
            'financial_settings': {
                'currency': group.currency,
                'share_value': float(group.share_value) if group.share_value else None,
                'standard_fine_amount': float(group.standard_fine_amount) if group.standard_fine_amount else None,
                'loan_interest_rate': float(group.loan_interest_rate) if group.loan_interest_rate else None,
                'negotiated_interest_rate': float(group.negotiated_interest_rate) if group.negotiated_interest_rate else None,
                'minimum_contribution': float(group.minimum_contribution) if group.minimum_contribution else None,
                'target_amount': float(group.target_amount) if group.target_amount else None,
            },
            
            # Mobile Money
            'mobile_money': mobile_money,
            
            # Financial Activities
            'financial_activities': {
                'personal_savings': {
                    'enabled': settings.personal_savings_enabled,
                    'minimum': float(settings.personal_savings_minimum) if settings.personal_savings_minimum else None,
                    'maximum': float(settings.personal_savings_maximum) if settings.personal_savings_maximum else None,
                },
                'ecd_fund': {
                    'enabled': settings.ecd_fund_enabled,
                    'minimum': float(settings.ecd_fund_minimum) if settings.ecd_fund_minimum else None,
                    'maximum': float(settings.ecd_fund_maximum) if settings.ecd_fund_maximum else None,
                },
                'emergency_fund': {
                    'enabled': settings.emergency_fund_enabled,
                },
                'social_fund': {
                    'enabled': settings.social_fund_enabled,
                    'minimum': float(settings.social_fund_minimum) if settings.social_fund_minimum else None,
                    'maximum': float(settings.social_fund_maximum) if settings.social_fund_maximum else None,
                },
                'target_fund': {
                    'enabled': settings.target_fund_enabled,
                },
            },
            
            # Attendance Tracking
            'attendance_tracking': {
                'enabled': settings.attendance_tracking_enabled,
            },
            
            # Loan Activities
            'loan_activities': {
                'loan_disbursement_enabled': settings.loan_disbursement_enabled,
                'loan_repayment_enabled': settings.loan_repayment_enabled,
                'max_loan_multiplier': float(settings.max_loan_multiplier) if settings.max_loan_multiplier else None,
                'min_months_for_loan': settings.min_months_for_loan,
                'min_attendance_for_loan': float(settings.min_attendance_for_loan) if settings.min_attendance_for_loan else None,
            },
            
            # Other Activities
            'other_activities': {
                'voting_session_enabled': settings.voting_session_enabled,
                'training_session_enabled': settings.training_session_enabled,
                'fine_collection_enabled': settings.fine_collection_enabled,
            },
            
            # Fine Settings
            'fine_settings': {
                'late_arrival_fine': float(settings.late_arrival_fine) if settings.late_arrival_fine else None,
                'absence_fine': float(settings.absence_fine) if settings.absence_fine else None,
                'missed_contribution_fine': float(settings.missed_contribution_fine) if settings.missed_contribution_fine else None,
            },
            
            # Meeting Settings
            'meeting_settings': {
                'quorum_percentage': float(settings.quorum_percentage) if settings.quorum_percentage else None,
                'allow_proxy_voting': settings.allow_proxy_voting,
            },
        }

        return jsonify({
            'status': 'success',
            'data': response_data
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@group_settings_blueprint.route('/<int:group_id>/settings', methods=['PUT'])
@authenticate
def update_group_settings(user_id, group_id):
    """Update group settings."""
    try:
        group = SavingsGroup.query.filter_by(id=group_id).first()
        if not group:
            return jsonify({
                'status': 'fail',
                'message': 'Group not found.'
            }), 404

        post_data = request.get_json()
        if not post_data:
            return jsonify({
                'status': 'fail',
                'message': 'Invalid payload.'
            }), 400

        # Get or create group settings
        settings = GroupSettings.query.filter_by(group_id=group_id).first()
        if not settings:
            settings = GroupSettings(group_id=group_id)
            db.session.add(settings)

        # Update basic info
        if 'basic_info' in post_data:
            basic = post_data['basic_info']
            if 'name' in basic:
                group.name = basic['name']
            if 'description' in basic:
                group.description = basic['description']
            if 'max_members' in basic:
                group.max_members = basic['max_members']
            if 'saving_cycle_months' in basic:
                group.saving_cycle_months = basic['saving_cycle_months']
            if 'status' in basic:
                group.status = basic['status']

        # Update location
        if 'location' in post_data:
            loc = post_data['location']
            if 'country' in loc:
                group.country = loc['country']
            if 'region' in loc:
                group.region = loc['region']
            if 'district' in loc:
                group.district = loc['district']
            if 'parish' in loc:
                group.parish = loc['parish']
            if 'village' in loc:
                group.village = loc['village']
            if 'meeting_location' in loc:
                group.meeting_location = loc['meeting_location']
            if 'latitude' in loc:
                group.latitude = loc['latitude']
            if 'longitude' in loc:
                group.longitude = loc['longitude']

        # Update meeting schedule
        if 'meeting_schedule' in post_data:
            meeting = post_data['meeting_schedule']
            if 'meeting_day' in meeting:
                group.meeting_day = meeting['meeting_day']
            if 'meeting_frequency' in meeting:
                group.meeting_frequency = meeting['meeting_frequency']
            if 'meeting_time' in meeting:
                group.meeting_time = meeting['meeting_time']

        # Update registration
        if 'registration' in post_data:
            reg = post_data['registration']
            if 'is_registered' in reg:
                group.is_registered = reg['is_registered']
            if 'registration_number' in reg:
                group.registration_number = reg['registration_number']
            if 'registration_authority' in reg:
                group.registration_authority = reg['registration_authority']
            if 'certificate_number' in reg:
                group.certificate_number = reg['certificate_number']

        # Update constitution
        if 'constitution' in post_data:
            const = post_data['constitution']
            if 'version' in const:
                group.constitution_version = const['version']
            if 'description' in const:
                group.constitution_description = const['description']

        # Update financial settings
        if 'financial_settings' in post_data:
            fin = post_data['financial_settings']
            if 'currency' in fin:
                group.currency = fin['currency']
            if 'share_value' in fin:
                group.share_value = fin['share_value']
            if 'standard_fine_amount' in fin:
                group.standard_fine_amount = fin['standard_fine_amount']
            if 'loan_interest_rate' in fin:
                group.loan_interest_rate = fin['loan_interest_rate']
            if 'negotiated_interest_rate' in fin:
                group.negotiated_interest_rate = fin['negotiated_interest_rate']
            if 'minimum_contribution' in fin:
                group.minimum_contribution = fin['minimum_contribution']

        # Update financial activities
        if 'financial_activities' in post_data:
            activities = post_data['financial_activities']
            if 'personal_savings' in activities:
                ps = activities['personal_savings']
                if 'enabled' in ps:
                    settings.personal_savings_enabled = ps['enabled']
                if 'minimum' in ps:
                    settings.personal_savings_minimum = ps['minimum']
                if 'maximum' in ps:
                    settings.personal_savings_maximum = ps['maximum']
            
            if 'ecd_fund' in activities:
                ecd = activities['ecd_fund']
                if 'enabled' in ecd:
                    settings.ecd_fund_enabled = ecd['enabled']
                if 'minimum' in ecd:
                    settings.ecd_fund_minimum = ecd['minimum']
                if 'maximum' in ecd:
                    settings.ecd_fund_maximum = ecd['maximum']
            
            if 'emergency_fund' in activities:
                settings.emergency_fund_enabled = activities['emergency_fund'].get('enabled', False)
            
            if 'social_fund' in activities:
                sf = activities['social_fund']
                if 'enabled' in sf:
                    settings.social_fund_enabled = sf['enabled']
                if 'minimum' in sf:
                    settings.social_fund_minimum = sf['minimum']
                if 'maximum' in sf:
                    settings.social_fund_maximum = sf['maximum']
            
            if 'target_fund' in activities:
                settings.target_fund_enabled = activities['target_fund'].get('enabled', False)

        # Update attendance tracking
        if 'attendance_tracking' in post_data:
            settings.attendance_tracking_enabled = post_data['attendance_tracking'].get('enabled', True)

        # Update loan activities
        if 'loan_activities' in post_data:
            loans = post_data['loan_activities']
            if 'loan_disbursement_enabled' in loans:
                settings.loan_disbursement_enabled = loans['loan_disbursement_enabled']
            if 'loan_repayment_enabled' in loans:
                settings.loan_repayment_enabled = loans['loan_repayment_enabled']
            if 'max_loan_multiplier' in loans:
                settings.max_loan_multiplier = loans['max_loan_multiplier']
            if 'min_months_for_loan' in loans:
                settings.min_months_for_loan = loans['min_months_for_loan']
            if 'min_attendance_for_loan' in loans:
                settings.min_attendance_for_loan = loans['min_attendance_for_loan']

        # Update other activities
        if 'other_activities' in post_data:
            other = post_data['other_activities']
            if 'voting_session_enabled' in other:
                settings.voting_session_enabled = other['voting_session_enabled']
            if 'training_session_enabled' in other:
                settings.training_session_enabled = other['training_session_enabled']
            if 'fine_collection_enabled' in other:
                settings.fine_collection_enabled = other['fine_collection_enabled']

        # Update fine settings
        if 'fine_settings' in post_data:
            fines = post_data['fine_settings']
            if 'late_arrival_fine' in fines:
                settings.late_arrival_fine = fines['late_arrival_fine']
            if 'absence_fine' in fines:
                settings.absence_fine = fines['absence_fine']
            if 'missed_contribution_fine' in fines:
                settings.missed_contribution_fine = fines['missed_contribution_fine']

        # Update meeting settings
        if 'meeting_settings' in post_data:
            meeting_set = post_data['meeting_settings']
            if 'quorum_percentage' in meeting_set:
                settings.quorum_percentage = meeting_set['quorum_percentage']
            if 'allow_proxy_voting' in meeting_set:
                settings.allow_proxy_voting = meeting_set['allow_proxy_voting']

        group.updated_date = datetime.datetime.utcnow()
        settings.updated_date = datetime.datetime.utcnow()
        
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Group settings updated successfully.'
        }), 200

    except exc.IntegrityError:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': 'Database integrity error.'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500

