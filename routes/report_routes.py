from flask import Blueprint, render_template, request
from models import Student, Faculty, Attendance, Result, Fee, Salary, Department
from utils.decorators import login_required, faculty_required
from utils.report_generator import generate_csv_response, generate_pdf_report

report_bp = Blueprint('report', __name__, url_prefix='/reports')

@report_bp.route('/')
@login_required
def index():
    return render_template('reports/index.html')

@report_bp.route('/students/export/<fmt>')
@faculty_required
def export_students(fmt):
    students = Student.query.all()
    headers = ["Roll No", "Full Name", "Gender", "Email", "Department", "Course", "Year", "Attendance %", "Avg Marks %", "Risk Level"]
    rows = []
    for s in students:
        risk = s.risk_assessment['level']
        rows.append([
            s.roll_no, s.full_name, s.gender, s.email,
            s.department.name if s.department else '',
            s.course.name if s.course else '',
            s.current_year, f"{s.attendance_percentage}%", f"{s.average_marks}%", risk
        ])

    if fmt == 'pdf':
        return generate_pdf_report("Student Directory Report", "Complete list of enrolled students and academic performance", headers, rows)
    return generate_csv_response("student_directory", headers, rows)

@report_bp.route('/faculty/export/<fmt>')
@faculty_required
def export_faculty(fmt):
    faculty_list = Faculty.query.all()
    headers = ["Emp ID", "Full Name", "Gender", "Email", "Department", "Designation", "Qualification", "Experience", "Basic Salary"]
    rows = []
    for f in faculty_list:
        rows.append([
            f.emp_id, f.full_name, f.gender, f.email,
            f.department.name if f.department else '',
            f.designation, f.qualification, f"{f.experience_years} Years", f"${f.basic_salary:,.2f}"
        ])

    if fmt == 'pdf':
        return generate_pdf_report("Faculty Roster Report", "Complete list of faculty members and credentials", headers, rows)
    return generate_csv_response("faculty_roster", headers, rows)

@report_bp.route('/fees/export/<fmt>')
@faculty_required
def export_fees(fmt):
    fees = Fee.query.all()
    headers = ["Roll No", "Student Name", "Tuition", "Exam", "Library", "Total Fee", "Paid Amount", "Pending Balance", "Status"]
    rows = []
    for f in fees:
        rows.append([
            f.student.roll_no if f.student else '',
            f.student.full_name if f.student else '',
            f"${f.tuition_fee:,.2f}", f"${f.exam_fee:,.2f}", f"${f.library_fee:,.2f}",
            f"${f.total_fee:,.2f}", f"${f.paid_amount:,.2f}", f"${f.pending_amount:,.2f}", f.payment_status
        ])

    if fmt == 'pdf':
        return generate_pdf_report("Student Fee Ledger Report", "Student tuition and fee payment statuses", headers, rows)
    return generate_csv_response("fee_ledger", headers, rows)

@report_bp.route('/salary/export/<fmt>')
@faculty_required
def export_salary(fmt):
    salaries = Salary.query.all()
    headers = ["Emp ID", "Faculty Name", "Department", "Basic", "Allowances", "Deductions", "Net Salary", "Month", "Year", "Status"]
    rows = []
    for s in salaries:
        rows.append([
            s.faculty.emp_id if s.faculty else '',
            s.faculty.full_name if s.faculty else '',
            s.faculty.department.name if s.faculty and s.faculty.department else '',
            f"${s.basic_salary:,.2f}", f"${s.allowances:,.2f}", f"${s.deductions:,.2f}",
            f"${s.net_salary:,.2f}", s.month, s.year, s.payment_status
        ])

    if fmt == 'pdf':
        return generate_pdf_report("Faculty Salary Payroll Report", "Faculty payroll and net disbursement history", headers, rows)
    return generate_csv_response("faculty_payroll", headers, rows)
