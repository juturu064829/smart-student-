from datetime import datetime
from models import db

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    duration_years = db.Column(db.Integer, default=4)
    total_semesters = db.Column(db.Integer, default=8)
    credits = db.Column(db.Integer, default=120)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subjects = db.relationship('Subject', backref='course', lazy=True, cascade="all, delete-orphan")
    students = db.relationship('Student', backref='course', lazy=True)
    lead_faculty = db.relationship('Faculty', backref='managed_courses', foreign_keys=[faculty_id])

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'duration_years': self.duration_years,
            'total_semesters': self.total_semesters,
            'credits': self.credits,
            'faculty_id': self.faculty_id,
            'faculty_name': f"{self.lead_faculty.first_name} {self.lead_faculty.last_name}" if self.lead_faculty else "Unassigned",
            'description': self.description,
            'status': self.status,
            'total_students': len(self.students)
        }
