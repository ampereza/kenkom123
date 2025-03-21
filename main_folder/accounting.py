from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Blueprint
from flask_login import login_required, current_user

accounting = Blueprint('accounting', __name__)


#templates for this blueprint are in the folder templates/accounts

#routes
#accounting_dashboard
#accounts_base
#create_invoice
#inventory
#invoice
#ledgers
#payroll
#reports
#taxes
#recipts
#payment_vouchers
#journal
#accounting_settings


@accounting.route('/accounts_dashboard')
@login_required
def accounting_dashboard():
    return render_template('accounts/accounts_dashboard.html')


@accounting.route('/accounts_base')
@login_required
def accounts_base():
    return render_template('accounts/accounts_base.html')

@accounting.route('/create_invoice')
@login_required
def create_base():
    return render_template('accounts/create_invoice.html')

@accounting.route('/inventory')
@login_required
def inventory():
    return render_template('accounts/inventory.html')

@accounting.route('/invoice')
@login_required
def invoice():
    return render_template('accounts/invoice.html')

@accounting.route('/ledgers')
@login_required
def ledgers():
    return render_template('accounts/ledgers.html')

@accounting.route('/payroll')
@login_required
def payroll():
    return render_template('accounts/payroll.html')

@accounting.route('/reports')
@login_required
def reports():
    return render_template('accounts/reports.html')

@accounting.route('/taxes')
@login_required
def taxes():
    return render_template('accounts/taxes.html')

@accounting.route('/recipts')
@login_required
def reciepts():
    return render_template('accounts/reciepts.html')


@accounting.route('/payment_vouchers')
@login_required
def payment_vouchers():
    return render_template('accounts/payment_vouchers.html')

@accounting.route('/journal')
@login_required
def journal():
    return render_template('accounts/journal.html')


