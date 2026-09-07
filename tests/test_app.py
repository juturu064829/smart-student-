import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Student, Faculty, Department, Course, User, Attendance, Result, Fee, Salary

class TestSmartSMS(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_database_counts(self):
        with self.app.app_context():
            student_count = Student.query.count()
            faculty_count = Faculty.query.count()
            dept_count = Department.query.count()
            course_count = Course.query.count()
            att_count = Attendance.query.count()
            result_count = Result.query.count()
            fee_count = Fee.query.count()
            salary_count = Salary.query.count()

            print(f"\n[VERIFICATION COUNTS]")
            print(f"Students: {student_count}")
            print(f"Faculty: {faculty_count}")
            print(f"Departments: {dept_count}")
            print(f"Courses: {course_count}")
            print(f"Attendance Logs: {att_count}")
            print(f"Exam Results: {result_count}")
            print(f"Fee Records: {fee_count}")
            print(f"Salary Records: {salary_count}")

            self.assertGreaterEqual(student_count, 100)
            self.assertGreaterEqual(faculty_count, 20)
            self.assertGreaterEqual(dept_count, 5)

    def test_login_and_api(self):
        # Test Login Page Render
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

        # Test API Endpoint
        api_res = self.client.get('/api/v1/students')
        self.assertEqual(api_res.status_code, 200)
        json_data = api_res.get_json()
        self.assertEqual(json_data['status'], 'success')
        self.assertGreater(json_data['count'], 0)

if __name__ == '__main__':
    unittest.main()
