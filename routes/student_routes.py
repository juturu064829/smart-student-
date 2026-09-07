from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Student, Department, Course, User, Fee
from utils.decorators import login_required, faculty_required, admin_required

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
@login_required
def index():
    dept_id = request.args.get('department_id', type=int)
    course_id = request.args.get('course_id', type=int)
    year = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    search_q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Student.query

    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if year:
        query = query.filter_by(current_year=year)
    if semester:
        query = query.filter_by(current_semester=semester)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search_q:
        query = query.filter(
            (Student.roll_no.ilike(f'%{search_q}%')) |
            (Student.first_name.ilike(f'%{search_q}%')) |
            (Student.last_name.ilike(f'%{search_q}%')) |
            (Student.email.ilike(f'%{search_q}%'))
        )

    students = query.order_by(Student.id.desc()).all()
    departments = Department.query.all()
    courses = Course.query.all()

    return render_template(
        'students/index.html',
        students=students,
        departments=departments,
        courses=courses,
        selected_dept=dept_id,
        selected_course=course_id,
        selected_year=year,
        selected_sem=semester,
        search_q=search_q,
        status_filter=status_filter
    )

@student_bp.route('/add', methods=['GET', 'POST'])
@faculty_required
def add_student():
    if request.method == 'POST':
        roll_no = request.form.get('roll_no', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        gender = request.form.get('gender', 'Male')
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        dept_id = request.form.get('department_id', type=int)
        course_id = request.form.get('course_id', type=int)
        current_year = request.form.get('current_year', type=int, default=1)
        current_semester = request.form.get('current_semester', type=int, default=1)
        guardian_name = request.form.get('guardian_name', '').strip()
        guardian_phone = request.form.get('guardian_phone', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        dob_str = request.form.get('dob')

        # Validation
        if Student.query.filter_by(roll_no=roll_no).first():
            flash('Error: Student Roll Number already exists.', 'danger')
            return redirect(url_for('student.add_student'))
        if Student.query.filter_by(email=email).first():
            flash('Error: Email address already registered.', 'danger')
            return redirect(url_for('student.add_student'))

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None

        student = Student(
            roll_no=roll_no,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            dob=dob,
            email=email,
            phone=phone,
            department_id=dept_id,
            course_id=course_id,
            current_year=current_year,
            current_semester=current_semester,
            admission_date=datetime.now().date(),
            guardian_name=guardian_name,
            guardian_phone=guardian_phone,
            blood_group=blood_group,
            address=address,
            city=city,
            state=state,
            status='Active'
        )
        db.session.add(student)
        db.session.flush()

        # Create matching user account for student login
        username = email.split('@')[0]
        if User.query.filter_by(username=username).first():
            username = f"{username}_{student.id}"

        user = User(
            username=username,
            email=email,
            role='Student',
            status='Active',
            student_id=student.id
        )
        user.set_password('student123')
        db.session.add(user)

        # Create initial fee ledger record
        initial_fee = Fee(
            student_id=student.id,
            tuition_fee=40000.0,
            exam_fee=2000.0,
            library_fee=1500.0,
            hostel_fee=0.0,
            other_fee=1000.0
        )
        initial_fee.update_totals()
        db.session.add(initial_fee)

        db.session.commit()

        flash(f'Student {student.full_name} added successfully! Login credentials generated (Password: student123).', 'success')
        return redirect(url_for('student.view_student', student_id=student.id))

    departments = Department.query.all()
    courses = Course.query.all()
    return render_template('students/add_edit.html', student=None, departments=departments, courses=courses)

@student_bp.route('/<int:student_id>')
@login_required
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    
    # Permission check for Student role
    user_role = session.get('user_role')
    if user_role == 'Student' and session.get('student_id') != student_id:
        flash('Unauthorized access: You can only view your own student profile.', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('students/profile.html', student=student)

@student_bp.route('/edit/<int:student_id>', methods=['GET', 'POST'])
@faculty_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.first_name = request.form.get('first_name', '').strip()
        student.last_name = request.form.get('last_name', '').strip()
        student.gender = request.form.get('gender', 'Male')
        student.email = request.form.get('email', '').strip()
        student.phone = request.form.get('phone', '').strip()
        student.department_id = request.form.get('department_id', type=int)
        student.course_id = request.form.get('course_id', type=int)
        student.current_year = request.form.get('current_year', type=int)
        student.current_semester = request.form.get('current_semester', type=int)
        student.guardian_name = request.form.get('guardian_name', '').strip()
        student.guardian_phone = request.form.get('guardian_phone', '').strip()
        student.blood_group = request.form.get('blood_group', '').strip()
        student.address = request.form.get('address', '').strip()
        student.city = request.form.get('city', '').strip()
        student.state = request.form.get('state', '').strip()
        student.status = request.form.get('status', 'Active')

        dob_str = request.form.get('dob')
        if dob_str:
            student.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

        db.session.commit()
        flash(f'Student profile for {student.full_name} updated successfully!', 'success')
        return redirect(url_for('student.view_student', student_id=student.id))

    departments = Department.query.all()
    courses = Course.query.all()
    return render_template('students/add_edit.html', student=student, departments=departments, courses=courses)

@student_bp.route('/delete/<int:student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.full_name
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {name} deleted successfully.', 'info')
    return redirect(url_for('student.index'))
