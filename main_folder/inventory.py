from flask import Flask, jsonify, request, blueprints, url_for, render_template
from dotenv import find_dotenv, load_dotenv
import os
from supabase import create_client, Client
from datetime import datetime
from flask import flash, redirect

inventory = blueprints.Blueprint('inventory', __name__)

# Load environment variables from .env file
load_dotenv(find_dotenv())

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
secret_key = os.getenv('SECRET_KEY')
supabase = create_client(supabase_url, supabase_key)

@inventory.route('/main')
def main():
    total_workers = supabase.table('cusual_workers').select('*').execute()
    total_workers_sum = len(total_workers.data)
    total_items = supabase.table('inventory').select('*').execute()
    # Get total chemicals from inventory
    chemical_items = supabase.table('inventory').select('quantity').eq('item', 'chemical').execute()
    total_chemicals = sum(item['quantity'] for item in chemical_items.data)

    #get Total endplates from inventory
    endplates_items = supabase.table('inventory').select('quantity').eq('item', 'endplate').execute()
    total_endplates = sum(item['quantity'] for item in endplates_items.data)

    #get total fuel from inventory
    fuel_items = supabase.table('inventory').select('quantity').eq('item', 'Fuel').execute()
    total_fuel = sum(item['quantity'] for item in fuel_items.data)

    #get total paint from inventory
    paint_items = supabase.table('inventory').select('quantity').eq('item', 'paint').execute()
    total_paint = sum(item['quantity'] for item in paint_items.data)

    #get total nails from inventory
    nails_items = supabase.table('inventory').select('quantity').eq('item', 'nails').execute()
    total_nails = sum(item['quantity'] for item in nails_items.data)

    return render_template('inventory/dash.html', 
                           total_workers=total_workers_sum, 
                           total_items=len(total_items.data),
                           total_chemicals=total_chemicals,
                           total_endplates=total_endplates,
                            total_fuel=total_fuel,
                            total_paint=total_paint,
                            total_nails=total_nails
                           )

@inventory.route('/casual_workers', methods=['GET', 'POST'])
def casual_workers():
    if request.method == 'POST':
        data = {
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'phone': request.form.get('phone'),
            'hire_date': request.form.get('hire_date'),
            'address': request.form.get('address'),
            'next_of_kin': request.form.get('next_of_kin')
        }
        result = supabase.table('cusual_workers').insert(data).execute()
        print(result.data)
        
    workers = supabase.table('cusual_workers').select('*').execute()
    return render_template('inventory/casual_workers.html', workers=workers.data)

@inventory.route('/daily_work', methods=['GET', 'POST'])
def daily_work():
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
    return render_template('inventory/daily_work.html', records=work_records.data, workers=workers.data)

@inventory.route('/manage_inventory', methods=['GET', 'POST'])
def manage_inventory():
    if request.method == 'POST':
        data = {
            'item': request.form.get('item'),
            'quantity': request.form.get('quantity'),
            'description': request.form.get('description'),
        }
        result = supabase.table('inventory').insert(data).execute()
    
    items = supabase.table('inventory').select('*').execute()
    return render_template('inventory/inventory.html', items=items.data)

@inventory.route('/inventory_use', methods=['GET', 'POST'])
def inventory_use():
    items = supabase.table('inventory').select('*').execute()
    if request.method == 'POST':
        data = {
            'item': request.form.get('item'),
            'quantity': request.form.get('quantity'),
            'description': request.form.get('description')
        }
        result = supabase.table('inventory_use').insert(data).execute()
    
    usage_records = supabase.table('inventory_use').select('*').execute()
    return render_template('inventory/inventory_use.html', records=usage_records.data, items=items.data)

@inventory.route('/pay_workers', methods=['GET', 'POST'])
def pay_workers():
    if request.method == 'POST':
        worker_id = request.form.get('worker_id')
        amount_paid = float(request.form.get('amount_paid', 0))
        is_advance = request.form.get('is_advance') == 'true'  # Convert to boolean

        # Insert payment record
        payment_data = {
            'workers_id': worker_id,  # Changed to workers_id
            'amount': amount_paid,
            'is_advance': is_advance,  # Ensure this is a boolean
            'payment_date': 'now()'
        }
        supabase.table('worker_payments').insert(payment_data).execute()
        
        if not is_advance:
            # Mark corresponding daily_work records as paid (numeric comparison for non-boolean fields)
            supabase.table('daily_work')\
                .update({'paid': 1})\
                .eq('worker_id', worker_id)\
                .eq('paid', 0)\
                .execute()
            print("Daily work records marked as paid.")
        else:
            # Mark corresponding daily_work records as advance
            supabase.table('daily_work')\
                .update({'advance': 1})\
                .eq('worker_id', worker_id)\
                .eq('advance', 0)\
                .execute()
            print("Daily work records marked as advance.")

        # If full amount is paid, mark summed total_pay as paid
        if not is_advance and amount_paid >= sum(
            record['total_pay'] for record in supabase.table('daily_work')
            .select('total_pay')
            .eq('worker_id', worker_id)
            .eq('paid', 0)
            .execute().data
        ):
            supabase.table('daily_work')\
                .update({'paid': 1})\
                .eq('worker_id', worker_id)\
                .eq('paid', 0)\
                .execute()
            print("Full amount paid. All unpaid records marked as paid.")

    try:
        # Call the custom Postgres function to calculate total_pay and amount for the current week
        weekly_payments = supabase.rpc('sum_weekly_payments').execute()
        weekly_payments_data = weekly_payments.data  # Access the data attribute directly
        print(f"Weekly payments data: {weekly_payments_data}")  # Debugging output

        # Log if no data is returned
        if not weekly_payments_data:
            print("No weekly payments data found. Check the daily_work and worker_payments tables for matching records.")
    except Exception as e:
        # Log the error and set weekly_payments_data to an empty list
        print(f"Error calculating weekly payments: {e}")
        weekly_payments_data = []

    # Get advance payments
    advance_payments = supabase.table('worker_payments')\
        .select('workers_id, amount, is_advance, payment_date')\
        .eq('is_advance', True)\
        .execute()

    # Group advance payments by workers_id
    advances_dict = {}
    for payment in advance_payments.data:
        worker_id = payment['workers_id']  # Changed to workers_id
        advances_dict[worker_id] = advances_dict.get(worker_id, 0) + payment['amount']

    # Get worker details
    workers = supabase.table('cusual_workers').select('*').execute()
    workers_dict = {w['id']: w for w in workers.data}

    # Combine payment data with worker details and advances
    payment_records = []
    for payment in weekly_payments_data:
        if payment['worker_id'] in workers_dict:  # worker_id remains as it refers to the daily_work table
            payment['worker'] = workers_dict[payment['worker_id']]
            payment['advance'] = advances_dict.get(payment['worker_id'], 0)
            # Calculate net_due as total_pay - advance
            payment['net_due'] = payment['total_pay'] - payment['advance']
            payment_records.append(payment)

    return render_template('inventory/pay_workers.html', payments=payment_records)

