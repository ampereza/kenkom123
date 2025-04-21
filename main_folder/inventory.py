from flask import Flask, jsonify, request, blueprints, url_for, render_template
from dotenv import find_dotenv, load_dotenv
import os
from supabase import create_client, Client







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
    work_records = supabase.table('daily_work').select('*, cusual_workers!inner(name)').execute()
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