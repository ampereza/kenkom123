from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, jsonify
from dotenv import load_dotenv
import os
from supabase import create_client, Client

from datetime import datetime

# Add a custom Jinja2 filter for datetime formatting
def format_datetime(value, format="%Y-%m-%d %H:%M:%S"):
    if value:
        return value.strftime(format)
    return ""

app = Flask(__name__)  # Ensure this matches your app initialization
app.jinja_env.filters['datetime'] = format_datetime

stock = Blueprint('stock', __name__)

#templates for this blueprint are in the stock folder

#routes for this blueprint
#stock_dashboard
#recieve_stock
#stock_report
#sort_stock
#delivery_note
#stock_transfer
#recieveclientsstock
#stock_adjustment

#load .env file
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
secret = os.getenv("SECRET_KEY")


def check_stock_balance(table_name, client_id=None):
    """Check current stock levels in specified table"""
    today = datetime.now().date().isoformat()
    try:
        if client_id:
            current_stock = supabase.table(table_name)\
                .select('*')\
                .eq('client_id', client_id)\
                .eq('date', today)\
                .execute()
        else:
            current_stock = supabase.table(table_name)\
                .select('*')\
                .eq('date', today)\
                .execute()
        return current_stock.data[0] if current_stock.data else None
    except Exception as e:
        print(f"Error checking stock: {str(e)}")
        return None

@stock.route('/stock_dashboard')
def stock_dashboard():
    try:
        # Fetch data from Supabase
        treated_stock = supabase.table('kdl_treated_poles').select("*").order('created_at', desc=True).execute().data
        untreated_stock = supabase.table('kdl_untreated_stock').select("*").order('created_at', desc=True).execute().data
        unsorted_stock = supabase.table('kdl_unsorted_stock').select("*").order('created_at', desc=True).execute().data
        received_stock = supabase.table('recieived_stock').select("*").order('created_at', desc=True).execute().data

        # Calculate sums for treated stock
        treated_sums = {
            'fencing_poles': sum(float(item.get('fencing_poles', 0) or 0) for item in treated_stock),
            'timber': sum(float(item.get('timber', 0) or 0) for item in treated_stock),
            'rafters': sum(float(item.get('rafters', 0) or 0) for item in treated_stock),
            'telecom_poles': sum(float(item.get('telecom_poles', 0) or 0) for item in treated_stock),
            '7m': sum(float(item.get('7m', 0) or 0) for item in treated_stock),
            '8m': sum(float(item.get('8m', 0) or 0) for item in treated_stock),
            '9m': sum(float(item.get('9m', 0) or 0) for item in treated_stock),
            '10m': sum(float(item.get('10m', 0) or 0) for item in treated_stock),
            '11m': sum(float(item.get('11m', 0) or 0) for item in treated_stock),
            '12m': sum(float(item.get('12m', 0) or 0) for item in treated_stock),
            '14m': sum(float(item.get('14m', 0) or 0) for item in treated_stock),
            '16m': sum(float(item.get('16m', 0) or 0) for item in treated_stock),
            '9m_telecom': sum(float(item.get('9m_telecom', 0) or 0) for item in treated_stock),
            '10m_telecom': sum(float(item.get('10m_telecom', 0) or 0) for item in treated_stock),
            '12m_telecom': sum(float(item.get('12m_telecom', 0) or 0) for item in treated_stock),
            'stubs': sum(float(item.get('stubs', 0) or 0) for item in treated_stock)
        }

        # Calculate sums for untreated stock
        untreated_sums = {
            'fencing_poles': sum(float(item.get('fencing_poles', 0) or 0) for item in untreated_stock),
            'timber': sum(float(item.get('timber', 0) or 0) for item in untreated_stock),
            'rafters': sum(float(item.get('rafters', 0) or 0) for item in untreated_stock),
            'telecom_poles': sum(float(item.get('telecom_poles', 0) or 0) for item in untreated_stock),
            '7m': sum(float(item.get('7m', 0) or 0) for item in untreated_stock),
            '8m': sum(float(item.get('8m', 0) or 0) for item in untreated_stock),
            '9m': sum(float(item.get('9m', 0) or 0) for item in untreated_stock),
            '10m': sum(float(item.get('10m', 0) or 0) for item in untreated_stock),
            '11m': sum(float(item.get('11m', 0) or 0) for item in untreated_stock),
            '12m': sum(float(item.get('12m', 0) or 0) for item in untreated_stock),
            '14m': sum(float(item.get('14m', 0) or 0) for item in untreated_stock),
            '16m': sum(float(item.get('16m', 0) or 0) for item in untreated_stock),
            '9m_telecom': sum(float(item.get('9m_telecom', 0) or 0) for item in untreated_stock),
            '10m_telecom': sum(float(item.get('10m_telecom', 0) or 0) for item in untreated_stock),
            '12m_telecom': sum(float(item.get('12m_telecom', 0) or 0) for item in untreated_stock),
            'stubs': sum(float(item.get('stubs', 0) or 0) for item in untreated_stock)
        }

        # Calculate sum for unsorted stock
        unsorted_sum = sum(float(item.get('quantity', 0) or 0) for item in unsorted_stock)

        return render_template('stock/stock_dashboard.html', 
                            treated_count=len(treated_stock),
                            untreated_count=len(untreated_stock),
                            unsorted_count=len(unsorted_stock),
                            recent_activities=received_stock,
                            treated_sums=treated_sums,
                            untreated_sums=untreated_sums,
                            unsorted_sum=unsorted_sum)

    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        return render_template('stock/stock_dashboard.html',
                            treated_count=0,
                            untreated_count=0,
                            unsorted_count=0,
                            recent_activities=[],
                            treated_sums={},
                            untreated_sums={},
                            unsorted_sum=0)

