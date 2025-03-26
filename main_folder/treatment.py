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


@treatment.route('/add_treatment', methods=['POST', 'GET'])
def add_treatment():
    try:
        # Fetch clients for both GET and POST methods
        try:
            result = supabase.table('clients').select('*').execute()
            print(result)
        except Exception as e:
            flash(f"Error fetching clients: {str(e)}", "danger")
            result = None
        clients = result.data if result else []

        if request.method == 'POST':
            # Get form data
            treatment_purpose = request.form.get('treatment_purpose')
            treatment_for = request.form.get('treatment_for')
            client_id = request.form.get('client_id')
            date = request.form.get('date')
            cylinder_no = request.form.get('cylinderNo')
            liters_added = request.form.get('litersAdded')
            kegs_added = request.form.get('kegsAdded')
            kegs_remaining = request.form.get('kegsRemaining')
            chemical_strength = request.form.get('strength')
            # Use current date and time if date is not provided
            if not date:
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                date = date.replace("T", " ")

            # Treatment item categories
            rafters = int(request.form.get('rafters', 0))
            timber = int(request.form.get('timber', 0))
            fencing_poles = int(request.form.get('fencing_poles', 0))
            poles_7m = int(request.form.get('7m', 0))
            poles_8m = int(request.form.get('8m', 0))
            telecom_poles = int(request.form.get('telecomPoles', 0))
            poles_9m = int(request.form.get('9m', 0))
            poles_10m = int(request.form.get('10m', 0))
            poles_11m = int(request.form.get('11m', 0))
            poles_12m = int(request.form.get('12m', 0))
            poles_14m = int(request.form.get('14m', 0))
            poles_16m = int(request.form.get('16m', 0))
            total_poles = rafters + timber + fencing_poles + poles_7m + poles_8m + telecom_poles + poles_9m + poles_10m + poles_11m + poles_12m + poles_14m + poles_16m


            # Save to treatment_log table
            treatment_log_data = {
                "treatment_for": treatment_for,
                "treatment_purpose": treatment_purpose,
                "client_id": client_id,
                "date": date,
                "cylinder_no": cylinder_no,
                "liters_added": liters_added,
                "kegs_added": kegs_added,
                "kegs_remaining": kegs_remaining,
                "chemical_strength": chemical_strength,
                "rafters": rafters,
                "timber": timber,
                "fencing_poles": fencing_poles,
                "7m": poles_7m,
                "8m": poles_8m,
                "telecom_poles": telecom_poles,
                "9m": poles_9m,
                "10m": poles_10m,
                "11m": poles_11m,
                "12m": poles_12m,
                "14m": poles_14m,
                "16m": poles_16m,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_poles": total_poles
            }
            supabase.table("treatment_log").insert(treatment_log_data).execute()

            # Update KDL or Client treated poles table
            target_table = "kdl_treated_poles" if treatment_purpose == "kenkom" else "clients_treated_poles"
            print ("Target Table: ", target_table)
            update_data = {
                "date": date,
                "rafters": rafters,
                "timber": timber,
                "fencing_poles": fencing_poles,
                "7m": poles_7m,
                "8m": poles_8m,
                "telecom_poles": telecom_poles,
                "9m": poles_9m,
                "10m": poles_10m,
                "11m": poles_11m,
                "12m": poles_12m,
                "14m": poles_14m,
                "16m": poles_16m,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            if treatment_purpose != "kenkom":
                update_data["client_id"] = client_id
            supabase.table(target_table).upsert(update_data, on_conflict=["date"]).execute()
            print("Treatment data saved successfully!")

            flash("Treatment record added successfully!", "success")
            return redirect(url_for("treatment.add_treatment"))

    except Exception as e:
        print(e)
        flash(f"Error adding treatment: {str(e)}", "danger")

    # Render the template with clients
    return render_template('treatment/add_treatment.html', clients=clients)
