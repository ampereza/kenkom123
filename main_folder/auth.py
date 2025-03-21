from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='../templates/auth')


#templates for this blueprint are in the folder templates/auth

#routes for this blueprint
#login
#logout
#index

@auth.route('/login')
def login():
    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    return render_template('auth/logout.html')

@auth.route('/')
def index():
    return render_template('auth/index.html')
