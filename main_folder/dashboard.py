from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
import os
from dotenv import load_dotenv
from supabase import create_client, Client
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

from flask import render_template
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



@dashboard.route('/maindashboard')
def maindashboard():
    # Query to get the total number of users
    total_users_response = supabase.table('users').select('id').execute()
    total_users = len(total_users_response.data) if total_users_response.data else 0
    
    # Query to get the total number of clients
    total_clients_response = supabase.table('clients').select('id').execute()
    total_clients = len(total_clients_response.data) if total_clients_response.data else 0
    
    # Query to get the total number of suppliers
    total_suppliers_response = supabase.table('suppliers').select('id').execute()
    total_suppliers = len(total_suppliers_response.data) if total_suppliers_response.data else 0
    
    # Query to get the total number of customers
    total_customers_response = supabase.table('customers').select('id').execute()
    total_customers = len(total_customers_response.data) if total_customers_response.data else 0
    
    # Query to get total sales (replace 'amount' with the actual column name)
    total_sales_response = supabase.table('sales').select('total_amount').execute()
    total_sales = sum([row['total_amount'] for row in total_sales_response.data]) if total_sales_response.data else 0
    
    # Query to get total purchases (replace 'amount' with the actual column name)
    total_purchases_response = supabase.table('purchases').select('total_amount').execute()
    total_purchases = sum([row['total_amount'] for row in total_purchases_response.data]) if total_purchases_response.data else 0
    
    # Query to get total expenses (replace 'amount' with the actual column name)
    total_expenses_response = supabase.table('expenses').select('amount').execute()
    total_expenses = sum([row['amount'] for row in total_expenses_response.data]) if total_expenses_response.data else 0

    # Pass the results to the template
    return render_template(
        'dashboard/main_dashboard.html',
        total_users=total_users,
        total_clients=total_clients,
        total_suppliers=total_suppliers,
        total_customers=total_customers,
        total_sales=total_sales,
        total_purchases=total_purchases,
        total_expenses=total_expenses
    )





@dashboard.route('/finance')
def finance():
    # Fetch data from Supabase
    sales = supabase.table('sales').select('total_amount').execute()
    purchases = supabase.table('purchases').select('total_amount').execute()
    receipts = supabase.table('receipts').select('amount').execute()
    expenses = supabase.table('expenses').select('amount').execute()
    salaries = supabase.table('salary_payments').select('amount').execute()
    payment_vouchers = supabase.table('payment_vouchers').select('total_amount').execute()

    # Sum up the amounts
    total_sales = sum(item['amount'] for item in sales.data) if sales.data else 0
    total_purchases = sum(item['amount'] for item in purchases.data) if purchases.data else 0
    total_receipts = sum(item['amount'] for item in receipts.data) if receipts.data else 0
    total_expenses = sum(item['amount'] for item in expenses.data) if expenses.data else 0
    total_salaries = sum(item['amount'] for item in salaries.data) if salaries.data else 0
    total_payment_vouchers = sum(item['amount'] for item in payment_vouchers.data) if payment_vouchers.data else 0

    final_expeses = total_expenses + total_salaries + total_payment_vouchers + total_purchases


    

    # Calculate net income
    net_income = (
        total_sales + total_receipts
        - final_expeses
    )

    # Pass data to the template
    context = {
        'total_sales': total_sales,
        'total_purchases': total_purchases,
        'total_receipts': total_receipts,
        'total_expenses': total_expenses,
        'total_salaries': total_salaries,
        'total_payment_vouchers': total_payment_vouchers,
        'net_income': net_income,

        'final_expeses' : final_expeses,
    }

    return render_template('dashboard/finance.html', **context)




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

# Route to add a new customer
@dashboard.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('telephone')

    # Add a new customer to Supabase
    supabase.table('customers').insert({
        'full_name': name,
        'email': email,
        'telephone': phone
    }).execute()

    return redirect(url_for('dashboard.customers'))


# fetch customers from supabase
@dashboard.route('/customers')
def customers():
    response = supabase.table('customers').select('*').execute()
    customers = response.data if response.data else []
    
    return render_template('customers/customers.html', customers=customers)




# Route to edit an existing customer
@dashboard.route('/edit_customer', methods=['POST'])
def edit_customer():
    customer_id = request.form.get('customer_id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Update the customer in Supabase
    supabase.table('customers').update({
        'name': name,
        'email': email,
        'phone': phone
    }).eq('id', customer_id).execute()

    return redirect(url_for('dashboard.main_dashboard'))

# Route to delete a customer
@dashboard.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    # Delete the customer from Supabase
    supabase.table('customers').delete().eq('id', customer_id).execute()
    return redirect(url_for('dashboard.main_customers'))

@dashboard.route('/suppliers')
def suppliers():
    return render_template('dashboard/suppliers.html')


@dashboard.route('/invoices')
def invoices():
    return render_template('dashboard/invoices.html')

@dashboard.route('/expenses')
def expenses():
    return render_template('dashboard/expenses.html')

@dashboard.route('/purchases')
def purchases():
    try:
        # Fetch all purchase records from the Supabase table
        response = supabase.table('purchases').select('*').execute()

        # Check if the response is successful and contains data
        if response:
            #print(response.data)  # Uncomment this line to see the raw response data
            print(response)
            purchases = response.data  # This contains the purchase records
        else:
            purchases = []

        return render_template('dashboard/purchase.html', purchases=purchases)

    except Exception as e:
        # In case of an error, return an empty list and log the error
        print(f"Error fetching purchases: {str(e)}")
        return render_template('dashboard/purchase.html', purchases=[])
    


@dashboard.route('/paymentvouchers')
def paymentvouchers():
    return render_template('dashboard/paymentvouchers.html')

#taxes
@dashboard.route('/taxes')
def taxes():
    return render_template('dashboard/taxes.html')

#recipts
@dashboard.route('/reciepts')
def reciepts():
    return render_template('dashboard/reciepts.html')
