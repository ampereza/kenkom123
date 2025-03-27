from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, session
from functools import wraps
from dotenv import load_dotenv
from supabase import create_client, Client
import random
from datetime import datetime, timedelta
import smtplib
import os
import logging

auth = Blueprint('auth', __name__, template_folder='../templates/auth')

# Load environment variables
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Role-to-Dashboard Mapping
ROLE_TO_DASHBOARD = {
    "Accountant": "accounting.accountant_dashboard",
    "Manager": "dashboard.maindashboard",
    "Stock Manager": "stock.stock_dashboard",
    "Treatment Manager": "treatment.treatment_dashboard",
    "Developer": "dashboard.maindashboard"
}

def send_otp(email):
    otp = f"{random.randint(100000, 999999)}"  # Generate a 6-digit OTP
    otp_expiry = datetime.utcnow() + timedelta(minutes=10)  # Set expiry time

    # Update OTP and expiry in Supabase
    response = supabase.table("users").update({"otp": otp, "otp_expiry": otp_expiry.isoformat()}).eq("email", email).execute()

    if response.status_code != 200:
        logging.error("Failed to update OTP in the database")
        return False

    # Send OTP email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = f"Subject: Your OTP Code\n\nYour OTP code is {otp}. It is valid for 10 minutes."
            server.sendmail(EMAIL_ADDRESS, email, message)
        logging.info("OTP sent successfully to %s", email)
        return True
    except Exception as e:
        logging.error("Failed to send OTP: %s", e)
        return False

@auth.route("/requestotp", methods=["GET", "POST"])
def request_otp():
    if request.method == "POST":
        email = request.form.get("email")
        response = supabase.table("users").select("id").eq("email", email).execute()
        if response.data:
            if send_otp(email):
                session["email"] = email
                return redirect(url_for("auth.verify_otp"))
            flash("Failed to send OTP!", "danger")
        else:
            flash("Email not found!", "danger")
    return render_template("auth/request_otp.html")

@auth.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if "email" not in session:
        return redirect(url_for("auth.request_otp"))

    if request.method == "POST":
        entered_otp = request.form.get("otp")
        email = session["email"]

        # Fetch user data
        response = supabase.table("users").select("otp, otp_expiry, role").eq("email", email).execute()
        if response.data:
            user_data = response.data[0]
            if user_data["otp"] == entered_otp and datetime.fromisoformat(user_data["otp_expiry"]) >= datetime.utcnow():
                # Clear OTP
                supabase.table("users").update({"otp": None, "otp_expiry": None}).eq("email", email).execute()

                # Redirect based on role
                role = user_data["role"]
                dashboard = ROLE_TO_DASHBOARD.get(role)
                if dashboard:
                    return redirect(url_for(dashboard))
                flash("Role not recognized!", "warning")
            else:
                flash("Invalid or expired OTP!", "danger")
        else:
            flash("User not found!", "danger")
    return render_template("auth/verify_otp.html")
