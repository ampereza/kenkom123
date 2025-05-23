from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
from dateutil.parser import parse  # Import the parser for ISO 8601 dates

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
@dashboard.route('/maindashboard')
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

    total_receipts_response = supabase.table('receipts').select('amount').execute()
    total_receipts = sum([row['amount'] for row in total_receipts_response.data]) if total_receipts_response.data else 0
    # Query to get total payment vouchers


    # Query to get daily treatments
    daily_treatments_response = supabase.table('treatment_log').select('date', 'cylinder_no', 'treatment_purpose', 'total_poles').execute()
    daily_treatments = daily_treatments_response.data if daily_treatments_response.data else []
    print (daily_treatments)

    # Sort treatments by date
    daily_treatments.sort(key=lambda x: x['date'], reverse=True)

    # Get the 10 most recent treatments
    recent_treatments = daily_treatments[:5]

    daily_sales_response = supabase.table('sales').select('receipt_number', 'description', 'quantity', 'total_amount').execute()
    daily_sales = daily_sales_response.data if daily_sales_response.data else []
    print (daily_sales)
    recent_sales = daily_sales[:5]


    daily_purchases_response = supabase.table('purchases').select('created_at', 'supplier', 'total_amount').execute()
    daily_purchases = daily_purchases_response.data if daily_purchases_response.data else []
    print (daily_purchases)
    recent_purchases = daily_purchases[:5]

    daily_expenses_response = supabase.table('expenses').select('date', 'description', 'amount') .order('date', desc=True).execute()
    daily_expenses = daily_expenses_response.data if daily_expenses_response.data else []
    print (daily_expenses)
    recent_expenses = daily_expenses[:10]

    # Sort recent_expenses by date in ascending order, handling ISO 8601 format
    recent_expenses = sorted(recent_expenses, key=lambda x: parse(x['date']))

















    # Pass the results to the template
    return render_template(
        'dashboard/main_dashboard.html',
        total_receipts=total_receipts, 
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
        print(sums)
    else:
        sums = {
            'rafters': 0, 'timber': 0, 'fencing_poles': 0, '7m': 0, '8m': 0,
            '9m': 0, '10m': 0, '11m': 0, '12m': 0, '14m': 0, '16m': 0
        }

    return render_template('dashboard/hdl_treated.html', total_poles=sums)






























@dashboard.route('/kdl_sales')
def kdl_sales():
    try:
        # Fetch sales data sorted by created_at in descending order
        sales_data = supabase.table('sales').select("*").order("created_at", desc=True).execute().data
        print(f"Sales Data: {sales_data}")  # For debugging

        # Fetch clients and customers for validation
        clients = supabase.table('clients').select('*').execute().data
        customers = supabase.table('customers').select('*').execute().data

        # Validate client data
        if not all(isinstance(client['id'], int) for client in clients):
            flash('Invalid client data fetched.', 'danger')
           
            clients = []

        # Validate customer data
        if not all(isinstance(customer['id'], int) for customer in customers):
            flash('Invalid customer data fetched.', 'danger')
            print(f"Customers: {customers}")
            customers = []

        return render_template('dashboard/sales.html', sales=sales_data, clients=clients, customers=customers)

    except Exception as e:
        flash(f'Error fetching sales data: {str(e)}', 'danger')
        return render_template('dashboard/sales.html', sales=[], clients=[], customers=[])

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

@dashboard.route('/clients', methods=['GET', 'POST'])
def clients():
    try:
        search_query = request.args.get('search', '').strip()  # Get the search query from the request
        if search_query:
            # Filter clients based on the search query
            response = supabase.table('clients').select('*').ilike('name', f'%{search_query}%').execute()
        else:
            # Fetch all clients if no search query is provided
            response = supabase.table('clients').select('*').execute()

        clients = response.data if response.data else []

        return render_template('dashboard/clients.html', clients=clients, search_query=search_query)
    except Exception as e:
        print(f"Error fetching clients: {str(e)}")
        return render_template('dashboard/clients.html', clients=[], search_query='')
    



@dashboard.route('/edit_client', methods=['POST'])
def edit_client():
    client_id = request.form.get('client_id')
    name = request.form.get('name')
    telephone = request.form.get('telephone')
    address = request.form.get('address')

    # Update client in Supabase
    supabase.table('clients').update({
        'name': name,
        'telephone': telephone,
        'address': address
    }).eq('id', client_id).execute()

    return redirect(url_for('dashboard.clients'))

@dashboard.route('/edit_client_form/<int:client_id>', methods=['GET'])
def edit_client_form(client_id):
    # Fetch client details from Supabase
    client_response = supabase.table('clients').select('*').eq('id', client_id).execute()
    client = client_response.data[0] if client_response.data else None

    if not client:
        flash('Client not found.', 'danger')
        return redirect(url_for('dashboard.clients'))

    return render_template('dashboard/edit_client.html', client=client)

@dashboard.route('/delete_client/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    # Delete client from Supabase 
    supabase.table('clients').delete().eq('id', client_id).execute()
    return redirect(url_for('dashboard.clients'))

@dashboard.route('/add_client', methods=['POST'])
def add_client():
    try:
        name = request.form.get('name')
        address = request.form.get('address')
        telephone = request.form.get('telephone')

        # Insert new client into Supabase
        supabase.table('clients').insert({
            'name': name,
            'address': address,
            'telephone': telephone
        }).execute()

        flash('Client added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding client: {str(e)}', 'danger')

    return redirect(url_for('dashboard.clients'))

@dashboard.route('/reports')
def reports():
    return render_template('dashboard/reports.html')

# Route to add a new customer
@dashboard.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form.get('full_name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Add a new customer to Supabase
    supabase.table('customers').insert({
        'full_name': name,
        'email': email,
        'phone': phone
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
    full_name = request.form.get('name')
    email = request.form.get('email')
    telephone = request.form.get('telephone')

    # Update the customer in Supabase
    supabase.table('customers').update({
        'full_name': full_name,
        'email': email,
        'phone': telephone
    }).eq('id', customer_id).execute()

    return redirect(url_for('dashboard.maindashboard'))

# Route to delete a customer
@dashboard.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    try:
        # Delete the customer from Supabase
        supabase.table('customers').delete().eq('id', customer_id).execute()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting customer: {str(e)}', 'danger')
    return redirect(url_for('dashboard.customers'))

@dashboard.route('/suppliers')
def suppliers():
    try:
        # Fetch all suppliers from Supabase
        response = supabase.table('suppliers').select('*').execute()
        suppliers = response.data if response.data else []
        return render_template('dashboard/suppliers.html', suppliers=suppliers)
    except Exception as e:
        print(f"Error fetching suppliers: {str(e)}")
        return render_template('dashboard/suppliers.html', suppliers=[])

@dashboard.route('/edit_supplier', methods=['POST'])
def edit_supplier():
    supplier_id = request.form.get('supplier_id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')

    # Update supplier in Supabase
    supabase.table('suppliers').update({
        'name': name,
        'email': email,
        'phone': phone,
        'address': address
    }).eq('id', supplier_id).execute()

    return redirect(url_for('dashboard.suppliers'))

@dashboard.route('/delete_supplier/<int:supplier_id>', methods=['POST'])
def delete_supplier(supplier_id):
    # Delete supplier from Supabase
    supabase.table('suppliers').delete().eq('id', supplier_id).execute()
    return redirect(url_for('dashboard.suppliers'))

@dashboard.route('/add_supplier', methods=['POST'])
def add_supplier():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')

    if not all([name, email, phone, address]):
        flash('All fields are required!', 'danger')
        return redirect(url_for('dashboard.suppliers'))

    # Insert new supplier into Supabase
    supabase.table('suppliers').insert({
        'name': name,
        'email': email,
        'phone': phone,
        'address': address
    }).execute()

    flash('Supplier added successfully!', 'success')
    return redirect(url_for('dashboard.suppliers'))

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

        #
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
        return render_template('dashboard/payment_vouchers.html', payment_vouchers=[])

#taxes
@dashboard.route('/taxes')
def taxes():
    return render_template('dashboard/taxes.html')

#recipts
@dashboard.route('/kdl_receipts')
def kdl_receipts():
    try:
        # Fetch receipts data with related client and customer names
        receipts_data = supabase.table('receipts').select(
            "*"
        ).order('date', desc=True).execute().data
        
        print(f"Receipts: {receipts_data}")  # For debugging
        
        return render_template('dashboard/kdl_receipts.html', receipts_data=receipts_data)

    except Exception as e:
        print(f"Error fetching receipts: {str(e)}")
        return render_template('dashboard/kdl_receipts.html', receipts_data=[])

@dashboard.route('/other_expenses')
def other_expenses():
    try:
        # Fetch all other expenses records from the Supabase table
        response = supabase.table('expenses').select('*') .order('date', desc=True).execute()

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


@dashboard.route('/treatment_log')
def treatment_log():
    try:
        # Get all treatments
        treatments = supabase.from_('treatment_log').select('*').order('created_at', desc=True).execute().data
        
        # Create a helper function to get client info
        def get_client(client_id):
            if client_id:
                client = supabase.from_('clients').select('*').eq('id', client_id).single().execute()
                return client.data if client else None
            return None
            
        return render_template('dashboard/treatement_log.html', 
                             treatments=treatments,
                             get_client=get_client)
    except Exception as e:
        print(f"Error: {str(e)}")
        return render_template('dashboard/treatement_log.html', 
                             treatments=[],
                             get_client=lambda x: None)
    



@dashboard.route('/edit_treatment_log', methods=['POST'])
def edit_treatment_log():
    try:
        log_id = request.form.get('log_id')
        data = {
            'date': request.form.get('date'),
            'cylinder_no': request.form.get('cylinder_no'),
            'treatment_purpose': request.form.get('treatment_purpose'),
            'total_poles': int(request.form.get('total_poles')),
            'client_id': request.form.get('client_id')
        }
        
        supabase.table('treatment_log').update(data).eq('id', log_id).execute()
        flash('Treatment log updated successfully', 'success')
        
    except Exception as e:
        flash(f'Error updating treatment log: {str(e)}', 'error')
        
    return redirect(url_for('dashboard.treatment_log'))

@dashboard.route('/delete_treatment_log/<int:log_id>', methods=['POST']) 
def delete_treatment_log(log_id):
    try:
        supabase.table('treatment_log').delete().eq('id', log_id).execute()
        flash('Treatment log deleted successfully', 'success')
        
    except Exception as e:
        flash(f'Error deleting treatment log: {str(e)}', 'error')
        
    return redirect(url_for('dashboard.treatment_log'))





@dashboard.route('/stock_overview')
def stock_overview():
    try:
        # Get untreated stock totals
        untreated_response = supabase.table('kdl_to_treat').select(
            'fencing_poles', 'rafters', 'timber', 'telecom_poles', 'stubs',
            '7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m'
        ).execute()

        # Get unsorted stock totals 
        unsorted_response = supabase.table('kdl_unsorted_stock').select('quantity').execute()

        # Get treated stock totals
        treated_response = supabase.table('total_kdl_treated_poles').select(
            'fencing_poles', 'rafters', 'timber', 'telecom_poles', 'stubs',
            '7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m'
        ).execute()

        # Get rejects stock totals
        rejects_response = supabase.table('rejects').select(
            'fencing_poles', 'rafters', 'timber', 'stabs', 'telecom',
            '7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m'
        ).execute()

        # Calculate sums for untreated stock
        untreated_totals = {
            'fencing_poles': sum(row['fencing_poles'] or 0 for row in untreated_response.data),
            'rafters': sum(row['rafters'] or 0 for row in untreated_response.data),
            'timber': sum(row['timber'] or 0 for row in untreated_response.data),
            'telecom_poles': sum(row['telecom_poles'] or 0 for row in untreated_response.data),
            'stubs': sum(row['stubs'] or 0 for row in untreated_response.data),
            '7m': sum(row['7m'] or 0 for row in untreated_response.data),
            '8m': sum(row['8m'] or 0 for row in untreated_response.data),
            '9m': sum(row['9m'] or 0 for row in untreated_response.data),
            '10m': sum(row['10m'] or 0 for row in untreated_response.data),
            '11m': sum(row['11m'] or 0 for row in untreated_response.data),
            '12m': sum(row['12m'] or 0 for row in untreated_response.data),
            '14m': sum(row['14m'] or 0 for row in untreated_response.data),
            '16m': sum(row['16m'] or 0 for row in untreated_response.data)
        }

        # Calculate total unsorted stock
        unsorted_total = sum(row['quantity'] or 0 for row in unsorted_response.data)

        # Calculate sums for treated stock
        treated_totals = {
            'fencing_poles': sum(row['fencing_poles'] or 0 for row in treated_response.data),
            'rafters': sum(row['rafters'] or 0 for row in treated_response.data),
            'timber': sum(row['timber'] or 0 for row in treated_response.data),
            'telecom_poles': sum(row['telecom_poles'] or 0 for row in treated_response.data),
            'stubs': sum(row['stubs'] or 0 for row in treated_response.data),
            '7m': sum(row['7m'] or 0 for row in treated_response.data),
            '8m': sum(row['8m'] or 0 for row in treated_response.data),
            '9m': sum(row['9m'] or 0 for row in treated_response.data),
            '10m': sum(row['10m'] or 0 for row in treated_response.data),
            '11m': sum(row['11m'] or 0 for row in treated_response.data),
            '12m': sum(row['12m'] or 0 for row in treated_response.data),
            '14m': sum(row['14m'] or 0 for row in treated_response.data),
            '16m': sum(row['16m'] or 0 for row in treated_response.data)
        }

        # Calculate sums for rejects stock
        rejects_totals = {
            'fencing_poles': sum(row['fencing_poles'] or 0 for row in rejects_response.data),
            'rafters': sum(row['rafters'] or 0 for row in rejects_response.data),
            'timber': sum(row['timber'] or 0 for row in rejects_response.data),
            'stabs': sum(row['stabs'] or 0 for row in rejects_response.data),
            'telecom': sum(row['telecom'] or 0 for row in rejects_response.data),
            '7m': sum(row['7m'] or 0 for row in rejects_response.data),
            '8m': sum(row['8m'] or 0 for row in rejects_response.data),
            '9m': sum(row['9m'] or 0 for row in rejects_response.data),
            '10m': sum(row['10m'] or 0 for row in rejects_response.data),
            '11m': sum(row['11m'] or 0 for row in rejects_response.data),
            '12m': sum(row['12m'] or 0 for row in rejects_response.data),
            '14m': sum(row['14m'] or 0 for row in rejects_response.data),
            '16m': sum(row['16m'] or 0 for row in rejects_response.data)
        }

        # Example: Set a default client_id (replace with actual logic to fetch client_id if needed)
        client_id = 1  # Replace with dynamic logic if necessary

        return render_template('dashboard/stock_overview.html',
                               untreated_totals=untreated_totals,
                               unsorted_total=unsorted_total,
                               treated_totals=treated_totals,
                               rejects_totals=rejects_totals,
                               client_id=client_id)  # Pass client_id to the template

    except Exception as e:
        print(f"Error fetching stock data: {str(e)}")
        return render_template('dashboard/stock_overview.html',
                               untreated_totals={},
                               unsorted_total=0,
                               treated_totals={},
                               rejects_totals={},
                               client_id=None)  # Pass None if client_id is unavailable
    







@dashboard.route('/select_client', methods=['GET', 'POST'])
def select_client():
    try:
        # Get client_id from either POST form data or GET query parameters
        client_id = request.form.get('client_id') if request.method == 'POST' else request.args.get('client_id')
        
        # First fetch all clients for dropdown
        clients_response = supabase.table('clients').select('*').execute()
        clients = clients_response.data if clients_response.data else []

        if not client_id:
            # If no client selected, just show the client list
            return render_template('dashboard/clients_stock.html', 
                                clients=clients,
                                untreated_totals={},
                                treated_totals={},
                                unsorted_total=0,
                                client_name=None)

        # Get client name
        client = next((c for c in clients if str(c['id']) == str(client_id)), None)
        client_name = client['name'] if client else 'Unknown Client'
                                  
        # Fetch untreated stock totals for the client
        untreated_response = supabase.table('client_to_treat').select(
            'fencing_poles', 'rafters', 'timber', 'telecom_poles', 'stubs',
            '7m', '8m', '9m', '9m_telecom', '10m', '10m_telecom', '11m', 
            '12m', '12m_telecom', '14m', '16m'
        ).eq('client_id', client_id).execute()

        # Fetch treated stock totals for the client
        treated_response = supabase.table('total_clients_treated_poles').select(
            'fencing_poles', 'rafters', 'timber', 'telecom_poles', 'stubs',
            '7m', '8m', '9m', '9m_telecom', '10m', '10m_telecom', '11m',
            '12m', '12m_telecom', '14m', '16m'
        ).eq('client_id', client_id).execute()

        # Fetch unsorted stock total for the client
        unsorted_response = supabase.table('total_clients_unsorted').select('quantity').eq('client_id', client_id).execute()

        # Calculate sums for untreated stock
        untreated_totals = {
            'fencing_poles': sum(row['fencing_poles'] or 0 for row in untreated_response.data),
            'rafters': sum(row['rafters'] or 0 for row in untreated_response.data),
            'timber': sum(row['timber'] or 0 for row in untreated_response.data),
            'telecom_poles': sum(row['telecom_poles'] or 0 for row in untreated_response.data),
            'stubs': sum(row['stubs'] or 0 for row in untreated_response.data),
            '7m': sum(row['7m'] or 0 for row in untreated_response.data),
            '8m': sum(row['8m'] or 0 for row in untreated_response.data),
            '9m': sum(row['9m'] or 0 for row in untreated_response.data),
            '9m_telecom': sum(row['9m_telecom'] or 0 for row in untreated_response.data),
            '10m': sum(row['10m'] or 0 for row in untreated_response.data),
            '10m_telecom': sum(row['10m_telecom'] or 0 for row in untreated_response.data),
            '11m': sum(row['11m'] or 0 for row in untreated_response.data),
            '12m': sum(row['12m'] or 0 for row in untreated_response.data),
            '12m_telecom': sum(row['12m_telecom'] or 0 for row in untreated_response.data),
            '14m': sum(row['14m'] or 0 for row in untreated_response.data),
            '16m': sum(row['16m'] or 0 for row in untreated_response.data)
        }

        # Calculate sums for treated stock
        treated_totals = {
            'fencing_poles': sum(row['fencing_poles'] or 0 for row in treated_response.data),
            'rafters': sum(row['rafters'] or 0 for row in treated_response.data),
            'timber': sum(row['timber'] or 0 for row in treated_response.data),
            'telecom_poles': sum(row['telecom_poles'] or 0 for row in treated_response.data),
            'stubs': sum(row['stubs'] or 0 for row in treated_response.data),
            '7m': sum(row['7m'] or 0 for row in treated_response.data),
            '8m': sum(row['8m'] or 0 for row in treated_response.data),
            '9m': sum(row['9m'] or 0 for row in treated_response.data),
            '9m_telecom': sum(row['9m_telecom'] or 0 for row in treated_response.data),
            '10m': sum(row['10m'] or 0 for row in treated_response.data),
            '10m_telecom': sum(row['10m_telecom'] or 0 for row in treated_response.data),
            '11m': sum(row['11m'] or 0 for row in treated_response.data),
            '12m': sum(row['12m'] or 0 for row in treated_response.data),
            '12m_telecom': sum(row['12m_telecom'] or 0 for row in treated_response.data),
            '14m': sum(row['14m'] or 0 for row in treated_response.data),
            '16m': sum(row['16m'] or 0 for row in treated_response.data)
        }

        unsorted_total = sum(row['quantity'] or 0 for row in unsorted_response.data)

        return render_template('dashboard/clients_stock.html',
                             clients=clients,
                             untreated_totals=untreated_totals,
                             treated_totals=treated_totals,
                             unsorted_total=unsorted_total,
                             selected_client_id=client_id,
                             client_name=client_name)
                             
    except Exception as e:
        print(f"Error fetching client stock data: {str(e)}")
        return render_template('dashboard/clients_stock.html',
                             clients=[],
                             untreated_totals={},
                             treated_totals={},
                             unsorted_total=0,
                             selected_client_id=None,
                             client_name=None)




@dashboard.route('/bbf_detail')
def bbf_detail():
    try:
        total_sales = supabase.table('sales').select('total_amount').execute()
        total_sales_sum = sum(item['total_amount'] for item in total_sales.data) if total_sales.data else 0
        print (total_sales_sum)

        total_receipts = supabase.table('receipts').select('amount').execute()
        total_receipts_sum = sum(item['amount'] for item in total_receipts.data) if total_receipts.data else 0
        print (total_receipts_sum)

        total_purchase = supabase.table('purchases').select('total_amount').execute()
        total_purchase_sum = sum(item['total_amount'] for item in total_purchase.data) if total_purchase.data else 0
        print (total_purchase_sum)

        total_expenses = supabase.table('expenses').select('amount').execute()
        total_expenses_sum = sum(item['amount'] for item in total_expenses.data) if total_expenses.data else 0
        print (total_expenses_sum)


        total_payment_vouchers = supabase.table('payment_vouchers').select('total_amount').execute()
        total_payment_vouchers_sum = sum(item['total_amount'] for item in total_payment_vouchers.data) if total_payment_vouchers.data else 0
        print (total_payment_vouchers_sum)

        balance_bf = total_sales_sum + total_receipts_sum - (
            total_purchase_sum + total_expenses_sum + total_payment_vouchers_sum
        )
        print (balance_bf)

        return render_template(
            'dashboard/balances.html',
            balance_bf=balance_bf,
            total_sales_sum = total_sales_sum,
            total_receipts_sum = total_receipts_sum,
            total_purchase_sum = total_purchase_sum,
            total_expenses_sum = total_expenses_sum,
            total_payment_vouchers_sum = total_payment_vouchers_sum,
        )
    except Exception as e:
        print(f"Error fetching BBF details: {str(e)}")



@dashboard.route('/gate_pass')
def gate_pass():
    try:
        response = supabase.table('get_pass_in').select('*').order('created_at', desc=True).execute()
        passes = response.data
        print(passes)  # For debugging
        return render_template('dashboard/get_pass_in.html', passes=passes)
    except Exception as e:
        print(f"Error fetching gate passes: {str(e)}")
        flash('Error fetching gate passes', 'error')
        return render_template('dashboard/get_pass_in.html')

@dashboard.route('/approve_gate_pass/<int:pass_id>', methods=['POST'])
def approve_gate_pass(pass_id):
    try:
        # Update the status column to "approved"
        supabase.table('get_pass_in').update({'status': 'approved'}).eq('id', pass_id).execute()
        flash('Gate pass approved successfully', 'success')
    except Exception as e:
        flash(f'Error approving gate pass: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.gate_pass'))


@dashboard.route('/add_gate_pass', methods=['POST'])
def add_gate_pass():
    try:
        data = {
            'time_in': request.form.get('time_in'),
            'time_out': request.form.get('time_out'),
            'reaseon': request.form.get('reason'),
            'items': request.form.get('items'),
            'quantity': float(request.form.get('quantity')) if request.form.get('quantity') else None,
            'description': request.form.get('description'),
            'comments': request.form.get('comments'),
            'drivers_name': request.form.get('drivers_name'),
            'vehicle_number': request.form.get('vehicle_number'),
            'checked_by': request.form.get('checked_by'),
            'type': request.form.get('type')
        }
        
        supabase.table('get_pass_in').insert(data).execute()
        flash('Gate pass added successfully', 'success')
    except Exception as e:
        flash(f'Error adding gate pass: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.gate_pass'))

@dashboard.route('/edit_gate_pass', methods=['POST'])
def edit_gate_pass():
    try:
        pass_id = request.form.get('pass_id')
        data = {
            'time_in': request.form.get('time_in'),
            'time_out': request.form.get('time_out'),
            'reaseon': request.form.get('reason'),
            'items': request.form.get('items'),
            'quantity': float(request.form.get('quantity')) if request.form.get('quantity') else None,
            'description': request.form.get('description'),
            'comments': request.form.get('comments'),
            'drivers_name': request.form.get('drivers_name'),
            'vehicle_number': request.form.get('vehicle_number'),
            'checked_by': request.form.get('checked_by'),
            'type': request.form.get('type')
        }
        
        supabase.table('get_pass_in').update(data).eq('id', pass_id).execute()
        flash('Gate pass updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating gate pass: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.gate_pass'))

@dashboard.route('/delete_gate_pass/<int:pass_id>', methods=['POST'])
def delete_gate_pass(pass_id):
    try:
        supabase.table('get_pass_in').delete().eq('id', pass_id).execute()
        flash('Gate pass deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting gate pass: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.gate_pass'))






@dashboard.route('/employees')
def employees():
    try:
        # Fetch all employees from Supabase
        response = supabase.table('employees').select('*').execute()
        employees = response.data if response.data else []
        return render_template('dashboard/employees.html', employees=employees)
    except Exception as e:
        print(f"Error fetching employees: {str(e)}")
        return render_template('dashboard/employees.html', employees=[])

@dashboard.route('/add_employee', methods=['POST'])
def add_employee():
    try:
        data = {
            'name': request.form.get('name'),
            'position': request.form.get('position'),
            'contact_number': request.form.get('contact_number'),
            'email': request.form.get('email'),
            'hire_date': request.form.get('hire_date'),
            'payment_type': request.form.get('payment_type'),
            'salary': float(request.form.get('salary', 0))
        }
        
        supabase.table('employees').insert(data).execute()
        flash('Employee added successfully', 'success')
    except Exception as e:
        flash(f'Error adding employee: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.employees'))

