from datetime import datetime
from models import db

class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    internal_marks = db.Column(db.Float, default=0.0)
    assignment_marks = db.Column(db.Float, default=0.0)
    practical_marks = db.Column(db.Float, default=0.0)
    external_marks = db.Column(db.Float, default=0.0)
    
    total_marks = db.Column(db.Float, default=0.0)
    percentage = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(5), default='F')
    grade_point = db.Column(db.Float, default=0.0)
    result_status = db.Column(db.String(10), default='Fail')  # Pass, Fail
    
    semester = db.Column(db.Integer, nullable=False, default=1)
    academic_year = db.Column(db.String(20), nullable=False, default='2025-2026')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def calculate_grade(self):
        from utils.calculations import calculate_grade_and_status
        subj_max = self.subject.total_max_marks if self.subject else 100.0
        self.total_marks = (self.internal_marks or 0.0) + (self.assignment_marks or 0.0) + \
                           (self.practical_marks or 0.0) + (self.external_marks or 0.0)
        self.percentage = round((self.total_marks / subj_max) * 100.0, 1) if subj_max > 0 else 0.0
        
        g_data = calculate_grade_and_status(self.percentage)
        self.grade = g_data['grade']
        self.grade_point = g_data['grade_point']
        self.result_status = g_data['status']

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'roll_no': self.student.roll_no if self.student else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'subject_code': self.subject.code if self.subject else None,
            'internal_marks': self.internal_marks,
            'assignment_marks': self.assignment_marks,
            'practical_marks': self.practical_marks,
            'external_marks': self.external_marks,
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'grade': self.grade,
            'grade_point': self.grade_point,
            'result_status': self.result_status,
            'semester': self.semester,
            'academic_year': self.academic_year
        }
