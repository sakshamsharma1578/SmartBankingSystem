from app import db
from app.models.user import User
from app.models.account import Account
from app.models.audit_log import AuditLog


def ensure_admin_exists():
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            full_name='SmartBank Admin',
            email='admin@smartbank.com',
            phone_number='+1-000-000-0000',
            is_admin=True
        )
        admin.set_password('Admin@123456')
        db.session.add(admin)
        db.session.commit()
        print('[SmartBank] Default admin created: admin@smartbank.com / Admin@123456')


def freeze_account(account_id, admin_user_id):
    account = Account.query.get(account_id)
    if account:
        account.status = 'frozen'
        db.session.commit()
        _log(admin_user_id, 'freeze_account', f'Froze account {account.account_number}')
        return True
    return False


def unfreeze_account(account_id, admin_user_id):
    account = Account.query.get(account_id)
    if account:
        account.status = 'active'
        db.session.commit()
        _log(admin_user_id, 'unfreeze_account', f'Unfroze account {account.account_number}')
        return True
    return False


def delete_user(user_id, admin_user_id):
    user = User.query.get(user_id)
    if user and not user.is_admin:
        db.session.delete(user)
        db.session.commit()
        _log(admin_user_id, 'delete_user', f'Deleted user ID {user_id}')
        return True
    return False


def _log(user_id, action, details):
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()
