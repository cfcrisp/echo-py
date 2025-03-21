from app.extensions import db
import uuid
from datetime import datetime

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default='In Progress') 
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='goals')
    initiatives = db.relationship('Initiative', back_populates='goal', lazy='dynamic')
    
    def __repr__(self):
        return f'<Goal {self.title}>'