@stock.route('/receive_unsorted_stock', methods=['GET', 'POST'])
def receive_unsorted_stock():
    if request.method == 'POST':
        # Retrieve and validate form data
        pole_type = request.form.get('pole_type')
        supplier_id = request.form.get('supplier_id')
        quantity = request.form.get('quantity')
        description = request.form.get('description')

        # Check for missing fields
        missing_fields = []
        if not pole_type:
            missing_fields.append('Pole Type')
        if not supplier_id:
            missing_fields.append('Supplier ID')
        if not quantity:
            missing_fields.append('Quantity')
        if not description:
            missing_fields.append('Description')

        if missing_fields:
            flash(f'Missing fields: {", ".join(missing_fields)}', 'danger')
            return redirect(url_for('stock.receive_unsorted_stock'))  # Ensure this is the correct route

        # Validate numeric fields
        try:
            quantity = float(quantity)
        except ValueError:
            flash('Quantity and Supplier ID must be valid numbers.', 'danger')
            return redirect(url_for('stock.receive_unsorted_stock'))

        # Generate receipt data
        date_created = datetime.utcnow().isoformat()
        receipt_data = {
            "pole_type": pole_type,
            "supplier_id": supplier_id,
            "description": description,
            "date": date_created,
            "quantity": quantity,
        }

        # Insert receipt into Supabase
        try:
            response = supabase.table('kdl_unsorted_stock').insert(receipt_data).execute()
            if response:  # Check for successful insertion
                flash('Stock entry created successfully!', 'success')
            else:
                flash('Failed to create stock entry. Please try again.', 'danger')
        except Exception as e:
            flash(f'Error saving stock entry: {str(e)}', 'danger')

        return redirect(url_for('stock.receive_unsorted_stock'))  # Redirect to the same page after submission

    # Fetch suppliers and unsorted stock
    try:
        suppliers = supabase.table('suppliers').select("*").execute().data
        unsorted = supabase.table('kdl_unsorted_stock') .select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        suppliers = []
        unsorted = []

    # Render template with data
    return render_template('stock/receuve_unsorted_stock.html', supplier_ids=suppliers, unsorted=unsorted)



#delivery route

@stock.route('/delivery', methods=['GET', 'POST'])
def delivery():
    if request.method == 'POST':
        try:
            # Get form data
            delivery_for = request.form.get('delivery_for')  # 'client' or 'customer'
            note_number = request.form.get('note_number')
            vehicle_number = request.form.get('vehicle_number')
            transporter = request.form.get('transporter')
            loaded_by = request.form.get('loaded_by')
            destination = request.form.get('destination')
            notes = request.form.get('notes')
            delivery_date = datetime.utcnow().date().isoformat()

            # Get quantities
            quantities = {
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)),
                'rafters': float(request.form.get('rafters', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0))
            }

            # Calculate total quantity
            total_quantity = sum(quantities.values())

            # Prepare delivery note data
            delivery_data = {
                'note_number': note_number,
                'date': delivery_date,
                'vehicle_number': vehicle_number,
                'transporter': transporter,
                'total_quantity': total_quantity,
                'loaded_by': loaded_by,
                'loaded_at': datetime.utcnow().isoformat(),
                'destination': destination,
                'notes': notes,
                'delivery_for': delivery_for,
                **quantities  # Include all quantities
            }

            if delivery_for == 'customer':
                # Add customer_id and reduce from KDL stock
                delivery_data['customers_id'] = request.form.get('customer_id')
                
                # Get current KDL stock
                kdl_stock = supabase.table('kdl_treated_poles').select("*").order('created_at', desc=True).limit(1).execute().data[0]
                
                # Calculate new quantities and update KDL stock
                updated_quantities = {k: max(0, kdl_stock.get(k, 0) - v) for k, v in quantities.items()}
                supabase.table('kdl_treated_poles').update(updated_quantities).eq('id', kdl_stock['id']).execute()
                
            else:  # delivery_for == 'client'
                # Add client_id and reduce from client's treated poles
                client_id = request.form.get('client_id')
                delivery_data['client_id'] = client_id
                
                # Get current client stock
                client_stock = supabase.table('clients_treated_poles').select("*").eq('client_id', client_id).order('created_at', desc=True).limit(1).execute().data[0]
                
                # Calculate new quantities and update client stock
                updated_quantities = {k: max(0, client_stock.get(k, 0) - v) for k, v in quantities.items()}
                supabase.table('clients_treated_poles').update(updated_quantities).eq('id', client_stock['id']).execute()

            # Insert delivery note
            response = supabase.table('delivery_notes').insert(delivery_data).execute()
            
            if response.data:
                flash('Delivery note created successfully', 'success')
            else:
                flash('Error creating delivery note', 'danger')

        except Exception as e:
            flash(f'Error processing delivery: {str(e)}', 'danger')
            return redirect(url_for('stock.delivery'))

    # GET request - fetch necessary data
    try:
        clients = supabase.table('clients').select("*").execute().data
        customers = supabase.table('customers').select("*").execute().data
        delivery_notes = supabase.table('delivery_notes').select("*").order('created_at', desc=True).execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        clients = []
        customers = []
        delivery_notes = []

    return render_template('stock/delivery.html',
                         clients=clients,
                         customers=customers,
                         delivery_notes=delivery_notes)
    


# recieve clients stock






@stock.route('/receive_stock', methods=['GET', 'POST'])
def receive_stock():
    if request.method == 'POST':
        # Retrieve form data
        source = request.form.get('from')
        quantity = request.form.get('quantity')
        wood_type = request.form.get('wood_type')
        vehicle_number = request.form.get('vehicle_number')
        name = request.form.get('name')
        reason = request.form.get('reason')
    

    try:
        # Create record with unsorted status
        data = {
            "from": source,
            "quantity": float(quantity),
            "wood_type": wood_type,
            "vehicle_number": vehicle_number,
            "name": name,
            "date": datetime.utcnow().date().isoformat(),
            "status": "unsorted",
            "reason": reason,
        }
        
        response = supabase.table('recieived_stock').insert(data).execute()
        if response:
            flash('Stock received successfully!', 'success')
        else:
            flash('Failed to record stock receipt', 'danger')
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        
# GET request - fetch existing records
    try:
        received_stock = supabase.table('recieived_stock').select("*").order('created_at', desc=True).execute().data
    except Exception as e:
        flash(f'Error fetching records: {str(e)}', 'danger')
        received_stock = []

    return render_template('stock/recieve_stock.html', received_stock=received_stock)


@stock.route('/update_stock_status/<int:id>', methods=['POST'])
def update_stock_status(id):
    try:
        response = supabase.table('recieived_stock').update({"status": "sorted"}).eq("id", id).execute()
        if response:
            flash('Status updated successfully', 'success')
        else:
            flash('Failed to update status', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('stock.receive_stock'))



@stock.route('/kdl_stock_report', methods=['GET'])
def kdl_stock_report():
    try:
        # Fetch treated and untreated stock data
        treated_stock = supabase.table('kdl_treated_poles').select("*").order('created_at', desc=True).execute().data
        untreated_stock = supabase.table('kdl_to_treat').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching records: {str(e)}', 'danger')
        treated_stock = []
        untreated_stock = []

    return render_template('stock/kdl_stock_report.html', 
                         treated_stock=treated_stock,
                         untreated_stock=untreated_stock)



@stock.route('/clients_stock', methods=['GET', 'POST'])
def clients_stock():
    try:
        # Fetch data from all relevant tables
        clients = supabase.table('clients').select("*").execute().data
        treated_poles = supabase.table('clients_treated_poles').select("*").execute().data
        untreated_stock = supabase.table('client_to_treat').select("*").execute().data

        return render_template('stock/clients_stock.html', 
                            clients=clients,
                            treated_poles=treated_poles, 
                            untreated_stock=untreated_stock)
    except Exception as e:
        flash(f'Error fetching client stock data: {str(e)}', 'danger')
        return render_template('stock/clients_stock.html', 
                            clients=[], 
                            treated_poles=[],
                            untreated_stock=[])
    

