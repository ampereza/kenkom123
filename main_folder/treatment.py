from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint 
from dotenv import load_dotenv
import os
from supabase import create_client
from datetime import datetime
import uuid  # Add this import for UUID generation


treatment = Blueprint('treatment', __name__)



#routes for this blueprint
#treatment_dashboard
#treatment_report
#treatment_log

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
SECRET_KEY = os.getenv("SECRET_KEY")



@treatment.route('/treatment_dashboard')
def treatment_dashboard():
    try:
        # Fetch all records from treatment_log table with ordered by date
        result = supabase.table('treatment_log').select('*').order('date', desc=True).execute()
        treatments = result.data if result else []
        
        # Also fetch client names for reference
        clients_result = supabase.table('clients').select('*').execute()
        clients = {client['id']: client['name'] for client in clients_result.data} if clients_result else {}

        # Calculate total poles treated and average strength
        total_poles_treated = sum(treatment['total_poles'] for treatment in treatments) if treatments else 0
        
        # Calculate average chemical strength
        average_strength = (
            sum(treatment['chemical_strength'] for treatment in treatments) / len(treatments)
            if treatments else 0
        )
        
        print("Total poles treated:", total_poles_treated)
        print("Average chemical strength:", average_strength)
        
        # Debug prints
        print("Number of treatments found:", len(treatments))
        print("First treatment record:", treatments[0] if treatments else "No treatments")
        
        # Return template with treatments and clients
        return render_template('treatment/treatment_dashboard.html', treatments=treatments, clients=clients, total_poles_treated=total_poles_treated, average_strength=average_strength)
    except Exception as e:
        flash(f"Error fetching treatment logs: {str(e)}", "danger")
        print("Error in treatment_dashboard:", e)
        return render_template('treatment/treatment_dashboard.html', treatments=[], clients={}, total_poles_treated=total_poles_treated, average_strength=average_strength)

@treatment.route('/treatment_plan')
def treatment_plan():
    return render_template('treatment/treatment_plan.html')


def validate_data(data):
    """Validate the input data."""
    for key, value in data.items():
        if value is None or (isinstance(value, (int, float)) and value < 0):
            flash(f"Invalid value for {key}: {value}", "danger")
            print(f"Validation error: {key} has invalid value {value}")
            return False
    return True

def calculate_total_poles(data, pole_fields):
    """Calculate the total poles."""
    return sum(data[field] for field in pole_fields if data.get(field))

def update_stock(data, pole_fields, stock_table, treated_table, stock_key):
    """Update stock and treated poles."""
    # Ensure the stock_key exists in the data
    if stock_key not in data or not data[stock_key]:
        flash(f"Error: Missing or invalid {stock_key} in data", "danger")
        print(f"Error: Missing or invalid {stock_key} in data: {data}")
        return False

    stock = supabase.table(stock_table).select("*").eq(stock_key, data[stock_key]).execute().data
    if not stock or any(stock[0].get(field, 0) < data.get(field, 0) for field in pole_fields if data.get(field, 0) > 0):
        flash(f"Error: Insufficient stock for {data[stock_key]}", "danger")
        return False

    # Reduce untreated stock
    updated_untreated_stock = {field: stock[0].get(field, 0) - data.get(field, 0) for field in pole_fields}
    supabase.table(stock_table).update(updated_untreated_stock).eq(stock_key, stock[0][stock_key]).execute()

    # Update treated poles
    treated_poles = supabase.table(treated_table).select("*").eq(stock_key, data[stock_key]).execute().data
    if treated_poles:
        updated_treated_poles = {field: treated_poles[0].get(field, 0) + data.get(field, 0) for field in pole_fields}
        supabase.table(treated_table).update(updated_treated_poles).eq(stock_key, data[stock_key]).execute()
    else:
        new_treated_poles = {field: data.get(field, 0) for field in pole_fields}
        new_treated_poles[stock_key] = data[stock_key]
        supabase.table(treated_table).insert(new_treated_poles).execute()
    return True

