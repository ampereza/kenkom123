from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask, make_response
from dotenv import load_dotenv
from supabase import create_client, Client

import os
from datetime import datetime, timedelta
import pdfkit  # Ensure you have installed pdfkit and wkhtmltopdf

reports = Blueprint('reports', __name__)

load_dotenv()

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
        sales = supabase.table('sales').select('total_amount').gte('created_at', period_start).execute()
        print(f"Sales data for {period_name}: {sales.data}")
        
        receipts = supabase.table('receipts').select('amount').gte('date', period_start).execute()
        payment_vouchers = supabase.table('payment_vouchers').select('total_amount').gte('date', period_start).execute()
        expenses = supabase.table('expenses').select('amount').gte('date', period_start).execute()
        salaries = supabase.table('salary_payments').select('amount').gte('date', period_start).execute()
        purchases = supabase.table('purchases').select('total_amount').gte('date', period_start).execute()
        
        # Calculate totals
        total_sales = sum(item['total_amount'] for item in sales.data)
        print(f"Total Sales for {period_name}: {total_sales}")
        total_receipts = sum(item['amount'] for item in receipts.data)
        total_payment_vouchers = sum(item['total_amount'] for item in payment_vouchers.data)
        total_expenses = sum(item['amount'] for item in expenses.data)
        total_salaries = sum(item['amount'] for item in salaries.data)
        total_purchases = sum(item['amount'] for item in purchases.data)
        
        total_revenue = total_sales + total_receipts
        print(f"Total Revenue for {period_name}: {total_revenue}")
        total_expenses = total_payment_vouchers + total_expenses + total_salaries + total_purchases
        print(f"Total Expenses for {period_name}: {total_expenses}")
        net_income = total_revenue - total_expenses
        print(f"Net Income for {period_name}: {net_income}")
        
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
    
    return render_template('dashboard/Income_statement.html', statements=statements)


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
    pdf = pdfkit.from_string(rendered_html, False)
    
    # Create a response with the PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=income_statement.pdf'
    return response


@reports.route('/stock_report')
def stock_report():
    try:
        # Get current data from the tables
        treated_response = supabase.table('kdl_treated_poles').select('*').execute()
        untreated_response = supabase.table('kdl_to_treat').select('*').execute()
        
        treated_data = treated_response.data if treated_response else []
        untreated_data = untreated_response.data if untreated_response else []
        
        # Calculate totals for treated poles
        treated_total = sum(sum(float(item.get(size) or 0) for size in 
            ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) 
            for item in treated_data)
        
        # Calculate totals for untreated poles
        untreated_total = sum(sum(float(item.get(size) or 0) for size in 
            ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) 
            for item in untreated_data)
        
        # Create summaries
        treated_summary = {
            'treated_total': treated_total,
            'treated_data': treated_data
        }
        
        untreated_summary = {
            'untreated_total': untreated_total,
            'untreated_data': untreated_data
        }

        return render_template('reports/stock_report.html',
                            current_date=datetime.now().strftime('%Y-%m-%d'),
                            treated_summary=treated_summary,
                            untreated_summary=untreated_summary)
    
    except Exception as e:
        print(f"Error generating stock report: {str(e)}")
        return render_template('reports/stock_report.html',
                            current_date=datetime.now().strftime('%Y-%m-%d'),
                            treated_summary={'treated_total': 0, 'treated_data': []},
                            untreated_summary={'untreated_total': 0, 'untreated_data': []})


@reports.route('/rejects_report')
def rejects_report():
    # Get rejects data and join with suppliers table
    rejects = supabase.table('rejects').select('*, suppliers(name)').execute()
    
    # First calculate totals
    rejects_data = {
        'total_poles': sum(sum(float(item.get(size) or 0) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']) for item in rejects.data),
        'rafters': sum(float(item.get('rafters') or 0) for item in rejects.data),
        'timber': sum(float(item.get('timber') or 0) for item in rejects.data),
        'fencing': sum(float(item.get('fencing_poles') or 0) for item in rejects.data),
        'telecom': sum(
            float(item.get('telecom') or 0) +  # general telecom poles
            float(item.get('9m_telecom') or 0) +  # 9m telecom poles
            float(item.get('10m_telecom') or 0) +  # 10m telecom poles
            float(item.get('12m_telecom') or 0)  # 12m telecom poles
            for item in rejects.data
        ),
        'stabs': sum(float(item.get('stabs') or 0) for item in rejects.data)
    }    # Group rejects by supplier
    supplier_rejects = {}
    for item in rejects.data:
        if item.get('supplier_id'):
            supplier_name = item['suppliers']['name'] if item.get('suppliers') else f"Supplier {item['supplier_id']}"
            if supplier_name not in supplier_rejects:
                supplier_rejects[supplier_name] = 0
            
            # Add to supplier's total quantity
            supplier_rejects[supplier_name] += float(item.get('quantity') or 0)
    
    # Get rejects by pole size where value > 0
    poles_rejects = {}
    pole_sizes = ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m']
    for size in pole_sizes:
        total = sum(float(item.get(size) or 0) for item in rejects.data)
        if total > 0:
            poles_rejects[size] = total
    
    return render_template('reports/rejects.html', 
                         rejects_data=rejects_data, 
                         supplier_rejects=supplier_rejects,
                         poles_rejects=poles_rejects)



