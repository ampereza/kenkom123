from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask, make_response
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import pdfkit  # Ensure you have installed pdfkit and wkhtmltopdf

# Configure pdfkit with the path to wkhtmltopdf
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')  # Update this path if necessary

reports = Blueprint('reports', __name__)

load_dotenv

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
secret_key = os.getenv('SECRET_KEY')

supabase = create_client(supabase_url, supabase_key)


@reports.route('/kdl_reports')
def kdl_reports():
    return render_template('dashboard/reports.html')


@reports.route('/income_statement')
def income_statement():
    # Get current date and calculate time periods
    current_date = datetime.now()
    
    # Define time periods
    periods = {
        'daily': current_date.date(),
        'weekly': current_date - timedelta(days=7),
        'monthly': current_date.replace(day=1),
        'annually': current_date.replace(month=1, day=1)
    }
    
    statements = {}
    
    for period_name, period_start in periods.items():
        # Fetch data for each category
        sales = supabase.table('sales').select('total_amount').gte('date', period_start).execute()
        receipts = supabase.table('receipts').select('amount').gte('date', period_start).execute()
        payment_vouchers = supabase.table('payment_vouchers').select('total_amount').gte('date', period_start).execute()
        expenses = supabase.table('expenses').select('amount').gte('date', period_start).execute()
        salaries = supabase.table('salary_payments').select('amount').gte('date', period_start).execute()
        purchases = supabase.table('purchases').select('total_amount').gte('date', period_start).execute()
        
        # Calculate totals
        total_sales = sum(item['total_amount'] for item in sales.data)
        total_receipts = sum(item['amount'] for item in receipts.data)
        total_payment_vouchers = sum(item['total_amount'] for item in payment_vouchers.data)
        total_expenses = sum(item['amount'] for item in expenses.data)
        total_salaries = sum(item['amount'] for item in salaries.data)
        total_purchases = sum(item['amount'] for item in purchases.data)
        
        total_revenue = total_sales + total_receipts
        total_expenses = total_payment_vouchers + total_expenses + total_salaries + total_purchases
        net_income = total_revenue - total_expenses
        
        statements[period_name] = {
            'revenue': {
                'sales': total_sales,
                'receipts': total_receipts,
                'total': total_revenue
            },
            'expenses': {
                'payment_vouchers': total_payment_vouchers,
                'purchases': total_purchases,
                'expenses': total_expenses,
                'salaries': total_salaries,
                'total': total_expenses
            },
            'net_income': net_income
        }
    
    return render_template('dashboard/income_statement.html', statements=statements)


@reports.route('/export_income_statement_pdf')
def export_income_statement_pdf():
    # Render a minimal template for the income statement
    current_date = datetime.now()
    
    periods = {
        'daily': current_date.date(),
        'weekly': current_date - timedelta(days=7),
        'monthly': current_date.replace(day=1),
        'annually': current_date.replace(month=1, day=1)
    }
    
    statements = {}
    
    for period_name, period_start in periods.items():
        # Fetch data for each category
        sales = supabase.table('sales').select('total_amount').gte('date', period_start).execute()
        receipts = supabase.table('receipts').select('amount').gte('date', period_start).execute()
        payment_vouchers = supabase.table('payment_vouchers').select('total_amount').gte('date', period_start).execute()
        expenses = supabase.table('expenses').select('amount').gte('date', period_start).execute()
        salaries = supabase.table('salary_payments').select('amount').gte('date', period_start).execute()
        purchases = supabase.table('purchases').select('total_amount').gte('date', period_start).execute()
        
        # Calculate totals
        total_sales = sum(item['total_amount'] for item in sales.data)
        total_receipts = sum(item['amount'] for item in receipts.data)
        total_payment_vouchers = sum(item['total_amount'] for item in payment_vouchers.data)
        total_expenses = sum(item['amount'] for item in expenses.data)
        total_salaries = sum(item['amount'] for item in salaries.data)
        total_purchases = sum(item['amount'] for item in purchases.data)
        
        total_revenue = total_sales + total_receipts
        total_expenses = total_payment_vouchers + total_expenses + total_salaries + total_purchases
        net_income = total_revenue - total_expenses
        
        statements[period_name] = {
            'revenue': {
                'sales': total_sales,
                'receipts': total_receipts,
                'total': total_revenue
            },
            'expenses': {
                'payment_vouchers': total_payment_vouchers,
                'purchases': total_purchases,
                'expenses': total_expenses,
                'salaries': total_salaries,
                'total': total_expenses
            },
            'net_income': net_income
        }
    
    rendered_html = render_template('dashboard/income_statement_pdf.html', statements=statements)
    
    # Generate PDF from the rendered HTML
    pdf = pdfkit.from_string(rendered_html, False, configuration=pdfkit_config)
    
    # Create a response with the PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=income_statement.pdf'
    return response