@inventory.route('/delivery_notes', methods=['GET', 'POST'])
def delivery_notes():
    if request.method == 'POST':
        try:
            print("POST request received for /delivery_notes")
            flash("Processing delivery note...", "info")

            deliver_for = request.form.get('deliver_for')
            client_id = request.form.get('client_id')
            customers_id = request.form.get('customers_id')
            print(f"Received deliver_for: {deliver_for}, client_id: {client_id}, customers_id: {customers_id}")

            # Ensure client_id and customers_id are set correctly
            if deliver_for == 'customer':
                client_id = None
                customers_id = int(customers_id) if customers_id else None
            elif deliver_for == 'client':
                customers_id = None
                client_id = int(client_id) if client_id else None
            else:
                flash('Invalid delivery details. Please check your input.', 'danger')
                print("Invalid delivery details.")
                return redirect(url_for('inventory.delivery_notes'))

            print(f"Processed client_id: {client_id}, customers_id: {customers_id}")

            # Fields to check for balance
            fields = [
                'fencing_poles', 'timber', 'rafters', '7m', '8m', '9m', '9m_telecom',
                '10m', '10m_telecom', '11m', '12m', '12m_telecom', '14m', '16m'
            ]
            requested_quantities = {field: float(request.form.get(field, 0)) for field in fields}
            print(f"Requested quantities: {requested_quantities}")

            # Check balance based on deliver_for
            if deliver_for == 'customer':
                balance_table = 'kdl_treated_poles'
                balance = supabase.table(balance_table).select('*').execute().data[0]
                print(f"Balance fetched from {balance_table}: {balance}")
            elif deliver_for == 'client':
                balance_table = 'clients_treated_poles'
                balance = supabase.table(balance_table).select('*').eq('client_id', client_id).execute().data[0]
                print(f"Balance fetched from {balance_table} for client_id {client_id}: {balance}")

            # Validate and update requested quantities against balance
            for field, requested_quantity in requested_quantities.items():
                if requested_quantity > balance.get(field, 0):
                    flash(f'Insufficient balance for {field}. Requested: {requested_quantity}, Available: {balance.get(field, 0)}', 'danger')
                    print(f"Insufficient balance for {field}. Requested: {requested_quantity}, Available: {balance.get(field, 0)}")
                    return redirect(url_for('inventory.delivery_notes'))
                else:
                    # Reduce the balance in the treated table
                    new_balance = balance.get(field, 0) - requested_quantity
                    supabase.table(balance_table).update({field: new_balance}).eq('id', balance['id']).execute()
                    print(f"Updated {field} balance in {balance_table} to {new_balance}")

            # Proceed with creating the delivery note
            data = {
                'deliver_form': deliver_for,
                'note_number': request.form.get('note_number'),
                'client_id': client_id,
                'vehicle_number': request.form.get('vehicle_number'),
                'transporter': request.form.get('transporter'),
                'total_quantity': int(request.form.get('total_quantity', '0')),  # Default to '0' if empty
                'loaded_by': request.form.get('loaded_by'),
                'loaded_at': datetime.utcnow().isoformat(),
                'driver_sign': request.form.get('driver_sign') == 'true',
                'received_by': request.form.get('received_by'),
                'notes': request.form.get('notes'),
                'customers_id': customers_id,
                **requested_quantities,
                'destination': request.form.get('destination')
            }
            print(f"Delivery note data to be inserted: {data}")

            response = supabase.table('delivery_notes').insert(data).execute()
            if response:
                flash('Delivery note created successfully', 'success')
                print("Delivery note created successfully.")
            else:
                flash('Failed to create delivery note', 'danger')
                print("Failed to create delivery note.")

        except Exception as e:
            print(f"Error creating delivery note: {e}")
            flash(f'Error creating delivery note: {str(e)}', 'danger')
        return redirect(url_for('inventory.delivery_notes'))

    # GET request - fetch existing delivery notes and related data
    try:
        print("GET request received for /delivery_notes")
        delivery_notes = supabase.table('delivery_notes').select("*").order('created_at', desc=True).execute().data
        clients = supabase.table('clients').select("*").execute().data
        customers = supabase.table('customers').select("*").execute().data
        print(f"Fetched delivery_notes: {delivery_notes}")
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(f"Error fetching data: {e}")
        delivery_notes = []
        clients = []
        customers = []

    return render_template('inventory/delivery_note.html', 
                            delivery_notes=delivery_notes,
                            clients=clients,
                            customers=customers)


