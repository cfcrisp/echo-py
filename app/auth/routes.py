from flask import request, jsonify, render_template
from app.auth import bp
from app.models.user import User
from app.models.tenant import Tenant
from app.extensions import db, jwt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Find user by email (tenant-specific)
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        # Use vague error message for security
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'tenant_id': str(user.tenant_id)
        }
    })

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({'access_token': access_token})

@bp.route('/login', methods=['GET'])
def login_page():
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET'])
def register_page():
    return render_template('auth/register.html')

@bp.route('/register-tenant', methods=['POST'])
def register_tenant():
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['tenant_name', 'username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Use AuthService to register tenant
    from app.services.auth_service import AuthService
    result, status_code = AuthService.register_tenant(
        tenant_name=data['tenant_name'],
        username=data['username'],
        email=data['email'],
        password=data['password'],
        plan_tier=data.get('plan_tier', 'basic')
    )
    
    return jsonify(result), status_code

@bp.route('/register-user', methods=['POST'])
@jwt_required()
def register_user():
    # Get current user from JWT token
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    # Check if current user has admin role
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin role required'}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Use AuthService to register user
    from app.services.auth_service import AuthService
    result, status_code = AuthService.register_user(
        tenant_id=current_user.tenant_id,
        username=data['username'],
        email=data['email'],
        password=data['password'],
        role=data['role']
    )
    
    return jsonify(result), status_code