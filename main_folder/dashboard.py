from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

dashboard = Blueprint('dashboard', __name__)

#routes for this blueprint
#maindashboard
#finance
#sales
#hr
#inventory
#stock
#treatment
#user mangement
#clients
#reports
#customers
#suppliers


@dashboard.route('/maindashboard')
def maindashboard():
    return render_template('dashboard/maindashboard.html')

@dashboard.route('/finance')
def finance():
    return render_template('dashboard/finance.html')

@dashboard.route('/sales')
def sales():
    return render_template('dashboard/sales.html')

@dashboard.route('/hr')
def hr():
    return render_template('dashboard/hr.html')

@dashboard.route('/inventory')
def inventory():
    return render_template('dashboard/inventory.html')

@dashboard.route('/stock')
def stock():
    return render_template('dashboard/stock.html')

@dashboard.route('/treatment')
def treatment():
    return render_template('dashboard/treatment.html')

@dashboard.route('/usermangement')
def usermangement():
    return render_template('dashboard/usermangement.html')

@dashboard.route('/clients')
def clients():
    return render_template('dashboard/clients.html')

@dashboard.route('/reports')
def reports():
    return render_template('dashboard/reports.html')

@dashboard.route('/customers')
def customers():
    return render_template('dashboard/customers.html')

@dashboard.route('/suppliers')
def suppliers():
    return render_template('dashboard/suppliers.html')



