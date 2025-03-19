from flask import request, jsonify
from app.api import bp
from app.models.user import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid

@bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Only fetch users from the same tenant
    users = User.query.filter_by(tenant_id=current_user.tenant_id).all()
    
    return jsonify({
        'users': [
            {
                'id': str(user.id),
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat()
            } for user in users
        ]
    })

@bp.route('/users/<uuid:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    user = User.query.get_or_404(user_id)
    
    # Check if user belongs to the same tenant
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    return jsonify({
        'id': str(user.id),
        'email': user.email,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    })

@bp.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user has admin role
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin role required'}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = [ 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Use AuthService to register user
    from app.services.auth_service import AuthService
    result, status_code = AuthService.register_user(
        tenant_id=current_user.tenant_id,
        email=data['email'],
        password=data['password'],
        role=data['role']
    )
    
    # If successful, return just the user data without tokens
    if status_code == 201 and 'user' in result:
        user_data = result['user']
        return jsonify({
            'id': user_data['id'],
            'email': user_data['email'],
            'role': user_data['role'],
            'created_at': User.query.get(uuid.UUID(user_data['id'])).created_at.isoformat()
        }), 201
    
    # Otherwise return the error
    return jsonify(result), status_code

@bp.route('/users/<uuid:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if user being updated belongs to the same tenant
    user = User.query.get_or_404(user_id)
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    # Only admin or the user themselves can update user info
    if current_user.role != 'admin' and current_user.id != user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json() or {}
    
    if 'email' in data:
        # Check if email is already taken within tenant
        existing_user = User.query.filter_by(tenant_id=current_user.tenant_id, email=data['email']).first()
        if existing_user and existing_user.id != user.id:
            return jsonify({'error': 'Email already in use within this tenant'}), 400
        user.email = data['email']
    
    if 'role' in data:
        # Only admin can change roles
        if current_user.role != 'admin':
            return jsonify({'error': 'Admin role required to change user roles'}), 403
        
        valid_roles = ['user', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({'error': f"Invalid role. Must be one of: {', '.join(valid_roles)}"}), 400
        
        user.role = data['role']
    
    if 'password' in data:
        user.set_password(data['password'])
    
    db.session.commit()
    
    return jsonify({
        'id': str(user.id),
        'email': user.email,
        'role': user.role,
        'updated_at': user.updated_at.isoformat()
    })

@bp.route('/users/<uuid:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Only admin can delete users
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin role required'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Check if user belongs to the same tenant
    if user.tenant_id != current_user.tenant_id:
        return jsonify({'error': 'Not authorized'}), 403
    
    # Prevent admins from deleting themselves
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return '', 204