@dashboard.route('/edit_employee', methods=['POST'])
def edit_employee():
    try:
        employee_id = request.form.get('employee_id')
        data = {
            'name': request.form.get('name'),
            'position': request.form.get('position'),
            'contact_number': request.form.get('contact_number'),
            'email': request.form.get('email'),
            'hire_date': request.form.get('hire_date'),
            'payment_type': request.form.get('payment_type'),
            'salary': float(request.form.get('salary', 0))
        }
        
        supabase.table('employees').update(data).eq('id', employee_id).execute()
        flash('Employee updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating employee: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.employees'))

@dashboard.route('/delete_employee/<employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        supabase.table('employees').delete().eq('id', employee_id).execute()
        flash('Employee deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.employees'))



@dashboard.route('/pay_roll')
def pay_roll():
    try:
        # Fetch payroll records
        payroll_response = supabase.table('payroll').select('*, employee_id(name)').execute()
        payroll_records = payroll_response.data if payroll_response else []

        # Calculate totals
        total_gross = sum(record['gross_salary'] for record in payroll_records)
        total_advance = sum(record['advance'] for record in payroll_records)
        total_nssf = sum(record['nssf'] for record in payroll_records)
        total_paye = sum(record['paye'] for record in payroll_records)
        total_local_tax = sum(record['local_tax'] for record in payroll_records)

        # Pass data to the template
        return render_template(
            'dashboard/pay_roll.html',
            payroll_records=payroll_records,
            total_gross=total_gross,
            total_advance=total_advance,
            total_nssf=total_nssf,
            total_paye=total_paye,
            total_local_tax=total_local_tax
        )

    except Exception as e:
        print(f"Error fetching payroll data: {str(e)}")
        return render_template(
            'dashboard/pay_roll.html',
            payroll_records=[],
            total_gross=0,
            total_advance=0,
            total_nssf=0,
            total_paye=0,
            total_local_tax=0
        )



