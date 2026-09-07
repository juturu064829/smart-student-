from datetime import datetime
from models import db

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_role = db.Column(db.String(20), default='All')  # All, Faculty, Student
    category = db.Column(db.String(30), default='Academic')  # Academic, Exam, Holiday, Fee, General
    priority = db.Column(db.String(20), default='Normal')  # Normal, High, Urgent
    
    created_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    author = db.relationship('User', foreign_keys=[created_by_user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'target_role': self.target_role,
            'category': self.category,
            'priority': self.priority,
            'author_username': self.author.username if self.author else 'System Admin',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }
