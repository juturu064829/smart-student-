# 🎓 Smart Student Management System

A full-stack, intelligent **Smart Student Management System** built using Python, Flask, SQLAlchemy ORM, Streamlit, HTML5, CSS3, JavaScript (Bootstrap 5 + glassmorphism theme), and REST APIs.

---

## 🌐 Application URLs

| Portal | Local URL | Description |
| :--- | :--- | :--- |
| **Main Web Portal** | [http://localhost:5000](http://localhost:5000) | Full college management system & executive dashboard |
| **Login Page** | [http://localhost:5000/login](http://localhost:5000/login) | Multi-credential login (User ID / Email / Username) |
| **Sign Up / Register** | [http://localhost:5000/register](http://localhost:5000/register) | Account registration with auto User ID allocation |
| **User Profile** | [http://localhost:5000/profile](http://localhost:5000/profile) | View permanent User ID, update details, change password |
| **Analytics Dashboard** | [http://localhost:8501](http://localhost:8501) | Streamlit & Plotly analytics with SQLite Database Explorer |

---

## 🚀 Key Features

* **User ID System (`USER-XXXXX`)**: Every user account receives a permanent, sequential unique User ID (e.g., `USER-10001`, `USER-10002`). Users can log in using **User ID**, **Email**, or **Username**.
* **Account Registration**: Self-registration for students and faculty with instant User ID generation and password encryption.
* **Role-Based Access Control**: Granular permissions across Admin, Faculty, and Student roles with secure session handling and `@login_required` decorators.
* **Executive Dashboard**: 10 live KPI cards, interactive Chart.js visualizations, real-time alerts, and campus noticeboard.
* **Intelligent At-Risk Watchlist**: Automatically detects students with attendance below 75% or failing marks below 50%.
* **Student & Faculty Management**: Full CRUD operations with department filtering and detailed tabbed profiles.
* **Bulk Attendance**: Date-wise attendance marking, monthly summaries, and low-attendance warnings.
* **Exams & Auto-Grading**: Subject-wise mark calculation, percentage grading (A+, A, B+, B, C, D, F), GPA computation, and marksheets.
* **Fees & Payroll**: Student fee ledgers with receipt tracking; Faculty payroll calculation (`Basic + Allowances + Bonus - Deductions`).
* **High-Performance Caching System**: Thread-safe in-memory cache, browser `Cache-Control` headers, and automatic asset cache-busting versioning.
* **Streamlit Executive Analytics & Database Explorer**: Live Plotly charts, demographic breakdowns, and interactive SQLite table browser with 1-click CSV exports.
* **Report Generation**: 1-click CSV and ReportLab PDF document exports across all modules.

---

## 🔑 Demo Login Credentials

You can log in using **User ID**, **Username**, or **Email**:

| Role | User ID | Username | Email | Password | Access Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admin** | `USER-10001` | `admin` | `admin@smartcollege.edu` | `admin123` | Full access to all modules, settings & payroll |
| **Faculty** | `USER-10002` *(to `USER-10021`)* | `faculty1` | `faculty1@smartcollege.edu` | `faculty123` | Mark attendance, enter exam marks, view classes |
| **Student** | `USER-10022` *(to `USER-10126`)* | `student1` | `student1@smartcollege.edu` | `student123` | Personal profile, attendance, results & fee ledger |

---

## 🛠️ Technology Stack

* **Backend**: Python 3.14, Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Gunicorn 21.2
* **Database**: SQLite (pre-seeded with 105+ students, 20 faculty) / MySQL compatible
* **Analytics**: Streamlit 1.61.1, Plotly 6.9, Pandas 2.1
* **PDF Engine**: ReportLab 5.0
* **Frontend**: HTML5, CSS3 (Glassmorphic Dark Theme), JavaScript, Bootstrap 5.3, FontAwesome 6, Chart.js

---

## 🏃 Quick Start & Local Execution

### 1. Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### 2. Seed Database (Optional - Database is pre-seeded)
```bash
py database/seed_data.py
```

### 3. Start Flask Web Server
```bash
py app.py
```
Open [http://localhost:5000](http://localhost:5000)

### 4. Start Streamlit Analytics Portal
```bash
py -m streamlit run streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501)

---

## ☁️ Deployment

* **Streamlit Community Cloud**: Connect repo `juturu064829/smart-student-` with main file `streamlit_app.py`.
* **Render.com / Railway**: Connect repo `juturu064829/smart-student-` with build command `pip install -r requirements.txt` and start command `gunicorn app:app`.
