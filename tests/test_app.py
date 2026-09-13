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
            user_count = User.query.count()
            user_with_uid = User.query.filter(User.user_uid.isnot(None)).count()

            print(f"\n[VERIFICATION COUNTS]")
            print(f"Students: {student_count}")
            print(f"Faculty: {faculty_count}")
            print(f"Total Users: {user_count}")
            print(f"Users with User ID (USER-XXXXX): {user_with_uid}")

            self.assertGreaterEqual(student_count, 100)
            self.assertGreaterEqual(faculty_count, 20)
            self.assertEqual(user_count, user_with_uid)

    def test_login_page_renders_with_user_id_and_controls(self):
        """Verify login page renders with User ID support, Remember Me, Show/Hide, and Register link"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn('User ID, Username or Email', html)
        self.assertIn('remember_me', html)
        self.assertIn('togglePasswordVisibility', html)
        self.assertIn('Forgot Password?', html)
        self.assertIn('Create Account', html)
        self.assertIn('Proceed', html)

    def test_login_via_user_id(self):
        """Test logging in using unique User ID (e.g. USER-10001)"""
        response = self.client.post('/login', data={
            'username': 'USER-10001',
            'password': 'admin123'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_login_via_email(self):
        """Test logging in using Email address"""
        response = self.client.post('/login', data={
            'username': 'admin@smartcollege.edu',
            'password': 'admin123'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_login_via_username(self):
        """Test logging in using username"""
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.headers.get('Location', ''))

    def test_registration_and_user_id_allocation(self):
        """Test new user registration, automatic User ID generation, and immediate login with new User ID"""
        reg_email = f"test_student_{os.getpid()}@example.com"
        reg_response = self.client.post('/register', data={
            'full_name': 'New Test Student',
            'email': reg_email,
            'role': 'Student',
            'password': 'testpassword123',
            'confirm_password': 'testpassword123'
        }, follow_redirects=False)

        self.assertEqual(reg_response.status_code, 302)
        redirect_url = reg_response.headers.get('Location', '')
        self.assertIn('/login', redirect_url)
        self.assertIn('user_id=USER-', redirect_url)

        # Retrieve created user from database
        with self.app.app_context():
            created_user = User.query.filter_by(email=reg_email).first()
            self.assertIsNotNone(created_user)
            self.assertTrue(created_user.user_uid.startswith('USER-'))
            new_uid = created_user.user_uid

        # Test login with the newly generated User ID
        login_res = self.client.post('/login', data={
            'username': new_uid,
            'password': 'testpassword123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn('Welcome back, New Test Student', login_res.get_data(as_text=True))

    def test_registration_validation_errors(self):
        """Test registration validation: mismatched passwords, invalid email, duplicate email"""
        # Mismatched passwords
        res_mismatch = self.client.post('/register', data={
            'full_name': 'Test User',
            'email': 'valid@example.com',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        }, follow_redirects=True)
        self.assertIn('Passwords do not match', res_mismatch.get_data(as_text=True))

        # Invalid email format
        res_invalid_email = self.client.post('/register', data={
            'full_name': 'Test User',
            'email': 'not-an-email',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn('valid email', res_invalid_email.get_data(as_text=True))

        # Duplicate email
        res_dup = self.client.post('/register', data={
            'full_name': 'Test User',
            'email': 'admin@smartcollege.edu',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertIn('already exists', res_dup.get_data(as_text=True))

    def test_user_profile_page(self):
        """Test profile page access and detail updates"""
        # Login as Admin
        self.client.post('/login', data={'username': 'USER-10001', 'password': 'admin123'})
        
        # View profile
        res_profile = self.client.get('/profile')
        self.assertEqual(res_profile.status_code, 200)
        html = res_profile.get_data(as_text=True)
        self.assertIn('USER-10001', html)
        self.assertIn('Account Details', html)

        # Update profile full name
        res_update = self.client.post('/profile', data={
            'full_name': 'Lead System Administrator',
            'email': 'admin@smartcollege.edu'
        }, follow_redirects=True)
        self.assertEqual(res_update.status_code, 200)
        self.assertIn('Lead System Administrator', res_update.get_data(as_text=True))

    def test_invalid_login_error_message(self):
        """Invalid credentials show 'Invalid username or password.'"""
        response = self.client.post('/login', data={
            'username': 'USER-99999',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Invalid username or password.', response.get_data(as_text=True))

    def test_logout_and_protection(self):
        """Test logout and protection of unauthorized routes"""
        self.client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        res_logout = self.client.get('/logout')
        self.assertEqual(res_logout.status_code, 302)

        # Access protected route
        res_prot = self.client.get('/dashboard')
        self.assertEqual(res_prot.status_code, 302)
        self.assertIn('/login', res_prot.headers.get('Location', ''))

if __name__ == '__main__':
    unittest.main()