@treatment.route('/add_treatment', methods=['GET', 'POST'])
def add_treatment():
    if request.method == 'POST':
        try:
            # Get all form data
            data = {
                'cylinder_no': request.form['cylinder_no'],
                'liters_added': int(request.form.get('liters_added', 0)),
                'kegs_added': int(request.form.get('kegs_added', 0)),
                'kegs_remaining': int(request.form.get('kegs_remaining', 0)),
                'chemical_strength': float(request.form.get('chemical_strength', 0.0)),
                'treatment_purpose': request.form['treatment_purpose'],
                # Add all pole fields with proper defaults
                'telecom_poles': int(request.form.get('telecom_poles', 0)),
                'timber': int(request.form.get('timber', 0)),
                'rafters': int(request.form.get('rafters', 0)),
                '7m': int(request.form.get('7', 0)),
                '8m': int(request.form.get('8', 0)),
                '9m': int(request.form.get('9', 0)),
                '9m_telecom': int(request.form.get('9m_teleco', 0)),
                '10m_telecom': int(request.form.get('10m_teleco', 0)),
                '10m': int(request.form.get('10', 0)),
                '11m': int(request.form.get('11', 0)),
                '12m': int(request.form.get('12', 0)),
                '12m_telecom': int(request.form.get('12m_teleco', 0)),
                '14m': int(request.form.get('14', 0)),
                '16m': int(request.form.get('16', 0)),
                'fencing_poles': float(request.form.get('fencing_poles', 0.0)),
                'initial_vacuum': request.form.get('initial_vacuum'),
                'flooding': request.form.get('flooding'),
                'pressure': request.form.get('pressure'),
                'final_vacuum': request.form.get('final_vacuum'),
                'client_id': int(request.form.get('client_id', 0)) if request.form.get('client_id') else None,
                'date': datetime.now().strftime('%Y-%m-%d')  # Add current date
            }

            # Log the data for debugging
            print("Data being inserted into treatment_log:", data)

            # Validate data
            if not validate_data(data):
                return redirect(url_for('treatment.add_treatment'))

            # Calculate total poles
            pole_fields = ['telecom_poles', 'timber', 'rafters', '7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m', 'fencing_poles', '9m_telecom', '10m_telecom', '12m_telecom']
            data['total_poles'] = calculate_total_poles(data, pole_fields)

            # Check stock based on treatment purpose
            untreated_stock = []  # Initialize untreated_stock here
            if data['treatment_purpose'] == 'client':
                untreated_stock = supabase.table('client_to_treat').select('*').eq('client_id', data['client_id']).execute().data
                
                # Validate client stock
                if not untreated_stock:
                    flash("Error: No untreated stock found for this client.", "danger")
                    return redirect(url_for('treatment.add_treatment'))
                
                # Validate sufficient stock for each pole field
                for field in pole_fields:
                    if data.get(field, 0) > untreated_stock[0].get(field, 0):
                        flash(f"Error: Insufficient stock for {field}.", "danger")
                        return redirect(url_for('treatment.add_treatment'))
                        
                # Update client stock
                if not update_stock(data, pole_fields, 'client_to_treat', 'clients_treated_poles', 'client_id'):
                    return redirect(url_for('treatment.add_treatment'))
                    
            elif data['treatment_purpose'] == 'kdl':
                # KDL stock handling
                # Get KDL stock data
                kdl_result = supabase.table('kdl_to_treat').select('*').execute()
                if not kdl_result.data:
                    flash("Error: No records found in KDL to treat table", "danger")
                    return redirect(url_for('treatment.add_treatment'))
                
                kdl_totals = kdl_result.data[0]  # Get first row
                
                # Map the form fields to database columns (remove 'total_' prefix)
                pole_fields_mapping = {
                    'telecom_poles': 'telecom_poles',
                    'timber': 'timber',
                    'rafters': 'rafters',
                    '7m': '7m',
                    '8m': '8m',
                    '9m': '9m',
                    '9m_telecom': '9m_telecom',
                    '10m_telecom': '10m_telecom',
                    '10m': '10m',
                    '11m': '11m',
                    '12m': '12m',
                    '12m_telecom': '12m_telecom',
                    '14m': '14m',
                    '16m': '16m',
                    'fencing_poles': 'fencing_poles'
                }
                
                # Create update data without the 'total_' prefix
                update_data = {}
                for form_field, db_field in pole_fields_mapping.items():
                    current_total = kdl_totals.get(db_field, 0) or 0  # Handle None values
                    requested = data.get(form_field, 0) or 0
                    if requested > current_total:
                        flash(f"Error: Insufficient stock for {form_field}. Available: {current_total}, Requested: {requested}", "danger")
                        return redirect(url_for('treatment.add_treatment'))
                    update_data[db_field] = current_total - requested
                
                try:
                    # Update kdl_to_treat table
                    supabase.table('kdl_to_treat').update(update_data).eq('id', kdl_totals['id']).execute()
                    
                    # Update treated poles
                    treated_data = {field: data.get(source_field, 0) for source_field, field in pole_fields_mapping.items()}
                    treated_data['id'] = kdl_totals['id']
                    
                    treated_result = supabase.table('kdl_treated_poles').select('*').eq('id', kdl_totals['id']).execute()
                    if treated_result.data:
                        # Update existing treated poles record
                        update_treated = {
                            field: (treated_result.data[0].get(field, 0) or 0) + (data.get(source_field, 0) or 0)
                            for source_field, field in pole_fields_mapping.items()
                        }
                        supabase.table('kdl_treated_poles').update(update_treated).eq('id', kdl_totals['id']).execute()
                    else:
                        # Insert new treated poles record
                        supabase.table('kdl_treated_poles').insert(treated_data).execute()
                except Exception as e:
                    flash(f"Error updating KDL stock: {str(e)}", "danger")
                    print(f"Error updating KDL stock: {str(e)}")  # Debug log
                    return redirect(url_for('treatment.add_treatment'))
            else:
                flash("Error: Invalid treatment purpose.", "danger")
                return redirect(url_for('treatment.add_treatment'))

            # Insert into treatment_log
            treatment_log_data = {key: value for key, value in data.items() if key != 'id'}
            supabase.table('treatment_log').insert(treatment_log_data).execute()
            flash('Treatment log added successfully!', 'success')
            return redirect(url_for('treatment.treatment_dashboard'))

        except Exception as e:
            print(f"Error adding treatment log: {str(e)}")
            return redirect(url_for('treatment.add_treatment'))

    # GET request - fetch clients for dropdown
    clients = supabase.table('clients').select('id', 'name').execute()
    return render_template('treatment/add_treatment.html', clients=clients.data)



