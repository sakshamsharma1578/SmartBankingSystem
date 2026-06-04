"""
SmartBank ML Fraud Detection Module
Uses Isolation Forest to detect anomalous transactions.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime


def detect_anomalies(account_id):
    """
    Run Isolation Forest on account transactions.
    Returns list of (transaction, anomaly_score, is_anomaly) tuples.
    """
    try:
        from app import create_app, db
        from app.models.transaction import Transaction

        app = create_app()
        with app.app_context():
            transactions = Transaction.query.filter_by(account_id=account_id)\
                .order_by(Transaction.created_at.asc()).all()

            if len(transactions) < 5:
                return None, "Not enough transactions for ML analysis (need at least 5)"

            # Feature engineering
            features = []
            for i, txn in enumerate(transactions):
                amount = txn.amount

                # Time gap in minutes from previous transaction
                if i > 0:
                    gap = (txn.created_at - transactions[i-1].created_at).total_seconds() / 60.0
                else:
                    gap = 0.0

                # Rolling frequency (transactions in last hour)
                one_hour_ago = txn.created_at - __import__('datetime').timedelta(hours=1)
                freq = sum(1 for t in transactions[:i] if t.created_at >= one_hour_ago)

                # Normalized hour of day
                hour_of_day = txn.created_at.hour

                features.append([amount, gap, freq, hour_of_day])

            X = np.array(features)

            # Train Isolation Forest
            model = IsolationForest(
                n_estimators=100,
                contamination=0.1,  # expect ~10% anomalies
                random_state=42,
                n_jobs=-1
            )
            model.fit(X)

            predictions = model.predict(X)        # 1=normal, -1=anomaly
            scores = model.score_samples(X)       # more negative = more anomalous
            normalized_scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)

            results = []
            for i, txn in enumerate(transactions):
                is_anomaly = predictions[i] == -1
                anomaly_score = round(float(1 - normalized_scores[i]), 4)  # higher=more suspicious

                # Update transaction in DB
                txn.anomaly_score = anomaly_score
                if is_anomaly and anomaly_score > 0.7:
                    txn.is_flagged = True

                results.append({
                    'transaction_id': txn.transaction_id,
                    'amount': txn.amount,
                    'type': txn.transaction_type,
                    'anomaly_score': anomaly_score,
                    'is_anomaly': is_anomaly,
                    'label': 'Suspicious' if is_anomaly else 'Normal'
                })

            db.session.commit()
            return results, None

    except Exception as e:
        return None, str(e)


if __name__ == '__main__':
    print("SmartBank ML Fraud Detection Module")
    print("Run via Flask app context for full functionality.")
