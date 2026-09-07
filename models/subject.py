from models import db

class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=1)
    credits = db.Column(db.Integer, default=4)
    
    max_internal = db.Column(db.Float, default=20.0)
    max_assignment = db.Column(db.Float, default=10.0)
    max_practical = db.Column(db.Float, default=20.0)
    max_external = db.Column(db.Float, default=50.0)

    # Relationships
    results = db.relationship('Result', backref='subject', lazy=True, cascade="all, delete-orphan")
    attendance_records = db.relationship('Attendance', backref='subject', lazy=True)
    timetable_entries = db.relationship('Timetable', backref='subject', lazy=True)

    @property
    def total_max_marks(self):
        return (self.max_internal or 0) + (self.max_assignment or 0) + (self.max_practical or 0) + (self.max_external or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'semester': self.semester,
            'credits': self.credits,
            'max_internal': self.max_internal,
            'max_assignment': self.max_assignment,
            'max_practical': self.max_practical,
            'max_external': self.max_external,
            'total_max_marks': self.total_max_marks
        }
