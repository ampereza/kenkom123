# This __init__.py file marks this directory as a Python package
from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")    

    from main_folder import accounting
    from main_folder import dashboard
    from main_folder import stock
    from main_folder import treatment
    from main_folder import auth
    from main_folder import sales




    app.register_blueprint(accounting.accounting)
    app.register_blueprint(dashboard.dashboard)
    app.register_blueprint(stock.stock)
    app.register_blueprint(treatment.treatment)
    app.register_blueprint(auth.auth)
    app.register_blueprint(sales.sales)


    return app