@dashboard.route('/expense_authorizations')
def expense_authorizations():
    try:
        # Fetch all expense authorizations from Supabase
        response = supabase.table('expense_authorizations').select('*').order('date', desc=True).execute()
        authorizations = response.data if response.data else []
        print (authorizations)  # For debugging
        return render_template('dashboard/expense_authorization.html', authorizations=authorizations)
    except Exception as e:
        print(f"Error fetching expense authorizations: {str(e)}")
        return jsonify({'error': 'Failed to fetch expense authorizations'}), 500

@dashboard.route('/add_expense_authorization', methods=['POST'])
def add_expense_authorization():
    try:
        data = {
            'authorization_number': request.form.get('authorization_number'),
            'date': request.form.get('date'),
            'pay_to': request.form.get('pay_to'),
            'sum_of_shillings': float(request.form.get('sum_of_shillings', 0)),
            'being_payment_of': request.form.get('being_payment_of'),
            'cash_cheque_no': request.form.get('cash_cheque_no'),
            'balance': float(request.form.get('balance', 0)),
            'signature': request.form.get('signature')
        }
        
        supabase.table('expense_authorizations').insert(data).execute()
        flash('Expense authorization added successfully', 'success')
    except Exception as e:
        flash(f'Error adding expense authorization: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard.expense_authorizations'))

