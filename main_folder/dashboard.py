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



# Route to the main dashboard
@dashboard.route('/')
def maindashboard():
    # Query to get the total number of clients
    total_clients_response = supabase.table('clients').select('id').execute()
    total_clients = len(total_clients_response.data) if total_clients_response.data else 0

    # Query to get the total number of suppliers
    total_suppliers_response = supabase.table('suppliers').select('id').execute()
    total_suppliers = len(total_suppliers_response.data) if total_suppliers_response.data else 0

    # Query to get the total number of customers
    total_customers_response = supabase.table('customers').select('id').execute()
    total_customers = len(total_customers_response.data) if total_customers_response.data else 0

    # Query to get total sales
    total_sales_response = supabase.table('sales').select('total_amount').execute()
    total_sales = sum([row['total_amount'] for row in total_sales_response.data]) if total_sales_response.data else 0

    # Query to get total purchases
    total_purchases_response = supabase.table('purchases').select('total_amount').execute()
    total_purchases = sum([row['total_amount'] for row in total_purchases_response.data]) if total_purchases_response.data else 0

    # Query to get total expenses
    total_expenses_response = supabase.table('expenses').select('amount').execute()
    total_expenses = sum([row['amount'] for row in total_expenses_response.data]) if total_expenses_response.data else 0

    total_treatments_response = supabase.table('treatment_log').select('total_poles').execute()
    total_treatments = sum([row['total_poles'] for row in total_treatments_response.data]) if total_treatments_response.data else 0




    # Query to get daily treatments
    daily_treatments_response = supabase.table('treatment_log').select('date', 'cylinder_no', 'treatment_purpose', 'total_poles').execute()
    daily_treatments = daily_treatments_response.data if daily_treatments_response.data else []
    print (daily_treatments)

    # Sort treatments by date
    daily_treatments.sort(key=lambda x: x['date'], reverse=True)

    # Get the 10 most recent treatments
    recent_treatments = daily_treatments[:5]

    daily_sales_response = supabase.table('sales').select('date', 'quantity', 'total_amount').execute()
    daily_sales = daily_sales_response.data if daily_sales_response.data else []
    print (daily_sales)
    recent_sales = daily_sales[:5]


    daily_purchases_response = supabase.table('purchases').select('created_at', 'supplier', 'total_amount').execute()
    daily_purchases = daily_purchases_response.data if daily_purchases_response.data else []
    print (daily_purchases)
    recent_purchases = daily_purchases[:5]

    daily_expenses_response = supabase.table('expenses').select('date', 'description', 'amount').execute()
    daily_expenses = daily_expenses_response.data if daily_expenses_response.data else []
    print (daily_expenses)
    recent_expenses = daily_expenses[:5]



















    # Pass the results to the template
    return render_template(
        'dashboard/main_dashboard.html',
        total_clients=total_clients,
        total_suppliers=total_suppliers,
        total_customers=total_customers,
        total_sales=total_sales,
        total_purchases=total_purchases,
        total_expenses=total_expenses,
        total_treatments=total_treatments,
        recent_treatments=recent_treatments,
        recent_sales=recent_sales,
        recent_purchases=recent_purchases,
        recent_expenses=recent_expenses

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
    total_purchases = sum(item['total_amount'] for item in purchases.data) if purchases.data else 0
    total_receipts = sum(item['amount'] for item in receipts.data) if receipts.data else 0
    total_expenses = sum(item['amount'] for item in expenses.data) if expenses.data else 0
    total_salaries = sum(item['amount'] for item in salaries.data) if salaries.data else 0
    total_payment_vouchers = sum(item['total_amount'] for item in payment_vouchers.data) if payment_vouchers.data else 0

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




@dashboard.route('/kdl_stock')
def kdl_stock():
    # Query to get all poles from the table
    total_poles_response = supabase.table('kdl_treated_poles').select('rafters', 'timber', 'fencing_poles', '7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m').execute()
    
    if total_poles_response.data:
        # Initialize sums for each category
        sums = {
            'rafters': sum(row['rafters'] for row in total_poles_response.data if row['rafters']),
            'timber': sum(row['timber'] for row in total_poles_response.data if row['timber']),
            'fencing_poles': sum(row['fencing_poles'] for row in total_poles_response.data if row['fencing_poles']),
            '7m': sum(row['7m'] for row in total_poles_response.data if row['7m']),
            '8m': sum(row['8m'] for row in total_poles_response.data if row['8m']),
            '9m': sum(row['9m'] for row in total_poles_response.data if row['9m']),
            '10m': sum(row['10m'] for row in total_poles_response.data if row['10m']),
            '11m': sum(row['11m'] for row in total_poles_response.data if row['11m']),
            '12m': sum(row['12m'] for row in total_poles_response.data if row['12m']),
            '14m': sum(row['14m'] for row in total_poles_response.data if row['14m']),
            '16m': sum(row['16m'] for row in total_poles_response.data if row['16m'])
        }
    else:
        sums = {
            'rafters': 0, 'timber': 0, 'fencing_poles': 0, '7m': 0, '8m': 0,
            '9m': 0, '10m': 0, '11m': 0, '12m': 0, '14m': 0, '16m': 0
        }

    return render_template('dashboard/hdl_treated.html', total_poles=sums)






























@dashboard.route('/kdl_sales')
def kdl_sales():
    try:
        # Fetch sales data with related client and customer names
        sales_data = supabase.table('sales').select("*", "client_id(name)", "customer_id(full_name)").order("date", desc=True).execute().data
        print(f"Sales: {sales_data}")

        # Fetch clients and customers for validation
        clients = supabase.table('clients').select('*').execute().data
        customers = supabase.table('customers').select('*').execute().data

        # Validate client data
        if not all(isinstance(client['id'], int) for client in clients):
            flash('Invalid client data fetched.', 'danger')
            print(f"Clients: {clients}")
            clients = []

        # Validate customer data
        if not all(isinstance(customer['id'], int) for customer in customers):
            flash('Invalid customer data fetched.', 'danger')
            print(f"Customers: {customers}")
            customers = []

        return render_template('dashboard/sales.html', sales=sales_data, clients=clients, customers=customers)

    except Exception as e:
        flash(f'Error fetching sales data: {str(e)}', 'danger')
        return render_template('dashboard/sales.html', sales=sales, clients= clients, customers=customers)

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


@dashboard.route('/invoice')
def invoice():
    return render_template('dashboard/invoice.html')

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
    try:
        # Fetch all payment vouchers records from the Supabase table
        response = supabase.table('payment_vouchers').select('*').execute()

        # Check if the response is successful and contains data
        if response:
            print(response)  # For debugging
            payment_vouchers = response.data
        else:
            payment_vouchers = []

        return render_template('dashboard/paymentvouchers.html', payment_vouchers=payment_vouchers)

    except Exception as e:
        # In case of an error, return an empty list and log the error
        print(f"Error fetching payment vouchers: {str(e)}")
        return render_template('dashboard/paymentvouchers.html', payment_vouchers=[])

#taxes
@dashboard.route('/taxes')
def taxes():
    return render_template('dashboard/taxes.html')

#recipts
@dashboard.route('/receipts')
def kdl_receipts():
    try:
        # Fetch receipts data with related client and customer names
        receipts_data = supabase.table('receipts').select(
            "*", 
            "client_id(name)",
            "customer_id(full_name)"
        ).execute().data
        
        print(f"Receipts: {receipts_data}")  # For debugging
        
        return render_template('dashboard/receipts.html', receipts=receipts_data)

    except Exception as e:
        print(f"Error fetching receipts: {str(e)}")
        return render_template('dashboard/kdl_receipts.html', receipts=[])

@dashboard.route('/other_expenses')
def other_expenses():
    try:
        # Fetch all other expenses records from the Supabase table
        response = supabase.table('expenses').select('*').execute()

        # Check if the response is successful and contains data
        if response:
            #print(response.data)  # Uncomment this line to see the raw response data
            print(response)
            expenses = response.data  # This contains the other expenses records
        else:
            expenses = []

        return render_template('dashboard/other_expenses.html', expenses=expenses)
    

    except Exception as e:
        # In case of an error, return an empty list and log the error
        print(f"Error fetching other expenses: {str(e)}")
        return render_template('dashboard/other_expenses.html', expenses=[])
