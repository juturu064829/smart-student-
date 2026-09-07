from datetime import datetime
from models import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    hod_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    courses = db.relationship('Course', backref='department', lazy=True, cascade="all, delete-orphan")
    faculty_members = db.relationship('Faculty', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'hod_name': self.hod_name,
            'email': self.email,
            'phone': self.phone,
            'description': self.description,
            'status': self.status,
            'total_students': len(self.students),
            'total_faculty': len(self.faculty_members),
            'total_courses': len(self.courses)
        }