@dashboard.route('/edit_expense_authorization', methods=['POST'])
def edit_expense_authorization():
    try:
        auth_id = request.form.get('auth_id')
        data = {
            'authorization_number': request.form.get('authorization_number'),
            'date': request.form.get('date'),
            'received_from': request.form.get('received_from'),
            'sum_of_shillings': float(request.form.get('sum_of_shillings', 0)),
            'being_payment_of': request.form.get('being_payment_of'),
            'cash_cheque_no': request.form.get('cash_cheque_no'),
            'balance': float(request.form.get('balance', 0)),
            'signature': request.form.get('signature')
        }
        
        supabase.table('expense_authorizations').update(data).eq('id', auth_id).execute()
        flash('Expense authorization updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating expense authorization: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.expense_authorizations'))

@dashboard.route('/delete_expense_authorization/<auth_id>', methods=['POST'])
def delete_expense_authorization(auth_id):
    try:
        supabase.table('expense_authorizations').delete().eq('id', auth_id).execute()
        flash('Expense authorization deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting expense authorization: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.expense_authorizations'))





















@dashboard.route('/admin_search', methods=['GET'])
def admin_search():
    try:
        clients = supabase.table('clients').select('*').execute().data
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Both start_date and end_date are required'}), 400

        # Search sales with explicit time range for end_date
        end_datetime = f"{end_date}T23:59:59"
        sales = supabase.table('sales')\
            .select('*')\
            .gte('created_at', f"{start_date}T00:00:00")\
            .lte('created_at', end_datetime)\
            .order('created_at', desc=True)\
            .execute()
        

        # Search receipts
        receipts = supabase.table('receipts')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .order('date', desc=True)\
            .execute()

        # Search purchases
        purchases = supabase.table('purchases')\
            .select('*')\
            .gte('created_at', f"{start_date}T00:00:00")\
            .lte('created_at', end_datetime)\
            .order('created_at', desc=True)\
            .execute()

        # Search payment vouchers
        payment_vouchers = supabase.table('payment_vouchers')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .order('date', desc=True)\
            .execute()
        
        #expenses
        expenses = supabase.table('expenses')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .order('date', desc=True)\
            .execute()
        
        #stock_movements
        stock_movements = supabase.table('stock_movements')\
            .select('*')\
            .gte('movement_date', f"{start_date}T00:00:00")\
            .lte('movement_date', end_datetime)\
            .order('movement_date', desc=True)\
            .execute()
        
        #kdl_untreated_stock
        kdl_untreated_stock = supabase.table('kdl_untreated_stock')\
            .select('*')\
            .gte('created_at', f"{start_date}T00:00:00")\
            .lte('created_at', end_datetime)\
            .order('created_at', desc=True)\
            .execute()
        
        #kdl_treated_stock
        kdl_treated_stock = supabase.table('kdl_treated_poles')\
            .select('*')\
            .gte('date', f"{start_date}T00:00:00")\
            .lte('date', end_datetime)\
            .lte('date', end_date)\
            .order('date', desc=True)\
            .execute()
        
        #client_untreated_stock
        client_untreated_stock = supabase.table('client_untreated_stock')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .order('date', desc=True)\
            .execute()
        
        #client_treated_stock
        client_treated_stock = supabase.table('clients_treated_poles')\
            .select('*')\
            .gte('created_at', f"{start_date}T00:00:00")\
            .lte('created_at', end_datetime)\
            .order('created_at', desc=True)\
            .execute()
        
        #client_unsorted_stock -> clients_unsorted_stock
        clients_unsorted_stock = supabase.table('clients_unsorted')\
            .select('*')\
            .gte('created_at', f"{start_date}T00:00:00")\
            .lte('created_at', end_datetime)\
            .order('created_at', desc=True)\
            .execute()
        
        #treatment_log
        treatment_log = supabase.table('treatment_log')\
            .select('*')\
            .gte('date', f"{start_date}T00:00:00")\
            .lte('date', end_datetime)\
            .order('date', desc=True)\
            .execute()


        results = {
            'sales': sales.data if sales else [],
            'receipts': receipts.data if receipts else [],
            'purchases': purchases.data if purchases else [],
            'payment_vouchers': payment_vouchers.data if payment_vouchers else [],
            'expenses':expenses.data if expenses else[],
            'stock_movements': stock_movements.data if stock_movements else [],
            'kdl_untreated_stock': kdl_untreated_stock.data if kdl_untreated_stock else [],
            'kdl_treated_stock': kdl_treated_stock.data if kdl_treated_stock else [],
            'client_untreated_stock': client_untreated_stock.data if client_untreated_stock else [],
            'client_treated_stock': client_treated_stock.data if client_treated_stock else [],
            'client_unsorted_stock': clients_unsorted_stock.data if clients_unsorted_stock else [],
            'treatment_log': treatment_log.data if treatment_log else []


        }

        # Calculate totals
        def calculate_totals(data, amount_field='amount'):
            if not data:
                return 0
            return sum(item.get(amount_field, 0) for item in data)

        # Daily totals (assuming today's date)
        today = datetime.now().date().isoformat()
        daily_sales = calculate_totals([s for s in sales.data if s['created_at'].split('T')[0] == today], 'total_amount')
        daily_receipts = calculate_totals([r for r in receipts.data if r['date'] == today])
        daily_purchases = calculate_totals([p for p in purchases.data if p['created_at'].split('T')[0] == today], 'total_amount')
        daily_expenses = calculate_totals([e for e in expenses.data if e['date'] == today])

        # Weekly totals (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        weekly_sales = calculate_totals([s for s in sales.data if s['created_at'].split('T')[0] > week_ago], 'total_amount')
        weekly_receipts = calculate_totals([r for r in receipts.data if r['date'] > week_ago])
        weekly_purchases = calculate_totals([p for p in purchases.data if p['created_at'].split('T')[0] > week_ago], 'total_amount')
        weekly_expenses = calculate_totals([e for e in expenses.data if e['date'] > week_ago])

        # Monthly totals (last 30 days)
        month_ago = (datetime.now() - timedelta(days=30)).date().isoformat()
        monthly_sales = calculate_totals([s for s in sales.data if s['created_at'].split('T')[0] > month_ago], 'total_amount')
        monthly_receipts = calculate_totals([r for r in receipts.data if r['date'] > month_ago])
        monthly_purchases = calculate_totals([p for p in purchases.data if p['created_at'].split('T')[0] > month_ago], 'total_amount')
        monthly_expenses = calculate_totals([e for e in expenses.data if e['date'] > month_ago])

        # Calculate search date range totals
        search_range_sales = calculate_totals([s for s in sales.data], 'total_amount')
        search_range_receipts = calculate_totals([r for r in receipts.data])
        search_range_purchases = calculate_totals([p for p in purchases.data], 'total_amount')
        search_range_expenses = calculate_totals([e for e in expenses.data])

        # Create totals dictionary
        totals = {
            'daily': {
                'sales': daily_sales,
                'receipts': daily_receipts,
                'purchases': daily_purchases,
                'expenses': daily_expenses
            },
            'weekly': {
                'sales': weekly_sales,
                'receipts': weekly_receipts,
                'purchases': weekly_purchases,
                'expenses': weekly_expenses
            },
            'monthly': {
                'sales': monthly_sales,
                'receipts': monthly_receipts,
                'purchases': monthly_purchases,
                'expenses': monthly_expenses
            },
            'search_range': {
                'sales': search_range_sales,
                'receipts': search_range_receipts,
                'purchases': search_range_purchases,
                'expenses': search_range_expenses
            }
        }

        return render_template('dashboard/admin_search.html', 
                            clients=clients,
                            results=results,
                            start_date=start_date,
                            end_date=end_date,
                            totals=totals)  # Add totals to template context

    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500





