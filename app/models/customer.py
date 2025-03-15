from app.extensions import db
import uuid
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    revenue = db.Column(db.Numeric(12, 2))
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='customers')
    ideas = db.relationship('Idea', secondary='ideas_customers', back_populates='customers')
    feedback = db.relationship('Feedback', secondary='feedback_customers', back_populates='customers')
    
    def __repr__(self):
        return f'<Customer {self.name}>'