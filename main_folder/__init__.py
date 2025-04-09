# This __init__.py file marks this directory as a Python package
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize globally
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'error'


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    from main_folder import accounting, dashboard, stock, treatment, auth, reports, smtp, teset  # <== your modules
    from main_folder.auth import load_user  # <== your loader from auth

    # Register blueprints
    app.register_blueprint(accounting.accounting)
    app.register_blueprint(dashboard.dashboard)
    app.register_blueprint(stock.stock)
    app.register_blueprint(treatment.treatment)
    app.register_blueprint(auth.auth)
    app.register_blueprint(reports.reports)
    app.register_blueprint(smtp.smtp)
    app.register_blueprint(teset.teset)

    # Init login manager
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(user_id):
        return load_user(user_id)

    return app


