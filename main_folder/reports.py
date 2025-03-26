from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask
from dotenv import load_dotenv
from supabase import create_client, Client
import os

reports = Blueprint('reports', __name__)

load_dotenv

supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
secret_key = os.getenv('SECRET_KEY')

supabase = create_client(supabase_url, supabase_key)



#create an income statement
@reports.route('/income_statement')
def income_statement():
    #calculate total sales
    #calculate total expenses
    # Connect to Supabase

    # Daily sales
    daily_sales = supabase.table('sales').select('total_amount').execute()
    daily_total = sum(row['total_amount'] for row in daily_sales.data)

    # Weekly sales
    weekly_sales = supabase.table('sales').select('total_amount').execute()
    weekly_total = sum(row['total_amount'] for row in weekly_sales.data)

    # Monthly sales
    monthly_sales = supabase.table('sales').select('total_amount').execute()
    monthly_total = sum(row['total_amount'] for row in monthly_sales.data)

    # Annual sales
    annual_sales = supabase.table('sales').select('total_amount').execute()
    annual_total = sum(row['total_amount'] for row in annual_sales.data)

    # Daily purchases
    daily_purchases = supabase.table('purchases').select('total_amount').execute()
    daily_purchase_total = sum(row['total_amount'] for row in daily_purchases.data)

    # Weekly purchases
    weekly_purchases = supabase.table('purchases').select('total_amount').execute()
    weekly_purchase_total = sum(row['total_amount'] for row in weekly_purchases.data)

    # Monthly purchases
    monthly_purchases = supabase.table('purchases').select('total_amount').execute()
    monthly_purchase_total = sum(row['total_amount'] for row in monthly_purchases.data)

    # Annual purchases
    annual_purchases = supabase.table('purchases').select('total_amount').execute()
    annual_purchase_total = sum(row['total_amount'] for row in annual_purchases.data)






































    return render_template('dashboard/income_statement.html', daily_total=daily_total, weekly_total=weekly_total, monthly_total=monthly_total, annual_total=annual_total, daily_purchase_total=daily_purchase_total, weekly_purchase_total=weekly_purchase_total, monthly_purchase_total=monthly_purchase_total, annual_purchase_total=annual_purchase_total)