@stock.route('/add_clients_current_stock', methods=['GET', 'POST'])
def add_clients_current_stock():
    if request.method == 'POST':
        pole_type = request.form.get('pole_type')
        client_id = request.form.get('client_id')
        
        # Validate pole_type
        valid_types = ['client_untreated_stock', 'clients_treated_poles']
        if pole_type not in valid_types:
            flash('Invalid pole type', 'danger')
            return redirect(url_for('stock.add_clients_current_stock'))

        try:
            data = {
                'client_id': client_id,
                'rafters': float(request.form.get('rafters', 0)),
                'timber': float(request.form.get('timber', 0)),
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)),
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                'stubs': float(request.form.get('stubs', 0)),
                '10m': float(request.form.get('10m', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '11m': float(request.form.get('11m', 0)), 
                '12m': float(request.form.get('12m', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                'date': datetime.utcnow().date().isoformat()
            }

            # Add cylinder_no for treated poles
            if pole_type == 'clients_treated_poles':
                data['cylinder_no'] = float(request.form.get('cylinder_no', 0))

            response = supabase.table(pole_type).insert(data).execute()
            flash('Data saved successfully!', 'success')

            if response.error:
                flash(f'Error saving data: {response.error}', 'danger')
                return redirect(url_for('stock.add_clients_current_stock'))

        except Exception as e:
            return redirect(url_for('stock.add_clients_current_stock'))

    # Fetch clients for the form
    try:
        clients = supabase.table('clients').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching clients: {str(e)}', 'danger')
        clients = []

    return render_template('stock/add_clients_current_stock.html', clients=clients)\









@stock.route('/rejects', methods=['GET', 'POST'])
def rejects():
    if request.method == 'POST':
        try:
            data = {
                'quantity': float(request.form.get('quantity', 0)),
                'kdl': request.form.get('kdl'),
                'client_id': request.form.get('client_id'),
                'supplier_id': request.form.get('supplier_id'),
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)),
                'stabs': float(request.form.get('stabs', 0)),
                'rafters': float(request.form.get('rafters', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                'telecom': float(request.form.get('telecom', 0)),
                '9m': float(request.form.get('9m', 0)),
                
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                '10m': float(request.form.get('10m', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                'date': datetime.utcnow().date().isoformat()
            }

            response = supabase.table('rejects').insert(data).execute()
            if response.data:
                flash('Reject record created successfully', 'success')
            else:
                flash('Failed to create reject record', 'danger')

        except Exception as e:
            flash(f'Error creating reject record: {str(e)}', 'danger')
        return redirect(url_for('stock.rejects'))

    try:
        rejects = supabase.table('rejects').select("*").order('created_at', desc=True).execute().data
        clients = supabase.table('clients').select("*").execute().data
        suppliers = supabase.table('suppliers').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        rejects = []
        clients = []
        suppliers = []

    return render_template('stock/rejects.html', 
                            rejects=rejects,
                            clients=clients,
                            suppliers=suppliers)


@stock.route('/add_kdl_untreated_stock', methods=['GET', 'POST'])
def add_kdl_untreated_stock():
    if request.method == 'POST':
        try:
            data = {
                'rafters': float(request.form.get('rafters', 0)),
                'timber': float(request.form.get('timber', 0)),
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)), 
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                'stubs': float(request.form.get('stubs', 0)),
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0)),
                'date': datetime.utcnow().date().isoformat()
            }

            response = supabase.table('kdl_untreated_stock').insert(data).execute()
            if response.data:
                flash('Untreated stock record created successfully', 'success')
            else:
                flash('Failed to create untreated stock record', 'danger')

        except Exception as e:
            flash(f'Error creating untreated stock record: {str(e)}', 'danger')
        return redirect(url_for('stock.add_kdl_untreated_stock'))

    try:
        untreated_stock = supabase.table('kdl_untreated_stock').select("*").order('created_at', desc=True).execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        untreated_stock = []

    return render_template('stock/add_kdl_untreated_stock.html', untreated_stock=untreated_stock)



@stock.route('/add_kdl_treated_poles', methods=['GET', 'POST'])
def add_kdl_treated_poles():
    if request.method == 'POST':
        try:
            data = {
                'rafters': float(request.form.get('rafters', 0)),
                'timber': float(request.form.get('timber', 0)),
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)), 
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0)),
                'cylinder_no': float(request.form.get('cylinder_no', 0)),
                'stubs': float(request.form.get('stubs', 0)),
                'date': datetime.utcnow().date().isoformat()
            }

            response = supabase.table('kdl_treated_poles').insert(data).execute()
            if response.data:
                flash('Treated poles record created successfully', 'success')
            else:
                flash('Failed to create treated poles record', 'danger')

        except Exception as e:
            flash(f'Error creating treated poles record: {str(e)}', 'danger')
        return redirect(url_for('stock.add_kdl_treated_poles'))

    try:
        treated_poles = supabase.table('kdl_treated_poles').select("*").order('created_at', desc=True).execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        treated_poles = []

    return render_template('stock/add_kdl_treated_poles.html', treated_poles=treated_poles)



@stock.route('/add_unsorted_poles', methods=['GET', 'POST'])
def add_unsorted_poles():
    if request.method == 'POST':
        try:
            data = {
                'pole_type': request.form.get('pole_type'),
                'quantity': float(request.form.get('quantity', 0)),
                'supplier_id': request.form.get('supplier_id'),
                'description': request.form.get('description'),
                'date': datetime.utcnow().date().isoformat()
            }

            response = supabase.table('kdl_unsorted_stock').insert(data).execute()
            if response.data:
                flash('Unsorted stock record created successfully', 'success')
            else:
                flash('Failed to create unsorted stock record', 'danger')

        except Exception as e:
            flash(f'Error creating unsorted stock record: {str(e)}', 'danger')
        return redirect(url_for('stock.add_unsorted_poles'))

    try:
        unsorted_stock = supabase.table('kdl_unsorted_stock').select("*").order('created_at', desc=True).execute().data
        suppliers = supabase.table('suppliers').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        unsorted_stock = []
        suppliers = []  # Initialize suppliers to an empty list in case of an exception

    return render_template('stock/add_unsorted_poles.html', 
                            unsorted_stock=unsorted_stock,
                            suppliers=suppliers)


