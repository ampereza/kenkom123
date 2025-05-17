from flask import render_template, Blueprint
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client
import os

# Load environment variables and initialize Supabase client
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing required environment variables SUPABASE_URL or SUPABASE_KEY")

daily_reports = Blueprint('daily_reports', __name__)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@daily_reports.route('/daily_reports')
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


@daily_reports.route('/cashflow')
def cashflow():
    try:
        current_date = datetime.now().date()
        start_of_day = current_date.isoformat()
        
        # Fetch daily sales
        sales_response = supabase.table('sales').select('*, customer_name').gte('created_at', start_of_day).execute()
        daily_sales = sales_response.data if sales_response else []
        total_sales = sum(float(sale.get('total_amount', 0)) for sale in daily_sales)
        print(f"Total sales: {total_sales}")
        print(f"Daily sales: {daily_sales}")    

        # Fetch daily purchases
        purchases_response = supabase.table('purchases').select('*').gte('created_at', start_of_day).execute()
        daily_purchases = purchases_response.data if purchases_response else [] 
        total_purchases = sum(float(purchase.get('total_amount', 0)) for purchase in daily_purchases)
        print(f"Total purchases: {total_purchases}")
        print(f"Daily purchases: {daily_purchases}")

        # Fetch daily expenses
        expenses_response = supabase.table('expenses').select('*').eq('date', start_of_day).execute()
        daily_expenses = expenses_response.data if expenses_response else []
        total_expenses = sum(float(expense.get('amount', 0)) for expense in daily_expenses)
        print(f"Total expenses: {total_expenses}")
        print(f"Daily expenses: {daily_expenses}")
        # Fetch daily receipts
        receipts_response = supabase.table('receipts').select('*').eq('date', start_of_day).execute()
        daily_receipts = receipts_response.data if receipts_response else []
        total_receipts = sum(float(receipt.get('amount', 0)) for receipt in daily_receipts)
        print(f"Total receipts: {total_receipts}")
        print(f"Daily receipts: {daily_receipts}")

        daily_net_cashflow = {
            'sales': total_sales,
            'purchases': total_purchases,
            'expenses': total_expenses,
            'receipts': total_receipts
        }

        total_daily_net_cashflow = total_sales - (total_purchases + total_expenses - total_receipts)



        return render_template('reports/cashflow.html',
                             current_date=current_date.strftime('%Y-%m-%d'),
                             total_sales=total_sales,
                             daily_sales=daily_sales,
                             daily_purchases=daily_purchases,
                             daily_expenses=daily_expenses,
                             daily_receipts=daily_receipts,
                             daily_net_cashflow=daily_net_cashflow,
                             total_daily_net_cashflow=total_daily_net_cashflow)
    

    except Exception as e:
        print(f"Error generating daily report: {str(e)}")
        return render_template('reports/cashflow.html',
                             current_date=datetime.now().date().strftime('%Y-%m-%d'),
                             daily_sales=[],
                             daily_purchases=[],
                             daily_expenses=[],
                             daily_receipts=[],
                             daily_net_cashflow={'sales': 0, 'purchases': 0, 'expenses': 0, 'receipts': 0},
                             total_daily_net_cashflow=0)


@daily_reports.route('/treatment_report')
def treatment_report():
    current_date = datetime.now().date()  # Move outside try block
    try:
        start_of_day = current_date.isoformat()

        # Fetch daily treated poles
        treated_response = supabase.table('treatment_log').select('*').gte('date', start_of_day).execute()
        
        treated_data = treated_response.data if treated_response else []
        treated_total = sum(sum(float(item.get(size, 0)) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) for item in treated_data) if treated_data else 0
        treated_summary = {
            'treated_total': treated_total,
            'treated_data': treated_data
        }
        print(f"Treated data: {treated_data}")
        # Fetch daily untreated poles

        return render_template('reports/treatment_report.html',
                                current_date=current_date.strftime('%Y-%m-%d'),
                                treated_summary=treated_summary)
    except Exception as e:
        print(f"Error generating treatment report: {str(e)}")
        return render_template('reports/treatment_report.html',
                             current_date=current_date.strftime('%Y-%m-%d'),
                             treated_summary={'treated_total': 0, 'treated_data': []})


@daily_reports.route('/stock_reports')
def stock_report():
    current_date = datetime.now().date()  # Move outside try block
    try:
        suppliers = supabase.table('suppliers').select('*').execute()
        suppliers_data = suppliers.data if suppliers else []

        # Fetch daily stock levels
        treated_response = supabase.table('kdl_treated_poles').select('*').execute()
        untreated_response = supabase.table('kdl_to_treat').select('*').execute()
        rejects_response = supabase.table('rejects').select('*, suppliers!inner(*)').eq('suppliers.id', 'rejects.supplier_id').execute()
        
        treated_data = treated_response.data if treated_response else []
        untreated_data = untreated_response.data if untreated_response else []
        rejects_data = rejects_response.data if rejects_response else []


        treated_total = sum(sum(float(item.get(size, 0)) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) for item in treated_data) if treated_data else 0
        untreated_total = sum(sum(float(item.get(size, 0)) for size in ['7m', '8m', '9m', '10m', '11m', '12m', '14m']) for item in untreated_data) if untreated_data else 0
        rejects_total = sum(float(item.get('quantity', 0)) for item in rejects_data) if suppliers_data else 0
        print(f"Treated data: {treated_data}")

        treated_summary = {
            'treated_total': treated_total,
            'treated_data': treated_data
        }
        untreated_summary = {
            'untreated_total': untreated_total,
            'untreated_data': untreated_data
        }
        rejects_summary = {
            'rejects_total': rejects_total,
            'rejects_data': rejects_data
        }
        print(f"Treated data: {treated_data}")

        return render_template('reports/stock_report.html',
                                suppliers_data=suppliers_data,
                                current_date=current_date.strftime('%Y-%m-%d'),
                                treated_summary=treated_summary,
                                untreated_summary=untreated_summary,
                                rejects_summary=rejects_summary)
    
    except Exception as e:
        print(f"Error generating stock report: {str(e)}")
        return render_template('reports/stock_report.html',
                                suppliers_data=[],
                                current_date=current_date.strftime('%Y-%m-%d'),
                                treated_summary={'treated_total': 0, 'treated_data': []},
                                untreated_summary={'untreated_total': 0, 'untreated_data': []},
                                rejects_summary={'rejects_total': 0, 'rejects_data': []})