@treatment.route('/pre_treatment', methods=['GET', 'POST'])
def add_pre_treatment():
    if request.method == 'POST':
        try:
            data = {
                'date': request.form['date'],
                'pile_owner': int(request.form['pile_owner']),
                'size': request.form['size'],
                'age': float(request.form['age']),
                'cracks': request.form['cracks'],
                'knots': request.form['knots'],
                'mc': float(request.form['mc']),
                'top_diameter': request.form['top_diameter'],
                'bottom_diameter': request.form['bottom_diameter'],
                'number': float(request.form['number']),
                'remarks': request.form['remarks']
            }
            result = supabase.table('pre_treatment').insert(data).execute()
            flash('Pre-treatment record added successfully!', 'success')
            return redirect(url_for('treatment.add_pre_treatment'))
        except Exception as e:
            flash(f'Error adding pre-treatment record: {str(e)}', 'danger')
    
    # Fetch pre-treatment records from the database
    pre_treatment_records = supabase.table('pre_treatment').select('*').execute().data
    return render_template('treatment/pre_treatment.html', pre_treatment_records=pre_treatment_records)

@treatment.route('/edit_pre_treatment/<int:id>', methods=['GET', 'POST'])
def edit_pre_treatment(id):
    if request.method == 'POST':
        try:
            data = {
                'date': request.form['date'],
                'pile_owner': int(request.form['pile_owner']),
                'size': request.form['size'],
                'age': float(request.form['age']),
                'mc': float(request.form['mc']),
                'top_diameter': request.form['top_diameter'],
                'bottom_diameter': request.form['bottom_diameter'],
                'number': float(request.form['number']),
                'remarks': request.form['remarks']
            }
            supabase.table('pre_treatment').update(data).eq('id', id).execute()
            flash('Pre-treatment record updated successfully!', 'success')
            return redirect(url_for('treatment.pre_treatment'))
        except Exception as e:
            flash(f'Error updating pre-treatment record: {str(e)}', 'danger')
    
    record = supabase.table('pre_treatment').select('*').eq('id', id).execute()
    return render_template('treatment/pre_treatment.html', record=record.data[0])

@treatment.route('/delete_pre_treatment/<int:id>')
def delete_pre_treatment(id):
    try:
        supabase.table('pre_treatment').delete().eq('id', id).execute()
        flash('Pre-treatment record deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting pre-treatment record: {str(e)}', 'danger')
    return redirect(url_for('treatment.pre_treatment'))



@treatment.route('/post_treatment', methods=['GET', 'POST'])
def add_post_treatment():
    if request.method == 'POST':
        try:
            data = {
                'diameter_dimensions': float(request.form['diameter_dimensions']) if request.form['diameter_dimensions'] else None,
                'pole_sample': request.form['pole_sample'],
                'penetration': float(request.form['penetration']) if request.form['penetration'] else None,
                'retention': float(request.form['retention']) if request.form['retention'] else None,
                'midpoint': float(request.form['midpoint']) if request.form['midpoint'] else None,
                'cantilever': float(request.form['cantilever']) if request.form['cantilever'] else None,
                'date': request.form['date'],
                'treatment_id': request.form['treatment_id']
            }
            result = supabase.table('post_treatment').insert(data).execute()
            flash('Post-treatment record added successfully!', 'success')
            return redirect(url_for('treatment.treatment_dashboard'))
        except Exception as e:
            flash(f'Error adding post-treatment record: {str(e)}', 'danger')

    treatments = supabase.table('treatment_log').select('*').execute()
    return render_template('treatment/post_treatment.html', treatments=treatments.data)