@stock.route('/add_clients_unsorted_stock', methods=['GET', 'POST'])
def add_clients_unsorted_stock():
    if request.method == 'POST':
        try:
            # Ensure only valid fields are inserted
            data = {
                'client_id': request.form.get('client_id'),
                'pole_type': request.form.get('pole_type'),
                'quantity': float(request.form.get('quantity', 0))
            }

            # Insert data into the correct table
            response = supabase.table('clients_unsorted').insert(data).execute()
            if response.data:
                flash('Client unsorted stock added successfully', 'success')
            else:
                flash('Failed to add unsorted stock record', 'danger')

        except Exception as e:
            flash(f'Error adding unsorted stock: {str(e)}', 'danger')
            print(e)

    try:
        # Fetch data for rendering the template
        cl_unsorted_stock = supabase.table('clients_unsorted').select("*").order('created_at', desc=True).execute().data
        clients = supabase.table('clients').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(e)
        cl_unsorted_stock = []
        clients = []

    return render_template('stock/add_clients_unsorted_stock.html',
                            unsorted_stock=cl_unsorted_stock,
                            clients=clients)


@stock.route('/get_pass', methods=['GET', 'POST'])
def get_pass():
    if request.method == 'POST':
        try:
            # Extract only the time portion (HH:MM) from the datetime-local input
            time_in = request.form.get('time_in').split('T')[1]
            time_out = request.form.get('time_out').split('T')[1]

            data = {
                'time_in': time_in,
                'time_out': time_out,
                'reaseon': request.form.get('reaseon'),
                'items': request.form.get('items'),
                'quantity': float(request.form.get('quantity', 0)),
                'description': request.form.get('description'),
                'comments': request.form.get('comments'),
                'drivers_name': request.form.get('drivers_name'),
                'vehicle_number': request.form.get('vehicle_number'),
                'checked_by': request.form.get('checked_by'),
                'type': request.form.get('type')
            }

            response = supabase.table('get_pass_in').insert(data).execute()
            if response.data:
                flash('Gate pass created successfully', 'success')
            else:
                flash('Failed to create gate pass', 'danger')

        except Exception as e:
            flash(f'Error creating gate pass: {str(e)}', 'danger')
        return redirect(url_for('stock.get_pass'))

    try:
        passes = supabase.table('get_pass_in').select("*").order('created_at', desc=True).execute().data
        return render_template('stock/get_pass.html', passes=passes)  # Render passes to the front end
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        return render_template('stock/get_pass.html', passes=[])




@stock.route('/move_untreated_stock', methods=['GET', 'POST'])
def move_untreated_stock():
    if request.method == 'POST':
        try:
            client_id = request.form.get('client_id')
            notes = request.form.get('notes')

            # Get stock data from the form
            movement_data = {
                'from_client_id': client_id,
                'to_kdl': True,
                'from_kdl': False,
                'movement_type': 'client_to_kdl',
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)),
                'rafters': float(request.form.get('rafters', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0)),

                'notes': notes
            }

            print("Movement Data:", movement_data)  # Debugging
            flash(f"Movement Data: {movement_data}", "info")  # Debugging

            # Add to KDL stock
            kdl_data = {
                'fencing_poles': movement_data['fencing_poles'],
                'timber': movement_data['timber'],
                'rafters': movement_data['rafters'],
                'telecom_poles': movement_data['telecom_poles'],
                '7m': movement_data['7m'],
                '8m': movement_data['8m'],
                '9m': movement_data['9m'],
                '10m': movement_data['10m'],
                '11m': movement_data['11m'],
                '12m': movement_data['12m'],
                '14m': movement_data['14m'],
                '16m': movement_data['16m'],
                'date': datetime.utcnow().date().isoformat(),
                'client_id': client_id
            }

            print("KDL Data:", kdl_data)  # Debugging
            flash(f"KDL Data: {kdl_data}", "info")  # Debugging

            # Get current client stock data
            client_stock_response = supabase.table('client_untreated_stock').select("*").eq('client_id', client_id).execute()
            client_stock = client_stock_response.data[0] if client_stock_response.data else {}

            # Execute all database operations
            response1 = supabase.table('stock_movements').insert(movement_data).execute()
            response2 = supabase.table('kdl_untreated_stock').insert(kdl_data).execute()

            # Deduct moved stock from the client's stock
            response3 = supabase.table('client_untreated_stock').update({
                'fencing_poles': max(0, (client_stock.get('fencing_poles', 0) - movement_data['fencing_poles'])),
                'timber': max(0, (client_stock.get('timber', 0) - movement_data['timber'])),
                'rafters': max(0, (client_stock.get('rafters', 0) - movement_data['rafters'])),
                'telecom_poles': max(0, (client_stock.get('telecom_poles', 0) - movement_data['telecom_poles'])),
                '7m': max(0, (client_stock.get('7m', 0) - movement_data['7m'])),
                '8m': max(0, (client_stock.get('8m', 0) - movement_data['8m'])),
                '9m': max(0, (client_stock.get('9m', 0) - movement_data['9m'])),
                '10m': max(0, (client_stock.get('10m', 0) - movement_data['10m'])),
                '11m': max(0, (client_stock.get('11m', 0) - movement_data['11m'])),
                '12m': max(0, (client_stock.get('12m', 0) - movement_data['12m'])),
                '14m': max(0, (client_stock.get('14m', 0) - movement_data['14m'])),
                '16m': max(0, (client_stock.get('16m', 0) - movement_data['16m'])),
            }).eq('client_id', client_id).execute()

            print("Response3:", response3)  # Debugging
            flash(f"Response3: {response3}", "info")  # Debugging

            if response1 and response2 and response3:
                flash('Stock moved successfully', 'success')
            else:
                flash('Error moving stock', 'danger')

        except Exception as e:
            print("Error:", str(e))  # Debugging
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('stock.move_untreated_stock'))

    # GET request - fetch clients
    try:
        clients = supabase.table('clients').select("*").execute().data
        print("Clients:", clients)  # Debugging
    except Exception as e:
        print("Error fetching clients:", str(e))  # Debugging
        flash(f'Error fetching clients: {str(e)}', 'danger')
        clients = []

    return render_template('stock/move_untreated_stock.html', clients=clients)


