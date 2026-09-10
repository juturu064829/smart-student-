import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
import sys

# Ensure project root is on sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

DB_PATH = os.path.join(BASE_DIR, 'smart_sms.db')

def init_db_if_needed():
    need_seed = False
    if not os.path.exists(DB_PATH):
        need_seed = True
    else:
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM students")
            count = cur.fetchone()[0]
            conn.close()
            if count == 0:
                need_seed = True
        except Exception:
            need_seed = True

    if need_seed:
        try:
            from database.seed_data import seed_database
            seed_database()
        except Exception as e:
            st.warning(f"Note: Database auto-seed attempt: {e}")

def get_connection():
    init_db_if_needed()
    return sqlite3.connect(DB_PATH)

def run_streamlit_app():
    # Page Configuration
    st.set_page_config(
        page_title="Smart SMS - Streamlit Analytics Dashboard",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS styling for Streamlit
    st.markdown("""
        <style>
        .main { background-color: #0f172a; color: #f8fafc; }
        .stMetric { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; }
        .css-1544g2n { background-color: #1e293b; }
        </style>
    """, unsafe_allow_html=True)

    conn = get_connection()

    # Sidebar Filters
    st.sidebar.image("https://img.icons8.com/isometric-line/100/4f46e5/graduation-cap.png", width=70)
    st.sidebar.title("🎓 Executive Analytics")
    st.sidebar.markdown("---")

    menu = st.sidebar.radio(
        "Select Analytics View",
        ["Executive Overview", "Student Demographics", "Attendance Analytics", "Exam & Performance", "Faculty & Payroll", "Financial Fees"],
        key="main_analytics_view_radio"
    )

    # Load Departments & Courses for filters
    try:
        depts_df = pd.read_sql_query("SELECT id, name, code FROM departments", conn)
        courses_df = pd.read_sql_query("SELECT id, name, code FROM courses", conn)
        dept_options = ["All"] + list(depts_df['code'].unique())
        course_options = ["All"] + list(courses_df['code'].unique())
    except Exception:
        depts_df = pd.DataFrame()
        courses_df = pd.DataFrame()
        dept_options = ["All"]
        course_options = ["All"]

    selected_dept_code = st.sidebar.selectbox("Filter Department", dept_options, key="filter_dept_selectbox")
    selected_course_code = st.sidebar.selectbox("Filter Course", course_options, key="filter_course_selectbox")

    st.sidebar.markdown("---")
    st.sidebar.info("💡 Connected directly to SQLite Database (`smart_sms.db`).")

    # ----------------------------------------------------
    # 1. EXECUTIVE OVERVIEW
    # ----------------------------------------------------
    if menu == "Executive Overview":
        st.title("📊 Executive College Overview")
        st.markdown("Real-time high level metrics across departments, students, faculty, and finances.")

        total_students = pd.read_sql_query("SELECT COUNT(*) FROM students", conn).iloc[0, 0]
        total_faculty = pd.read_sql_query("SELECT COUNT(*) FROM faculty", conn).iloc[0, 0]
        total_depts = pd.read_sql_query("SELECT COUNT(*) FROM departments", conn).iloc[0, 0]
        total_pending_fee = pd.read_sql_query("SELECT SUM(pending_amount) FROM fees", conn).iloc[0, 0] or 0.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Enrolled Students", f"{total_students}", "Active")
        col2.metric("Faculty Members", f"{total_faculty}", "Staff")
        col3.metric("Academic Depts", f"{total_depts}", "Departments")
        col4.metric("Pending Fee Dues", f"${total_pending_fee:,.2f}", "Outstanding", delta_color="inverse")

        st.markdown("---")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Students by Department")
            df_dept_stu = pd.read_sql_query("""
                SELECT d.name as Department, COUNT(s.id) as StudentCount 
                FROM departments d 
                LEFT JOIN students s ON d.id = s.department_id 
                GROUP BY d.id
            """, conn)
            fig1 = px.bar(
                df_dept_stu,
                x="Department",
                y="StudentCount",
                color="Department",
                text_auto=True,
                color_discrete_sequence=['#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6']
            )
            fig1.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)

        with col_chart2:
            st.subheader("Attendance Distribution")
            df_att_dist = pd.read_sql_query("""
                SELECT status, COUNT(*) as count 
                FROM attendance 
                GROUP BY status
            """, conn)
            fig2 = px.pie(df_att_dist, names="status", values="count", hole=0.4, color_discrete_sequence=['#10b981', '#ef4444', '#f59e0b', '#06b6d4'])
            fig2.update_layout(template="plotly_dark")
            st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------------
    # 2. STUDENT DEMOGRAPHICS
    # ----------------------------------------------------
    elif menu == "Student Demographics":
        st.title("👨‍🎓 Student Demographics & Breakdown")

        query = """
            SELECT s.roll_no, s.first_name || ' ' || s.last_name as name, s.gender, s.city, s.state, d.name as department, c.name as course, s.current_year
            FROM students s
            JOIN departments d ON s.department_id = d.id
            JOIN courses c ON s.course_id = c.id
        """
        students_df = pd.read_sql_query(query, conn)

        if selected_dept_code != "All" and not depts_df.empty:
            dept_name = depts_df[depts_df['code'] == selected_dept_code]['name'].values[0]
            students_df = students_df[students_df['department'] == dept_name]

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Gender Breakdown")
            gender_fig = px.pie(students_df, names="gender", title="Gender Diversity Ratio", color_discrete_sequence=['#6366f1', '#ec4899', '#06b6d4'])
            gender_fig.update_layout(template="plotly_dark")
            st.plotly_chart(gender_fig, use_container_width=True)

        with col2:
            st.subheader("Year-wise Student Distribution")
            year_fig = px.histogram(students_df, x="current_year", color="current_year", nbins=4, title="Students per Academic Year")
            year_fig.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(year_fig, use_container_width=True)

        st.subheader("Filtered Student Roster")
        st.dataframe(students_df, use_container_width=True)

    # ----------------------------------------------------
    # 3. ATTENDANCE ANALYTICS
    # ----------------------------------------------------
    elif menu == "Attendance Analytics":
        st.title("📋 Attendance & Risk Tracking Analytics")

        df_risk = pd.read_sql_query("""
            SELECT s.roll_no, s.first_name || ' ' || s.last_name as name, d.code as dept,
                   COUNT(a.id) as total_days,
                   SUM(CASE WHEN a.status IN ('Present', 'Late') THEN 1 ELSE 0 END) as present_days
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            LEFT JOIN departments d ON s.department_id = d.id
            GROUP BY s.id
        """, conn)

        df_risk['Attendance_Pct'] = (df_risk['present_days'] / df_risk['total_days'] * 100).round(1).fillna(100.0)

        st.subheader("Attendance Percentage Histogram")
        hist_fig = px.histogram(df_risk, x="Attendance_Pct", nbins=10, title="Student Attendance % Distribution", color_discrete_sequence=['#10b981'])
        hist_fig.update_layout(template="plotly_dark")
        st.plotly_chart(hist_fig, use_container_width=True)

        st.subheader("⚠️ Attendance Risk Flag (< 75%)")
        low_att_df = df_risk[df_risk['Attendance_Pct'] < 75.0]
        st.dataframe(low_att_df, use_container_width=True)

    # ----------------------------------------------------
    # 4. EXAM & PERFORMANCE
    # ----------------------------------------------------
    elif menu == "Exam & Performance":
        st.title("📈 Academic Exam Results & Grade Analytics")

        df_results = pd.read_sql_query("""
            SELECT r.grade, r.result_status, r.percentage, r.total_marks, sub.name as subject_name
            FROM results r
            JOIN subjects sub ON r.subject_id = sub.id
        """, conn)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Grade Frequency Distribution")
            grade_fig = px.bar(df_results['grade'].value_counts().reset_index(), x="grade", y="count", color="grade", title="Grade Distribution Count")
            grade_fig.update_layout(template="plotly_dark")
            st.plotly_chart(grade_fig, use_container_width=True)

        with col2:
            st.subheader("Pass vs Fail Percentage")
            pf_fig = px.pie(df_results, names="result_status", color="result_status", color_discrete_map={'Pass':'#10b981', 'Fail':'#ef4444'})
            pf_fig.update_layout(template="plotly_dark")
            st.plotly_chart(pf_fig, use_container_width=True)

    # ----------------------------------------------------
    # 5. FACULTY & PAYROLL
    # ----------------------------------------------------
    elif menu == "Faculty & Payroll":
        st.title("💼 Faculty Roster & Payroll Expense Analytics")

        df_salary = pd.read_sql_query("""
            SELECT f.emp_id, f.first_name || ' ' || f.last_name as faculty_name, d.name as department, s.basic_salary, s.net_salary, s.month, s.payment_status
            FROM salaries s
            JOIN faculty f ON s.faculty_id = f.id
            JOIN departments d ON f.department_id = d.id
        """, conn)

        st.subheader("Net Salary Expenditure by Department")
        sal_fig = px.box(df_salary, x="department", y="net_salary", color="department", points="all", title="Faculty Net Salary Distribution")
        sal_fig.update_layout(template="plotly_dark")
        st.plotly_chart(sal_fig, use_container_width=True)

    # ----------------------------------------------------
    # 6. FINANCIAL FEES
    # ----------------------------------------------------
    elif menu == "Financial Fees":
        st.title("💰 Student Fee Collections & Pending Ledger")

        df_fees = pd.read_sql_query("""
            SELECT f.total_fee, f.paid_amount, f.pending_amount, f.payment_status, d.name as department
            FROM fees f
            JOIN students s ON f.student_id = s.id
            JOIN departments d ON s.department_id = d.id
        """, conn)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Fee Payment Status Breakdown")
            status_fig = px.pie(df_fees, names="payment_status", color="payment_status", color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444'])
            status_fig.update_layout(template="plotly_dark")
            st.plotly_chart(status_fig, use_container_width=True)

        with col2:
            st.subheader("Pending Balance by Department")
            pending_dept_df = df_fees.groupby("department")["pending_amount"].sum().reset_index()
            p_fig = px.bar(pending_dept_df, x="department", y="pending_amount", color="department", text_auto=True)
            p_fig.update_layout(template="plotly_dark")
            st.plotly_chart(p_fig, use_container_width=True)

    conn.close()

if __name__ == '__main__':
    run_streamlit_app()
