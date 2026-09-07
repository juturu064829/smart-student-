from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Student, Faculty
from utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            if user.status != 'Active':
                flash('Your account has been deactivated. Please contact administration.', 'danger')
                return render_template('login.html')

            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['user_email'] = user.email
            session['faculty_id'] = user.faculty_id
            session['student_id'] = user.student_id

            if user.role == 'Faculty' and user.faculty_profile:
                session['display_name'] = user.faculty_profile.full_name
            elif user.role == 'Student' and user.student_profile:
                session['display_name'] = user.student_profile.full_name
            else:
                session['display_name'] = 'System Administrator'

            flash(f'Welcome back, {session["display_name"]}!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')

    user = User.query.get(session['user_id'])
    if not user.check_password(current_pw):
        flash('Current password is incorrect.', 'danger')
        return redirect(request.referrer or url_for('dashboard.index'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(request.referrer or url_for('dashboard.index'))

    user.set_password(new_pw)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))
