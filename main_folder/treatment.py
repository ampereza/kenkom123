from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint 
from dotenv import load_dotenv
import os
from supabase import create_client
from datetime import datetime


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



@treatment.route('/add_treatment', methods=['GET', 'POST'])
def add_treatment():
    if request.method == 'POST':
        try:
            # Get all form data
            data = {
                'cylinder_no': request.form['cylinder_no'],
                'liters_added': request.form['liters_added'],
                'kegs_added': int(request.form['kegs_added']),
                'kegs_remaining': int(request.form['kegs_remaining']),
                'chemical_strength': float(request.form['chemical_strength']),
                'treatment_purpose': request.form['treatment_purpose'],
                'telecom_poles': int(request.form.get('telecom_poles', 0)),
                'timber': int(request.form.get('timber', 0)),
                'rafters': int(request.form.get('rafters', 0)),
                '7m': int(request.form.get('7m', 0)),
                '8m': int(request.form.get('8m', 0)),
                '9m': int(request.form.get('9m', 0)),
                '10m': int(request.form.get('10m', 0)),
                '11m': int(request.form.get('11m', 0)),
                '12m': int(request.form.get('12m', 0)),
                '14m': int(request.form.get('14m', 0)),
                '16m': int(request.form.get('16m', 0)),
                'fencing_poles': float(request.form.get('fencing_poles', 0)),
                'client_id': int(request.form['client_id']),
                'initial_vacuum_start': request.form.get('initial_vacuum_start'),
                'initial_vacuum_end': request.form.get('initial_vacuum_end'),
                'final_vacuum_start': request.form.get('final_vacuum_start'),
                'final_vacuum_end': request.form.get('final_vacuum_end')
            }

            # Calculate total poles
            pole_fields = ['telecom_poles', 'timber', 'rafters', '7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']
            data['total_poles'] = sum(data[field] for field in pole_fields if data.get(field))

            # Insert into database
            result = supabase.table('treatment_log').insert(data).execute()
            print("Insert result:", result)

            flash('Treatment log added successfully!', 'success')
            return redirect(url_for('treatment.treatment_dashboard'))

        except Exception as e:
            flash(f'Error adding treatment log: {str(e)}', 'danger')
            return redirect(url_for('treatment.add_treatment'))

    # GET request - fetch clients for dropdown
    clients = supabase.table('clients').select('id', 'name').execute()
    return render_template('treatment/add_treatment.html', clients=clients.data)