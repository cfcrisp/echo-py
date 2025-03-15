from app.extensions import db
import uuid
from datetime import datetime

# Junction table for ideas and customers
ideas_customers = db.Table('ideas_customers',
    db.Column('idea_id', db.UUID(as_uuid=True), db.ForeignKey('ideas.id', ondelete='CASCADE'), primary_key=True),
    db.Column('customer_id', db.UUID(as_uuid=True), db.ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True)
)

class Idea(db.Model):
    __tablename__ = 'ideas'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    initiative_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('initiatives.id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), nullable=False)
    effort = db.Column(db.String(5), nullable=False)
    source = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='ideas')
    initiative = db.relationship('Initiative', back_populates='ideas')
    customers = db.relationship('Customer', secondary=ideas_customers, back_populates='ideas')
    comments = db.relationship('Comment', primaryjoin="and_(Comment.entity_type=='idea', Comment.entity_id==Idea.id)", back_populates='idea')
    
    def __repr__(self):
        return f'<Idea {self.title}>'