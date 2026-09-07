from datetime import datetime
from models import db

class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False, default='Male')
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    designation = db.Column(db.String(50), nullable=False, default='Assistant Professor')
    qualification = db.Column(db.String(100), nullable=True)
    joining_date = db.Column(db.Date, nullable=True)
    experience_years = db.Column(db.Integer, default=0)
    basic_salary = db.Column(db.Float, default=50000.0)
    
    address = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, On Leave
    photo_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    salaries = db.relationship('Salary', backref='faculty', lazy=True, cascade="all, delete-orphan")
    timetable_entries = db.relationship('Timetable', backref='faculty', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            'id': self.id,
            'emp_id': self.emp_id,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'designation': self.designation,
            'qualification': self.qualification,
            'joining_date': self.joining_date.strftime('%Y-%m-%d') if self.joining_date else None,
            'experience_years': self.experience_years,
            'basic_salary': self.basic_salary,
            'address': self.address,
            'status': self.status,
            'photo_url': self.photo_url
        }
