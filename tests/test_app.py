import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, Student, Faculty, Department, Course, User, Attendance, Result, Fee, Salary

class TestSmartSMSAuthentication(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_database_counts(self):
        with self.app.app_context():
            student_count = Student.query.count()
            faculty_count = Faculty.query.count()
            dept_count = Department.query.count()
            course_count = Course.query.count()
            att_count = Attendance.query.count()
            result_count = Result.query.count()

            print(f"\n[VERIFICATION COUNTS]")
            print(f"Students: {student_count}")
            print(f"Faculty: {faculty_count}")
            print(f"Departments: {dept_count}")
            print(f"Courses: {course_count}")
            print(f"Attendance Logs: {att_count}")
            print(f"Exam Results: {result_count}")

            self.assertGreaterEqual(student_count, 100)
            self.assertGreaterEqual(faculty_count, 20)
            self.assertGreaterEqual(dept_count, 5)

    def test_login_page_renders_with_proceed_and_show_hide(self):
        """Verify login page renders with Proceed button and Show/Hide password toggle"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Proceed', html)
        self.assertIn('togglePasswordVisibility', html)
        self.assertIn('Forgot Password?', html)
        self.assertIn('username_input', html)
        self.assertIn('password_input', html)

    def test_valid_login_redirects_to_dashboard(self):
        """Valid login credentials -> Redirect to Dashboard"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

        # Follow redirect and verify session
        res_follow = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(res_follow.status_code, 200)
        self.assertIn('Welcome back', res_follow.get_data(as_text=True))

    def test_invalid_password_displays_error(self):
        """Invalid password -> Displays 'Invalid username or password.' without redirecting"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpassword999'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('Invalid username or password.', html)

    def test_empty_credentials_validation(self):
        """Empty fields -> Displays appropriate validation message"""
        # Both empty
        res_both = self.client.post('/login', data={'username': '', 'password': ''}, follow_redirects=True)
        self.assertIn('Please enter', res_both.get_data(as_text=True))

        # Empty password
        res_pw = self.client.post('/login', data={'username': 'admin', 'password': ''}, follow_redirects=True)
        self.assertIn('Please enter your password', res_pw.get_data(as_text=True))

        # Empty username
        res_user = self.client.post('/login', data={'username': '', 'password': 'admin123'}, follow_redirects=True)
        self.assertIn('Please enter your username', res_user.get_data(as_text=True))

    def test_authenticated_user_login_redirect(self):
        """Logged in user visiting /login -> Automatically redirected to Dashboard"""
        # Login first
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        # Attempt to visit /login
        res_login_again = self.client.get('/login')
        self.assertEqual(res_login_again.status_code, 302)
        self.assertIn('/dashboard', res_login_again.headers.get('Location', ''))

    def test_logout_invalidates_session(self):
        """Logout -> Clears session and redirects to login"""
        # Login
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        # Logout
        res_logout = self.client.get('/logout')
        self.assertEqual(res_logout.status_code, 302)
        self.assertIn('/login', res_logout.headers.get('Location', ''))

        # Check protected dashboard route redirects to login
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 302)
        self.assertIn('/login', res_dash.headers.get('Location', ''))

    def test_unauthorized_access_redirects_to_login(self):
        """Unauthenticated user accessing protected routes -> Redirect to Login"""
        with self.client.session_transaction() as sess:
            sess.clear()
        res = self.client.get('/students/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers.get('Location', ''))

if __name__ == '__main__':
    unittest.main()
