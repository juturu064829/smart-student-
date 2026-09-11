from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Student, Faculty
from utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated, automatically redirect to Dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Validation: Check for empty fields
        if not username_or_email or not password:
            if not username_or_email and not password:
                flash('Please enter both your username/email and password.', 'warning')
            elif not username_or_email:
                flash('Please enter your username or email address.', 'warning')
            else:
                flash('Please enter your password.', 'warning')
            return render_template('login.html', username=username_or_email)

        try:
            # Query user by username or email
            user = User.query.filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()

            # Authenticate with secure password hashing check
            if user and user.check_password(password):
                if user.status != 'Active':
                    flash('Your account has been deactivated. Please contact administration.', 'danger')
                    return render_template('login.html', username=username_or_email)

                # Set session state
                session.clear()
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
                flash('Invalid username or password.', 'danger')
                return render_template('login.html', username=username_or_email)

        except Exception as e:
            # Graceful error handling
            flash('An unexpected server error occurred during authentication. Please try again.', 'danger')
            return render_template('login.html', username=username_or_email)

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email', '').strip()
    if not email:
        flash('Please provide your registered email address.', 'warning')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if user:
        flash(f'A password reset request has been logged for {email}. Please contact your system administrator or check with IT helpdesk.', 'info')
    else:
        flash('If that email is registered in our records, password recovery instructions have been initiated.', 'info')

    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password', '').strip()
    new_pw = request.form.get('new_password', '').strip()
    confirm_pw = request.form.get('confirm_password', '').strip()

    if not current_pw or not new_pw or not confirm_pw:
        flash('All password fields are required.', 'warning')
        return redirect(request.referrer or url_for('dashboard.index'))

    user = User.query.get(session['user_id'])
    if not user.check_password(current_pw):
        flash('Current password is incorrect.', 'danger')
        return redirect(request.referrer or url_for('dashboard.index'))

    if new_pw != confirm_pw:
        flash('New passwords do not match.', 'danger')
        return redirect(request.referrer or url_for('dashboard.index'))

    if len(new_pw) < 6:
        flash('New password must be at least 6 characters long.', 'warning')
        return redirect(request.referrer or url_for('dashboard.index'))

    user.set_password(new_pw)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))