@treatment.route('/edit_post_treatment/<int:id>', methods=['GET', 'POST'])
def edit_post_treatment(id):
    if request.method == 'POST':
        try:
            data = {
                'diameter_dimensions': float(request.form['diameter_dimensions']) if request.form['diameter_dimensions'] else None,
                'pole_sample': request.form['pole_sample'],
                'penetration': float(request.form['penetration']) if request.form['penetration'] else None,
                'retention': float(request.form['retention']) if request.form['retention'] else None,
                'midpoint': float(request.form['midpoint']) if request.form['midpoint'] else None,
                'cantilever': float(request.form['cantilever']) if request.form['cantilever'] else None,
                'date': request.form['date'],
                'treatment_id': request.form['treatment_id']
            }
            supabase.table('post_treatment').update(data).eq('id', id).execute()
            flash('Post-treatment record updated successfully!', 'success')
            return redirect(url_for('treatment.treatment_dashboard'))
        except Exception as e:
            flash(f'Error updating post-treatment record: {str(e)}', 'danger')
    
    record = supabase.table('post_treatment').select('*').eq('id', id).execute()
    treatments = supabase.table('treatment_log').select('*').execute()
    return render_template('treatment/post_treatment.html', record=record.data[0], treatments=treatments.data)

@treatment.route('/delete_post_treatment/<int:id>')
def delete_post_treatment(id):
    try:
        supabase.table('post_treatment').delete().eq('id', id).execute()
        flash('Post-treatment record deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting post-treatment record: {str(e)}', 'danger')
    return redirect(url_for('treatment.treatment_dashboard'))





from datetime import datetime

@treatment.route('/get_treatment_logs')
def get_treatment_logs():
    try:
        # Fetch all records from treatment_log table with ordered by date
        result = supabase.table('treatment_log').select('*').order('date', desc=True).execute()
        treatments = result.data if result else []

        # Also fetch client names for reference
        clients_result = supabase.table('clients').select('*').execute()
        clients = {client['id']: client['name'] for client in clients_result.data} if clients_result else {}

        # Calculate total poles treated and average strength
        total_poles_treated = sum(treatment['total_poles'] for treatment in treatments) if treatments else 0
        
        # Calculate average chemical strength
        average_strength = (
            sum(treatment['chemical_strength'] for treatment in treatments) / len(treatments)
            if treatments else 0
        )
        
        print("Total poles treated:", total_poles_treated)
        print("Average chemical strength:", average_strength)
        
        # Debug prints
        print("Number of treatments found:", len(treatments))
        print("First treatment record:", treatments[0] if treatments else "No treatments")
        
        # Return template with treatments and clients
        return render_template('treatment/treatment_logs.html', treatments=treatments, clients=clients, total_poles_treated=total_poles_treated, average_strength=average_strength)
    except Exception as e:
        print("Error in treatment_dashboard:", e)
        return render_template('treatment/treatment_logs.html', treatments=[], clients={}, total_poles_treated=total_poles_treated, average_strength=average_strength)


@treatment.route('/treatment_view')
def treatment_view():
    try:
        treatment_id = request.args.get('treatment_id')
        print(f"Fetching treatment with ID: {treatment_id}")  # Debug log
        
        if not treatment_id:
            flash("Error: Treatment ID is required.", "danger")
            return redirect(url_for('treatment.get_treatment_logs'))

        # Fetch the treatment log by ID
        treatment_log = supabase.table('treatment_log').select('*').eq('id', treatment_id).execute()
        print(f"Treatment log result: {treatment_log.data}")  # Debug log
        
        if not treatment_log.data:
            flash("Error: Treatment log not found.", "danger")
            return redirect(url_for('treatment.get_treatment_logs'))

        # Fetch client data if client_id exists
        client = None
        if treatment_log.data[0].get('client_id'):
            client_result = supabase.table('clients').select('*').eq('id', treatment_log.data[0]['client_id']).execute()
            client = client_result.data[0] if client_result.data else None

        # Fetch the post-treatment record by treatment ID
        post_treatment = supabase.table('post_treatment').select('*').eq('treatment_id', treatment_id).execute()

        return render_template('treatment/treatment_view.html', 
                            treatment=treatment_log.data[0], 
                            post_treatment=post_treatment.data,
                            client=client)
    except Exception as e:
        print(f"Error in treatment_view: {str(e)}")  # Debug log
        flash(f"Error fetching treatment details: {str(e)}", "danger")
        return redirect(url_for('treatment.get_treatment_logs'))