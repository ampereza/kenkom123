import time
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import requests
import html
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash

smtp = Blueprint('smtp', __name__)

# Ensure Supabase credentials are correctly set
SUPABASE_URL = "https://wkrqxttzwuvemjfhlqao.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndrcnF4dHR6d3V2ZW1qZmhscWFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk0NDEwNzQsImV4cCI6MjA1NTAxNzA3NH0.JSN5TS2h2tdcK1hW84bqm8zoytYrlmbBgS2yp9CeiNM"

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials. Check .env file.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SMS API endpoint
url_sms = "https://www.egosms.co/api/v1/plain/"

# Function to send SMS
def send_sms(client_telephone, treatment_details):
    # Ensure the telephone number is a string
    client_telephone = str(client_telephone)

    message = "Treatment Completed: "
    for column, value in treatment_details.items():
        if value and value > 0:  # Include only non-null, positive values
            message += f"{column} = {value}, "
    message = message.rstrip(", ")  # Remove trailing comma

    parameters = {
        'username': html.escape("beampereza"),
        'password': html.escape("xKgWUPwD@QAs5"),
        'number': html.escape(client_telephone),
        'message': html.escape(message),
        'sender': html.escape("Egosms")
    }

    try:
        r = requests.get(url=url_sms, params=parameters, timeout=5)
        print(f"SMS sent successfully: {r.text}")
    except (requests.ConnectionError, requests.Timeout):
        print("Error: Check your internet connection")
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")

# Monitor `clients_treated_poles` table
def monitor_treated_poles():
    last_checked_timestamp = None  # Track last processed timestamp

    print("Starting SMS Monitoring Service...")

    while True:
        query = supabase.table("clients_treated_poles") \
            .select('*') \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()

        if query.data:
            latest_entry = query.data[0]

            # Check if this entry is already processed
            if last_checked_timestamp == latest_entry['created_at']:
                time.sleep(60)  # Wait before checking again
                continue

            client_id = latest_entry['client_id']

            # Fetch client telephone number
            client_response = supabase.table("clients").select("telephone").eq("id", client_id).single().execute()
            client_data = client_response.data  # Fixing the `SingleAPIResponse` issue

            if not client_data:
                print(f"Client with ID {client_id} not found.")
                continue

            client_telephone = client_data.get('telephone')
            print(f"Client telephone number: {client_telephone}")

            # Ensure client telephone is valid
            if client_telephone is None:
                print(f"No telephone number found for client ID {client_id}. Skipping SMS.")
                continue

            # Prepare treatment details
            treatment_details = {key: latest_entry[key] for key in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m', 'telecom_poles', 'rafters', 'timber', 'fencing_poles'] if key in latest_entry and latest_entry[key] is not None}
            print(f"Treatment details for client {client_id}: {treatment_details}")

            # Send SMS
            send_sms(client_telephone, treatment_details)
            print(f"SMS sent to {client_telephone} for treatment details: {treatment_details}")

            # Update last processed timestamp
            last_checked_timestamp = latest_entry['created_at']

        # Sleep before checking again
        time.sleep(1)