@reports.route('/stock_report')
def stock_report():
    current_date = datetime.now()
    
    periods = {
        'daily': current_date.date(),
        'weekly': current_date - timedelta(days=7),
        'monthly': current_date.replace(day=1),
        'annually': current_date.replace(month=1, day=1)
    }
    
    stock_data = {}
    
    for period_name, period_start in periods.items():
        # Fetch data from each table
        client_untreated = supabase.table('client_untreated_stock').select('*').gte('date', period_start).execute()
        client_treated = supabase.table('clients_treated_poles').select('*').gte('date', period_start).execute()
        kdl_treated = supabase.table('kdl_treated_poles').select('*').gte('date', period_start).execute()
        kdl_untreated = supabase.table('kdl_untreated_stock').select('*').gte('date', period_start).execute()
        kdl_unsorted = supabase.table('kdl_unsorted_stock').select('*').gte('date', period_start).execute()
        
        # Calculate totals for each category
        stock_data[period_name] = {
            'client_untreated': {
                'total_poles': sum(sum(float(item.get(size) or 0) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']) for item in client_untreated.data),
                'rafters': sum(float(item.get('rafters') or 0) for item in client_untreated.data),
                'timber': sum(float(item.get('timber') or 0) for item in client_untreated.data),
                'fencing': sum(float(item.get('fencing_poles') or 0) for item in client_untreated.data),
                'telecom': sum(float(item.get('telecom_poles') or 0) for item in client_untreated.data)
            },
            'client_treated': {
                'total_poles': sum(sum(float(item.get(size) or 0) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']) for item in client_treated.data),
                'rafters': sum(float(item.get('rafters') or 0) for item in client_treated.data),
                'timber': sum(float(item.get('timber') or 0) for item in client_treated.data),
                'fencing': sum(float(item.get('fencing_poles') or 0) for item in client_treated.data),
                'telecom': sum(float(item.get('telecom_poles') or 0) for item in client_treated.data)
            },
            'kdl_treated': {
                'total_poles': sum(sum(float(item.get(size) or 0) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']) for item in kdl_treated.data),
                'rafters': sum(float(item.get('rafters') or 0) for item in kdl_treated.data),
                'timber': sum(float(item.get('timber') or 0) for item in kdl_treated.data),
                'fencing': sum(float(item.get('fencing_poles') or 0) for item in kdl_treated.data),
                'telecom': sum(float(item.get('telecom_poles') or 0) for item in kdl_treated.data)
            },
            'kdl_untreated': {
                'total_poles': sum(sum(float(item.get(size) or 0) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']) for item in kdl_untreated.data),
                'rafters': sum(float(item.get('rafters') or 0) for item in kdl_untreated.data),
                'timber': sum(float(item.get('timber') or 0) for item in kdl_untreated.data),
                'fencing': sum(float(item.get('fencing_poles') or 0) for item in kdl_untreated.data),
                'telecom': sum(float(item.get('telecom_poles') or 0) for item in kdl_untreated.data)
            },
            'kdl_unsorted': {
                'total': sum(float(item.get('quantity') or 0) for item in kdl_unsorted.data)
            }
        }
    
    return render_template('dashboard/stock_report.html', stock_data=stock_data)


@reports.route('/rejects_report')
def rejects_report():
    current_date = datetime.now()
    
    periods = {
        'daily': current_date.date(),
        'weekly': current_date - timedelta(days=7),
        'monthly': current_date.replace(day=1),
        'annually': current_date.replace(month=1, day=1)
    }
    
    rejects_data = {}
    
    for period_name, period_start in periods.items():
        rejects = supabase.table('rejects').select('*').gte('date', period_start).execute()
        
        rejects_data[period_name] = {
            'total_poles': sum(sum(float(item.get(size) or 0) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']) for item in rejects.data),
            'rafters': sum(float(item.get('rafters') or 0) for item in rejects.data),
            'timber': sum(float(item.get('timber') or 0) for item in rejects.data),
            'fencing': sum(float(item.get('fencing_poles') or 0) for item in rejects.data),
            'telecom': sum(float(item.get('telecom_poles') or 0) for item in rejects.data),
            'stabs': sum(float(item.get('stabs') or 0) for item in rejects.data)
        }
    
    return render_template('stock/rejects.html', rejects_data=rejects_data)