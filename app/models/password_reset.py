from app import db
from datetime import datetime, timedelta
import secrets


class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_token(user_id):
        token = secrets.token_urlsafe(48)
        reset_token = PasswordResetToken(
            user_id=user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        return reset_token

    def is_valid(self):
        return not self.is_used and datetime.utcnow() < self.expires_at

    def __repr__(self):
        return f'<PasswordResetToken user={self.user_id}>'
