import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User, Student, Faculty
from utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already authenticated, automatically redirect to Dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        login_identifier = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember_me = request.form.get('remember_me')

        # Validation: Check for empty fields
        if not login_identifier or not password:
            if not login_identifier and not password:
                flash('Please enter your User ID / Email and password.', 'warning')
            elif not login_identifier:
                flash('Please enter your User ID, username, or email address.', 'warning')
            else:
                flash('Please enter your password.', 'warning')
            return render_template('login.html', username=login_identifier)

        try:
            # Query user by User ID (e.g. USER-10001), Username, or Email
            user = User.query.filter(
                (User.user_uid == login_identifier) | 
                (User.username == login_identifier) | 
                (User.email == login_identifier)
            ).first()

            # Authenticate with secure password hashing check
            if user and user.check_password(password):
                if user.status != 'Active':
                    flash('Your account has been deactivated. Please contact administration.', 'danger')
                    return render_template('login.html', username=login_identifier)

                # Set session state
                session.clear()
                if remember_me:
                    session.permanent = True
                
                session['user_id'] = user.id
                session['user_uid'] = user.user_uid
                session['username'] = user.username
                session['user_role'] = user.role
                session['user_email'] = user.email
                session['faculty_id'] = user.faculty_id
                session['student_id'] = user.student_id

                # Resolve friendly display name
                if user.full_name:
                    session['display_name'] = user.full_name
                elif user.role == 'Faculty' and user.faculty_profile:
                    session['display_name'] = user.faculty_profile.full_name
                elif user.role == 'Student' and user.student_profile:
                    session['display_name'] = user.student_profile.full_name
                else:
                    session['display_name'] = user.username

                flash(f'Welcome back, {session["display_name"]}! (User ID: {user.user_uid or "N/A"})', 'success')
                next_url = request.args.get('next')
                return redirect(next_url or url_for('dashboard.index'))
            else:
                flash('Invalid username or password.', 'danger')
                return render_template('login.html', username=login_identifier)

        except Exception as e:
            # Graceful error handling
            flash('An unexpected server error occurred during authentication. Please try again.', 'danger')
            return render_template('login.html', username=login_identifier)

    # Allow prefilling User ID from registration redirect
    prefilled_uid = request.args.get('user_id', '')
    return render_template('login.html', username=prefilled_uid)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        role = request.form.get('role', 'Student').strip()

        # 1. Check required fields
        if not full_name or not email or not password or not confirm_password:
            flash('All fields are required for registration.', 'warning')
            return render_template('register.html', full_name=full_name, email=email, role=role)

        # 2. Email format validation
        if not re.match(EMAIL_REGEX, email):
            flash('Please enter a valid email address format.', 'warning')
            return render_template('register.html', full_name=full_name, email=email, role=role)

        # 3. Password match & strength validation
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', full_name=full_name, email=email, role=role)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('register.html', full_name=full_name, email=email, role=role)

        # 4. Check whether email already exists
        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists. Please login.', 'danger')
            return render_template('register.html', full_name=full_name, email=email, role=role)

        try:
            # Generate unique base username and unique User ID (USER-10001, etc.)
            base_username = email.split('@')[0]
            candidate_username = base_username
            idx = 1
            while User.query.filter_by(username=candidate_username).first():
                candidate_username = f"{base_username}_{idx}"
                idx += 1

            new_user_uid = User.generate_next_user_uid()

            # Create User record
            new_user = User(
                user_uid=new_user_uid,
                full_name=full_name,
                username=candidate_username,
                email=email,
                role=role if role in ['Student', 'Faculty'] else 'Student',
                status='Active'
            )
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash(f'🎉 Registration successful! Your allocated User ID is {new_user_uid}. You can now log in using your User ID or Email.', 'success')
            return redirect(url_for('auth.login', user_id=new_user_uid))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred during account registration. Please try again.', 'danger')
            return render_template('register.html', full_name=full_name, email=email, role=role)

    return render_template('register.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(session['user_id'])

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()

        if not full_name:
            flash('Full name cannot be empty.', 'warning')
            return render_template('profile.html', user=user)

        # Check email uniqueness if modified
        if email and email != user.email:
            if not re.match(EMAIL_REGEX, email):
                flash('Please provide a valid email address.', 'warning')
                return render_template('profile.html', user=user)
            if User.query.filter(User.email == email, User.id != user.id).first():
                flash('Email is already registered with another account.', 'danger')
                return render_template('profile.html', user=user)
            user.email = email
            session['user_email'] = email

        user.full_name = full_name
        session['display_name'] = full_name
        db.session.commit()
        flash('Profile information updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=user)

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
        flash(f'Password reset verification instructions have been dispatched for {email}. (User ID: {user.user_uid or user.username})', 'info')
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
