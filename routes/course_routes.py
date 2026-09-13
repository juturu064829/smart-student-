from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Course, Department, Subject, Faculty
from utils.decorators import login_required, admin_required
from utils.cache import invalidate_cache

course_bp = Blueprint('course', __name__, url_prefix='/courses')

@course_bp.route('/')
@login_required
def index():
    courses = Course.query.all()
    departments = Department.query.all()
    faculty_list = Faculty.query.filter_by(status='Active').all()
    return render_template('courses/index.html', courses=courses, departments=departments, faculty_list=faculty_list)

@course_bp.route('/add', methods=['POST'])
@admin_required
def add_course():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    dept_id = request.form.get('department_id', type=int)
    duration = request.form.get('duration_years', type=int, default=4)
    semesters = request.form.get('total_semesters', type=int, default=8)
    credits_val = request.form.get('credits', type=int, default=160)
    faculty_id = request.form.get('faculty_id', type=int)
    description = request.form.get('description', '').strip()

    if Course.query.filter_by(code=code).first():
        flash('Course Code already exists.', 'danger')
        return redirect(url_for('course.index'))

    course = Course(
        code=code,
        name=name,
        department_id=dept_id,
        duration_years=duration,
        total_semesters=semesters,
        credits=credits_val,
        faculty_id=faculty_id,
        description=description,
        status='Active'
    )
    db.session.add(course)
    db.session.commit()
    # Invalidate cache
    invalidate_cache('api_courses')
    invalidate_cache('dashboard')
    flash(f'Course {name} added successfully!', 'success')
    return redirect(url_for('course.index'))

@course_bp.route('/<int:course_id>/subjects')
@login_required
def course_subjects(course_id):
    course = Course.query.get_or_404(course_id)
    subjects = Subject.query.filter_by(course_id=course_id).order_by(Subject.semester.asc()).all()
    return render_template('courses/subjects.html', course=course, subjects=subjects)

@course_bp.route('/<int:course_id>/subjects/add', methods=['POST'])
@admin_required
def add_subject(course_id):
    course = Course.query.get_or_404(course_id)
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    semester = request.form.get('semester', type=int, default=1)
    credits_val = request.form.get('credits', type=int, default=4)
    max_internal = request.form.get('max_internal', type=float, default=20.0)
    max_assignment = request.form.get('max_assignment', type=float, default=10.0)
    max_practical = request.form.get('max_practical', type=float, default=20.0)
    max_external = request.form.get('max_external', type=float, default=50.0)

    subj = Subject(
        code=code,
        name=name,
        course_id=course_id,
        semester=semester,
        credits=credits_val,
        max_internal=max_internal,
        max_assignment=max_assignment,
        max_practical=max_practical,
        max_external=max_external
    )
    db.session.add(subj)
    db.session.commit()
    # Invalidate cache
    invalidate_cache('api_courses')
    invalidate_cache('dashboard')
    flash(f'Subject {name} added to {course.name}!', 'success')
    return redirect(url_for('course.course_subjects', course_id=course_id))

@course_bp.route('/delete/<int:course_id>', methods=['POST'])
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    name = course.name
    db.session.delete(course)
    db.session.commit()
    # Invalidate cache
    invalidate_cache('api_courses')
    invalidate_cache('dashboard')
    flash(f'Course {name} deleted successfully.', 'info')
    return redirect(url_for('course.index'))
