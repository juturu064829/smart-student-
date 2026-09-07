from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Fee, Student
from utils.decorators import login_required, faculty_required, admin_required

fee_bp = Blueprint('fee', __name__, url_prefix='/fees')

@fee_bp.route('/')
@login_required
def index():
    user_role = session.get('user_role')
    student_id = session.get('student_id')

    if user_role == 'Student' and student_id:
        fees = Fee.query.filter_by(student_id=student_id).all()
        return render_template('fees/student_view.html', fees=fees)

    status_filter = request.args.get('status', '').strip()
    search_q = request.args.get('q', '').strip()

    query = Fee.query

    if status_filter:
        query = query.filter_by(payment_status=status_filter)
    if search_q:
        query = query.join(Student).filter(
            (Student.roll_no.ilike(f'%{search_q}%')) |
            (Student.first_name.ilike(f'%{search_q}%')) |
            (Student.last_name.ilike(f'%{search_q}%'))
        )

    fees = query.all()

    total_expected = sum(f.total_fee for f in fees)
    total_collected = sum(f.paid_amount for f in fees)
    total_pending = sum(f.pending_amount for f in fees)

    return render_template(
        'fees/index.html',
        fees=fees,
        status_filter=status_filter,
        search_q=search_q,
        total_expected=total_expected,
        total_collected=total_collected,
        total_pending=total_pending
    )

@fee_bp.route('/pay/<int:fee_id>', methods=['POST'])
@faculty_required
def process_payment(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    payment_amount = request.form.get('amount', type=float, default=0.0)
    remarks = request.form.get('remarks', '').strip()

    if payment_amount <= 0:
        flash('Invalid payment amount.', 'danger')
        return redirect(url_for('fee.index'))

    fee.paid_amount += payment_amount
    fee.payment_date = date.today()
    fee.remarks = remarks if remarks else f"Payment of ${payment_amount:.2f} received."
    fee.update_totals()

    db.session.commit()
    flash(f'Payment of ${payment_amount:,.2f} recorded for {fee.student.full_name}. New Pending Balance: ${fee.pending_amount:,.2f}', 'success')
    return redirect(url_for('fee.index'))