@dashboard.route('/clients_ledgers', methods=['GET'])
def clients_ledgers():
    try:
        # Get client_id from query parameter
        client_id = request.args.get('client_id')
        
        # Fetch all clients for dropdown
        clients = supabase.table('clients').select('*').execute().data

        # Initialize selected_client_name
        selected_client_name = None

        # If client_id is provided, fetch their ledger entries and name
        if client_id:
            ledger_response = supabase.table('clients_ledger')\
                .select('*, clients(name)')\
                .eq('client_id', client_id)\
                .order('transaction_date', desc=True)\
                .execute()
            ledger = ledger_response.data if ledger_response.data else []

            # Fetch the selected client's name
            client_response = supabase.table('clients').select('name').eq('id', client_id).execute()
            if client_response.data:
                selected_client_name = client_response.data[0]['name']

            # Compute running balance from top (most recent) to bottom
            balance = 0
            for entry in reversed(ledger):  # reverse to get oldest first
                transaction_type = entry.get('transaction_type')
                amount = entry.get('amount', 0)

                if transaction_type == 'payment':
                    balance += amount
                elif transaction_type == 'treatment':
                    balance -= amount

                entry['balance'] = balance  # inject into entry for frontend

            # Calculate total balance
            total_balance = sum(
                entry['amount'] if entry['transaction_type'] == 'payment' else -entry['amount']
                for entry in ledger
                if entry['transaction_type'] in ['payment', 'treatment']
            )
        else:
            ledger = []
            total_balance = 0  # Initialize total_balance with a default value

        return render_template('dashboard/clients_ledgers.html', 
                                clients=clients,
                                ledger=ledger,
                                selected_client=client_id,
                                selected_client_name=selected_client_name,
                                total_balance=total_balance)

    except Exception as e:
        print(f"Error fetching clients ledger: {str(e)}")
        # Initialize default values for clients and ledger
        clients = []
        ledger = []
        total_balance = 0  # Ensure total_balance is initialized in case of an exception
        return render_template('dashboard/clients_ledgers.html', 
                                clients=clients,
                                ledger=ledger,
                                selected_client=None,
                                selected_client_name=None,
                                total_balance=total_balance)




