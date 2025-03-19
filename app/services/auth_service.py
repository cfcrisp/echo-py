# app/services/auth_service.py
from app.models import User, Tenant
from app.extensions import db
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token
from flask import abort, jsonify
import uuid
import re

class AuthService:
    @staticmethod
    def register_tenant(domain_name, email, password, plan_tier='basic'):
        """
        Register a new tenant with an initial admin user if domain_name is new,
        or register a new user under an existing tenant if domain_name exists.
        
        Parameters:
        - domain_name: Domain name of the organization (e.g., example.com)
        - email: Email for the user
        - password: Password for the user
        - plan_tier: Subscription tier (default: 'basic') - used only for new tenants
        
        Returns a tuple of (response_dict, status_code)
        """
        # Validate inputs
        validation_errors = AuthService.validate_registration(domain_name, email, password)
        if validation_errors:
            return {'error': validation_errors}, 400
        
        # Check if email is already in use across all tenants
        if User.query.filter_by(email=email).first():
            return {'error': 'Email already in use'}, 400
        
        # Check if tenant exists by domain_name
        tenant = Tenant.query.filter_by(domain_name=domain_name).first()
        
        if tenant:
            # Domain exists, register a new user under this tenant (default role: 'user')
            return AuthService.register_user(
                tenant_id=tenant.id,
                email=email,
                password=password,
                role='user'  # New users on existing tenants default to 'user'
            )
        else:
            # Domain is new, create a new tenant and its first admin user
            tenant = Tenant(
                domain_name=domain_name,
                plan_tier=plan_tier
            )
            db.session.add(tenant)
            db.session.flush()  # Generate tenant ID
            
            user = User(
                tenant_id=tenant.id,
                email=email,
                role='admin'  # First user of a new tenant is admin
            )
            user.set_password(password)
            db.session.add(user)
            
            db.session.commit()
            
            # Create tokens with user_id as identity and tenant_id as additional claim
            access_token = create_access_token(identity=str(user.id), additional_claims={"tenant_id": str(tenant.id)})
            refresh_token = create_refresh_token(identity=str(user.id), additional_claims={"tenant_id": str(tenant.id)})
            
            return {
                'tenant': {
                    'id': str(tenant.id),
                    'domain_name': tenant.domain_name,
                    'plan_tier': tenant.plan_tier
                },
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'role': user.role,
                    'tenant_id': str(user.tenant_id)
                },
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 201

    @staticmethod
    def register_user(tenant_id, email, password, role):
        """
        Register a new user within an existing tenant
        
        Parameters:
        - tenant_id: UUID of the tenant
        - email: Email for the new user
        - password: Password for the new user
        - role: User role 
        
        Returns the created user object and tokens
        """
        # Validate inputs
        validation_errors = AuthService.validate_registration(None, email, password)
        if validation_errors:
            return {'error': validation_errors}, 400
            
        # Check if tenant exists
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            return {'error': 'Tenant not found'}, 404
            
        # Check if email already exists within tenant
        if User.query.filter_by(tenant_id=tenant_id, email=email).first():
            return {'error': 'Email already in use within this tenant'}, 400
            
        # Validate role
        valid_roles = ['user', 'admin']
        if role not in valid_roles:
            return {'error': f"Invalid role. Must be one of: {', '.join(valid_roles)}"}, 400
            
        # Create new user
        user = User(
            tenant_id=tenant_id,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Create tokens with user_id as identity and tenant_id as additional claim
        access_token = create_access_token(identity=str(user.id), additional_claims={"tenant_id": str(user.tenant_id)})
        refresh_token = create_refresh_token(identity=str(user.id), additional_claims={"tenant_id": str(user.tenant_id)})
        
        return {
            'user': {
                'id': str(user.id),
                'email': user.email,
                'role': user.role,
                'tenant_id': str(user.tenant_id)
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 201
    
    @staticmethod
    def validate_registration(domain_name, email, password):
        """
        Validate registration inputs
        
        Returns None if valid, or error message if invalid
        """
        if domain_name and not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$', domain_name):
            return 'Invalid domain name format'
            
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return 'Invalid email format'
            
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
        
    @staticmethod
    def find_tenant_by_domain(domain_name):
        """
        Find a tenant by domain name
        
        Parameters:
        - domain_name: Domain name to search for
        
        Returns the tenant or None if not found
        """
        return Tenant.query.filter_by(domain_name=domain_name).first()
        
    @staticmethod
    def get_domain_from_email(email):
        """
        Extract domain from email address
        
        Parameters:
        - email: Email address
        
        Returns the domain part of the email
        """
        try:
            return email.split('@')[1]
        except (IndexError, AttributeError):
            return None