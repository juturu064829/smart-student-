# Smart Student Management System

A full-stack, intelligent **Smart Student Management System** built using Python, Flask, SQLAlchemy ORM, Streamlit, HTML5, CSS3, JavaScript (Bootstrap 5 + glassmorphism theme), and REST APIs.

---

## 🚀 Features

* **Role-Based Authentication**: Secure accounts for Admin, Faculty, and Student roles with password hashing (`Werkzeug`) and session protection.
* **Executive Dashboard**: 10 live KPI cards, interactive Chart.js visualizations, recent activity feeds, and noticeboard announcements.
* **Intelligent Performance Watchlist ("At-Risk Students")**: Automatically flags students with low attendance (< 75%) or failing grades (< 50%).
* **Student & Faculty Management**: Full CRUD operations, filtering by Department, Course, Year, Semester, and detailed tabbed profiles.
* **Attendance Management**: Bulk attendance marking, date-wise logs, progress bars, and attendance warnings.
* **Exams & Grading System**: Automatic score calculation, percentage grading (A+, A, B+, B, C, D, F), GPA computation, and marksheets.
* **Fees Ledger & Faculty Payroll**: Tuition, hostel fee ledgers with receipt tracking; Faculty payroll generation (`Basic + Allowances + Bonus - Deductions`).
* **Streamlit Analytics Dashboard**: Standalone Streamlit application providing interactive Plotly charts and cross-departmental filterable insights.
* **Reporting Hub**: Export CSV and ReportLab PDF reports for all major modules.
* **REST APIs**: Full RESTful JSON endpoints (`/api/v1/...`).

---

## 🛠️ Technology Stack

* **Backend**: Python 3.14, Flask 3.1.3, Flask-SQLAlchemy 3.1.1
* **Database**: SQLite (default local development) / MySQL compatible via SQLAlchemy ORM
* **Analytics**: Streamlit 1.61.1, Plotly 6.9, Pandas 2.1
* **PDF Reports**: ReportLab 5.0
* **Frontend**: HTML5, CSS3 (Glassmorphic Theme + Dark/Light Mode), JavaScript, Bootstrap 5.3, FontAwesome 6, Chart.js

---

## 📁 Directory Structure

```text
smart_student_management_system/
├── app.py                     # Flask application entry point
├── config.py                  # Database & App configurations
├── requirements.txt           # Python dependencies
├── README.md                  # System documentation
├── .env.example               # Environment variable sample
├── models/                    # SQLAlchemy ORM Models
│   ├── user.py
│   ├── department.py
│   ├── course.py
│   ├── subject.py
│   ├── faculty.py
│   ├── student.py
│   ├── attendance.py
│   ├── result.py
│   ├── fee.py
│   ├── salary.py
│   ├── timetable.py
│   ├── announcement.py
│   └── notification.py
├── routes/                    # Flask Blueprints
│   ├── auth_routes.py
│   ├── dashboard_routes.py
│   ├── student_routes.py
│   ├── faculty_routes.py
│   ├── department_routes.py
│   ├── course_routes.py
│   ├── attendance_routes.py
│   ├── result_routes.py
│   ├── fee_routes.py
│   ├── salary_routes.py
│   ├── timetable_routes.py
│   ├── announcement_routes.py
│   ├── report_routes.py
│   └── api_routes.py
├── utils/                     # Business Logic & Helpers
│   ├── decorators.py
│   ├── calculations.py
│   └── report_generator.py
├── database/
│   └── seed_data.py           # Database seeder script
├── streamlit_app/
│   └── app.py                 # Streamlit analytics dashboard
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/                 # Jinja2 HTML templates
└── tests/
    └── test_app.py            # Unit test suite
```

---

## 🔑 Demo Login Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` |
| **Faculty** | `faculty1` (to `faculty20`) | `faculty123` |
| **Student** | `student1` (to `student105`) | `student123` |

---

## 🏃 Running the Application

### 1. Database Seeding (First Time Setup)
```bash
py database/seed_data.py
```

### 2. Flask Web Application
```bash
py app.py
```
Open [http://localhost:5000](http://localhost:5000)

### 3. Streamlit Analytics Dashboard
```bash
streamlit run streamlit_app/app.py
```
Open [http://localhost:8501](http://localhost:8501)
