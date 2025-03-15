from app.models import User, Tenant
from app.extensions import db
from flask_jwt_extended import get_jwt_identity
from flask import abort
import uuid

class AuthService:
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