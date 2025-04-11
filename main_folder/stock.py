from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from dotenv import load_dotenv
import os
from supabase import create_client, Client

from datetime import datetime





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
        suppliers = supabase.table('suppliers').select("*").execute().data
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




@stock.route('/stock_movement', methods=['GET', 'POST'])
def stock_movement():
    if request.method == 'POST':
        try:
            # Capture form data
            from_client_id = request.form.get('from_client_id')
            to_client_id = request.form.get('to_client_id')
            
            # Handle KDL logic: If KDL is involved, set client_id to None
            from_client_id = None if request.form.get('from_kdl') == 'true' else from_client_id
            to_client_id = None if request.form.get('to_kdl') == 'true' else to_client_id

            # Movement details
            data = {
                'from_client_id': from_client_id,
                'to_client_id': to_client_id,
                'from_kdl': request.form.get('from_kdl') == 'true',
                'to_kdl': request.form.get('to_kdl') == 'true',
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
                'treated': request.form.get('treated') == 'true',
                'notes': request.form.get('notes')
            }

            # Insert stock movement into the database
            response = supabase.table('stock_movements').insert(data).execute()
            
            if response.data:
                # Adjust stock quantities based on the movement details
                adjust_stock_quantities(data)

                flash('Stock movement recorded and stock adjusted successfully', 'success')
            else:
                flash('Failed to record stock movement', 'danger')

        except Exception as e:
            flash(f'Error recording stock movement: {str(e)}', 'danger')

        return redirect(url_for('stock.stock_movement'))

    try:
        # Fetch movements and clients from Supabase
        movements = supabase.table('stock_movements').select("*").order('movement_date', desc=True).execute().data
        clients = supabase.table('clients').select("*").execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        movements = []
        clients = []

    return render_template('stock/stock_movements.html', 
                            movements=movements,
                            clients=clients)


def adjust_stock_quantities(movement_data):
    """Helper function to adjust stock quantities based on movement data"""
    stock_fields = [
        'fencing_poles', 'timber', 'rafters', '7m', '8m', 
        '9m', '10m', '11m', '12m', '14m', '16m'
    ]
    
    # 1. Handle stock movement from Client to KDL
    if movement_data.get('from_client_id') and movement_data.get('to_kdl'):
        # Reduce stock from the client
        update_client_stock(movement_data['from_client_id'], stock_fields, movement_data, is_incoming=False)
        print(f"Moving stock from client ID: {movement_data['from_client_id']} to KDL")
        
        # Increase stock at KDL
        update_kdl_stock(stock_fields, movement_data, is_incoming=True)

    # 2. Handle stock movement from KDL to Client
    if movement_data.get('from_kdl') and movement_data.get('to_client_id'):
        print(f"Moving stock from KDL to client ID: {movement_data['to_client_id']}")
        # Reduce stock from KDL
        update_kdl_stock(stock_fields, movement_data, is_incoming=False)
        
        # Increase stock at the client
        update_client_stock(movement_data['to_client_id'], stock_fields, movement_data, is_incoming=True)

    # 3. Handle stock movement between two clients
    if movement_data.get('from_client_id') and movement_data.get('to_client_id'):
        # Reduce stock from the source client
        update_client_stock(movement_data['from_client_id'], stock_fields, movement_data, is_incoming=False)
        
        # Increase stock at the destination client
        update_client_stock(movement_data['to_client_id'], stock_fields, movement_data, is_incoming=True)

def update_client_stock(client_id, stock_fields, movement_data, is_incoming):
    """Helper function to update the stock for a client"""
    stock_table = 'client_untreated_stock'
    stock_action = lambda x, y: x + y if is_incoming else max(x - y, 0)

    print(f"Attempting to update client stock for client_id: {client_id}")

    try:
        # Fetch the client stock data
        client_stock = supabase.table(stock_table).select("*").eq('client_id', client_id).execute().data
        
        if client_stock is None:
            print(f"Error: No data returned when fetching client stock for client_id: {client_id}")
        else:
            print(f"Fetched client stock for client {client_id}: {client_stock}")
        
        if client_stock:
            updated_stock = {field: stock_action(client_stock[0].get(field, 0), movement_data.get(field, 0)) for field in stock_fields}
            print(f"Updated stock for client {client_id}: {updated_stock}")
            
            # Apply the update
            result = supabase.table(stock_table).update(updated_stock).eq('client_id', client_id).execute()
            print(f"Update result for client stock: {result}")
            
            if result.error:
                print(f"Error updating client stock: {result.error}")
            else:
                print(f"Client stock updated successfully for client_id: {client_id}")
        else:
            print(f"Error: No client stock found for client_id {client_id}.")
    
    except Exception as e:
        print(f"An error occurred while updating client stock: {e}")

def update_kdl_stock(stock_fields, movement_data, is_incoming):
    """Helper function to update the KDL stock"""
    stock_table = 'kdl_untreated_stock'
    print(f"Updating KDL stock with data: {movement_data}")
    stock_action = lambda x, y: x + y if is_incoming else max(x - y, 0)

    # Fetch the KDL stock before attempting to update
    kdl_stock = supabase.table(stock_table).select("*").execute().data
    print(f"Fetched KDL stock data: {kdl_stock}")

    if kdl_stock:
        updated_stock = {field: stock_action(kdl_stock[0].get(field, 0), movement_data.get(field, 0)) for field in stock_fields}
        print(f"Updated KDL stock: {updated_stock}")
        
        # Ensure the WHERE clause is applied correctly using the id
        result = supabase.table(stock_table).update(updated_stock).eq('id', kdl_stock[0]['id']).execute()  # Use 'id' for the WHERE clause
        print(f"Update result: {result}")
        if result.error:
            print(f"Error updating KDL stock: {result.error}")
    else:
        print(f"No stock found for KDL.")




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
