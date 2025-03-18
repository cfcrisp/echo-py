from app.models import User, Tenant
from app.extensions import db
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token
from flask import abort, jsonify
import uuid
import re

class AuthService:
    @staticmethod
    def register_tenant(tenant_name, username, email, password, plan_tier='basic'):
        """
        Register a new tenant with an admin user
        
        Parameters:
        - tenant_name: Name of the tenant/organization
        - username: Username for the admin user
        - email: Email for the admin user
        - password: Password for the admin user
        - plan_tier: Subscription tier (default: 'basic')
        
        Returns a tuple of (tenant, user, access_token, refresh_token)
        """
        # Validate inputs
        validation_errors = AuthService.validate_registration(tenant_name, username, email, password)
        if validation_errors:
            return {'error': validation_errors}, 400
        
        # Check if email is already in use
        if User.query.filter_by(email=email).first():
            return {'error': 'Email already in use'}, 400
            
        # Create new tenant
        tenant = Tenant(
            name=tenant_name,
            plan_tier=plan_tier
        )
        db.session.add(tenant)
        
        # Create admin user for the tenant
        user = User(
            tenant_id=tenant.id,
            username=username,
            email=email,
            role='admin'
        )
        user.set_password(password)
        db.session.add(user)
        
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
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
        }, 201
    
    @staticmethod
    def register_user(tenant_id, username, email, password, role='business'):
        """
        Register a new user within an existing tenant
        
        Parameters:
        - tenant_id: UUID of the tenant
        - username: Username for the new user
        - email: Email for the new user
        - password: Password for the new user
        - role: User role (default: 'business')
        
        Returns the created user object and tokens
        """
        # Validate inputs
        validation_errors = AuthService.validate_registration(None, username, email, password)
        if validation_errors:
            return {'error': validation_errors}, 400
            
        # Check if username or email already exists within tenant
        if User.query.filter_by(tenant_id=tenant_id, username=username).first():
            return {'error': 'Username already in use within this tenant'}, 400
        if User.query.filter_by(tenant_id=tenant_id, email=email).first():
            return {'error': 'Email already in use within this tenant'}, 400
            
        # Validate role
        valid_roles = ['admin', 'business', 'product']
        if role not in valid_roles:
            return {'error': f"Invalid role. Must be one of: {', '.join(valid_roles)}"}, 400
            
        # Create new user
        user = User(
            tenant_id=tenant_id,
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'tenant_id': str(user.tenant_id)
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201
    
    @staticmethod
    def validate_registration(tenant_name, username, email, password):
        """
        Validate registration inputs
        
        Returns None if valid, or error message if invalid
        """
        # Check for empty fields
        if username and len(username.strip()) < 3:
            return 'Username must be at least 3 characters'
            
        if tenant_name and len(tenant_name.strip()) < 2:
            return 'Organization name must be at least 2 characters'
            
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return 'Invalid email format'
            
        # Validate password strength
        if len(password) < 8:
            return 'Password must be at least 8 characters'
            
        return None
    
    @staticmethod
    def get_current_user():
        """Get the currently authenticated user from JWT token"""
        user_id = get_jwt_identity()
        if not user_id:
            abort(401, description="Authentication required")
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            abort(401, description="Invalid authentication token")
            
        user = User.query.get(user_uuid)
        if not user:
            abort(401, description="User not found")
            
        return user
    
    @staticmethod
    def verify_tenant_access(tenant_id):
        """Verify the current user has access to the given tenant"""
        current_user = AuthService.get_current_user()
        
        if current_user.tenant_id != tenant_id:
            abort(403, description="Access to this tenant is forbidden")
            
        return current_user
    
    @staticmethod
    def verify_admin_role():
        """Verify the current user has admin role"""
        current_user = AuthService.get_current_user()
        
        if current_user.role != 'admin':
            abort(403, description="Admin role required")
            
        return current_user
    
    @staticmethod
    def ensure_user_tenant_match(user, entity_or_tenant_id):
        """
        Ensure a user belongs to the same tenant as an entity or tenant ID
        
        Parameters:
        - user: User model instance
        - entity_or_tenant_id: Either a UUID object/string of a tenant ID or
                              an entity object with a tenant_id attribute
        
        Returns True if matching, aborts with 403 if not
        """
        tenant_id = getattr(entity_or_tenant_id, 'tenant_id', entity_or_tenant_id)
        
        if user.tenant_id != tenant_id:
            abort(403, description="Access forbidden")
            
        return True