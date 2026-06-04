from flask import Blueprint, send_file, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.transaction import Transaction
from app.services.report_service import generate_statement_pdf
from datetime import datetime

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/download-statement')
@login_required
def download_statement():
    account = current_user.get_primary_account()
    start_str = request.args.get('start_date', '')
    end_str = request.args.get('end_date', '')

    query = Transaction.query.filter_by(account_id=account.id)
    start_date = end_date = None

    try:
        if start_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d')
            query = query.filter(Transaction.created_at >= start_date)
        if end_str:
            end_date = datetime.strptime(end_str, '%Y-%m-%d')
            query = query.filter(Transaction.created_at <= end_date)
    except ValueError:
        pass

    transactions = query.order_by(Transaction.created_at.desc()).all()
    pdf_buffer = generate_statement_pdf(account, transactions, start_str, end_str)
    filename = f'smartbank_statement_{account.account_number}_{datetime.utcnow().strftime("%Y%m%d")}.pdf'
    return send_file(pdf_buffer, mimetype='application/pdf',
                     as_attachment=True, download_name=filename)