@stock.route('/move_treated_stock', methods=['GET', 'POST'])
def move_treated_stock():
    if request.method == 'POST':
        try:
            client_id = request.form.get('client_id')
            notes = request.form.get('notes')

            # Get stock data from the form
            movement_data = {
                'from_client_id': client_id,
                'to_kdl': True,
                'from_kdl': False,
                'movement_type': 'client_to_kdl',
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)),
                'rafters': float(request.form.get('rafters', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                'notes': notes
            }

            print("Movement Data:", movement_data)  # Debugging
            flash(f"Movement Data: {movement_data}", "info")  # Debugging

            # Add to KDL stock
            kdl_data = {
                'fencing_poles': movement_data['fencing_poles'],
                'timber': movement_data['timber'],
                'rafters': movement_data['rafters'],
                'telecom_poles': movement_data['telecom_poles'],
                '7m': movement_data['7m'],
                '8m': movement_data['8m'],
                '9m': movement_data['9m'],
                '10m': movement_data['10m'],
                '11m': movement_data['11m'],
                '12m': movement_data['12m'],
                '14m': movement_data['14m'],
                '16m': movement_data['16m'],
                'date': datetime.utcnow().date().isoformat(),
                'client_id': client_id
            }
            print("KDL Data:", kdl_data)  # Debugging
            flash(f"KDL Data: {kdl_data}", "info")  # Debugging

            # Get current client stock data
            client_stock_response = supabase.table('clients_treated_poles').select("*").eq('client_id', client_id).execute()
            client_stock = client_stock_response.data[0] if client_stock_response.data else {}
            print("Client Stock:", client_stock)  # Debugging

            flash(f"Client Stock: {client_stock}", "info")  # Debugging

            # Execute all database operations
            response1 = supabase.table('stock_movements').insert(movement_data).execute()
            response2 = supabase.table('kdl_treated_poles').insert(kdl_data).execute()

            # Deduct moved stock from the client's stock
            response3 = supabase.table('clients_treated_poles').update({
                'fencing_poles': max(0, (client_stock.get('fencing_poles', 0) - movement_data['fencing_poles'])),
                'timber': max(0, (client_stock.get('timber', 0) - movement_data['timber'])),
                'rafters': max(0, (client_stock.get('rafters', 0) - movement_data['rafters'])),
                'telecom_poles': max(0, (client_stock.get('telecom_poles', 0) - movement_data['telecom_poles'])),
                '7m': max(0, (client_stock.get('7m', 0) - movement_data['7m'])),
                '8m': max(0, (client_stock.get('8m', 0) - movement_data['8m'])),
                '9m': max(0, (client_stock.get('9m', 0) - movement_data['9m'])),
                '10m': max(0, (client_stock.get('10m', 0) - movement_data['10m'])),
                '11m': max(0, (client_stock.get('11m', 0) - movement_data['11m'])),
                '12m': max(0, (client_stock.get('12m', 0) - movement_data['12m'])),
                '14m': max(0, (client_stock.get('14m', 0) - movement_data['14m'])),
                '16m': max(0, (client_stock.get('16m', 0) - movement_data['16m'])),
            }).eq('client_id', client_id).execute()
            print("Response3:", response3)  # Debugging


            flash(f"Response3: {response3}", "info")  # Debugging
            
            if response1 and response2 and response3:
                flash('Stock moved successfully', 'success')
            else:
                flash('Error moving stock', 'danger')

        except Exception as e:
            print("Error:", str(e))
            flash(f'Error: {str(e)}', 'danger')

        # Redirect to the same page after processing the POST request
        return redirect(url_for('stock.move_treated_stock'))

    # GET request - fetch clients
    try:
        clients = supabase.table('clients').select("*").execute().data
        print("Clients:", clients)  # Debugging
    except Exception as e:
        print("Error fetching clients:", str(e))  # Debugging
        flash(f'Error fetching clients: {str(e)}', 'danger')
        clients = []

    return render_template('stock/move_treated_stock.html', clients=clients)



#move from kdl_untreated_stock to client_untreated_stock
@stock.route('/move_untreated_to_client', methods=['GET', 'POST'])
def move_untreated_to_client():
    if request.method == 'POST':
        try:
            client_id = request.form.get('client_id')
            notes = request.form.get('notes')

            # Get stock data from the form
            movement_data = {
                'from_client_id': client_id,
                'to_kdl': False,
                'from_kdl': True,
                'movement_type': 'kdl_to_client',  # Correct movement type
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)),
                'rafters': float(request.form.get('rafters', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                'notes': notes
            }

            print("Movement Data:", movement_data)  # Debugging
            flash(f"Movement Data: {movement_data}", "info")  # Debugging

            # Add to client stock
            client_data = {
                'fencing_poles': movement_data['fencing_poles'],
                'timber': movement_data['timber'],
                'rafters': movement_data['rafters'],
                'telecom_poles': movement_data['telecom_poles'],
                '7m': movement_data['7m'],
                '8m': movement_data['8m'],
                '9m': movement_data['9m'],
                '10m': movement_data['10m'],
                '11m': movement_data['11m'],
                '12m': movement_data['12m'],
                '14m': movement_data['14m'],
                '16m': movement_data['16m'],
                'date': datetime.utcnow().date().isoformat(),
                'client_id': client_id
            }

            print("Client Data:", client_data)  # Debugging
            flash(f"Client Data: {client_data}", "info")  # Debugging

            # Check if a record with the same date and client_id already exists
            existing_record = supabase.table('client_untreated_stock').select("*").eq('client_id', client_id).eq('date', client_data['date']).execute().data
            if existing_record:
                # Update the existing record
                response2 = supabase.table('client_untreated_stock').update({
                    'fencing_poles': existing_record[0]['fencing_poles'] + client_data['fencing_poles'],
                    'timber': existing_record[0]['timber'] + client_data['timber'],
                    'rafters': existing_record[0]['rafters'] + client_data['rafters'],
                    'telecom_poles': existing_record[0]['telecom_poles'] + client_data['telecom_poles'],
                    '7m': existing_record[0]['7m'] + client_data['7m'],
                    '8m': existing_record[0]['8m'] + client_data['8m'],
                    '9m': existing_record[0]['9m'] + client_data['9m'],
                    '10m': existing_record[0]['10m'] + client_data['10m'],
                    '11m': existing_record[0]['11m'] + client_data['11m'],
                    '12m': existing_record[0]['12m'] + client_data['12m'],
                    '14m': existing_record[0]['14m'] + client_data['14m'],
                    '16m': existing_record[0]['16m'] + client_data['16m'],
                }).eq('id', existing_record[0]['id']).execute()
            else:
                # Insert a new record
                response2 = supabase.table('client_untreated_stock').insert(client_data).execute()

            # Deduct moved stock from the KDL stock
            kdl_stock_response = supabase.table('kdl_untreated_stock').select("*").execute()
            kdl_stock = kdl_stock_response.data[0] if kdl_stock_response.data else {}

            response3 = supabase.table('kdl_untreated_stock').update({
                'fencing_poles': max(0, (kdl_stock.get('fencing_poles', 0) - movement_data['fencing_poles'])),
                'timber': max(0, (kdl_stock.get('timber', 0) - movement_data['timber'])),
                'rafters': max(0, (kdl_stock.get('rafters', 0) - movement_data['rafters'])),
                'telecom_poles': max(0, (kdl_stock.get('telecom_poles', 0) - movement_data['telecom_poles'])),
                '7m': max(0, (kdl_stock.get('7m', 0) - movement_data['7m'])),
                '8m': max(0, (kdl_stock.get('8m', 0) - movement_data['8m'])),
                '9m': max(0, (kdl_stock.get('9m', 0) - movement_data['9m'])),
                '10m': max(0, (kdl_stock.get('10m', 0) - movement_data['10m'])),
                '11m': max(0, (kdl_stock.get('11m', 0) - movement_data['11m'])),
                '12m': max(0, (kdl_stock.get('12m', 0) - movement_data['12m'])),
                '14m': max(0, (kdl_stock.get('14m', 0) - movement_data['14m'])),
                '16m': max(0, (kdl_stock.get('16m', 0) - movement_data['16m'])),
            }).eq('id', kdl_stock.get('id')).execute()

            print("Response3:", response3)  # Debugging
            flash(f"Response3: {response3}", "info")  # Debugging

            if response2 and response3:
                flash('Stock moved successfully', 'success')
            else:
                flash('Error moving stock', 'danger')

        except Exception as e:
            print("Error:", str(e))
            flash(f'Error: {str(e)}', 'danger')

        # Redirect to the same page after processing the POST request
        return redirect(url_for('stock.move_untreated_to_client'))

    # GET request - fetch clients
    try:
        clients = supabase.table('clients').select("*").execute().data
        print("Clients:", clients)  # Debugging
    except Exception as e:
        print("Error fetching clients:", str(e))  # Debugging
        flash(f'Error fetching clients: {str(e)}', 'danger')
        clients = []

    return render_template('stock/move_untreated_to_client.html', clients=clients)






#move from kdl_untreated_stock to client_untreated_stock
@stock.route('/move_treated_to_client', methods=['GET', 'POST'])
def move_treated_to_client():
    if request.method == 'POST':
        try:
            client_id = request.form.get('client_id')
            notes = request.form.get('notes')

            # Get stock data from the form
            movement_data = {
                'from_client_id': client_id,
                'to_kdl': False,
                'from_kdl': True,
                'movement_type': 'kdl_to_client',
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)),
                'rafters': float(request.form.get('rafters', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)),
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)),
                '16m': float(request.form.get('16m', 0)),
                'notes': notes
            }

            print("Movement Data:", movement_data)  # Debugging
            flash(f"Movement Data: {movement_data}", "info")  # Debugging

            # Add to client stock
            client_data = {
                'fencing_poles': movement_data['fencing_poles'],
                'timber': movement_data['timber'],
                'rafters': movement_data['rafters'],
                'telecom_poles': movement_data['telecom_poles'],
                '7m': movement_data['7m'],
                '8m': movement_data['8m'],
                '9m': movement_data['9m'],
                '10m': movement_data['10m'],
                '11m': movement_data['11m'],
                '12m': movement_data['12m'],
                '14m': movement_data['14m'],
                '16m': movement_data['16m'],
                'date': datetime.utcnow().date().isoformat(),
                'client_id': client_id
            }

            # Check if a record with the same date and client_id already exists
            existing_record = supabase.table('clients_treated_poles').select("*").eq('client_id', client_id).eq('date', client_data['date']).execute().data
            if existing_record:
                # Update the existing record
                response2 = supabase.table('clients_treated_poles').update({
                    'fencing_poles': existing_record[0]['fencing_poles'] + client_data['fencing_poles'],
                    'timber': existing_record[0]['timber'] + client_data['timber'],
                    'rafters': existing_record[0]['rafters'] + client_data['rafters'],
                    'telecom_poles': existing_record[0]['telecom_poles'] + client_data['telecom_poles'],
                    '7m': existing_record[0]['7m'] + client_data['7m'],
                    '8m': existing_record[0]['8m'] + client_data['8m'],
                    '9m': existing_record[0]['9m'] + client_data['9m'],
                    '10m': existing_record[0]['10m'] + client_data['10m'],
                    '11m': existing_record[0]['11m'] + client_data['11m'],
                    '12m': existing_record[0]['12m'] + client_data['12m'],
                    '14m': existing_record[0]['14m'] + client_data['14m'],
                    '16m': existing_record[0]['16m'] + client_data['16m'],
                }).eq('id', existing_record[0]['id']).execute()
            else:
                # Insert a new record
                response2 = supabase.table('clients_treated_poles').insert(client_data).execute()

            # Deduct moved stock from the KDL stock
            kdl_stock_response = supabase.table('kdl_treated_poles').select("*").execute()
            kdl_stock = kdl_stock_response.data[0] if kdl_stock_response.data else {}
            print("KDL Stock:", kdl_stock)  # Debugging

            # Deduct moved stock from the client's stock
            response3 = supabase.table('clients_treated_poles').update({
                'fencing_poles': max(0, (client_stock.get('fencing_poles', 0) - movement_data['fencing_poles'])),
                'timber': max(0, (client_stock.get('timber', 0) - movement_data['timber'])),
                'rafters': max(0, (client_stock.get('rafters', 0) - movement_data['rafters'])),
                'telecom_poles': max(0, (client_stock.get('telecom_poles', 0) - movement_data['telecom_poles'])),
                '7m': max(0, (client_stock.get('7m', 0) - movement_data['7m'])),
                '8m': max(0, (client_stock.get('8m', 0) - movement_data['8m'])),
                '9m': max(0, (client_stock.get('9m', 0) - movement_data['9m'])),
                '10m': max(0, (client_stock.get('10m', 0) - movement_data['10m'])),
                '11m': max(0, (client_stock.get('11m', 0) - movement_data['11m'])),
                '12m': max(0, (client_stock.get('12m', 0) - movement_data['12m'])),
                '14m': max(0, (client_stock.get('14m', 0) - movement_data['14m'])),
                '16m': max(0, (client_stock.get('16m', 0) - movement_data['16m'])),
            }).eq('client_id', client_id).execute()
            print("Response3:", response3)  # Debugging


            flash(f"Response3: {response3}", "info")  # Debugging
            
            if response1 and response2 and response3:
                flash('Stock moved successfully', 'success')
            else:
                flash('Error moving stock', 'danger')

        except Exception as e:
            print("Error:", str(e))
            flash(f'Error: {str(e)}', 'danger')

        # Redirect to the same page after processing the POST request
        return redirect(url_for('stock.move_treated_to_client'))

    # GET request - fetch clients
    try:
        clients = supabase.table('clients').select("*").execute().data
        print("Clients:", clients)  # Debugging
    except Exception as e:
        print("Error fetching clients:", str(e))  # Debugging
        flash(f'Error fetching clients: {str(e)}', 'danger')
        clients = []

    return render_template('stock/move_treated_to_client.html', clients=clients)


