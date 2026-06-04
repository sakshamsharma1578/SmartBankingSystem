from app import db
from datetime import datetime
import random
import string


class Account(db.Model):
    __tablename__ = 'accounts'

    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(12), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_type = db.Column(db.String(20), nullable=False, default='savings')  # savings, current
    balance = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, frozen, closed
    is_primary = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy='dynamic',
                                   foreign_keys='Transaction.account_id', cascade='all, delete-orphan')
    sent_transfers = db.relationship('Transfer', backref='sender_account', lazy='dynamic',
                                     foreign_keys='Transfer.from_account_id')
    received_transfers = db.relationship('Transfer', backref='receiver_account', lazy='dynamic',
                                         foreign_keys='Transfer.to_account_id')
    fraud_alerts = db.relationship('FraudAlert', backref='account', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def generate_account_number():
        from app.models.account import Account
        while True:
            number = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            if not Account.query.filter_by(account_number=number).first():
                return number

    def get_total_deposits(self):
        from app.models.transaction import Transaction
        result = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.account_id == self.id,
            Transaction.transaction_type == 'deposit'
        ).scalar()
        return result or 0.0

    def get_total_withdrawals(self):
        from app.models.transaction import Transaction
        result = db.session.query(db.func.sum(Transaction.amount)).filter(
            Transaction.account_id == self.id,
            Transaction.transaction_type == 'withdrawal'
        ).scalar()
        return result or 0.0

    def get_total_transfers_sent(self):
        from app.models.transfer import Transfer
        result = db.session.query(db.func.sum(Transfer.amount)).filter(
            Transfer.from_account_id == self.id,
            Transfer.status == 'completed'
        ).scalar()
        return result or 0.0

    def __repr__(self):
        return f'<Account {self.account_number}>'
