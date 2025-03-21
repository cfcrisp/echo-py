# app/auth/routes.py
from flask import request, jsonify, render_template, make_response, redirect, current_app
from app.auth import bp
from app.models.user import User
from app.models.tenant import Tenant
from app.extensions import db, jwt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
import uuid

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    # Extract domain from request if available
    email_domain = data.get('domain')
    
    # Find tenant by domain
    tenant = None
    if email_domain:
        tenant = Tenant.query.filter_by(domain_name=email_domain).first()
        if not tenant:
            return jsonify({'error': 'No organization found for this email domain'}), 404
    
    # Find user by email within the tenant if tenant was found
    user = None
    if tenant:
        user = User.query.filter_by(email=data['email'], tenant_id=tenant.id).first()
    else:
        # Fallback to finding user by email only if no domain was provided
        user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        # Use vague error message for security
        return jsonify({'error': 'Invalid email or password'}), 401
        
    # Get tenant information if not already retrieved
    if not tenant:
        tenant = Tenant.query.get(user.tenant_id)
    
    # Create tokens with user_id as identity and tenant_id as additional claim
    access_token = create_access_token(identity=str(user.id), additional_claims={"tenant_id": str(user.tenant_id)})
    refresh_token = create_refresh_token(identity=str(user.id), additional_claims={"tenant_id": str(user.tenant_id)})
    
    # Create response and set cookie
    response = make_response(jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'tenant_id': str(user.tenant_id)
        },
        'tenant': {
            'id': str(tenant.id),
            'domain_name': tenant.domain_name
        }
    }))
    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=current_app.config['JWT_COOKIE_SECURE'],
        samesite='Lax',
        max_age=3600
    )
    return response

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()  # String (user_id)
    current_claims = get_jwt()  # Full JWT payload, including tenant_id
    access_token = create_access_token(identity=current_user_id, additional_claims={"tenant_id": current_claims["tenant_id"]})
    
    response = jsonify({'access_token': access_token})
    response.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=current_app.config['JWT_COOKIE_SECURE'],
        samesite='Lax',
        max_age=3600
    )
    return response

@bp.route('/login', methods=['GET'])
def login_page():
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET'])
def register_page():
    return render_template('auth/register.html')

@bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()  # String (user_id)
    claims = get_jwt()  # Full JWT payload
    user = User.query.get_or_404(uuid.UUID(user_id))
    tenant = Tenant.query.get_or_404(uuid.UUID(claims['tenant_id']))
    
    # Validate tenant_id consistency
    if user.tenant_id != tenant.id:
        return jsonify({'error': 'Tenant mismatch'}), 403
    
    # Fetch goals for the current tenant
    from app.models.goal import Goal
    goals = Goal.query.filter_by(tenant_id=tenant.id).all()
    
    return render_template('dashboard/goals.html', 
                          user=user, 
                          tenant=tenant,
                          goals=goals,
                          active_section='goals')

# app/auth/routes.py (partial update for /register-tenant)
@bp.route('/register-tenant', methods=['POST'])
def register_tenant():
    data = request.get_json() or {}
    
    required_fields = ['domain_name', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    from app.services.auth_service import AuthService
    result, status_code = AuthService.register_tenant(
        domain_name=data['domain_name'],
        email=data['email'],
        password=data['password'],
        plan_tier=data.get('plan_tier', 'basic')
    )
    
    if status_code == 201:
        # Determine if this is a new tenant or just a new user
        user_id = result['user']['id']
        tenant_id = result['user']['tenant_id']
        access_token = create_access_token(identity=user_id, additional_claims={"tenant_id": tenant_id})
        refresh_token = create_refresh_token(identity=user_id, additional_claims={"tenant_id": tenant_id})
        result['access_token'] = access_token
        result['refresh_token'] = refresh_token
        
        response = make_response(jsonify(result))
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=current_app.config['JWT_COOKIE_SECURE'],
            samesite='Lax',
            max_age=3600
        )
        return response, status_code
    
    return jsonify(result), status_code

@bp.route('/register-user', methods=['POST'])
@jwt_required()
def register_user():
    user_id = get_jwt_identity()  # String (user_id)
    claims = get_jwt()  # Full JWT payload
    current_user = User.query.get_or_404(uuid.UUID(user_id))
    
    # Validate tenant_id from JWT
    if str(current_user.tenant_id) != claims['tenant_id']:
        return jsonify({'error': 'Tenant mismatch'}), 403
    
    # Check if current user has admin role
    if current_user.role != 'admin':
        return jsonify({'error': 'Admin role required'}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ['email', 'password', 'role']
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
    
    return jsonify(result), status_code

@bp.route('/logout', methods=['GET'])
def logout():
    response = make_response(redirect('/'))  # Redirect to landing page
    response.delete_cookie('access_token')   # Clear the access_token cookie
    return response

@bp.route('/initiatives', methods=['GET'])
@jwt_required()
def initiatives():
    user_id = get_jwt_identity()  # String (user_id)
    claims = get_jwt()  # Full JWT payload
    user = User.query.get_or_404(uuid.UUID(user_id))
    tenant = Tenant.query.get_or_404(uuid.UUID(claims['tenant_id']))
    
    # Validate tenant_id consistency
    if user.tenant_id != tenant.id:
        return jsonify({'error': 'Tenant mismatch'}), 403
    
    # In a real application, you would fetch initiatives from the database
    # For now, we'll just render the template with empty data
    initiatives = []
    
    return render_template('dashboard/initiatives.html', 
                          user=user, 
                          tenant=tenant,
                          initiatives=initiatives,
                          active_section='initiatives')

@bp.route('/feedback', methods=['GET'])
@jwt_required()
def feedback():
    user_id = get_jwt_identity()  # String (user_id)
    claims = get_jwt()  # Full JWT payload
    user = User.query.get_or_404(uuid.UUID(user_id))
    tenant = Tenant.query.get_or_404(uuid.UUID(claims['tenant_id']))
    
    # Validate tenant_id consistency
    if user.tenant_id != tenant.id:
        return jsonify({'error': 'Tenant mismatch'}), 403
    
    # In a real application, you would fetch feedback from the database
    # For now, we'll just render the template with empty data
    feedback = []
    
    return render_template('dashboard/feedback.html', 
                          user=user, 
                          tenant=tenant,
                          feedback=feedback,
                          active_section='feedback')

@bp.route('/ideas', methods=['GET'])
@jwt_required()
def ideas():
    user_id = get_jwt_identity()  # String (user_id)
    claims = get_jwt()  # Full JWT payload
    user = User.query.get_or_404(uuid.UUID(user_id))
    tenant = Tenant.query.get_or_404(uuid.UUID(claims['tenant_id']))
    
    # Validate tenant_id consistency
    if user.tenant_id != tenant.id:
        return jsonify({'error': 'Tenant mismatch'}), 403
    
    # In a real application, you would fetch ideas from the database
    # For now, we'll just render the template with empty data
    ideas = []
    
    return render_template('dashboard/ideas.html', 
                          user=user, 
                          tenant=tenant,
                          ideas=ideas,
                          active_section='ideas')