@stock.route('/stock_transfer', methods=['GET', 'POST'])
def stock_transfer():
    try:
        # Fetch all stock movements
        movements = supabase.table('stock_movements').select("*").order('movement_date', desc=True).execute().data
        
        # Fetch clients for reference
        clients = supabase.table('clients').select("*").execute().data
        
        # Fetch current KDL untreated stock
        kdl_stock = supabase.table('kdl_untreated_stock').select("*").order('created_at', desc=True).execute().data
        
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        movements = []
        clients = []
        kdl_stock = []

    return render_template('stock/stock_movements.html', 
                            movements=movements,
                            clients=clients,
                            kdl_stock=kdl_stock)


#stock_search route by date
@stock.route('/stock_search', methods=['GET'])
def stock_search():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Both start_date and end_date are required'}), 400

        # Search sales
        stock_movements = supabase.table('stock_movements')\
            .select('*')\
            .gte('movement_date', start_date)\
            .lte('movement_date', end_date)\
            .execute()

        # Search receipts
        kdl_unsorted_stock = supabase.table('kdl_unsorted_stock')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()

        # Search purchases
        kdl_untreated_stock = supabase.table('kdl_untreated_stock')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()
        
        clients = supabase.table('clients').select("*").execute().data

        results = {
            'stock_movements': stock_movements.data if stock_movements else [],
            'kdl_unsorted_stock': kdl_unsorted_stock.data if kdl_unsorted_stock else [],
            'kdl_untreated': kdl_untreated_stock.data if kdl_untreated_stock else [],
        }

        return render_template('stock/search_results.html', 
                                results=results,
                                start_date=start_date,
                                end_date=end_date,
                                clients=clients)  # Pass clients to the template
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500



