from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.department import Department
from models.course import Course
from models.subject import Subject
from models.faculty import Faculty
from models.student import Student
from models.attendance import Attendance
from models.result import Result
from models.fee import Fee
from models.salary import Salary
from models.timetable import Timetable
from models.announcement import Announcement
from models.notification import Notification
