from app.extensions import db
import uuid
from datetime import datetime

class Tenant(db.Model):
    __tablename__ = 'tenants'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    plan_tier = db.Column(db.String(20), nullable=False, default='basic')
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='tenant', cascade='all, delete-orphan')
    goals = db.relationship('Goal', back_populates='tenant', cascade='all, delete-orphan')
    initiatives = db.relationship('Initiative', back_populates='tenant', cascade='all, delete-orphan')
    customers = db.relationship('Customer', back_populates='tenant', cascade='all, delete-orphan')
    ideas = db.relationship('Idea', back_populates='tenant', cascade='all, delete-orphan')
    feedback = db.relationship('Feedback', back_populates='tenant', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Tenant {self.name}>'