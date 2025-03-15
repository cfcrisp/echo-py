from flask import request, jsonify
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

@bp.route('/register-tenant', methods=['POST'])
def register_tenant():
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['tenant_name', 'username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if email is already in use
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already in use'}), 400
    
    # Create new tenant
    tenant = Tenant(
        name=data['tenant_name'],
        plan_tier=data.get('plan_tier', 'basic')
    )
    db.session.add(tenant)
    
    # Create admin user for the tenant
    user = User(
        tenant_id=tenant.id,
        username=data['username'],
        email=data['email'],
        role='admin'
    )
    user.set_password(data['password'])
    db.session.add(user)
    
    db.session.commit()
    
    # Create tokens
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    return jsonify({
        'tenant': {
            'id': str(tenant.id),
            'name': tenant.name,
            'plan_tier': tenant.plan_tier
        },
        'user': {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role
        },
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201