# This __init__.py file marks this directory as a Python package
from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask



def create_app():
    app = Flask(__name__)

    from main_folder import accounting
    from main_folder import dashboard
    from main_folder import stock
    from main_folder import treatment
    from main_folder import auth




    app.register_blueprint(accounting.accounting)
    app.register_blueprint(dashboard.dashboard)
    app.register_blueprint(stock.stock)
    app.register_blueprint(treatment.treatment)
    app.register_blueprint(auth.auth)


    return app

