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

    return render_template('inventory/dash.html', 
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
        print(result.data)
    
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