@stock.route('/sort_client_stock', methods=['GET', 'POST'])
def sort_client_stock():
    if request.method == 'POST':
        try:
            unsorted_id = request.form.get('unsorted_id')
            # Get the unsorted record
            unsorted_id = request.form.get('unsorted_id')
            poles_to_sort = float(request.form.get('poles_to_sort', 0))

            # Get the unsorted record
            unsorted_record = supabase.table('client_unsorted').select("*").eq('id', unsorted_id).execute().data[0]
            client_id = unsorted_record['client_id']
            current_quantity = float(unsorted_record['quantity'])

            # Validate poles_to_sort against available quantity
            if poles_to_sort > current_quantity:
                flash('Cannot sort more poles than available in unsorted stock', 'danger')
                return redirect(url_for('stock.sort_client_stock'))

            # Get or create today's untreated stock record for this client
            today = datetime.utcnow().date().isoformat()
            existing_record = supabase.table('client_untreated_stock').select("*").eq('client_id', client_id).eq('date', today).execute().data

            # Convert the unsorted quantity into graded quantities
            graded_stock = {
                'rafters': float(request.form.get('rafters', 0)),
                'timber': float(request.form.get('timber', 0)),
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
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
                'date': today,
                'client_id': client_id
            }

            # Verify total graded quantity matches poles_to_sort
            total_graded = sum(graded_stock[k] for k in graded_stock if k not in ['date', 'client_id'])
            if abs(total_graded - poles_to_sort) > 0.01:  # Allow small rounding differences
                flash('Total graded quantity must match quantity to sort', 'danger')
                return redirect(url_for('stock.sort_client_stock'))

            if existing_record:
                # Update existing record by adding the new quantities
                update_data = {}
                for key in graded_stock:
                    if key not in ['date', 'client_id']:
                        update_data[key] = float(existing_record[0].get(key, 0)) + graded_stock[key]
                
                response = supabase.table('client_untreated_stock').update(update_data).eq('id', existing_record[0]['id']).execute()
            else:
                # Create new record
                response = supabase.table('client_untreated_stock').insert(graded_stock).execute()

            # Update the unsorted record by reducing the quantity
            new_quantity = current_quantity - poles_to_sort
            if new_quantity > 0:
                supabase.table('client_unsorted').update({'quantity': new_quantity}).eq('id', unsorted_id).execute()
            else:
                # Delete the record if no quantity remains
                supabase.table('client_unsorted').delete().eq('id', unsorted_id).execute()

            flash('Stock sorted successfully', 'success')
            return redirect(url_for('stock.sort_client_stock'))

        except Exception as e:
            flash(f'Error sorting stock: {str(e)}', 'danger')
            return redirect(url_for('stock.sort_client_stock'))

    # GET request - fetch unsorted stock and clients
    try:
        unsorted_stock = supabase.table('client_unsorted').select("*").execute().data
        clients = supabase.table('clients').select("*").execute().data
        return render_template('stock/sort_stock.html', 
                            unsorted_stock=unsorted_stock,
                            clients=clients)
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        return render_template('stock/sort_stock.html', 
                            unsorted_stock=[],
                            clients=[])







# Get client details
@stock.route('/savana')
def savana():
    try:
        # Fetch stock from all 3 tables for client_id 18
        untreated = supabase.table('client_untreated_stock').select("*").eq('client_id', 18).execute().data
        treated = supabase.table('clients_treated_poles').select("*").eq('client_id', 18).execute().data 
        unsorted = supabase.table('clients_unsorted').select("*").eq('client_id', 18).execute().data

        # Get client details
        client = supabase.table('clients').select("*").eq('id', 18).execute().data[0]

        return render_template('stock/savana.html',
                            untreated=untreated,
                            treated=treated, 
                            unsorted=unsorted,
                            client=client)

    except Exception as e:
        flash(f'Error fetching client stock: {str(e)}', 'danger')
        return render_template('stock/savana.html',
                            untreated=[],
                            treated=[],
                            unsorted=[],
                            client=None)






