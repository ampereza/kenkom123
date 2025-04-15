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


@stock.route('/stock_dashboard')
def stock_dashboard():
    return render_template('stock/stock_dashboard.html')

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
        # Retrieve and validate form data
        pole_status = request.form.get('pole_status')
        quantity = request.form.get('quantity')
        description = request.form.get('description')

        # Check for missing fields
        missing_fields = []
        if not pole_status:
            missing_fields.append('Pole Type')
        if not quantity:
            missing_fields.append('Quantity')
        if not description:
            missing_fields.append('Description')

        if missing_fields:
            flash(f'Missing fields: {", ".join(missing_fields)}', 'danger')
            return redirect(url_for('stock.delivery'))
        
        return render_template('stock/delivery.html')
    


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
        untreated_stock = supabase.table('kdl_untreated_stock').select("*").order('created_at', desc=True).execute().data
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
        untreated_stock = supabase.table('client_untreated_stock').select("*").execute().data

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
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)), 
                '12m': float(request.form.get('12m', 0)),
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
            flash(f'Error saving data: {str(e)}', 'danger')
            return redirect(url_for('stock.add_clients_current_stock'))

    # Fetch clients for the form
    try:
        clients = supabase.table('clients').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching clients: {str(e)}', 'danger')
        clients = []

    return render_template('stock/add_clients_current_stock.html', clients=clients)\



@stock.route('/delivery_notes', methods=['GET', 'POST'])
def delivery_notes():
    if request.method == 'POST':
        try:
            data = {
                'deliver_form': request.form.get('deliver_for'),  
                'note_number': request.form.get('note_number'),
                'client_id': request.form.get('client_id'),
                'vehicle_number': request.form.get('vehicle_number'),
                'transporter': request.form.get('transporter'),
                'total_quantity': int(request.form.get('total_quantity', 0)),
                'loaded_by': request.form.get('loaded_by'),
                'loaded_at': datetime.utcnow().isoformat(),
                'driver_sign': request.form.get('driver_sign') == 'true',
                'received_by': request.form.get('received_by'),
                'notes': request.form.get('notes'),
                'customers_id': request.form.get('customers_id'),
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
                'destination': request.form.get('destination')
            }

            response = supabase.table('delivery_notes').insert(data).execute()
            if response:
                print(response)
                flash('Delivery note created successfully', 'success')
            else:
                flash('Failed to create delivery note', 'danger')

        except Exception as e:
            print(e)
            flash(f'Error creating delivery note: {str(e)}', 'danger')
        return redirect(url_for('stock.delivery_notes'))

    # GET request - fetch existing delivery notes and related data
    try:
        delivery_notes = supabase.table('delivery_notes').select("*").order('created_at', desc=True).execute().data
        clients = supabase.table('clients').select("*").execute().data
        customers = supabase.table('customers').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(e)
        delivery_notes = []
        clients = []
        customers = []

    return render_template('stock/delivery_note.html', 
                            delivery_notes=delivery_notes,
                            clients=clients,
                            customers=customers)








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
                '10m': float(request.form.get('10m', 0)),
                '11m': float(request.form.get('11m', 0)),
                '12m': float(request.form.get('12m', 0)),
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
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        unsorted_stock = []
        suppliers = []

    return render_template('stock/add_unsorted_poles.html', 
                            unsorted_stock=unsorted_stock,
                            suppliers=suppliers)


@stock.route('/add_clients_unsorted_stock', methods=['GET', 'POST'])
def add_clients_unsorted_stock():
    if request.method == 'POST':
        try:
            data = {
                'client_id': request.form.get('client_id'),
                'pole_type': request.form.get('pole_type'),
                'quantity': float(request.form.get('quantity', 0))
            }

            response = supabase.table('client_unsorted').insert(data).execute()
            if response.data:
                flash('Client unsorted stock added successfully', 'success')
            else:
                flash('Failed to add unsorted stock record', 'danger')

        except Exception as e:
            flash(f'Error creating unsorted stock record: {str(e)}', 'danger')
            print(e)
        return redirect(url_for('stock.add_clients_unsorted_stock'))

    try:
        unsorted_stock = supabase.table('client_unsorted').select("*").order('created_at', desc=True).execute().data
        clients = supabase.table('clients').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(e)    
        unsorted_stock = []
        clients = []

    return render_template('stock/add_clients_unsorted_stock.html',
                            unsorted_stock=unsorted_stock,
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
                print(response.data)
            else:
                flash('Failed to create gate pass', 'danger')
                print(response.error)

        except Exception as e:
            flash(f'Error creating gate pass: {str(e)}', 'danger')
        return redirect(url_for('stock.get_pass'))

    try:
        passes = supabase.table('get_pass_in').select("*").order('created_at', desc=True).execute().data
        print(passes)
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(e)
        passes = []

    return render_template('stock/get_pass.html', passes=passes)




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

            response3 = supabase.table('kdl_treated_poles').update({
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
