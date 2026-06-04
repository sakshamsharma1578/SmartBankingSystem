from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.banking_service import deposit, withdraw, transfer, get_transactions
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit_funds():
    account = current_user.get_primary_account()

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            description = request.form.get('description', 'Deposit')
            success, result = deposit(account.id, amount, description,
                                      user_id=current_user.id,
                                      ip=request.remote_addr)
            if success:
                flash(f'Successfully deposited ${amount:,.2f}. New balance: ${account.balance:,.2f}', 'success')
            else:
                flash(result, 'danger')
        except ValueError:
            flash('Invalid amount entered.', 'danger')
        return redirect(url_for('transactions.deposit_funds'))

    return render_template('user/deposit.html', account=account)


@transactions_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw_funds():
    account = current_user.get_primary_account()

    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            description = request.form.get('description', 'Withdrawal')
            success, result = withdraw(account.id, amount, description,
                                       user_id=current_user.id,
                                       ip=request.remote_addr)
            if success:
                flash(f'Successfully withdrew ${amount:,.2f}. New balance: ${account.balance:,.2f}', 'success')
            else:
                flash(result, 'danger')
        except ValueError:
            flash('Invalid amount entered.', 'danger')
        return redirect(url_for('transactions.withdraw_funds'))

    return render_template('user/withdraw.html', account=account)


@transactions_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer_funds():
    account = current_user.get_primary_account()

    if request.method == 'POST':
        try:
            to_account_number = request.form.get('to_account_number', '').strip()
            amount = float(request.form.get('amount', 0))
            description = request.form.get('description', 'Transfer')
            success, result = transfer(account.id, to_account_number, amount, description,
                                       user_id=current_user.id,
                                       ip=request.remote_addr)
            if success:
                flash(f'Transfer of ${amount:,.2f} completed successfully.', 'success')
            else:
                flash(result, 'danger')
        except ValueError:
            flash('Invalid amount entered.', 'danger')
        return redirect(url_for('transactions.transfer_funds'))

    return render_template('user/transfer.html', account=account)


@transactions_bp.route('/transactions')
@login_required
def history():
    account = current_user.get_primary_account()
    page = request.args.get('page', 1, type=int)
    txn_type = request.args.get('type', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    min_amount = request.args.get('min_amount', '')
    max_amount = request.args.get('max_amount', '')

    start_date = None
    end_date = None
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    except ValueError:
        pass

    pagination = get_transactions(account.id, page=page, per_page=15,
                                  txn_type=txn_type or None,
                                  start_date=start_date, end_date=end_date,
                                  min_amount=min_amount or None,
                                  max_amount=max_amount or None)

    return render_template('user/transactions.html',
                           account=account,
                           pagination=pagination,
                           transactions=pagination.items,
                           filters={
                               'type': txn_type,
                               'start_date': start_date_str,
                               'end_date': end_date_str,
                               'min_amount': min_amount,
                               'max_amount': max_amount
                           })
