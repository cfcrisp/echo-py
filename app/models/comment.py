from app.extensions import db
import uuid
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    entity_type = db.Column(db.String(20), nullable=False)
    entity_id = db.Column(db.UUID(as_uuid=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='comments')
    
    # Dynamic relationships based on entity_type
    @declared_attr
    def idea(cls):
        return relationship(
            'Idea',
            primaryjoin="and_(Comment.entity_type=='idea', Comment.entity_id==Idea.id)",
            foreign_keys=[cls.entity_id],
            viewonly=True
        )
    
    @declared_attr
    def feedback(cls):
        return relationship(
            'Feedback',
            primaryjoin="and_(Comment.entity_type=='feedback', Comment.entity_id==Feedback.id)",
            foreign_keys=[cls.entity_id],
            viewonly=True
        )
    
    @declared_attr
    def initiative(cls):
        return relationship(
            'Initiative',
            primaryjoin="and_(Comment.entity_type=='initiative', Comment.entity_id==Initiative.id)",
            foreign_keys=[cls.entity_id],
            viewonly=True
        )
    
    def __repr__(self):
        return f'<Comment {self.id} on {self.entity_type} {self.entity_id}>'