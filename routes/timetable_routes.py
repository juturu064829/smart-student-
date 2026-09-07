from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Timetable, Department, Course, Subject, Faculty
from utils.decorators import login_required, admin_required

timetable_bp = Blueprint('timetable', __name__, url_prefix='/timetable')

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

@timetable_bp.route('/')
@login_required
def index():
    dept_id = request.args.get('department_id', type=int)
    course_id = request.args.get('course_id', type=int)

    departments = Department.query.all()
    courses = Course.query.all()
    faculty_list = Faculty.query.all()
    subjects = Subject.query.all()

    query = Timetable.query
    if course_id:
        query = query.filter_by(course_id=course_id)
    elif dept_id:
        query = query.filter_by(department_id=dept_id)

    entries = query.all()

    # Build weekly schedule matrix: grid[day][time_slot] = entry
    grid = {day: [] for day in DAYS}
    for e in entries:
        if e.day_of_week in grid:
            grid[e.day_of_week].append(e)

    return render_template(
        'timetable/index.html',
        grid=grid,
        departments=departments,
        courses=courses,
        faculty_list=faculty_list,
        subjects=subjects,
        selected_dept=dept_id,
        selected_course=course_id,
        days=DAYS
    )

@timetable_bp.route('/add', methods=['POST'])
@admin_required
def add_slot():
    dept_id = request.form.get('department_id', type=int)
    course_id = request.form.get('course_id', type=int)
    subject_id = request.form.get('subject_id', type=int)
    faculty_id = request.form.get('faculty_id', type=int)
    room_number = request.form.get('room_number', 'Hall A-101').strip()
    day_of_week = request.form.get('day_of_week', 'Monday')
    start_time = request.form.get('start_time', '09:00 AM')
    end_time = request.form.get('end_time', '10:00 AM')
    semester = request.form.get('semester', type=int, default=1)

    tt = Timetable(
        department_id=dept_id,
        course_id=course_id,
        subject_id=subject_id,
        faculty_id=faculty_id,
        room_number=room_number,
        day_of_week=day_of_week,
        start_time=start_time,
        end_time=end_time,
        semester=semester
    )
    db.session.add(tt)
    db.session.commit()
    flash('Timetable slot added successfully!', 'success')
    return redirect(url_for('timetable.index', course_id=course_id))

@timetable_bp.route('/delete/<int:slot_id>', methods=['POST'])
@admin_required
def delete_slot(slot_id):
    tt = Timetable.query.get_or_404(slot_id)
    c_id = tt.course_id
    db.session.delete(tt)
    db.session.commit()
    flash('Timetable slot removed.', 'info')
    return redirect(url_for('timetable.index', course_id=c_id))