@dashboard.route('/inventory_dash')
def inventory_dash():
    total_workers = supabase.table('cusual_workers').select('*').execute()
    total_workers_sum = len(total_workers.data)
    total_items = supabase.table('inventory').select('*').execute()
    # Get total chemicals from inventory
    chemical_items = supabase.table('inventory').select('quantity').eq('item', 'chemical').execute()
    total_chemicals = sum(item['quantity'] for item in chemical_items.data)

    #get Total endplates from inventory
    endplates_items = supabase.table('inventory').select('quantity').eq('item', 'endplates').execute()
    total_endplates = sum(item['quantity'] for item in endplates_items.data)
    print(total_endplates)
    total_endplates_used = supabase.table('inventory_use').select('quantity').eq('item', 'endplates').execute()
    total_endplates_used = sum(item['quantity'] for item in total_endplates_used.data)
    balance_endplates = total_endplates - total_endplates_used

    #get total fuel from inventory
    fuel_items = supabase.table('inventory').select('quantity').eq('item', 'Fuel').execute()
    total_fuel = sum(item['quantity'] for item in fuel_items.data)
    fuel_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'Fuel').execute()
    total_fuel_used = sum(item['quantity'] for item in fuel_items_used.data)
    balance_fuel = total_fuel - total_fuel_used

    #get total paint from inventory
    paint_items = supabase.table('inventory').select('quantity').eq('item', 'paint').execute()
    total_paint = sum(item['quantity'] for item in paint_items.data)
    paint_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'paint').execute()
    total_paint_used = sum(item['quantity'] for item in paint_items_used.data)
    balance_paint = total_paint - total_paint_used

    #get total nails from inventory
    nails_items = supabase.table('inventory').select('quantity').eq('item', 'unails').execute()
    total_nails = sum(item['quantity'] for item in nails_items.data)
    nails_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'unails').execute()
    total_nails_used = sum(item['quantity'] for item in nails_items_used.data)
    balance_nails = total_nails - total_nails_used

    #label_nails
    label_nails_items = supabase.table('inventory').select('quantity').eq('item', 'label_nails').execute()
    total_label_nails = sum(item['quantity'] for item in label_nails_items.data)
    label_nails_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'label_nails').execute()
    total_label_nails_used = sum(item['quantity'] for item in label_nails_items_used.data)
    balance_label_nails = total_label_nails - total_label_nails_used

    #chemicals
    chemicals_items = supabase.table('inventory').select('quantity').eq('item', 'chemical').execute()
    total_chemicals = sum(item['quantity'] for item in chemicals_items.data)
    total_chemicals_used = supabase.table('inventory_use').select('quantity').eq('item', 'chemical').execute()
    total_chemicals_used = sum(item['quantity'] for item in total_chemicals_used.data)
    balance_chemicals = total_chemicals - total_chemicals_used 

    return render_template('dashboard/inventory_dash.html', 
                           total_workers=total_workers_sum, 
                           total_items=len(total_items.data),
                           total_chemicals=total_chemicals,
                           total_endplates=total_endplates,
                            total_endplates_used=total_endplates_used,
                            balance_endplates=balance_endplates,
                            total_fuel=total_fuel,
                            total_paint=total_paint,
                            total_nails=total_nails,
                            total_fuel_used=total_fuel_used,
                            total_paint_used=total_paint_used,
                            total_nails_used=total_nails_used,
                            total_label_nails=total_label_nails,
                            total_label_nails_used=total_label_nails_used,
                            balance_fuel=balance_fuel,
                            balance_paint=balance_paint,
                            balance_nails=balance_nails,
                            balance_label_nails=balance_label_nails,
                            balance_chemicals=balance_chemicals,
                            total_chemicals_used=total_chemicals_used,
                           )


@dashboard.route('/kdl_unsorted_stock')
def kdl_unsorted_stock():
    try:
        # Fetch unsorted stock records without using a non-existent relationship
        response = supabase.table('kdl_unsorted_stock').select('*').order('created_at', desc= True) .execute()
        unsorted_stock = response.data if response.data else []
        print(unsorted_stock)  # For debugging

        # Fetch suppliers separately
        suppliers = supabase.table('suppliers').select('id', 'name').execute().data

        # Map supplier names to unsorted stock records
        for stock in unsorted_stock:
            supplier_id = stock.get('supplier_id')
            if supplier_id:
                supplier = next((s for s in suppliers if s['id'] == supplier_id), None)
                stock['supplier_name'] = supplier['name'] if supplier else 'Unknown Supplier'
                print(stock['supplier_name'])  # For debugging
            else:
                stock['supplier_name'] = 'No Supplier'

        return render_template('dashboard/kdl_unsorted.html', 
                               unsorted_stock=unsorted_stock,
                               suppliers=suppliers)

    except Exception as e:
        print(f"Error fetching unsorted stock: {str(e)}")
        return render_template('dashboard/kdl_unsorted.html', 
                               unsorted_stock=[],
                               suppliers=[])

@dashboard.route('/mark_stock_sorted/<int:stock_id>', methods=['POST'])
def mark_as_sorted(stock_id):
    try:
        # Update the stock status to sorted
        supabase.table('kdl_unsorted_stock').update({
            'status': 'sorted'
        }).eq('id', stock_id).execute()
        
        flash('Stock marked as sorted successfully', 'success')
    except Exception as e:
        print(f"Error marking stock as sorted: {str(e)}")
        flash('Error marking stock as sorted', 'error')
    
    return redirect(url_for('dashboard.kdl_unsorted_stock'))

@dashboard.route('/add_unsorted_stock', methods=['POST'])
def add_unsorted_stock():
    try:
        data = {
            'pole_type': request.form.get('pole_type'),
            'quantity': float(request.form.get('quantity')),
            'date': request.form.get('date'),
            'supplier_id': request.form.get('supplier_id'),
            'description': request.form.get('description'),
            'status': 'unsorted'
        }
        
        supabase.table('kdl_unsorted_stock').insert(data).execute()
        flash('Unsorted stock added successfully', 'success')
    except Exception as e:
        flash(f'Error adding unsorted stock: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.kdl_unsorted_stock'))




@dashboard.route('/daily_workers', methods=['GET', 'POST'])
def daily_workers():
    workers = supabase.table('cusual_workers').select('*').execute()  # Ensure workers is always defined
    if request.method == 'POST':
        data = {
            'worker_id': request.form.get('worker_id'),
            'date': request.form.get('date'),
            'description': request.form.get('description'),
            'quantity': request.form.get('quantity'),
            'rate': request.form.get('rate'),
            'total_pay': request.form.get('total_pay')
        }
        result = supabase.table('daily_work').insert(data).execute()
    
    # Fetch work records with worker details
    work_records = supabase.table('daily_work').select('*, cusual_workers(first_name, last_name)').execute()
    return render_template('dashboard/daily_workers.html', records=work_records.data, workers=workers.data)







