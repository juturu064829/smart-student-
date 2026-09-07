from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Faculty, Department, User, Salary
from utils.decorators import login_required, admin_required

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.route('/')
@login_required
def index():
    dept_id = request.args.get('department_id', type=int)
    search_q = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Faculty.query

    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if search_q:
        query = query.filter(
            (Faculty.emp_id.ilike(f'%{search_q}%')) |
            (Faculty.first_name.ilike(f'%{search_q}%')) |
            (Faculty.last_name.ilike(f'%{search_q}%')) |
            (Faculty.email.ilike(f'%{search_q}%')) |
            (Faculty.designation.ilike(f'%{search_q}%'))
        )

    faculty_list = query.order_by(Faculty.id.desc()).all()
    departments = Department.query.all()

    return render_template(
        'faculty/index.html',
        faculty_list=faculty_list,
        departments=departments,
        selected_dept=dept_id,
        search_q=search_q,
        status_filter=status_filter
    )

@faculty_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_faculty():
    if request.method == 'POST':
        emp_id = request.form.get('emp_id', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        gender = request.form.get('gender', 'Male')
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        dept_id = request.form.get('department_id', type=int)
        designation = request.form.get('designation', 'Assistant Professor')
        qualification = request.form.get('qualification', '').strip()
        exp_years = request.form.get('experience_years', type=int, default=0)
        basic_salary = request.form.get('basic_salary', type=float, default=50000.0)
        joining_str = request.form.get('joining_date')
        address = request.form.get('address', '').strip()

        if Faculty.query.filter_by(emp_id=emp_id).first():
            flash('Error: Faculty Employee ID already exists.', 'danger')
            return redirect(url_for('faculty.add_faculty'))
        if Faculty.query.filter_by(email=email).first():
            flash('Error: Faculty email address already registered.', 'danger')
            return redirect(url_for('faculty.add_faculty'))

        joining_date = datetime.strptime(joining_str, '%Y-%m-%d').date() if joining_str else None

        fac = Faculty(
            emp_id=emp_id,
            first_name=first_name,
            last_name=last_name,
            gender=gender,
            email=email,
            phone=phone,
            department_id=dept_id,
            designation=designation,
            qualification=qualification,
            experience_years=exp_years,
            basic_salary=basic_salary,
            joining_date=joining_date,
            address=address,
            status='Active'
        )
        db.session.add(fac)
        db.session.flush()

        username = email.split('@')[0]
        if User.query.filter_by(username=username).first():
            username = f"{username}_{fac.id}"

        user = User(
            username=username,
            email=email,
            role='Faculty',
            status='Active',
            faculty_id=fac.id
        )
        user.set_password('faculty123')
        db.session.add(user)

        # Create salary record for current month
        sal = Salary(
            faculty_id=fac.id,
            basic_salary=basic_salary,
            allowances=round(basic_salary * 0.10, 2),
            bonus=0.0,
            deductions=round(basic_salary * 0.05, 2),
            month='August',
            year=2026,
            payment_status='Pending'
        )
        sal.calculate_net_salary()
        db.session.add(sal)

        db.session.commit()

        flash(f'Faculty member {fac.full_name} created successfully! Login credentials generated (Password: faculty123).', 'success')
        return redirect(url_for('faculty.view_faculty', faculty_id=fac.id))

    departments = Department.query.all()
    return render_template('faculty/add_edit.html', faculty=None, departments=departments)

@faculty_bp.route('/<int:faculty_id>')
@login_required
def view_faculty(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)
    return render_template('faculty/profile.html', faculty=fac)

@faculty_bp.route('/edit/<int:faculty_id>', methods=['GET', 'POST'])
@admin_required
def edit_faculty(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)

    if request.method == 'POST':
        fac.first_name = request.form.get('first_name', '').strip()
        fac.last_name = request.form.get('last_name', '').strip()
        fac.gender = request.form.get('gender', 'Male')
        fac.email = request.form.get('email', '').strip()
        fac.phone = request.form.get('phone', '').strip()
        fac.department_id = request.form.get('department_id', type=int)
        fac.designation = request.form.get('designation', '').strip()
        fac.qualification = request.form.get('qualification', '').strip()
        fac.experience_years = request.form.get('experience_years', type=int, default=0)
        fac.basic_salary = request.form.get('basic_salary', type=float, default=50000.0)
        fac.address = request.form.get('address', '').strip()
        fac.status = request.form.get('status', 'Active')

        joining_str = request.form.get('joining_date')
        if joining_str:
            fac.joining_date = datetime.strptime(joining_str, '%Y-%m-%d').date()

        db.session.commit()
        flash(f'Faculty details for {fac.full_name} updated successfully!', 'success')
        return redirect(url_for('faculty.view_faculty', faculty_id=fac.id))

    departments = Department.query.all()
    return render_template('faculty/add_edit.html', faculty=fac, departments=departments)

@faculty_bp.route('/delete/<int:faculty_id>', methods=['POST'])
@admin_required
def delete_faculty(faculty_id):
    fac = Faculty.query.get_or_404(faculty_id)
    name = fac.full_name
    db.session.delete(fac)
    db.session.commit()
    flash(f'Faculty member {name} deleted successfully.', 'info')
    return redirect(url_for('faculty.index'))
