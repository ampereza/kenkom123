from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint 

treatment = Blueprint('treatment', __name__)

#routes for this blueprint
#treatment_dashboard
#treatment_report
#treatment_log
#treatment_plan

@treatment.route('/treatment_dashboard')
def treatment_dashboard():
    return render_template('treatment/treatment_dashboard.html')

@treatment.route('/treatment_report')
def treatment_report():
    return render_template('treatment/treatment_report.html')


@treatment.route('/treatment_log')
def treatment_log():
    return render_template('treatment/treatment_log.html')

@treatment.route('/treatment_plan')
def treatment_plan():
    return render_template('treatment/treatment_plan.html')