@dashboard.route('/client_details')
def client_details(client_id):
    try:
        # Fetch client details
        response = supabase.table('clients').select('*').eq('id').execute()
        client = response.data[0] if response.data else None

        # Only fetch related data if client exists
        if client:
            treated_poles = supabase.table('clients_treated_poles')\
                .select('*')\
                .eq('client_id', client_id)\
                .execute().data

            deliveries = supabase.table('delivery_notes')\
                .select('*')\
                .eq('client_id', client_id)\
                .execute().data
        else:
            treated_poles = []
            deliveries = []

        return render_template('dashboard/client_details.html',
                            client=client,
                            treated_poles=treated_poles,
                            deliveries=deliveries)

    except Exception as e:
        print(f"Error fetching client details: {str(e)}")
        flash('Error fetching client details', 'error')
        return redirect(url_for('dashboard.clients'))
    


@dashboard.route('/notices')
def notices():
    try:
        # Fetch all notices ordered by date
        notices_response = supabase.table('notice').select('*').order('from_date', desc=True).execute()
        notices = notices_response.data if notices_response.data else []
        print(notices)
        return render_template('dashboard/notices.html', notices=notices)
    except Exception as e:
        print(f"Error fetching notices: {str(e)}")
        return render_template('dashboard/notices.html', notices=[])

@dashboard.route('/add_notice', methods=['POST'])
def add_notice():
    try:
        data = {
            'from_date': request.form.get('from_date'),
            'to_date': request.form.get('to_date'),
            'content': request.form.get('content')
        }
        
        supabase.table('notice').insert(data).execute()
        flash('Notice added successfully', 'success')
    except Exception as e:
        flash(f'Error adding notice: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.notices'))


@dashboard.route('/edit_notice', methods=['POST'])
def edit_notice():    
    try:
        notice_id = request.form.get('notice_id')
        if not notice_id:
            raise ValueError("Notice ID is required")

        data = {
            'from_date': request.form.get('from_date'),
            'to_date': request.form.get('to_date'),
            'content': request.form.get('content')
        }
        
        # Ensure required fields are present
        if not all([data['from_date'], data['to_date'], data['content']]):
            raise ValueError("All fields are required")
            
        supabase.table('notice').update(data).eq('id', notice_id).execute()
        flash('Notice updated successfully', 'success')
    except ValueError as e:
        flash(f'Validation error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error updating notice: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.notices'))

@dashboard.route('/delete_notice/<int:notice_id>', methods=['POST'])
def delete_notice(notice_id):
    try:
        supabase.table('notice').delete().eq('id', notice_id).execute()
        flash('Notice deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting notice: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.notices'))




@dashboard.route('/messages')
def messages():
    try:
        # Get current user's UUID from session/auth
        current_user_id = 'some-uuid'  # Replace with actual UUID from auth.uid()
        
        # Get received messages
        received = supabase.table('messages')\
            .select('*, sender:profiles!sender_id(*)')\
            .eq('recipient_id', current_user_id)\
            .order('created_at', desc=True)\
            .execute()

        # Get sent messages
        sent = supabase.table('messages')\
            .select('*, recipient:profiles!recipient_id(*)')\
            .eq('sender_id', current_user_id)\
            .order('created_at', desc=True)\
            .execute()

        # Get potential recipients by role
        recipients = supabase.table('profiles')\
            .select('id, role')\
            .neq('id', current_user_id)\
            .execute()

        # Group recipients by role
        roles = ['admin', 'accountant', 'stock_manager', 'treatment_manager', 
                'developer', 'user', 'askari', 'inventory']

        return render_template('dashboard/messages.html',
                            received_messages=received.data if received.data else [],
                            sent_messages=sent.data if sent.data else [],
                            roles=roles)

    except Exception as e:
        print(f"Error fetching messages: {str(e)}")
        return render_template('dashboard/messages.html', 
                            received_messages=[], 
                            sent_messages=[], 
                            roles=[])

@dashboard.route('/send_message', methods=['POST'])
def send_message():
    try:
        current_user_id = 'some-uuid'  # Replace with actual UUID from auth.uid()
        recipient_role = request.form.get('recipient_id')
        
        # Get all users with the selected role
        recipients = supabase.table('profiles')\
            .select('id')\
            .eq('role', recipient_role)\
            .execute()
        
        if not recipients.data:
            raise ValueError(f"No recipients found with role: {recipient_role}")
        
        # Send message to all users with the selected role
        for recipient in recipients.data:
            data = {
                'sender_id': current_user_id,
                'recipient_id': recipient['id'],
                'content': request.form.get('content'),
                'read': False
            }
            
            if not all([data['sender_id'], data['recipient_id'], data['content']]):
                raise ValueError("All fields are required")
                
            supabase.table('messages').insert(data).execute()
            
        flash(f'Message sent successfully to all {recipient_role}s', 'success')
    except ValueError as e:
        flash(f'Validation error: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error sending message: {str(e)}', 'error')
        print(f"Error details: {str(e)}")
    
    return redirect(url_for('dashboard.messages'))

