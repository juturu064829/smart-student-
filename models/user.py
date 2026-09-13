from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    user_uid = db.Column(db.String(30), unique=True, nullable=True, index=True)  # e.g., USER-10001
    full_name = db.Column(db.String(120), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Student')  # Admin, Faculty, Student
    status = db.Column(db.String(20), default='Active')  # Active, Inactive
    
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='SET NULL'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    faculty_profile = db.relationship('Faculty', backref='user_account', uselist=False, foreign_keys=[faculty_id])
    student_profile = db.relationship('Student', backref='user_account', uselist=False, foreign_keys=[student_id])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_next_user_uid():
        """Generates a sequential, unique User ID formatted as USER-10001, USER-10002, etc."""
        try:
            last_user = User.query.filter(User.user_uid.like('USER-%')).order_by(User.id.desc()).first()
            if last_user and last_user.user_uid:
                parts = last_user.user_uid.split('-')
                if len(parts) == 2 and parts[1].isdigit():
                    return f"USER-{int(parts[1]) + 1}"
            count = User.query.count()
            return f"USER-{10001 + count}"
        except Exception:
            count = User.query.count()
            return f"USER-{10001 + count}"

    def to_dict(self):
        return {
            'id': self.id,
            'user_uid': self.user_uid,
            'full_name': self.full_name,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'faculty_id': self.faculty_id,
            'student_id': self.student_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
