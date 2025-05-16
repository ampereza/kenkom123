from flask import render_template, Blueprint
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import os


daily_reports = Blueprint('daily_reports', __name__)


# Load environment variables and initialize Supabase client
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


@daily_reports.route('/daily_report')
def daily_report():
    try:
        current_date = datetime.now().date()
        start_of_day = current_date.isoformat()
        
        # Fetch daily sales
        sales_response = supabase.table('sales').select('*, customer_name').gte('created_at', start_of_day).execute()
        daily_sales = sales_response.data if sales_response else []
        total_sales = sum(float(sale.get('total_amount', 0)) for sale in daily_sales)

        # Fetch daily purchases
        purchases_response = supabase.table('purchases').select('*').gte('created_at', start_of_day).execute()
        daily_purchases = purchases_response.data if purchases_response else []
        total_purchases = sum(float(purchase.get('total_amount', 0)) for purchase in daily_purchases)

        # Fetch daily expenses
        expenses_response = supabase.table('expenses').select('*').eq('date', start_of_day).execute()
        daily_expenses = expenses_response.data if expenses_response else []
        total_expenses = sum(float(expense.get('amount', 0)) for expense in daily_expenses)

        # Fetch daily receipts
        receipts_response = supabase.table('receipts').select('*').eq('date', start_of_day).execute()
        daily_receipts = receipts_response.data if receipts_response else []
        total_receipts = sum(float(receipt.get('amount', 0)) for receipt in daily_receipts)

        # Fetch daily stock movements
        stock_movements = supabase.table('stock_movement').select('*').eq('movement_date', start_of_day).execute()
        
        # Fetch daily worker records
        worker_records = supabase.table('daily_work').select('*, cusual_workers(first_name, last_name)').eq('date', start_of_day).execute()

        # Fetch stock summary for the day
        treated_response = supabase.table('kdl_treated_poles').select('*').gte('date', start_of_day).execute()
        untreated_response = supabase.table('kdl_untreated_stock').select('*').gte('date', start_of_day).execute()
        rejects_response = supabase.table('rejects').select('*').gte('date', start_of_day).execute()

        treated_total = sum(sum(float(item.get(size, 0)) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) for item in treated_response.data) if treated_response.data else 0
        untreated_total = sum(sum(float(item.get(size, 0)) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) for item in untreated_response.data) if untreated_response.data else 0
        rejects_total = sum(float(item.get('quantity', 0)) for item in rejects_response.data) if rejects_response.data else 0

        daily_totals = {
            'sales': total_sales,
            'purchases': total_purchases,
            'expenses': total_expenses,
            'receipts': total_receipts
        }

        daily_stock = {
            'treated_total': treated_total,
            'untreated_total': untreated_total,
            'rejects': rejects_total
        }

        daily_activities = {
            'sales': daily_sales,
            'stock_movements': stock_movements.data if stock_movements else [],
            'worker_records': worker_records.data if worker_records else []
        }

        return render_template('dashboard/daily_report.html',
                             current_date=current_date.strftime('%Y-%m-%d'),
                             daily_totals=daily_totals,
                             daily_stock=daily_stock,
                             daily_activities=daily_activities)
    
    except Exception as e:
        print(f"Error generating daily report: {str(e)}")
        return render_template('dashboard/daily_report.html',
                             current_date=datetime.now().date().strftime('%Y-%m-%d'),
                             daily_totals={'sales': 0, 'purchases': 0, 'expenses': 0, 'receipts': 0},
                             daily_stock={'treated_total': 0, 'untreated_total': 0, 'rejects': 0},
                             daily_activities={'sales': [], 'stock_movements': [], 'worker_records': []})
