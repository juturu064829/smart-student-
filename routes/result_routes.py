from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Result, Student, Course, Subject
from utils.decorators import login_required, faculty_required
from utils.calculations import calculate_gpa

result_bp = Blueprint('result', __name__, url_prefix='/results')

@result_bp.route('/')
@login_required
def index():
    user_role = session.get('user_role')
    student_id = session.get('student_id')

    if user_role == 'Student' and student_id:
        student = Student.query.get_or_404(student_id)
        results = Result.query.filter_by(student_id=student_id).all()
        gpa = calculate_gpa(results)
        return render_template('results/student_view.html', student=student, results=results, gpa=gpa)

    # Admin & Faculty overview
    course_id = request.args.get('course_id', type=int)
    subject_id = request.args.get('subject_id', type=int)
    search_q = request.args.get('q', '').strip()

    courses = Course.query.all()
    subjects = Subject.query.filter_by(course_id=course_id).all() if course_id else []

    query = Result.query
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    elif course_id:
        query = query.join(Subject).filter(Subject.course_id == course_id)

    if search_q:
        query = query.join(Student).filter(
            (Student.roll_no.ilike(f'%{search_q}%')) |
            (Student.first_name.ilike(f'%{search_q}%')) |
            (Student.last_name.ilike(f'%{search_q}%'))
        )

    results = query.all()

    return render_template(
        'results/index.html',
        results=results,
        courses=courses,
        subjects=subjects,
        selected_course=course_id,
        selected_subject=subject_id,
        search_q=search_q
    )

@result_bp.route('/enter', methods=['GET', 'POST'])
@faculty_required
def enter_marks():
    if request.method == 'POST':
        subject_id = request.form.get('subject_id', type=int)
        student_ids = request.form.getlist('student_ids')

        subject = Subject.query.get_or_404(subject_id)
        saved_count = 0

        for s_id in student_ids:
            s_id_int = int(s_id)
            internal = request.form.get(f'internal_{s_id_int}', type=float, default=0.0)
            assignment = request.form.get(f'assignment_{s_id_int}', type=float, default=0.0)
            practical = request.form.get(f'practical_{s_id_int}', type=float, default=0.0)
            external = request.form.get(f'external_{s_id_int}', type=float, default=0.0)

            # Cap input to max subject marks
            internal = min(subject.max_internal or 20.0, internal)
            assignment = min(subject.max_assignment or 10.0, assignment)
            practical = min(subject.max_practical or 20.0, practical)
            external = min(subject.max_external or 50.0, external)

            existing = Result.query.filter_by(student_id=s_id_int, subject_id=subject_id).first()
            if existing:
                existing.internal_marks = internal
                existing.assignment_marks = assignment
                existing.practical_marks = practical
                existing.external_marks = external
                existing.calculate_grade()
            else:
                res = Result(
                    student_id=s_id_int,
                    subject_id=subject_id,
                    internal_marks=internal,
                    assignment_marks=assignment,
                    practical_marks=practical,
                    external_marks=external,
                    semester=subject.semester,
                    academic_year='2025-2026'
                )
                res.calculate_grade()
                db.session.add(res)
            saved_count += 1

        db.session.commit()
        flash(f'Marks saved and auto-graded for {saved_count} students in {subject.name}!', 'success')
        return redirect(url_for('result.index', subject_id=subject_id))

    # GET: Load marks entry selection
    course_id = request.args.get('course_id', type=int)
    subject_id = request.args.get('subject_id', type=int)

    courses = Course.query.all()
    subjects = Subject.query.filter_by(course_id=course_id).all() if course_id else []
    students = Student.query.filter_by(course_id=course_id).all() if course_id else []

    existing_results = {}
    if subject_id:
        res_list = Result.query.filter_by(subject_id=subject_id).all()
        existing_results = {r.student_id: r for r in res_list}

    subject_obj = Subject.query.get(subject_id) if subject_id else None

    return render_template(
        'results/enter.html',
        courses=courses,
        subjects=subjects,
        students=students,
        selected_course=course_id,
        selected_subject=subject_id,
        existing_results=existing_results,
        subject_obj=subject_obj
    )
