from app.extensions import db
import uuid
from datetime import datetime
from sqlalchemy.orm import foreign

# Junction table for feedback and customers
feedback_customers = db.Table('feedback_customers',
    db.Column('feedback_id', db.UUID(as_uuid=True), db.ForeignKey('feedback.id', ondelete='CASCADE'), primary_key=True),
    db.Column('customer_id', db.UUID(as_uuid=True), db.ForeignKey('customers.id', ondelete='CASCADE'), primary_key=True)
)

# Junction table for feedback and initiatives
feedback_initiatives = db.Table('feedback_initiatives',
    db.Column('feedback_id', db.UUID(as_uuid=True), db.ForeignKey('feedback.id', ondelete='CASCADE'), primary_key=True),
    db.Column('initiative_id', db.UUID(as_uuid=True), db.ForeignKey('initiatives.id', ondelete='CASCADE'), primary_key=True)
)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    sentiment = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', back_populates='feedback')
    customers = db.relationship('Customer', secondary=feedback_customers, back_populates='feedback')
    initiatives = db.relationship('Initiative', secondary=feedback_initiatives, back_populates='feedback')
    comments = db.relationship('Comment', primaryjoin="and_(Comment.entity_type=='feedback', foreign(Comment.entity_id)==Feedback.id)", back_populates='feedback', overlaps="idea,initiative")
    
    def __repr__(self):
        return f'<Feedback {self.title}>'