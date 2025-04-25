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


@inventory.route('/delivery_note', methods=['GET', 'POST'])
def delivery_note():
    clients = supabase.table('clients').select('*').execute()
    customers = supabase.table('customers').select('*').execute()

    if request.method == 'POST':
        def parse_numeric(value):
            try:
                return int(value) if value else 0
            except ValueError:
                return 0

        delivery_for = request.form.get('delivery_for')
        delivery_data = {
            'note_number': request.form.get('note_number'),
            'date': request.form.get('date'),
            'vehicle_number': request.form.get('vehicle_number'),
            'transporter': request.form.get('transporter'),
            'loaded_by': request.form.get('loaded_by'),
            'destination': request.form.get('destination'),
            'delivery_for': delivery_for,
            'notes': request.form.get('notes'),
            'fencing_poles': float(request.form.get('fencing_poles') or 0),
            'timber': float(request.form.get('timber') or 0),
            'rafters': float(request.form.get('rafters') or 0),
            '7m': float(request.form.get('7m') or 0),
            '8m': float(request.form.get('8m') or 0),
            '9m': float(request.form.get('9m') or 0),
            '10m': float(request.form.get('10m') or 0),
            '11m': float(request.form.get('11m') or 0),
            '12m': float(request.form.get('12m') or 0),
            '14m': float(request.form.get('14m') or 0),
            '16m': float(request.form.get('16m') or 0),
            '9m_telecom': float(request.form.get('9m_telecom') or 0),
            '10m_telecom': float(request.form.get('10m_telecom') or 0),
            '12m_telecom': float(request.form.get('12m_telecom') or 0)
        }

        # Conditionally include client_id or customers_id
        if delivery_for == 'client':
            delivery_data['client_id'] = parse_numeric(request.form.get('client_id'))
            # Validate client_id
            client_exists = supabase.table('clients').select('id').eq('id', delivery_data['client_id']).execute()
            if not client_exists.data:
                flash('Invalid client ID.', 'danger')
                return redirect(url_for('inventory.delivery_note'))
        elif delivery_for == 'customer':
            delivery_data['customers_id'] = parse_numeric(request.form.get('customers_id'))
            # Validate customers_id
            customer_exists = supabase.table('customers').select('id').eq('id', delivery_data['customers_id']).execute()
            if not customer_exists.data:
                flash('Invalid customer ID.', 'danger')
                return redirect(url_for('inventory.delivery_note'))

        # Save delivery note
        result = supabase.table('delivery_notes').insert(delivery_data).execute()

        # Update stock based on delivery_for
        columns = ['fencing_poles', 'timber', 'rafters', '7m', '8m', '9m', '10m', '11m', '12m', 
                    '14m', '16m', '9m_telecom', '10m_telecom', '12m_telecom']
        
        if request.form.get('delivery_for') == 'client':
            table = 'clients_treated_poles'
            condition = {'client_id': request.form.get('client_id')}
        else:
            table = 'kdl_treated_poles'
            condition = {'date': datetime.now().date().isoformat()}

        # Get current stock
        current_stock = supabase.table(table).select('*').match(condition).execute()
        
        if current_stock.data:
            stock_id = current_stock.data[0]['id']
            updates = {}
            
            for col in columns:
                if request.form.get(col):
                    new_value = float(current_stock.data[0].get(col, 0)) - float(request.form.get(col, 0))
                    updates[col] = max(0, new_value)  # Ensure stock doesn't go negative
            
            if updates:
                supabase.table(table).update(updates).eq('id', stock_id).execute()

        flash('Delivery note created successfully', 'success')
        return redirect(url_for('inventory.delivery_note'))

    delivery_notes = supabase.table('delivery_notes').select('*').execute()
    return render_template('inventory/delivery_note.html', 
                            notes=delivery_notes.data,
                            clients=clients.data,
                            customers=customers.data)