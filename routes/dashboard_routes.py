from datetime import date
from flask import Blueprint, render_template, session, jsonify
from models import db, Student, Faculty, Department, Course, Attendance, Result, Fee, Salary, Announcement
from utils.decorators import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_role = session.get('user_role')
    
    # Core KPIs
    total_students = Student.query.filter_by(status='Active').count()
    total_faculty = Faculty.query.filter_by(status='Active').count()
    total_courses = Course.query.filter_by(status='Active').count()
    total_departments = Department.query.filter_by(status='Active').count()

    # Today's Attendance calculation
    today = date.today()
    today_att_records = Attendance.query.filter_by(date=today).all()
    if today_att_records:
        present_count = sum(1 for r in today_att_records if r.status in ['Present', 'Late'])
        today_att_pct = round((present_count / len(today_att_records)) * 100.0, 1)
    else:
        # Fallback to overall historical average if no logs marked today
        all_att = Attendance.query.all()
        if all_att:
            present_cnt = sum(1 for r in all_att if r.status in ['Present', 'Late'])
            today_att_pct = round((present_cnt / len(all_att)) * 100.0, 1)
        else:
            today_att_pct = 92.5

    # Average Student Percentage
    all_results = Result.query.all()
    if all_results:
        avg_student_pct = round(sum(r.percentage for r in all_results if r.percentage is not None) / len(all_results), 1)
    else:
        avg_student_pct = 78.4

    # Pending Fees Total
    all_fees = Fee.query.all()
    total_pending_fees = sum(f.pending_amount for f in all_fees) if all_fees else 0.0

    # Monthly Faculty Salary Total (Current Month)
    all_salaries = Salary.query.filter_by(month='August', year=2026).all()
    monthly_salary_total = sum(s.net_salary for s in all_salaries) if all_salaries else sum(f.basic_salary * 1.05 for f in Faculty.query.all())

    # Intelligent Risk Analysis: Identify At-Risk Students
    all_students_obj = Student.query.all()
    at_risk_students = []
    for s in all_students_obj:
        risk = s.risk_assessment
        if risk['level'] in ['High Risk', 'Moderate Risk']:
            at_risk_students.append({
                'id': s.id,
                'roll_no': s.roll_no,
                'name': s.full_name,
                'department': s.department.name if s.department else 'N/A',
                'attendance': s.attendance_percentage,
                'average_marks': s.average_marks,
                'risk_level': risk['level'],
                'risk_color': risk['color'],
                'reasons': ", ".join(risk['reasons'])
            })
    
    # Sort at risk students by highest priority (High Risk first)
    at_risk_students.sort(key=lambda x: 0 if x['risk_level'] == 'High Risk' else 1)

    # Announcements
    if user_role == 'Student':
        announcements = Announcement.query.filter(Announcement.target_role.in_(['All', 'Student'])).order_by(Announcement.created_at.desc()).limit(5).all()
    elif user_role == 'Faculty':
        announcements = Announcement.query.filter(Announcement.target_role.in_(['All', 'Faculty'])).order_by(Announcement.created_at.desc()).limit(5).all()
    else:
        announcements = Announcement.query.order_by(Announcement.created_at.desc()).limit(5).all()

    # Recent Students added
    recent_students = Student.query.order_by(Student.id.desc()).limit(5).all()

    # Student specific data if logged in as student
    student_specific_data = None
    if user_role == 'Student' and session.get('student_id'):
        s_obj = Student.query.get(session['student_id'])
        if s_obj:
            student_specific_data = s_obj.to_dict()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_courses=total_courses,
        total_departments=total_departments,
        today_att_pct=today_att_pct,
        avg_student_pct=avg_student_pct,
        total_pending_fees=total_pending_fees,
        monthly_salary_total=monthly_salary_total,
        at_risk_students=at_risk_students[:10],
        at_risk_count=len(at_risk_students),
        announcements=announcements,
        recent_students=recent_students,
        student_specific_data=student_specific_data
    )

from utils.cache import cached

@dashboard_bp.route('/api/dashboard-charts')
@login_required
@cached(ttl=60, prefix='dashboard_charts')
def dashboard_charts_api():
    # 1. Dept wise student count
    depts = Department.query.all()
    dept_labels = [d.code for d in depts]
    dept_student_counts = [len(d.students) for d in depts]

    # 2. Gender distribution
    male_students = Student.query.filter_by(gender='Male').count()
    female_students = Student.query.filter_by(gender='Female').count()
    other_students = Student.query.filter_by(gender='Other').count()

    # 3. Grade distribution
    results = Result.query.all()
    grade_counts = {'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for r in results:
        if r.grade in grade_counts:
            grade_counts[r.grade] += 1

    # 4. Fee status breakdown
    fees = Fee.query.all()
    paid_count = sum(1 for f in fees if f.payment_status == 'Paid')
    partial_count = sum(1 for f in fees if f.payment_status == 'Partially Paid')
    pending_count = sum(1 for f in fees if f.payment_status == 'Pending')

    return jsonify({
        'dept_labels': dept_labels,
        'dept_student_counts': dept_student_counts,
        'gender_distribution': {'Male': male_students, 'Female': female_students, 'Other': other_students},
        'grade_counts': grade_counts,
        'fee_status': {'Paid': paid_count, 'Partially Paid': partial_count, 'Pending': pending_count}
    })
