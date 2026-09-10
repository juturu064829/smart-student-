import os
import sys
from flask import Flask, render_template
from config import Config
from models import db

def is_running_under_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is not None:
            return True
    except Exception:
        pass
    try:
        import streamlit as st
        if getattr(st, "_is_running_with_streamlit", False):
            return True
    except Exception:
        pass
    return False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.student_routes import student_bp
    from routes.faculty_routes import faculty_bp
    from routes.department_routes import department_bp
    from routes.course_routes import course_bp
    from routes.attendance_routes import attendance_bp
    from routes.result_routes import result_bp
    from routes.fee_routes import fee_bp
    from routes.salary_routes import salary_bp
    from routes.timetable_routes import timetable_bp
    from routes.announcement_routes import announcement_bp
    from routes.report_routes import report_bp
    from routes.api_routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(department_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(fee_bp)
    app.register_blueprint(salary_bp)
    app.register_blueprint(timetable_bp)
    app.register_blueprint(announcement_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(api_bp)

    # Custom Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    # If Streamlit is running app.py as main entry point
    if is_running_under_streamlit():
        from streamlit_app import run_streamlit_app
        run_streamlit_app()
    else:
        # Flask server startup
        with app.app_context():
            db.create_all()
            from models import Student
            if Student.query.count() == 0:
                try:
                    from database.seed_data import seed_database
                    seed_database()
                except Exception as e:
                    print(f"Auto-seeding note: {e}")

        port = int(os.environ.get('PORT', 5000))
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
        print(f"Starting Smart Student Management System on http://0.0.0.0:{port}")
        app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=False)
