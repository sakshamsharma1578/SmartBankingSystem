from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.account import Account
from app.models.audit_log import AuditLog
from app.models.password_reset import PasswordResetToken
from app.services.fraud_service import check_failed_logins
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))
    return render_template('auth/landing.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone_number', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        account_type = request.form.get('account_type', 'savings')

        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not email or '@' not in email:
            errors.append('Valid email is required.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return render_template('auth/register.html')

        user = User(full_name=full_name, email=email, phone_number=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        account = Account(
            account_number=Account.generate_account_number(),
            user_id=user.id,
            account_type=account_type,
            balance=0.0,
            is_primary=True
        )
        db.session.add(account)
        db.session.commit()

        log = AuditLog(user_id=user.id, action='register',
                       details=f'New user registered: {email}',
                       ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()

        flash(f'Registration successful! Your account number is {account.account_number}. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return render_template('auth/login.html')

            user.failed_login_attempts = 0
            user.last_login = datetime.utcnow()
            db.session.commit()

            login_user(user, remember=remember)

            log = AuditLog(user_id=user.id, action='login',
                           details=f'User logged in: {email}',
                           ip_address=request.remote_addr,
                           user_agent=request.user_agent.string[:255])
            db.session.add(log)
            db.session.commit()

            next_page = request.args.get('next')
            if user.is_admin:
                return redirect(next_page or url_for('admin.dashboard'))
            return redirect(next_page or url_for('dashboard.home'))
        else:
            if user:
                user.failed_login_attempts += 1
                db.session.commit()
                check_failed_logins(user)
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    log = AuditLog(user_id=current_user.id, action='logout',
                   details='User logged out',
                   ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = PasswordResetToken.generate_token(user.id)
            db.session.add(token)
            db.session.commit()
            # In production, email the reset link
            flash(f'Password reset link generated. Token: {token.token[:20]}... (In production this would be emailed)', 'info')
        else:
            flash('If that email exists, a reset link has been sent.', 'info')
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset = PasswordResetToken.query.filter_by(token=token).first()
    if not reset or not reset.is_valid():
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            user = User.query.get(reset.user_id)
            user.set_password(password)
            reset.is_used = True
            db.session.commit()
            flash('Password reset successful. Please login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)
