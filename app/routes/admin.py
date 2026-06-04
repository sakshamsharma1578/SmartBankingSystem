from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert
from app.models.audit_log import AuditLog
from app.services.admin_service import freeze_account, unfreeze_account, delete_user

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard.home'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    total_users = User.query.filter_by(is_admin=False).count()
    total_accounts = Account.query.count()
    total_transactions = Transaction.query.count()
    open_alerts = FraudAlert.query.filter_by(is_resolved=False).count()
    total_volume = db.session.query(db.func.sum(Transaction.amount)).scalar() or 0
    recent_alerts = FraudAlert.query.filter_by(is_resolved=False)\
        .order_by(FraudAlert.created_at.desc()).limit(5).all()
    recent_users = User.query.filter_by(is_admin=False)\
        .order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_users=total_users,
                           total_accounts=total_accounts,
                           total_transactions=total_transactions,
                           open_alerts=open_alerts,
                           total_volume=total_volume,
                           recent_alerts=recent_alerts,
                           recent_users=recent_users)


@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = User.query.filter_by(is_admin=False)
    if search:
        query = query.filter(
            db.or_(User.email.ilike(f'%{search}%'), User.full_name.ilike(f'%{search}%'))
        )
    pagination = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', pagination=pagination, users=pagination.items, search=search)


@admin_bp.route('/accounts')
@admin_required
def accounts():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    query = Account.query
    if search:
        query = query.filter(Account.account_number.ilike(f'%{search}%'))
    if status_filter:
        query = query.filter_by(status=status_filter)
    pagination = query.order_by(Account.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/accounts.html', pagination=pagination, accounts=pagination.items,
                           search=search, status_filter=status_filter)


@admin_bp.route('/transactions')
@admin_required
def transactions():
    page = request.args.get('page', 1, type=int)
    pagination = Transaction.query.order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=25, error_out=False)
    return render_template('admin/transactions.html', pagination=pagination, transactions=pagination.items)


@admin_bp.route('/fraud-alerts')
@admin_required
def fraud_alerts():
    page = request.args.get('page', 1, type=int)
    severity = request.args.get('severity', '')
    resolved = request.args.get('resolved', '')
    query = FraudAlert.query
    if severity:
        query = query.filter_by(severity=severity)
    if resolved == 'yes':
        query = query.filter_by(is_resolved=True)
    elif resolved == 'no':
        query = query.filter_by(is_resolved=False)
    pagination = query.order_by(FraudAlert.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/fraud_alerts.html', pagination=pagination,
                           alerts=pagination.items, severity=severity, resolved=resolved)


@admin_bp.route('/audit-logs')
@admin_required
def audit_logs():
    page = request.args.get('page', 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc())\
        .paginate(page=page, per_page=25, error_out=False)
    return render_template('admin/audit_logs.html', pagination=pagination, logs=pagination.items)


@admin_bp.route('/freeze-account/<int:account_id>', methods=['POST'])
@admin_required
def freeze(account_id):
    freeze_account(account_id, current_user.id)
    flash('Account frozen successfully.', 'warning')
    return redirect(request.referrer or url_for('admin.accounts'))


@admin_bp.route('/unfreeze-account/<int:account_id>', methods=['POST'])
@admin_required
def unfreeze(account_id):
    unfreeze_account(account_id, current_user.id)
    flash('Account unfrozen successfully.', 'success')
    return redirect(request.referrer or url_for('admin.accounts'))


@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@admin_required
def delete(user_id):
    if delete_user(user_id, current_user.id):
        flash('User deleted successfully.', 'success')
    else:
        flash('Could not delete user.', 'danger')
    return redirect(url_for('admin.users'))


@admin_bp.route('/resolve-alert/<int:alert_id>', methods=['POST'])
@admin_required
def resolve_alert(alert_id):
    from app.models.fraud_alert import FraudAlert
    from datetime import datetime
    alert = FraudAlert.query.get_or_404(alert_id)
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    db.session.commit()
    flash('Alert resolved.', 'success')
    return redirect(request.referrer or url_for('admin.fraud_alerts'))
