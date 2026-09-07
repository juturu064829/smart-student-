from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Attendance, Student, Course, Subject, Faculty
from utils.decorators import login_required, faculty_required

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/')
@login_required
def index():
    user_role = session.get('user_role')
    student_id = session.get('student_id')

    if user_role == 'Student' and student_id:
        student = Student.query.get_or_404(student_id)
        records = Attendance.query.filter_by(student_id=student_id).order_by(Attendance.date.desc()).all()
        return render_template('attendance/student_view.html', student=student, records=records)

    # Admin & Faculty overview
    course_id = request.args.get('course_id', type=int)
    date_str = request.args.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    courses = Course.query.all()
    query = Attendance.query.filter_by(date=selected_date)
    if course_id:
        query = query.filter_by(course_id=course_id)

    records = query.all()

    # List of all active students with their attendance percentage & warnings
    students = Student.query.all()
    warning_students = [s for s in students if s.attendance_percentage < 75.0]

    return render_template(
        'attendance/index.html',
        records=records,
        courses=courses,
        selected_course=course_id,
        selected_date=selected_date,
        warning_students=warning_students
    )

@attendance_bp.route('/mark', methods=['GET', 'POST'])
@faculty_required
def mark_attendance():
    if request.method == 'POST':
        course_id = request.form.get('course_id', type=int)
        subject_id = request.form.get('subject_id', type=int)
        date_str = request.form.get('date')
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

        student_ids = request.form.getlist('student_ids')
        faculty_id = session.get('faculty_id') or Faculty.query.first().id

        marked_count = 0
        for s_id in student_ids:
            s_id_int = int(s_id)
            status = request.form.get(f'status_{s_id_int}', 'Present')
            remarks = request.form.get(f'remarks_{s_id_int}', '')

            # Check if record already exists for date + student + subject
            existing = Attendance.query.filter_by(
                student_id=s_id_int,
                subject_id=subject_id,
                date=att_date
            ).first()

            if existing:
                existing.status = status
                existing.remarks = remarks
                existing.marked_by_faculty_id = faculty_id
            else:
                att = Attendance(
                    student_id=s_id_int,
                    course_id=course_id,
                    subject_id=subject_id,
                    date=att_date,
                    status=status,
                    marked_by_faculty_id=faculty_id,
                    remarks=remarks
                )
                db.session.add(att)
            marked_count += 1

        db.session.commit()
        flash(f'Attendance recorded successfully for {marked_count} students on {att_date}!', 'success')
        return redirect(url_for('attendance.index', course_id=course_id, date=att_date.strftime('%Y-%m-%d')))

    # GET: Load selection form
    course_id = request.args.get('course_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    date_str = request.args.get('date')
    selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

    courses = Course.query.all()
    subjects = Subject.query.filter_by(course_id=course_id).all() if course_id else []
    students = Student.query.filter_by(course_id=course_id).all() if course_id else []

    # Get existing status for date if pre-marked
    existing_map = {}
    if course_id and subject_id:
        existing_records = Attendance.query.filter_by(course_id=course_id, subject_id=subject_id, date=selected_date).all()
        existing_map = {r.student_id: r.status for r in existing_records}

    return render_template(
        'attendance/mark.html',
        courses=courses,
        subjects=subjects,
        students=students,
        selected_course=course_id,
        selected_subject=subject_id,
        selected_date=selected_date,
        existing_map=existing_map
    )
