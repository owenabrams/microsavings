"""API endpoints for managing saving types."""

from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import text
from functools import wraps
import jwt

from project import db
from project.api.models import SavingType

saving_types_blueprint = Blueprint('saving_types', __name__)


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


@saving_types_blueprint.route('/groups/<int:group_id>/saving-types', methods=['GET'])
@authenticate
def get_group_saving_types(user_id, group_id):
    """Get all saving types available for a group (system + group-specific)."""
    try:
        # Query to get all saving types for this group
        query = text("""
            SELECT 
                st.id,
                st.name,
                st.description,
                st.code,
                st.is_mandatory,
                st.is_system,
                st.group_id AS owner_group_id,
                COALESCE(gsts.minimum_amount, st.minimum_amount) AS minimum_amount,
                COALESCE(gsts.maximum_amount, st.maximum_amount) AS maximum_amount,
                COALESCE(gsts.allows_withdrawal, st.allows_withdrawal) AS allows_withdrawal,
                COALESCE(gsts.withdrawal_notice_days, st.withdrawal_notice_days) AS withdrawal_notice_days,
                COALESCE(gsts.interest_rate, st.interest_rate) AS interest_rate,
                COALESCE(gsts.is_enabled, TRUE) AS is_enabled,
                COALESCE(gsts.display_order, 0) AS display_order,
                st.is_active
            FROM saving_types st
            LEFT JOIN group_saving_type_settings gsts 
                ON st.id = gsts.saving_type_id AND gsts.group_id = :group_id
            WHERE (st.is_system = TRUE OR st.group_id = :group_id)
                AND st.is_active = TRUE
            ORDER BY display_order, st.name
        """)
        
        result = db.session.execute(query, {'group_id': group_id})
        saving_types = []
        
        for row in result:
            saving_types.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'code': row[3],
                'is_mandatory': row[4],
                'is_system': row[5],
                'owner_group_id': row[6],
                'minimum_amount': float(row[7]) if row[7] else None,
                'maximum_amount': float(row[8]) if row[8] else None,
                'allows_withdrawal': row[9],
                'withdrawal_notice_days': row[10],
                'interest_rate': float(row[11]) if row[11] else 0.0,
                'is_enabled': row[12],
                'display_order': row[13],
                'is_active': row[14],
                'can_delete': not row[5]  # Can only delete non-system types
            })
        
        return jsonify({
            'status': 'success',
            'data': saving_types
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@saving_types_blueprint.route('/groups/<int:group_id>/saving-types', methods=['POST'])
@authenticate
def create_saving_type(user_id, group_id):
    """Create a new custom saving type for a group."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'fail',
                'message': 'No data provided.'
            }), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        code = data.get('code', '').strip().upper()
        
        if not name:
            return jsonify({
                'status': 'fail',
                'message': 'Saving type name is required.'
            }), 400
        
        if not code:
            # Auto-generate code from name
            code = ''.join(c for c in name.upper() if c.isalnum())[:20]
        
        # Check if code already exists for this group
        check_query = text("""
            SELECT id FROM saving_types 
            WHERE code = :code 
            AND (group_id = :group_id OR (group_id IS NULL AND is_system = TRUE))
        """)
        existing = db.session.execute(check_query, {
            'code': code,
            'group_id': group_id
        }).fetchone()
        
        if existing:
            return jsonify({
                'status': 'fail',
                'message': f'A saving type with code "{code}" already exists.'
            }), 400
        
        # Insert new saving type
        insert_query = text("""
            INSERT INTO saving_types (
                name, description, code, is_mandatory, is_system, 
                minimum_amount, maximum_amount, allows_withdrawal, 
                withdrawal_notice_days, interest_rate, is_active, group_id
            ) VALUES (
                :name, :description, :code, :is_mandatory, FALSE,
                :minimum_amount, :maximum_amount, :allows_withdrawal,
                :withdrawal_notice_days, :interest_rate, TRUE, :group_id
            ) RETURNING id
        """)
        
        result = db.session.execute(insert_query, {
            'name': name,
            'description': data.get('description', ''),
            'code': code,
            'is_mandatory': data.get('is_mandatory', False),
            'minimum_amount': data.get('minimum_amount'),
            'maximum_amount': data.get('maximum_amount'),
            'allows_withdrawal': data.get('allows_withdrawal', True),
            'withdrawal_notice_days': data.get('withdrawal_notice_days', 0),
            'interest_rate': data.get('interest_rate', 0.0),
            'group_id': group_id
        })
        
        new_id = result.fetchone()[0]
        db.session.commit()
        
        # Create group settings entry
        settings_query = text("""
            INSERT INTO group_saving_type_settings (
                group_id, saving_type_id, is_enabled, display_order
            ) VALUES (
                :group_id, :saving_type_id, TRUE, 
                (SELECT COALESCE(MAX(display_order), 0) + 1 
                 FROM group_saving_type_settings WHERE group_id = :group_id)
            )
        """)
        
        db.session.execute(settings_query, {
            'group_id': group_id,
            'saving_type_id': new_id
        })
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Saving type created successfully.',
            'data': {
                'id': new_id,
                'name': name,
                'code': code
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@saving_types_blueprint.route('/groups/<int:group_id>/saving-types/<int:type_id>', methods=['PUT'])
@authenticate
def update_saving_type(user_id, group_id, type_id):
    """Update a saving type (only custom types can be fully edited)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'fail',
                'message': 'No data provided.'
            }), 400
        
        # Check if this is a system type or group-owned type
        check_query = text("""
            SELECT is_system, group_id FROM saving_types WHERE id = :type_id
        """)
        result = db.session.execute(check_query, {'type_id': type_id}).fetchone()
        
        if not result:
            return jsonify({
                'status': 'fail',
                'message': 'Saving type not found.'
            }), 404
        
        is_system = result[0]
        owner_group_id = result[1]
        
        # If it's a system type, only update group-specific settings
        if is_system:
            update_query = text("""
                INSERT INTO group_saving_type_settings (
                    group_id, saving_type_id, is_enabled, minimum_amount,
                    maximum_amount, allows_withdrawal, withdrawal_notice_days,
                    interest_rate, display_order
                ) VALUES (
                    :group_id, :type_id, :is_enabled, :minimum_amount,
                    :maximum_amount, :allows_withdrawal, :withdrawal_notice_days,
                    :interest_rate, :display_order
                )
                ON CONFLICT (group_id, saving_type_id) 
                DO UPDATE SET
                    is_enabled = EXCLUDED.is_enabled,
                    minimum_amount = EXCLUDED.minimum_amount,
                    maximum_amount = EXCLUDED.maximum_amount,
                    allows_withdrawal = EXCLUDED.allows_withdrawal,
                    withdrawal_notice_days = EXCLUDED.withdrawal_notice_days,
                    interest_rate = EXCLUDED.interest_rate,
                    display_order = EXCLUDED.display_order,
                    updated_date = CURRENT_TIMESTAMP
            """)
            
            db.session.execute(update_query, {
                'group_id': group_id,
                'type_id': type_id,
                'is_enabled': data.get('is_enabled', True),
                'minimum_amount': data.get('minimum_amount'),
                'maximum_amount': data.get('maximum_amount'),
                'allows_withdrawal': data.get('allows_withdrawal'),
                'withdrawal_notice_days': data.get('withdrawal_notice_days'),
                'interest_rate': data.get('interest_rate'),
                'display_order': data.get('display_order', 0)
            })
        else:
            # For custom types, verify ownership
            if owner_group_id != group_id:
                return jsonify({
                    'status': 'fail',
                    'message': 'You can only edit saving types owned by your group.'
                }), 403
            
            # Update the saving type itself
            update_query = text("""
                UPDATE saving_types SET
                    name = :name,
                    description = :description,
                    minimum_amount = :minimum_amount,
                    maximum_amount = :maximum_amount,
                    allows_withdrawal = :allows_withdrawal,
                    withdrawal_notice_days = :withdrawal_notice_days,
                    interest_rate = :interest_rate
                WHERE id = :type_id
            """)
            
            db.session.execute(update_query, {
                'type_id': type_id,
                'name': data.get('name'),
                'description': data.get('description'),
                'minimum_amount': data.get('minimum_amount'),
                'maximum_amount': data.get('maximum_amount'),
                'allows_withdrawal': data.get('allows_withdrawal'),
                'withdrawal_notice_days': data.get('withdrawal_notice_days'),
                'interest_rate': data.get('interest_rate')
            })
        
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Saving type updated successfully.'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@saving_types_blueprint.route('/groups/<int:group_id>/saving-types/<int:type_id>', methods=['DELETE'])
@authenticate
def delete_saving_type(user_id, group_id, type_id):
    """Delete a custom saving type (system types cannot be deleted)."""
    try:
        # Check if this is a system type
        check_query = text("""
            SELECT is_system, group_id, name FROM saving_types WHERE id = :type_id
        """)
        result = db.session.execute(check_query, {'type_id': type_id}).fetchone()

        if not result:
            return jsonify({
                'status': 'fail',
                'message': 'Saving type not found.'
            }), 404

        is_system = result[0]
        owner_group_id = result[1]
        name = result[2]

        # Cannot delete system types
        if is_system:
            return jsonify({
                'status': 'fail',
                'message': 'System saving types cannot be deleted. You can disable them instead.'
            }), 403

        # Verify ownership
        if owner_group_id != group_id:
            return jsonify({
                'status': 'fail',
                'message': 'You can only delete saving types owned by your group.'
            }), 403

        # Check if there are any transactions or balances
        check_usage_query = text("""
            SELECT
                (SELECT COUNT(*) FROM member_savings WHERE saving_type_id = :type_id) AS savings_count,
                (SELECT COUNT(*) FROM saving_transactions WHERE saving_type_id = :type_id) AS transactions_count
        """)
        usage = db.session.execute(check_usage_query, {'type_id': type_id}).fetchone()

        savings_count = usage[0]
        transactions_count = usage[1]

        # Warn if there's data (but still allow deletion due to CASCADE)
        warning_message = None
        if savings_count > 0 or transactions_count > 0:
            warning_message = (
                f'This will delete {savings_count} member savings records and '
                f'{transactions_count} transactions associated with this saving type.'
            )

        # Delete the saving type (CASCADE will handle related records)
        delete_query = text("""
            DELETE FROM saving_types WHERE id = :type_id
        """)
        db.session.execute(delete_query, {'type_id': type_id})
        db.session.commit()

        response_data = {
            'status': 'success',
            'message': f'Saving type "{name}" deleted successfully.'
        }

        if warning_message:
            response_data['warning'] = warning_message

        return jsonify(response_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500


@saving_types_blueprint.route('/groups/<int:group_id>/saving-types/<int:type_id>/usage', methods=['GET'])
@authenticate
def get_saving_type_usage(user_id, group_id, type_id):
    """Get usage statistics for a saving type before deletion."""
    try:
        query = text("""
            SELECT
                st.name,
                st.is_system,
                (SELECT COUNT(*) FROM member_savings ms
                 WHERE ms.saving_type_id = :type_id) AS members_using,
                (SELECT COALESCE(SUM(current_balance), 0) FROM member_savings ms
                 WHERE ms.saving_type_id = :type_id) AS total_balance,
                (SELECT COUNT(*) FROM saving_transactions st
                 WHERE st.saving_type_id = :type_id) AS total_transactions,
                (SELECT COALESCE(SUM(amount), 0) FROM saving_transactions st
                 WHERE st.saving_type_id = :type_id AND transaction_type = 'DEPOSIT') AS total_deposits,
                (SELECT COALESCE(SUM(amount), 0) FROM saving_transactions st
                 WHERE st.saving_type_id = :type_id AND transaction_type = 'WITHDRAWAL') AS total_withdrawals
            FROM saving_types st
            WHERE st.id = :type_id
        """)

        result = db.session.execute(query, {'type_id': type_id}).fetchone()

        if not result:
            return jsonify({
                'status': 'fail',
                'message': 'Saving type not found.'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {
                'name': result[0],
                'is_system': result[1],
                'members_using': result[2],
                'total_balance': float(result[3]),
                'total_transactions': result[4],
                'total_deposits': float(result[5]),
                'total_withdrawals': float(result[6]),
                'can_delete': not result[1]
            }
        }), 200

    except Exception as e:
        return jsonify({
            'status': 'fail',
            'message': str(e)
        }), 500

