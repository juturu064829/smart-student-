from datetime import datetime, date
from models import db

class Fee(db.Model):
    __tablename__ = 'fees'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    
    tuition_fee = db.Column(db.Float, default=40000.0)
    exam_fee = db.Column(db.Float, default=2000.0)
    library_fee = db.Column(db.Float, default=1500.0)
    hostel_fee = db.Column(db.Float, default=0.0)
    other_fee = db.Column(db.Float, default=1000.0)
    
    total_fee = db.Column(db.Float, default=44500.0)
    paid_amount = db.Column(db.Float, default=0.0)
    pending_amount = db.Column(db.Float, default=44500.0)
    
    payment_date = db.Column(db.Date, nullable=True)
    payment_status = db.Column(db.String(20), default='Pending')  # Paid, Partially Paid, Pending
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def update_totals(self):
        self.total_fee = (self.tuition_fee or 0.0) + (self.exam_fee or 0.0) + (self.library_fee or 0.0) + \
                         (self.hostel_fee or 0.0) + (self.other_fee or 0.0)
        self.pending_amount = max(0.0, self.total_fee - (self.paid_amount or 0.0))
        
        if self.pending_amount <= 0:
            self.payment_status = 'Paid'
        elif self.paid_amount > 0:
            self.payment_status = 'Partially Paid'
        else:
            self.payment_status = 'Pending'

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'roll_no': self.student.roll_no if self.student else None,
            'tuition_fee': self.tuition_fee,
            'exam_fee': self.exam_fee,
            'library_fee': self.library_fee,
            'hostel_fee': self.hostel_fee,
            'other_fee': self.other_fee,
            'total_fee': self.total_fee,
            'paid_amount': self.paid_amount,
            'pending_amount': self.pending_amount,
            'payment_date': self.payment_date.strftime('%Y-%m-%d') if self.payment_date else None,
            'payment_status': self.payment_status,
            'remarks': self.remarks
        }
