from flask import Blueprint, render_template, request, redirect, url_for
import supabase

# Initialize Supabase client
url = "https://your-supabase-url.supabase.co"
key = "your-supabase-api-key"
supabase_client = supabase.create_client(url, key)

# Create the dashboard blueprint
dashboard = Blueprint('dashboard', __name__, template_folder='templates/dashboard')

# Dashboard main route
@dashboard.route('/')
def main_dashboard():
    # Fetch customers from Supabase
    response = supabase_client.table('customers').select('*').execute()
    customers = response.data if response.status_code == 200 else []
    return render_template('main_dashboard.html', customers=customers)

# Route to add a new customer
@dashboard.route('/add_customer', methods=['POST'])
def add_customer():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Add a new customer to Supabase
    supabase_client.table('customers').insert({
        'name': name,
        'email': email,
        'phone': phone
    }).execute()

    return redirect(url_for('dashboard.main_dashboard'))

# Route to edit an existing customer
@dashboard.route('/edit_customer', methods=['POST'])
def edit_customer():
    customer_id = request.form.get('customer_id')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Update the customer in Supabase
    supabase_client.table('customers').update({
        'name': name,
        'email': email,
        'phone': phone
    }).eq('id', customer_id).execute()

    return redirect(url_for('dashboard.main_dashboard'))

# Route to delete a customer
@dashboard.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    # Delete the customer from Supabase
    supabase_client.table('customers').delete().eq('id', customer_id).execute()
    return redirect(url_for('dashboard.main_dashboard'))
