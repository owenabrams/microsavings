"""Authentication blueprint."""
from flask import Blueprint, request, jsonify
from sqlalchemy import exc
from project import db, bcrypt
from project.api.models import User


auth_blueprint = Blueprint('auth', __name__)


@auth_blueprint.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    
    if not post_data:
        return jsonify(response_object), 400
    
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    
    try:
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            response_object['message'] = 'Sorry. That email already exists.'
            return jsonify(response_object), 400
        
        # Add new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        # Generate auth token
        auth_token = new_user.encode_token(new_user.id)
        response_object['status'] = 'success'
        response_object['message'] = 'Successfully registered.'
        response_object['auth_token'] = auth_token
        return jsonify(response_object), 201
        
    except (exc.IntegrityError, ValueError):
        db.session.rollback()
        return jsonify(response_object), 400


@auth_blueprint.route('/login', methods=['POST'])
def login():
    """Login user."""
    post_data = request.get_json()
    response_object = {
        'status': 'fail',
        'message': 'Invalid payload.'
    }
    
    if not post_data:
        return jsonify(response_object), 400
    
    email = post_data.get('email')
    password = post_data.get('password')
    
    try:
        # Fetch user
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            auth_token = user.encode_token(user.id)
            if auth_token:
                response_object['status'] = 'success'
                response_object['message'] = 'Successfully logged in.'
                response_object['auth_token'] = auth_token
                response_object['user'] = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_super_admin': user.is_super_admin
                }
                return jsonify(response_object), 200
        else:
            response_object['message'] = 'Invalid credentials.'
            return jsonify(response_object), 401
            
    except Exception as e:
        response_object['message'] = 'Try again.'
        return jsonify(response_object), 500


@auth_blueprint.route('/status', methods=['GET'])
def status():
    """Get user status."""
    auth_header = request.headers.get('Authorization')
    response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.'
    }
    
    if auth_header:
        try:
            auth_token = auth_header.split(' ')[1]
            user_id = User.decode_token(auth_token)
            if not isinstance(user_id, str):
                user = User.query.filter_by(id=user_id).first()
                if user:
                    response_object['status'] = 'success'
                    response_object['authenticated'] = True
                    response_object['user_id'] = user.id
                    response_object['data'] = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'active': user.active,
                        'admin': user.admin,
                        'role': user.role,
                        'is_super_admin': user.is_super_admin
                    }
                    return jsonify(response_object), 200
            response_object['message'] = user_id
            return jsonify(response_object), 401
        except IndexError:
            return jsonify(response_object), 401
    else:
        return jsonify(response_object), 401


@auth_blueprint.route('/logout', methods=['GET'])
def logout():
    """Logout user."""
    auth_header = request.headers.get('Authorization')
    response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.'
    }

    if auth_header:
        try:
            auth_token = auth_header.split(' ')[1]
            user_id = User.decode_token(auth_token)
            if not isinstance(user_id, str):
                response_object['status'] = 'success'
                response_object['message'] = 'Successfully logged out.'
                return jsonify(response_object), 200
            response_object['message'] = user_id
            return jsonify(response_object), 401
        except IndexError:
            return jsonify(response_object), 401
    else:
        return jsonify(response_object), 401


@auth_blueprint.route('/profile', methods=['GET'])
def get_user_profile():
    """Get current user's profile."""
    auth_header = request.headers.get('Authorization')
    response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.'
    }

    if auth_header:
        try:
            auth_token = auth_header.split(' ')[1]
            user_id = User.decode_token(auth_token)
            if not isinstance(user_id, str):
                user = User.query.filter_by(id=user_id).first()
                if user:
                    response_object['status'] = 'success'
                    response_object['data'] = {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'is_super_admin': user.is_super_admin,
                        'active': user.active,
                        'created_date': user.created_date.isoformat() if user.created_date else None
                    }
                    return jsonify(response_object), 200
            response_object['message'] = user_id
            return jsonify(response_object), 401
        except IndexError:
            return jsonify(response_object), 401
    else:
        return jsonify(response_object), 401


@auth_blueprint.route('/profile', methods=['PUT'])
def update_user_profile():
    """Update current user's profile (username, email, password)."""
    auth_header = request.headers.get('Authorization')
    response_object = {
        'status': 'fail',
        'message': 'Provide a valid auth token.'
    }

    if not auth_header:
        return jsonify(response_object), 401

    try:
        auth_token = auth_header.split(' ')[1]
        user_id = User.decode_token(auth_token)
        if isinstance(user_id, str):
            response_object['message'] = user_id
            return jsonify(response_object), 401

        user = User.query.filter_by(id=user_id).first()
        if not user:
            response_object['message'] = 'User not found.'
            return jsonify(response_object), 404

        post_data = request.get_json()
        if not post_data:
            response_object['message'] = 'Invalid payload.'
            return jsonify(response_object), 400

        # Update username if provided
        if 'username' in post_data:
            new_username = post_data['username']
            # Check if username is already taken
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user and existing_user.id != user_id:
                response_object['message'] = 'Username already taken.'
                return jsonify(response_object), 400
            user.username = new_username

        # Update email if provided
        if 'email' in post_data:
            new_email = post_data['email']
            # Check if email is already taken
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user and existing_user.id != user_id:
                response_object['message'] = 'Email already taken.'
                return jsonify(response_object), 400
            user.email = new_email

        # Update password if provided
        if 'password' in post_data and 'current_password' in post_data:
            # Verify current password
            if not bcrypt.check_password_hash(user.password, post_data['current_password']):
                response_object['message'] = 'Current password is incorrect.'
                return jsonify(response_object), 401
            # Update to new password
            user.password = bcrypt.generate_password_hash(post_data['password']).decode('utf-8')

        db.session.commit()

        response_object['status'] = 'success'
        response_object['message'] = 'Profile updated successfully.'
        response_object['data'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
        return jsonify(response_object), 200

    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object['message'] = 'Error updating profile.'
        return jsonify(response_object), 400
    except IndexError:
        return jsonify(response_object), 401

