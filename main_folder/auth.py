from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from flask_login import LoginManager
from flask import Flask, session
from flask_login import UserMixin


# Load environment variables
load_dotenv()

# Initialize Flask Blueprint
auth = Blueprint("auth", __name__)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@auth.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required", "error")
            return redirect(url_for("auth.login"))

        try:
            # Attempt to sign in user with Supabase
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not response or "error" in response:
                flash("Invalid email or password", "error")
                print(response)
                return redirect(url_for("auth.login"))

            # Fetch user role from profiles table
            user_id = response.user.id
            role_query = supabase.table("profiles").select("role").eq("id", user_id).single()
            role_response = role_query.execute()

            if not role_response.data:
                flash("Unable to fetch user role", "error")
                print(role_response)
                return redirect(url_for("auth.login"))

            role = role_response.data["role"]

            # Store user session
            session["user"] = user_id
            session["role"] = role

            # Redirect based on role
            if role == "developer":
                return redirect(url_for("dashboard.maindashboard"))
            elif role == "admin":
                return redirect(url_for("dashboard.maindashboard"))
            elif role == "accountant":
                return redirect(url_for("accounting.accounting_dashboard"))
            elif role == "stock_manager":
                return redirect(url_for("stock.stock_dashboard"))
            elif role == "treatment":
                return redirect(url_for("treatment.treatment_dashboard"))
            else:
                flash("Invalid role", "error")
                return redirect(url_for("auth.login"))

        except Exception as e:
            flash("Invalid credentials", "error")
            print(f"Login error: {str(e)}")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "success")
    return redirect(url_for("auth.login"))




class User(UserMixin):
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f'<User {self.username}>'

# Initialize LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'error'

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        if user_data.data:
            user_info = user_data.data
            # Create a User object and return it
            return User(
                id=user_info['id'],
                username=user_info['username'],
                email=user_info['email'],
                role=user_info['role']
            )
        return None
    except Exception as e:
        print(f"Error loading user: {str(e)}")
        return None
