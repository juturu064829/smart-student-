import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart_student_management_system_super_secret_key_2026')
    
    # SQLAlchemy configuration: Default to SQLite for easy local dev, fallback to MySQL if DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(BASE_DIR, "smart_sms.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # Academic Configuration
    ATTENDANCE_WARNING_THRESHOLD = 75.0  # Percentage below which attendance triggers a warning
    FAILING_GRADE_THRESHOLD = 50.0       # Average marks below which triggers academic risk