@stock.route('/delivery_notess', methods=['GET', 'POST'])
def delivery_notess():
    clients = supabase.table('clients').select('*').execute()
    customers = supabase.table('customers').select('*').execute()

    if request.method == 'POST':
        try:
            delivery_for = request.form.get('delivery_for')
            
            # Get requested quantities 
            requested_quantities = {
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'timber': float(request.form.get('timber', 0)), 
                'rafters': float(request.form.get('rafters', 0)),
                '7m': float(request.form.get('7m', 0)),
                '8m': float(request.form.get('8m', 0)),
                '9m': float(request.form.get('9m', 0)), 
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
                '14m': float(request.form.get('14m', 0)), 
                '16m': float(request.form.get('16m', 0)),
                '9m_telecom': float(request.form.get('9m_telecom', 0)),
                '10m_telecom': float(request.form.get('10m_telecom', 0)),
                '12m_telecom': float(request.form.get('12m_telecom', 0)),
                'telecom_poles': float(request.form.get('telecom_poles', 0)),
                'stubs': float(request.form.get('stubs', 0))
            }

            # Check appropriate stock table based on delivery type
            if delivery_for == 'client':
                client_id = request.form.get('client_id')
                current_stock = check_stock_balance('total_clients_treated_poles', client_id)
                if not current_stock:
                    flash('No client stock record found for today', 'danger')
                    return redirect(url_for('stock.delivery_notess'))
            else:
                current_stock = check_stock_balance('total_kdl_treated_poles')
                if not current_stock:
                    flash('No KDL stock record found for today', 'danger') 
                    return redirect(url_for('stock.delivery_notess'))

            # Check if requested quantities exceed available stock
            for col in ['fencing_poles', 'timber', 'rafters', '7m', '8m', '9m', '10m', '11m', '12m', 
                       '14m', '16m', '9m_telecom', '10m_telecom', '12m_telecom', 'telecom_poles', 'stubs']:
                requested = float(request.form.get(col) or 0)
                available = float(current_stock.get(col) or 0)
                if requested > available:
                    flash(f'Insufficient stock for {col}. Available: {available}, Requested: {requested}', 'danger')
                    return redirect(url_for('stock.delivery_notess'))            # Continue with existing delivery note creation code
            delivery_data = {
                'note_number': request.form.get('note_number'),
                'date': request.form.get('date'),
                'vehicle_number': request.form.get('vehicle_number'),
                'transporter': request.form.get('transporter'),
                'loaded_by': request.form.get('loaded_by'),
                'destination': request.form.get('destination'),
                'delivery_for': delivery_for,
                'notes': request.form.get('notes'),
                **requested_quantities
            }

            # Conditionally include client_id or customers_id
            if delivery_for == 'client':
                delivery_data['client_id'] = (request.form.get('client_id'))
                # Validate client_id
                client_exists = supabase.table('clients').select('id').eq('id', delivery_data['client_id']).execute()
                if not client_exists.data:
                    flash('Invalid client ID.', 'danger')
                    return redirect(url_for('inventory.delivery_note'))
            elif delivery_for == 'customer':
                delivery_data['customers_id'] = (request.form.get('customers_id'))
                # Validate customers_id
                customer_exists = supabase.table('customers').select('id').eq('id', delivery_data['customers_id']).execute()
                if not customer_exists.data:
                    flash('Invalid customer ID.', 'danger')
                    return redirect(url_for('inventory.delivery_note'))

            # Save delivery note
            result = supabase.table('delivery_notes').insert(delivery_data).execute()

            # Update stock based on delivery_for
            columns = ['fencing_poles', 'timber', 'rafters', '7m', '8m', '9m', '10m', '11m', '12m', 
                    '14m', '16m', '9m_telecom', '10m_telecom', '12m_telecom', 'telecom_poles', 'stubs']
            
            if request.form.get('delivery_for') == 'client':
                table = 'total_clients_treated_poles'
                today = datetime.now().date().isoformat()
                client_id = request.form.get('client_id')
                
                # Get current total stock for client
                current_stock = supabase.table(table).select('*')\
                    .eq('client_id', client_id)\
                    .eq('date', today)\
                    .execute()
                
                if current_stock.data:
                    stock_id = current_stock.data[0]['id']
                    updates = {}
                    
                    for col in columns:
                        if request.form.get(col):
                            new_value = float(current_stock.data[0].get(col, 0)) - float(request.form.get(col, 0))
                            updates[col] = max(0, new_value)  # Ensure stock doesn't go negative
                    
                    if updates:
                        supabase.table(table).update(updates).eq('id', stock_id).execute()
                else:
                    flash('No stock record found for client on this date', 'danger')
                    return redirect(url_for('stock.delivery_notess'))
            else:
                table = 'total_kdl_treated_poles'
                today = datetime.now().date().isoformat()
                
                # Get current KDL total stock
                current_stock = supabase.table(table).select('*')\
                    .eq('date', today)\
                    .execute()
                
                if current_stock.data:
                    stock_id = current_stock.data[0]['id']
                    updates = {}
                    
                    for col in columns:
                        if request.form.get(col):
                            new_value = float(current_stock.data[0].get(col, 0)) - float(request.form.get(col, 0))
                            updates[col] = max(0, new_value)  # Ensure stock doesn't go negative
                    
                    if updates:
                        supabase.table(table).update(updates).eq('id', stock_id).execute()
                else:
                    flash('No stock record found for KDL on this date', 'danger')
                    return redirect(url_for('stock.delivery_notess'))

            flash('Delivery note created successfully', 'success')
        except Exception as e:
            flash(f'Error processing delivery: {str(e)}', 'danger')
            return redirect(url_for('stock.delivery_notess'))

    # GET request handling
    delivery_notes = supabase.table('delivery_notes').select('*').execute()
    return render_template('stock/delivery_note.html', 
                         notes=delivery_notes.data,
                         clients=clients.data, 
                         customers=customers.data)

@stock.route('/delivery_note/<int:note_id>')
def view_delivery_note(note_id):
    try:
        # Fetch the delivery note
        note = supabase.table('delivery_notes').select('*').eq('id', note_id).single().execute().data
        
        if not note:
            flash('Delivery note not found', 'danger')
            return redirect(url_for('stock.delivery_note'))
        
        # Get client/customer details if they exist
        client = None
        customer = None
        if note.get('client_id'):
            client = supabase.table('clients').select('*').eq('id', note['client_id']).single().execute().data
        elif note.get('customers_id'):
            customer = supabase.table('customers').select('*').eq('id', note['customers_id']).single().execute().data
        
        return render_template('stock/view_delivery_note.html', note=note, client=client, customer=customer)
        
    except Exception as e:
        flash(f'Error retrieving delivery note: {str(e)}', 'danger')
        return redirect(url_for('stock.delivery_note'))

@stock.route('/print_delivery_note/<int:note_id>')
def print_delivery_note(note_id):
    try:
        # Fetch the delivery note
        note = supabase.table('delivery_notes').select('*').eq('id', note_id).single().execute()
        if not note.data:
            flash('Delivery note not found', 'danger')
            return redirect(url_for('stock.delivery_notess'))

        # Get client/customer details if they exist
        client = None
        customer = None
        if note.data.get('client_id'):
            client = supabase.table('clients').select('*').eq('id', note.data['client_id']).single().execute().data
        elif note.data.get('customers_id'):
            customer = supabase.table('customers').select('*').eq('id', note.data['customers_id']).single().execute().data

        return render_template('stock/print_delivery_note.html', 
                            note=note.data, 
                            client=client, 
                            customer=customer)
        
    except Exception as e:
        flash(f'Error retrieving delivery note: {str(e)}', 'danger')
        return redirect(url_for('stock.delivery_note'))
