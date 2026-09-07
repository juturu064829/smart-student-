from models import db

class Timetable(db.Model):
    __tablename__ = 'timetables'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    
    room_number = db.Column(db.String(30), nullable=False, default='Hall A-101')
    day_of_week = db.Column(db.String(20), nullable=False, default='Monday')  # Monday, Tuesday, etc.
    start_time = db.Column(db.String(10), nullable=False, default='09:00 AM')
    end_time = db.Column(db.String(10), nullable=False, default='10:00 AM')
    semester = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    department = db.relationship('Department', backref='timetable_entries')
    course = db.relationship('Course', backref='timetable_entries')

    def to_dict(self):
        return {
            'id': self.id,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else None,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty.full_name if self.faculty else None,
            'room_number': self.room_number,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'semester': self.semester
        }
