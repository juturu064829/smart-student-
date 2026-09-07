from datetime import datetime, date
from models import db

class Salary(db.Model):
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    
    basic_salary = db.Column(db.Float, default=50000.0)
    allowances = db.Column(db.Float, default=5000.0)
    bonus = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=2000.0)
    net_salary = db.Column(db.Float, default=53000.0)
    
    payment_date = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(20), default='Pending')  # Paid, Pending
    month = db.Column(db.String(20), nullable=False, default='August')
    year = db.Column(db.Integer, nullable=False, default=2026)
    payment_method = db.Column(db.String(30), default='Bank Transfer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_net_salary(self):
        self.net_salary = (self.basic_salary or 0.0) + (self.allowances or 0.0) + \
                          (self.bonus or 0.0) - (self.deductions or 0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty.full_name if self.faculty else None,
            'emp_id': self.faculty.emp_id if self.faculty else None,
            'department_name': self.faculty.department.name if self.faculty and self.faculty.department else None,
            'basic_salary': self.basic_salary,
            'allowances': self.allowances,
            'bonus': self.bonus,
            'deductions': self.deductions,
            'net_salary': self.net_salary,
            'payment_date': self.payment_date.strftime('%Y-%m-%d') if self.payment_date else None,
            'payment_status': self.payment_status,
            'month': self.month,
            'year': self.year,
            'payment_method': self.payment_method
        }
