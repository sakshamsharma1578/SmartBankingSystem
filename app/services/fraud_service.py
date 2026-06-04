from app import db
from app.models.fraud_alert import FraudAlert
from datetime import datetime, timedelta


LARGE_TRANSACTION_THRESHOLD = 10000.0
RAPID_WITHDRAWAL_COUNT = 5
RAPID_WITHDRAWAL_WINDOW = 10  # minutes
RAPID_TRANSFER_COUNT = 3
RAPID_TRANSFER_WINDOW = 5  # minutes


def check_fraud_rules(account, transaction):
    alerts = []

    # Rule 1: Large transaction
    if transaction.amount >= LARGE_TRANSACTION_THRESHOLD:
        severity = 'critical' if transaction.amount >= 50000 else 'high'
        alert = FraudAlert(
            account_id=account.id,
            alert_type='large_transaction',
            severity=severity,
            description=f'Large {transaction.transaction_type} of ${transaction.amount:,.2f} detected on account {account.account_number}.',
            transaction_id=transaction.transaction_id
        )
        alerts.append(alert)

    # Rule 2: Multiple withdrawals in short period
    if transaction.transaction_type == 'withdrawal':
        window_start = datetime.utcnow() - timedelta(minutes=RAPID_WITHDRAWAL_WINDOW)
        from app.models.transaction import Transaction
        recent_withdrawals = Transaction.query.filter(
            Transaction.account_id == account.id,
            Transaction.transaction_type == 'withdrawal',
            Transaction.created_at >= window_start
        ).count()

        if recent_withdrawals >= RAPID_WITHDRAWAL_COUNT:
            alert = FraudAlert(
                account_id=account.id,
                alert_type='rapid_withdrawals',
                severity='high',
                description=f'{recent_withdrawals} withdrawals detected within {RAPID_WITHDRAWAL_WINDOW} minutes on account {account.account_number}.',
                transaction_id=transaction.transaction_id
            )
            alerts.append(alert)

    # Rule 3: Rapid transfers
    if transaction.transaction_type == 'transfer_out':
        window_start = datetime.utcnow() - timedelta(minutes=RAPID_TRANSFER_WINDOW)
        from app.models.transaction import Transaction
        recent_transfers = Transaction.query.filter(
            Transaction.account_id == account.id,
            Transaction.transaction_type == 'transfer_out',
            Transaction.created_at >= window_start
        ).count()

        if recent_transfers >= RAPID_TRANSFER_COUNT:
            alert = FraudAlert(
                account_id=account.id,
                alert_type='rapid_transfers',
                severity='medium',
                description=f'{recent_transfers} outgoing transfers detected within {RAPID_TRANSFER_WINDOW} minutes.',
                transaction_id=transaction.transaction_id
            )
            alerts.append(alert)

    for alert in alerts:
        db.session.add(alert)
    if alerts:
        db.session.commit()

    return alerts


def check_failed_logins(user):
    from app.models.fraud_alert import FraudAlert
    from app.models.account import Account

    if user.failed_login_attempts >= 5:
        account = user.get_primary_account()
        if account:
            existing = FraudAlert.query.filter_by(
                account_id=account.id,
                alert_type='repeated_failed_logins',
                is_resolved=False
            ).first()
            if not existing:
                alert = FraudAlert(
                    account_id=account.id,
                    alert_type='repeated_failed_logins',
                    severity='high',
                    description=f'{user.failed_login_attempts} failed login attempts for user {user.email}.'
                )
                db.session.add(alert)
                db.session.commit()


def run_ml_fraud_detection(account_id):
    """Run Isolation Forest ML model on recent transactions."""
    try:
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ml'))
        from fraud_detection import detect_anomalies
        return detect_anomalies(account_id)
    except Exception as e:
        return None, str(e)
