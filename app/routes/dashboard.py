from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import json

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def home():
    account = current_user.get_primary_account()
    if not account:
        return redirect(url_for('auth.logout'))

    recent_txns = Transaction.query.filter_by(account_id=account.id)\
        .order_by(Transaction.created_at.desc()).limit(5).all()

    fraud_alerts = FraudAlert.query.filter_by(account_id=account.id, is_resolved=False)\
        .order_by(FraudAlert.created_at.desc()).limit(3).all()

    total_deposits = account.get_total_deposits()
    total_withdrawals = account.get_total_withdrawals()
    total_transfers = account.get_total_transfers_sent()

    # Monthly chart data (last 6 months)
    monthly_data = _get_monthly_data(account.id)

    return render_template('dashboard/home.html',
                           account=account,
                           recent_transactions=recent_txns,
                           fraud_alerts=fraud_alerts,
                           total_deposits=total_deposits,
                           total_withdrawals=total_withdrawals,
                           total_transfers=total_transfers,
                           monthly_data=json.dumps(monthly_data))


@dashboard_bp.route('/profile')
@login_required
def profile():
    account = current_user.get_primary_account()
    from app.models.audit_log import AuditLog
    logs = AuditLog.query.filter_by(user_id=current_user.id)\
        .order_by(AuditLog.created_at.desc()).limit(20).all()
    return render_template('dashboard/profile.html', account=account, logs=logs)


@dashboard_bp.route('/analytics')
@login_required
def analytics():
    account = current_user.get_primary_account()
    monthly_data = _get_monthly_data(account.id)
    category_data = _get_category_data(account.id)
    growth_data = _get_balance_growth(account.id)
    return render_template('dashboard/analytics.html',
                           account=account,
                           monthly_data=json.dumps(monthly_data),
                           category_data=json.dumps(category_data),
                           growth_data=json.dumps(growth_data))


def _get_monthly_data(account_id):
    months = []
    deposits = []
    withdrawals = []
    now = datetime.utcnow()

    for i in range(5, -1, -1):
        target = now - timedelta(days=30 * i)
        label = target.strftime('%b %Y')
        months.append(label)

        dep = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == 'deposit',
            extract('month', Transaction.created_at) == target.month,
            extract('year', Transaction.created_at) == target.year
        ).scalar() or 0

        wdl = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == 'withdrawal',
            extract('month', Transaction.created_at) == target.month,
            extract('year', Transaction.created_at) == target.year
        ).scalar() or 0

        deposits.append(round(dep, 2))
        withdrawals.append(round(wdl, 2))

    return {'months': months, 'deposits': deposits, 'withdrawals': withdrawals}


def _get_category_data(account_id):
    types = ['deposit', 'withdrawal', 'transfer_out', 'transfer_in']
    data = {}
    for t in types:
        val = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.account_id == account_id,
            Transaction.transaction_type == t
        ).scalar() or 0
        data[t.replace('_', ' ').title()] = round(val, 2)
    return data


def _get_balance_growth(account_id):
    txns = Transaction.query.filter_by(account_id=account_id)\
        .order_by(Transaction.created_at.asc()).all()
    labels = [t.created_at.strftime('%Y-%m-%d') for t in txns[-30:]]
    balances = [t.balance_after for t in txns[-30:]]
    return {'labels': labels, 'balances': balances}
