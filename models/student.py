from datetime import datetime
from models import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False, default='Male')
    dob = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    current_year = db.Column(db.Integer, default=1)
    current_semester = db.Column(db.Integer, default=1)
    admission_date = db.Column(db.Date, nullable=True)
    
    guardian_name = db.Column(db.String(100), nullable=True)
    guardian_phone = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Active')  # Active, Graduated, Suspended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy=True, cascade="all, delete-orphan")
    results = db.relationship('Result', backref='student', lazy=True, cascade="all, delete-orphan")
    fee_records = db.relationship('Fee', backref='student', lazy=True, cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def attendance_percentage(self):
        records = self.attendance_records
        if not records:
            return 100.0
        present_count = sum(1 for r in records if r.status in ['Present', 'Late'])
        return round((present_count / len(records)) * 100.0, 1)

    @property
    def average_marks(self):
        res = self.results
        if not res:
            return 0.0
        total_pct = sum(r.percentage for r in res if r.percentage is not None)
        return round(total_pct / len(res), 1)

    @property
    def pending_fee_total(self):
        fees = self.fee_records
        if not fees:
            return 0.0
        return sum(f.pending_amount for f in fees)

    @property
    def risk_assessment(self):
        att = self.attendance_percentage
        avg = self.average_marks
        has_failed = any(r.result_status == 'Fail' for r in self.results)
        
        reasons = []
        if att < 75.0:
            reasons.append(f"Low Attendance ({att}%)")
        if avg < 50.0 and len(self.results) > 0:
            reasons.append(f"Low Marks ({avg}%)")
        if has_failed:
            reasons.append("Failed Subject(s)")

        if att < 65.0 or (avg < 45.0 and len(self.results) > 0) or sum(1 for r in self.results if r.result_status == 'Fail') >= 2:
            return {'level': 'High Risk', 'color': 'danger', 'reasons': reasons}
        elif att < 75.0 or (avg < 55.0 and len(self.results) > 0) or has_failed:
            return {'level': 'Moderate Risk', 'color': 'warning', 'reasons': reasons}
        else:
            return {'level': 'Low Risk / Good', 'color': 'success', 'reasons': []}

    def to_dict(self):
        risk = self.risk_assessment
        return {
            'id': self.id,
            'roll_no': self.roll_no,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'current_year': self.current_year,
            'current_semester': self.current_semester,
            'status': self.status,
            'attendance_percentage': self.attendance_percentage,
            'average_marks': self.average_marks,
            'pending_fee': self.pending_fee_total,
            'risk_level': risk['level'],
            'risk_color': risk['color'],
            'risk_reasons': ", ".join(risk['reasons']) if risk['reasons'] else "None"
        }
