from app import db
from datetime import datetime
import uuid


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, transfer_in, transfer_out
    amount = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    reference_id = db.Column(db.String(36), nullable=True)  # for linking transfers
    is_flagged = db.Column(db.Boolean, default=False)
    anomaly_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'balance_after': self.balance_after,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'is_flagged': self.is_flagged
        }

    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'
