from app.extensions import db
import uuid
from datetime import datetime
from sqlalchemy.orm import foreign

class Initiative(db.Model):
    __tablename__ = 'initiatives'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    goal_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('goals.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False)
    priority = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='initiatives')
    goal = db.relationship('Goal', back_populates='initiatives')
    ideas = db.relationship('Idea', back_populates='initiative', lazy='dynamic')
    feedback = db.relationship('Feedback', secondary='feedback_initiatives', back_populates='initiatives')
    comments = db.relationship('Comment', primaryjoin="and_(Comment.entity_type=='initiative', foreign(Comment.entity_id)==Initiative.id)", back_populates='initiative', overlaps="idea,feedback")
    
    def __repr__(self):
        return f'<Initiative {self.title}>'