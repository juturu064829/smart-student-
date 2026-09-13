from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Department
from utils.decorators import login_required, admin_required
from utils.cache import invalidate_cache

department_bp = Blueprint('department', __name__, url_prefix='/departments')

@department_bp.route('/')
@login_required
def index():
    departments = Department.query.all()
    return render_template('departments/index.html', departments=departments)

@department_bp.route('/add', methods=['POST'])
@admin_required
def add_department():
    code = request.form.get('code', '').strip().upper()
    name = request.form.get('name', '').strip()
    hod_name = request.form.get('hod_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    description = request.form.get('description', '').strip()

    if Department.query.filter_by(code=code).first():
        flash('Department Code already exists.', 'danger')
        return redirect(url_for('department.index'))

    dept = Department(
        code=code,
        name=name,
        hod_name=hod_name,
        email=email,
        phone=phone,
        description=description,
        status='Active'
    )
    db.session.add(dept)
    db.session.commit()
    # Invalidate cache
    invalidate_cache('api_departments')
    invalidate_cache('dashboard')
    flash(f'Department {name} added successfully!', 'success')
    return redirect(url_for('department.index'))

@department_bp.route('/edit/<int:dept_id>', methods=['POST'])
@admin_required
def edit_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    dept.name = request.form.get('name', '').strip()
    dept.hod_name = request.form.get('hod_name', '').strip()
    dept.email = request.form.get('email', '').strip()
    dept.phone = request.form.get('phone', '').strip()
    dept.description = request.form.get('description', '').strip()
    dept.status = request.form.get('status', 'Active')

    db.session.commit()
    # Invalidate cache
    invalidate_cache('api_departments')
    invalidate_cache('dashboard')
    flash(f'Department {dept.name} updated successfully!', 'success')
    return redirect(url_for('department.index'))

@department_bp.route('/delete/<int:dept_id>', methods=['POST'])
@admin_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    name = dept.name
    db.session.delete(dept)
    db.session.commit()
    # Invalidate cache
    invalidate_cache('api_departments')
    invalidate_cache('dashboard')
    flash(f'Department {name} deleted successfully.', 'info')
    return redirect(url_for('department.index'))
