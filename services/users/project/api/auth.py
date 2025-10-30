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

