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
    return render_template('inventory/main.html')

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
        return url_for('inventory.casual_workers')
        
    
    workers = supabase.table('cusual_workers').select('*').execute()
    return render_template('inventory/casual_workers.html', workers=workers.data)



@inventory.route('/daily_work', methods=['GET', 'POST'])
def daily_work():
    if request.method == 'POST':
        data = {
            'worker_id': request.form.get('worker_id'),
            'date': request.form.get('date'),
            'description': request.form.get('description'),
            'quantity': request.form.get('quantity'),
            'total_pay': request.form.get('total_pay')
        }
        result = supabase.table('daily_work').insert(data).execute()
        return result.data
    
    work_records = supabase.table('daily_work').select('*').execute()
    return render_template('inventory/daily_work.html', records=work_records.data)




@inventory.route('/inventory', methods=['GET', 'POST'])
def manage_inventory():
    if request.method == 'POST':
        data = {
            'item': request.form.get('item'),
            'date_of_purchase': request.form.get('date_of_purchase')
        }
        result = supabase.table('inventory').insert(data).execute()
        return result.data
    
    items = supabase.table('inventory').select('*').execute()
    return render_template('inventory/inventory.html', items=items.data)