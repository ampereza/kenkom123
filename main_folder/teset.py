from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import Dict, Union
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime

# Initialize Flask Blueprint
teset = Blueprint('teset', __name__)

# Load environment variables
load_dotenv()

# Validate and load Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise EnvironmentError("Supabase credentials are not properly set in the environment variables.")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)


@teset.route("/search_by_date", methods=["GET"])
def search_by_date():
    # Search for info from the database
    date = request.form.get("date")
    
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    # Validate date format (e.g., YYYY-MM-DD)
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    try:
        # Query the database for the given date
        response = supabase.from_("sales").select("*").eq("date", date).execute()
        data = response.data
        
        # Debugging output
        print("Query Response:", data)
        
        if not data:
            return jsonify({"message": "No records found for the given date"}), 404
        
        # Render results in a template
        return jsonify({"message": "Records found", "data": data}), 200  # Changed to JSON response for consistency
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"error": "An error occurred while fetching data.", "details": str(e)}), 500