@dashboard.route('/mark_read/<int:message_id>', methods=['POST'])
def mark_read(message_id):
    try:
        supabase.table('messages').update({'read': True}).eq('id', message_id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard.route('/delete_message/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    try:
        current_user_id = 'some-uuid'  # Replace with actual UUID from session
        
        # Only allow deletion if user is sender or recipient
        message = supabase.table('messages')\
            .select('*')\
            .eq('id', message_id)\
            .execute()\
            .data[0]
            
        if message['sender_id'] == current_user_id or message['recipient_id'] == current_user_id:
            supabase.table('messages').delete().eq('id', message_id).execute()
            flash('Message deleted successfully', 'success')
        else:
            flash('Unauthorized to delete this message', 'error')
    except Exception as e:
        flash(f'Error deleting message: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.messages'))


def format_datetime(value):
    """Format a datetime object to a readable string"""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return value
    return value.strftime("%Y-%m-%d %H:%M:%S")

# Register the filter



@dashboard.route('/sort_stock/<int:stock_id>', methods=['POST'])
def sort_stock(stock_id):
    try:
        # Get the unsorted stock record
        unsorted_response = supabase.table('kdl_unsorted_stock')\
            .select('*')\
            .eq('id', stock_id)\
            .single()\
            .execute()
        
        if not unsorted_response.data:
            flash('Unsorted stock record not found', 'error')
            return redirect(url_for('dashboard.kdl_unsorted_stock'))

        unsorted_stock = unsorted_response.data

        # Get sorting data from form
        sorted_data = {
            'fencing_poles': float(request.form.get('fencing_poles', 0)),
            '7m': float(request.form.get('7m', 0)),
            '8m': float(request.form.get('8m', 0)), 
            '9m': float(request.form.get('9m', 0)),
            '9m_telecom': float(request.form.get('9m_telecom', 0)),
            '10m': float(request.form.get('10m', 0)),
            '10m_telecom': float(request.form.get('10m_telecom', 0)),
            '11m': float(request.form.get('11m', 0)),
            '12m': float(request.form.get('12m', 0)),
            '12m_telecom': float(request.form.get('12m_telecom', 0)),
            '14m': float(request.form.get('14m', 0)),
            '16m': float(request.form.get('16m', 0)),
            'rafters': float(request.form.get('rafters', 0)),
            'timber': float(request.form.get('timber', 0)),
            'telecom_poles': float(request.form.get('telecom_poles', 0)),
            'stubs': float(request.form.get('stubs', 0)),
            'date': unsorted_stock['date'],
            'supplier_id': unsorted_stock['supplier_id'],
            'category': request.form.get('category'),
            'created_at': datetime.now().isoformat()  # Add created_at timestamp
        }

        # Verify total sorted quantity matches original quantity
        total_sorted = sum(
            value for key, value in sorted_data.items() 
            if key not in ['date', 'supplier_id', 'category', 'created_at']
        )

        if total_sorted > unsorted_stock['quantity']:
            flash('Total sorted quantity exceeds original quantity', 'error')
            return redirect(url_for('dashboard.kdl_unsorted_stock'))

        # Insert into kdl_untreated_stock
        supabase.table('kdl_untreated_stock').insert(sorted_data).execute()

        # Insert into sorted_data table
        supabase.table('sorted_data').insert(sorted_data).execute()

        # Update original unsorted stock quantity
        remaining_quantity = unsorted_stock['quantity'] - total_sorted
        if remaining_quantity > 0:
            supabase.table('kdl_unsorted_stock').update({
                'quantity': remaining_quantity
            }).eq('id', stock_id).execute()
        else:
            # If no quantity remains, mark as sorted
            supabase.table('kdl_unsorted_stock').update({
                'status': 'sorted',
                'quantity': 0
            }).eq('id', stock_id).execute()

        flash('Stock sorted successfully', 'success')

    except Exception as e:
        flash(f'Error sorting stock: {str(e)}', 'error')
        print(f"Error details: {str(e)}")

    return redirect(url_for('dashboard.kdl_unsorted_stock'))



@dashboard.route('/supplier_payments')
def supplier_payments():
    try:
        # Fetch all suppliers
        suppliers_response = supabase.table('suppliers').select('*').execute()
        suppliers = suppliers_response.data if suppliers_response.data else []

        # Get selected supplier if any
        supplier_id = request.args.get('supplier_id')
        sorted_data = []
        selected_supplier_name = None

        if supplier_id:
            # Fetch sorted data for selected supplier
            sorted_response = supabase.table('sorted_data')\
                .select('*')\
                .eq('supplier_id', supplier_id)\
                .order('date', desc=True)\
                .execute()
            
            sorted_data = sorted_response.data if sorted_response.data else []
            
            # Get supplier name
            selected_supplier = next(
                (s for s in suppliers if str(s['id']) == str(supplier_id)), 
                None
            )
            selected_supplier_name = selected_supplier['name'] if selected_supplier else 'Unknown Supplier'
            rejects = supabase.table('kdl_unsorted_stock').select('*').eq('supplier_id', supplier_id).execute()
            supplier_rejects = rejects.data if selected_supplier_name else []
            print(supplier_rejects)
            total_supplier_rejects = sum(item['quantity'] for item in supplier_rejects)
            print(total_supplier_rejects)


            return render_template(
                'dashboard/suppliers_payments.html',
                suppliers=suppliers,
                sorted_data=sorted_data,
                selected_supplier_id=supplier_id,
                selected_supplier_name=selected_supplier_name,
                supplier_rejects=supplier_rejects,
                total_rejects=total_supplier_rejects
            )

        return render_template(
            'dashboard/suppliers_payments.html',
            suppliers=suppliers,
            sorted_data=sorted_data,
            selected_supplier_id=supplier_id,
            selected_supplier_name=selected_supplier_name
        )

    except Exception as e:
        print(f"Error in suppliers_payments: {str(e)}")
        flash('Error fetching suppliers data', 'error')
        return render_template(
            'dashboard/suppliers_payments.html',
            suppliers=[],
            sorted_data=[],
            selected_supplier_id=None,
            selected_supplier_name=None
        )
    

# Get client details
@dashboard.route('/savanah')
def savanah():
    try:
        # Fetch stock from all 3 tables for client_id 18
        untreated = supabase.table('client_to_treat').select("*").eq('client_id', 18).execute().data
        treated = supabase.table('total_clients_treated_poles').select("*").eq('client_id', 18).execute().data
        unsorted = supabase.table('total_clients_unsorted').select("*").eq('client_id', 18).execute().data


        # Get client details
        client = supabase.table('clients').select("*").eq('id', 18).execute().data[0]

        return render_template('dashboard/savanah.html',
                            untreated=untreated,
                            treated=treated, 
                            unsorted=unsorted,
                            client=client)

    except Exception as e:
        flash(f'Error fetching client stock: {str(e)}', 'danger')
        return render_template('dashboard/savanah.html',
                            untreated=[],
                            treated=[],
                            unsorted=[],
                            client=None)
    



    
@dashboard.route('/orders')
def orders():
    try:
        # Fetch purchase orders with customer information
        P_orders_response = supabase.table('purchase_order')\
            .select('*, customers!customer_id(*)')\
            .order('created_at', desc=True)\
            .execute()
        purchase_orders = P_orders_response.data if P_orders_response.data else []

        # Fetch dispatch orders with purchase order and customer information
        d_orders_response = supabase.table('dispatch_order')\
            .select('*, purchase_order:purchase_order!purchases_order_id(*, customers(*))')\
            .order('created_at', desc=True)\
            .execute()
        dispatch_orders = d_orders_response.data if d_orders_response.data else []

        return render_template('dashboard/orders.html', 
                            purchase_orders=purchase_orders, 
                            dispatch_orders=dispatch_orders)

    except Exception as e:
        print(f"Error fetching orders: {str(e)}")
        flash(f'Error fetching orders: {str(e)}', 'danger')
        return render_template('dashboard/orders.html', purchase_orders=[], dispatch_orders=[])
    



@dashboard.route('/quotation')
def quotations():
    try:
        # Fetch all quotations with customer information
        quotations_response = supabase.table('quotations')\
            .select('*, customers!customer_id(*)')\
            .order('created_at', desc=True)\
            .execute()
        quotations = quotations_response.data if quotations_response.data else []

        # Fetch customers for dropdown
        customers_response = supabase.table('customers').select('*').execute()
        customers = customers_response.data if customers_response.data else []

        return render_template('dashboard/quotations.html',
                            quotations=quotations,
                            customers=customers)

    except Exception as e:
        print(f"Error fetching quotations: {str(e)}")
        return render_template('dashboard/quotations.html',
                            quotations=[],
                            customers=[])

@dashboard.route('/edit_quotation', methods=['POST'])
def edit_quotation():
    try:
        quotation_id = request.form.get('quotation_id')
        data = {
            'customer_id': request.form.get('customer_id'),
            'details': request.form.get('details'),
            'total_amount': float(request.form.get('total_amount', 0)),
            'rate': float(request.form.get('rate', 0)),
            'vat_18percent': float(request.form.get('vat_18percent', 0)),
            '7m': float(request.form.get('7m', 0)),
            '8m': float(request.form.get('8m', 0)),
            '9m': float(request.form.get('9m', 0)), 
            '10m': float(request.form.get('10m', 0)),
            '11m': float(request.form.get('11m', 0)),
            '12m': float(request.form.get('12m', 0)),
            '14m': float(request.form.get('14m', 0)),
            '16m': float(request.form.get('16m', 0)),
            'fencing_poles': float(request.form.get('fencing_poles', 0)),
            'rafters': float(request.form.get('rafters', 0)),
            'timber': float(request.form.get('timber', 0)),
            'telecom_poles': float(request.form.get('telecom_poles', 0)),
            'stubs': float(request.form.get('stubs', 0))
        }

        supabase.table('quotations').update(data).eq('id', quotation_id).execute()
        flash('Quotation updated successfully', 'success')

    except Exception as e:
        flash(f'Error updating quotation: {str(e)}', 'error')

    return redirect(url_for('dashboard.quotations'))

@dashboard.route('/delete_quotation/<int:quotation_id>', methods=['POST'])
def delete_quotation(quotation_id):
    try:
        supabase.table('quotations').delete().eq('id', quotation_id).execute()
        flash('Quotation deleted successfully', 'success')

    except Exception as e:
        flash(f'Error deleting quotation: {str(e)}', 'error')

    return redirect(url_for('dashboard.quotations'))