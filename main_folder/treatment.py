from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint 
from dotenv import load_dotenv
import os
from supabase import create_client


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
    return render_template('treatment/treatment_log.html')


@treatment.route('/treatment_plan')
def treatment_plan():
    return render_template('treatment/treatment_plan.html')


@treatment.route('/add_treatment', methods=['POST', 'GET'])
def add_treatment():
    try:
        # Fetch clients for both GET and POST methods
        result = supabase.table('clients').select('*').execute()
        clients = result.data if result else []

        if request.method == 'POST':
            # Get form data
            treatment_for = request.form.get('treatmentFor')
            client_id = request.form.get('client_id')
            date = request.form.get('date')
            cylinder_no = request.form.get('cylinderNo')
            liters_added = request.form.get('litersAdded')
            kegs_added = request.form.get('kegsAdded')
            kegs_remaining = request.form.get('kegsRemaining')
            strength = request.form.get('strength')

            # Treatment item categories
            rafters = int(request.form.get('rafters', 0))
            timber = int(request.form.get('timber', 0))
            fencing_poles = int(request.form.get('fencingPoles', 0))
            poles_7m = int(request.form.get('poles7m', 0))
            poles_8m = int(request.form.get('poles8m', 0))
            telecom_poles = int(request.form.get('telecomPoles', 0))
            poles_9m = int(request.form.get('poles9m', 0))
            poles_10m = int(request.form.get('poles10m', 0))
            poles_11m = int(request.form.get('poles11m', 0))
            poles_12m = int(request.form.get('poles12m', 0))
            poles_14m = int(request.form.get('poles14m', 0))
            poles_16m = int(request.form.get('poles16m', 0))

            # Save to treatment_log table
            treatment_log_data = {
                "treatment_for": treatment_for,
                "client_id": client_id,
                "date": date,
                "cylinder_no": cylinder_no,
                "liters_added": liters_added,
                "kegs_added": kegs_added,
                "kegs_remaining": kegs_remaining,
                "strength": strength,
                "rafters": rafters,
                "timber": timber,
                "fencing_poles": fencing_poles,
                "poles_7m": poles_7m,
                "poles_8m": poles_8m,
                "telecom_poles": telecom_poles,
                "poles_9m": poles_9m,
                "poles_10m": poles_10m,
                "poles_11m": poles_11m,
                "poles_12m": poles_12m,
                "poles_14m": poles_14m,
                "poles_16m": poles_16m,
            }
            supabase.table("treatment_log").insert(treatment_log_data).execute()

            # Update KDL or Client treated poles table
            target_table = "kdl_treated_poles" if treatment_for == "KDL" else "clients_treated_poles"
            update_data = {
                "rafters": rafters,
                "timber": timber,
                "fencing_poles": fencing_poles,
                "poles_7m": poles_7m,
                "poles_8m": poles_8m,
                "telecom_poles": telecom_poles,
                "poles_9m": poles_9m,
                "poles_10m": poles_10m,
                "poles_11m": poles_11m,
                "poles_12m": poles_12m,
                "poles_14m": poles_14m,
                "poles_16m": poles_16m,
            }
            supabase.table(target_table).upsert(update_data, on_conflict=["date"]).execute()

            flash("Treatment record added successfully!", "success")
            return redirect('/add_treatment')

    except Exception as e:
        flash(f"Error adding treatment: {str(e)}", "danger")

    # Render the template with clients
    return render_template('treatment/add_treatment.html', clients=clients)
