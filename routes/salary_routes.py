from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Salary, Faculty
from utils.decorators import login_required, admin_required

salary_bp = Blueprint('salary', __name__, url_prefix='/salary')

@salary_bp.route('/')
@login_required
def index():
    user_role = session.get('user_role')
    faculty_id = session.get('faculty_id')

    if user_role == 'Faculty' and faculty_id:
        salaries = Salary.query.filter_by(faculty_id=faculty_id).order_by(Salary.id.desc()).all()
        return render_template('salary/faculty_view.html', salaries=salaries)

    # Admin view
    month = request.args.get('month', 'August')
    year = request.args.get('year', type=int, default=2026)
    status_filter = request.args.get('status', '').strip()

    query = Salary.query.filter_by(month=month, year=year)
    if status_filter:
        query = query.filter_by(payment_status=status_filter)

    salaries = query.all()

    total_payout = sum(s.net_salary for s in salaries)
    total_paid = sum(s.net_salary for s in salaries if s.payment_status == 'Paid')
    total_pending = sum(s.net_salary for s in salaries if s.payment_status == 'Pending')

    return render_template(
        'salary/index.html',
        salaries=salaries,
        selected_month=month,
        selected_year=year,
        status_filter=status_filter,
        total_payout=total_payout,
        total_paid=total_paid,
        total_pending=total_pending
    )

@salary_bp.route('/process/<int:salary_id>', methods=['POST'])
@admin_required
def process_salary(salary_id):
    sal = Salary.query.get_or_404(salary_id)
    payment_method = request.form.get('payment_method', 'Direct Bank Transfer')
    
    sal.payment_status = 'Paid'
    sal.payment_date = date.today()
    sal.payment_method = payment_method
    
    db.session.commit()
    flash(f'Salary of ${sal.net_salary:,.2f} disbursed to {sal.faculty.full_name} for {sal.month} {sal.year}!', 'success')
    return redirect(url_for('salary.index', month=sal.month, year=sal.year))

@salary_bp.route('/generate-payroll', methods=['POST'])
@admin_required
def generate_monthly_payroll():
    month = request.form.get('month', 'September')
    year = request.form.get('year', type=int, default=2026)

    active_faculty = Faculty.query.filter_by(status='Active').all()
    created_count = 0

    for fac in active_faculty:
        existing = Salary.query.filter_by(faculty_id=fac.id, month=month, year=year).first()
        if not existing:
            basic = fac.basic_salary
            allowances = round(basic * 0.10, 2)
            bonus = 0.0
            deductions = round(basic * 0.05, 2)

            sal = Salary(
                faculty_id=fac.id,
                basic_salary=basic,
                allowances=allowances,
                bonus=bonus,
                deductions=deductions,
                month=month,
                year=year,
                payment_status='Pending'
            )
            sal.calculate_net_salary()
            db.session.add(sal)
            created_count += 1

    db.session.commit()
    flash(f'Generated payroll records for {created_count} faculty members for {month} {year}!', 'success')
    return redirect(url_for('salary.index', month=month, year=year))
