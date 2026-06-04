from app import db
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.transfer import Transfer
from app.models.audit_log import AuditLog
from app.services.fraud_service import check_fraud_rules
from datetime import datetime
import uuid


def deposit(account_id, amount, description=None, user_id=None, ip=None):
    account = Account.query.get(account_id)
    if not account:
        return False, "Account not found"
    if account.status != 'active':
        return False, f"Account is {account.status}. Transactions not allowed."
    if amount <= 0:
        return False, "Amount must be positive"

    account.balance += amount
    txn = Transaction(
        account_id=account_id,
        transaction_type='deposit',
        amount=amount,
        balance_after=account.balance,
        description=description or 'Deposit'
    )
    db.session.add(txn)
    db.session.commit()

    check_fraud_rules(account, txn)
    _log(user_id, 'deposit', f'Deposited ${amount:.2f} to account {account.account_number}', ip)
    return True, txn


def withdraw(account_id, amount, description=None, user_id=None, ip=None):
    account = Account.query.get(account_id)
    if not account:
        return False, "Account not found"
    if account.status != 'active':
        return False, f"Account is {account.status}. Transactions not allowed."
    if amount <= 0:
        return False, "Amount must be positive"
    if amount > account.balance:
        return False, "Insufficient funds"

    account.balance -= amount
    txn = Transaction(
        account_id=account_id,
        transaction_type='withdrawal',
        amount=amount,
        balance_after=account.balance,
        description=description or 'Withdrawal'
    )
    db.session.add(txn)
    db.session.commit()

    check_fraud_rules(account, txn)
    _log(user_id, 'withdrawal', f'Withdrew ${amount:.2f} from account {account.account_number}', ip)
    return True, txn


def transfer(from_account_id, to_account_number, amount, description=None, user_id=None, ip=None):
    from_account = Account.query.get(from_account_id)
    to_account = Account.query.filter_by(account_number=to_account_number).first()

    if not from_account:
        return False, "Source account not found"
    if not to_account:
        return False, "Destination account not found"
    if from_account.id == to_account.id:
        return False, "Cannot transfer to the same account"
    if from_account.status != 'active':
        return False, f"Source account is {from_account.status}"
    if to_account.status != 'active':
        return False, f"Destination account is {to_account.status}"
    if amount <= 0:
        return False, "Amount must be positive"
    if amount > from_account.balance:
        return False, "Insufficient funds"

    ref_id = str(uuid.uuid4())
    from_account.balance -= amount
    to_account.balance += amount

    transfer_record = Transfer(
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=amount,
        description=description or f'Transfer to {to_account.account_number}',
        status='completed'
    )
    db.session.add(transfer_record)

    out_txn = Transaction(
        account_id=from_account.id,
        transaction_type='transfer_out',
        amount=amount,
        balance_after=from_account.balance,
        description=f'Transfer to {to_account.account_number}',
        reference_id=ref_id
    )
    in_txn = Transaction(
        account_id=to_account.id,
        transaction_type='transfer_in',
        amount=amount,
        balance_after=to_account.balance,
        description=f'Transfer from {from_account.account_number}',
        reference_id=ref_id
    )
    db.session.add(out_txn)
    db.session.add(in_txn)
    db.session.commit()

    check_fraud_rules(from_account, out_txn)
    _log(user_id, 'transfer', f'Transferred ${amount:.2f} from {from_account.account_number} to {to_account.account_number}', ip)
    return True, transfer_record


def get_transactions(account_id, page=1, per_page=10, txn_type=None,
                     start_date=None, end_date=None, min_amount=None, max_amount=None):
    query = Transaction.query.filter_by(account_id=account_id)

    if txn_type:
        query = query.filter_by(transaction_type=txn_type)
    if start_date:
        query = query.filter(Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(Transaction.created_at <= end_date)
    if min_amount:
        query = query.filter(Transaction.amount >= float(min_amount))
    if max_amount:
        query = query.filter(Transaction.amount <= float(max_amount))

    return query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)


def _log(user_id, action, details, ip=None):
    log = AuditLog(user_id=user_id, action=action, details=details, ip_address=ip)
    db.session.add(log)
    db.session.commit()
