from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models.transaction import Transaction
from app.models.fraud_alert import FraudAlert
from app import db
from sqlalchemy import func, extract
from datetime import datetime, timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/account/summary')
@login_required
def account_summary():
    account = current_user.get_primary_account()
    return jsonify({
        'balance': account.balance,
        'account_number': account.account_number,
        'account_type': account.account_type,
        'status': account.status,
        'total_deposits': account.get_total_deposits(),
        'total_withdrawals': account.get_total_withdrawals(),
    })


@api_bp.route('/fraud-alerts/count')
@login_required
def fraud_alert_count():
    account = current_user.get_primary_account()
    count = FraudAlert.query.filter_by(account_id=account.id, is_resolved=False).count()
    return jsonify({'count': count})


@api_bp.route('/admin/stats')
@login_required
def admin_stats():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    from app.models.user import User
    from app.models.account import Account
    return jsonify({
        'total_users': User.query.filter_by(is_admin=False).count(),
        'total_accounts': Account.query.count(),
        'total_transactions': Transaction.query.count(),
        'open_alerts': FraudAlert.query.filter_by(is_resolved=False).count(),
        'total_volume': db.session.query(func.sum(Transaction.amount)).scalar() or 0,
    })
