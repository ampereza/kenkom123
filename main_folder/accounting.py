from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint, send_file
from flask_login import login_required, current_user
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
from flask_login import LoginManager, current_user, login_required
from main_folder.auth import role_required
from main_folder.teset import fetch_table_sum, bal_brought_forward
from flask import Flask, session
import os
import pandas as pd
from io import BytesIO




accounting = Blueprint('accounting', __name__)

# Load environment variables from .env file
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
SECRET_KEY = os.getenv("SECRET_KEY")


#templates for this blueprint are in the folder templates/accounts

#routes
#accounting_dashboard
#accounts_base
#create_invoice
#inventory
#invoice
#ledgers
#payroll
#reports
#taxes
#recipts
#payment_vouchers
#journal
#accounting_settings



@accounting.route('/accounts_dashboard')
def accounting_dashboard():
    try:
        current_date = datetime.now()

        # Daily totals
        daily_sales = supabase.table("sales").select("total_amount").eq("date", current_date.date().isoformat()).execute()
        
        print(daily_sales.data)
        daily_sales_sum = sum([sale['total_amount'] for sale in daily_sales.data])
        print(daily_sales_sum)

        daily_expenses = supabase.table("expenses").select("amount").eq("date", current_date.date().isoformat()).execute()
        daily_expenses_sum = sum([expense['amount'] for expense in daily_expenses.data])
        print(daily_expenses_sum)

        daily_purchases = supabase.table("purchases").select("total_amount").eq("date", current_date.date().isoformat()).execute()
        daily_purchases_sum = sum([purchase['total_amount'] for purchase in daily_purchases.data])
        print(daily_purchases_sum)

        # Weekly totals (last 7 days)
        week_ago = (current_date - timedelta(days=7)).date().isoformat()
        weekly_sales = supabase.table("sales").select("total_amount").gte("date", week_ago).execute()
        weekly_sales_sum = sum([sale['total_amount'] for sale in weekly_sales.data])
        print(weekly_sales_sum)

        weekly_expenses = supabase.table("expenses").select("amount").gte("date", week_ago).execute()
        weekly_expenses_sum = sum([expense['amount'] for expense in weekly_expenses.data])
        print(weekly_expenses_sum)

        weekly_purchases = supabase.table("purchases").select("total_amount").gte("date", week_ago).execute()
        weekly_purchases_sum = sum([purchase['total_amount'] for purchase in weekly_purchases.data])
        print(weekly_purchases_sum)

        # Monthly totals (last 30 days)
        month_ago = (current_date - timedelta(days=30)).date().isoformat()
        monthly_sales = supabase.table("sales").select("total_amount").gte("date", month_ago).execute()
        monthly_sales_sum = sum([sale['total_amount'] for sale in monthly_sales.data])
        print(monthly_sales_sum)

        monthly_expenses = supabase.table("expenses").select("amount").gte("date", month_ago).execute()
        monthly_expenses_sum = sum([expense['amount'] for expense in monthly_expenses.data])
        print(monthly_expenses_sum)

        monthly_purchases = supabase.table("purchases").select("total_amount").gte("date", month_ago).execute()
        monthly_purchases_sum = sum([purchase['total_amount'] for purchase in monthly_purchases.data])
        print(monthly_purchases_sum)

        # Annual totals (last 365 days)
        year_ago = (current_date - timedelta(days=365)).date().isoformat()
        annual_sales = supabase.table("sales").select("total_amount").gte("date", year_ago).execute()
        annual_sales_sum = sum([sale['total_amount'] for sale in annual_sales.data])
        print(annual_sales_sum)

        annual_expenses = supabase.table("expenses").select("amount").gte("date", year_ago).execute()
        annual_expenses_sum = sum([expense['amount'] for expense in annual_expenses.data])
        print(annual_expenses_sum)

        annual_purchases = supabase.table("purchases").select("total_amount").gte("date", year_ago).execute()
        annual_purchases_sum = sum([purchase['total_amount'] for purchase in annual_purchases.data])
        print(annual_purchases_sum)

        # Fetch recent transactions
        recent_sales = supabase.table('sales').select('*').order('date', desc="desc").limit(10).execute().data
        recent_expenses = supabase.table('expenses').select('*').order('date', desc="desc").limit(10).execute().data
        recent_invoices = supabase.table('invoices').select('*').order('created_at', desc="desc").limit(10).execute().data
        recent_payment_vouchers = supabase.table('payment_vouchers').select('*').order('date', desc="desc").limit(10).execute().data

        return render_template('accounts/accounts_dashboard.html',
                            daily_sales=daily_sales_sum,
                            daily_expenses=daily_expenses_sum,
                            daily_purchases=daily_purchases_sum,
                            weekly_sales=weekly_sales_sum,
                            weekly_expenses=weekly_expenses_sum,
                            weekly_purchases=weekly_purchases_sum,
                            monthly_sales=monthly_sales_sum,
                            monthly_expenses=monthly_expenses_sum,
                            monthly_purchases=monthly_purchases_sum,
                            annual_sales=annual_sales_sum,
                            annual_expenses=annual_expenses_sum,
                            annual_purchases=annual_purchases_sum,
                            recent_sales=recent_sales,
                            recent_expenses=recent_expenses,
                            recent_invoices=recent_invoices,
                            recent_payment_vouchers=recent_payment_vouchers)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return render_template('accounts/accounts_dashboard.html',
                            daily_sales=0,
                            daily_expenses=0,
                            daily_purchases=0,
                            weekly_sales=0,
                            weekly_expenses=0,
                            weekly_purchases=0,
                            monthly_sales=0,
                            monthly_expenses=0,
                            monthly_purchases=0,
                            annual_sales=0,
                            annual_expenses=0,
                            annual_purchases=0,
                            recent_sales=[],
                            recent_expenses=[],
                            recent_invoices=[],
                            recent_payment_vouchers=[])









@accounting.route('/accounting_purchases')
def accounting_purchases():
    try:
        # Fetch all purchase records from the Supabase table
        response = supabase.table('purchases').select('*').execute()

        # Check if the response is successful and contains data
        if response:
            #print(response.data)  # Uncomment this line to see the raw response data
            print(response)
            purchases = response.data  # This contains the purchase records
        else:
            purchases = []

        return render_template('accounts/purchases.html', purchases=purchases)

    except Exception as e:
        # In case of an error, return an empty list and log the error
        print(f"Error fetching purchases: {str(e)}")
        return render_template('accounts/purchases.html', purchases=[])



@accounting.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if request.method == 'POST':
        try:
            # Retrieve form data
            supplier = request.form.get('supplier')  # Adjusted to match the form
            item = request.form.get('item')
            quantity = request.form.get('quantity')
            rate = request.form.get('rate')
            total_amount = request.form.get('total_amount')
            description = request.form.get('description')

            # Ensure mandatory fields are provided
            if not all([quantity, rate, total_amount]):
                flash("Missing required fields. Please provide all inputs.", "danger")
                return redirect(url_for('accounting.accounting_purchases'))

            # Convert inputs to floats and handle potential errors
            try:
                quantity = float(quantity)
                rate = float(rate)
                total_amount = float(total_amount)
            except ValueError:
                flash("Invalid numeric values for quantity, unit price, or amount.", "danger")
                return redirect(url_for('accounting.accounting_purchases'))

            # Prepare purchase data for insertion
            purchase_data = {
                "supplier": supplier,  # Adjusted to match the form
                "item": item,
                "quantity": quantity,
                "rate": rate,
                "total_amount": total_amount,
                "description": description,
            }

            # Insert purchase into Supabase
            response = supabase.table('purchases').insert(purchase_data).execute()
            print(response)

            # Check response status and handle accordingly

        except Exception as e:
            flash(f'Error adding purchase: {str(e)}', 'danger')
            print(f'Error: {str(e)}')

        return redirect(url_for('accounting.accounting_purchases'))

    return render_template('accounts/purchases.html')



@accounting.route('/add_payment_vouchers', methods=['POST'])
def add_payment_vouchers():
    # Retrieve form data
    voucher_number = request.form.get('voucher_number')
    date = request.form.get('date')
    paid_to = request.form.get('payee')
    total_amount = request.form.get('total_amount')
    payment_method = request.form.get('payment_method')
    description = request.form.get('description')

    # Save the payment voucher to the database (Example: Supabase)
    try:
        payment_voucher = {
            "voucher_number": voucher_number,
            "date": date,
            "paid_to": paid_to,
            "total_amount": float(total_amount),
            "payment_method": payment_method,
            "description": description,
        }

        # Insert into Supabase (assuming a table named 'payment_vouchers')
        result = supabase.table('payment_vouchers').insert(payment_voucher).execute()
        print(result)
        return redirect (url_for('accounting.payment_vouchers'))

        

    except Exception as e:
        print (e)
        return ({"error": str(e)}), 500




@accounting.route('/payment_vouchers')
def payment_vouchers():
    try:
        # Fetch all payment vouchers from the database (Example: Supabase)
        response = supabase.table('payment_vouchers').select('*').execute()
        print(response)
        if response:
            payment_vouchers = response.data  # This contains the payment voucher records
        else:
            payment_vouchers = []

        return render_template('accounts/payment_vouchers.html', payment_vouchers=payment_vouchers)

    except Exception as e:
        print(f"Error fetching payment vouchers: {str(e)}")
        return render_template('accounts/payment_vouchers.html', payment_vouchers=[])
    

#delivery_note

@accounting.route('/delivery_note')
def delivery_note():
    # Fetch all delivery notes from the database (Example: Supabase)
    try:
        response= supabase.table('delivery_note').select('*').execute()
        print(response)
        if response:
            delivery_note = response.data

        else:
            delivery_note = []

        return render_template('accounts/delivery_note.html', delivery_note=delivery_note)
    
    except Exception as e:
        print(f"Error fetching delivery_notes: {str(e)}")



    return render_template('accounts/delivery_note.html')




#handle adding expenses'
@accounting.route('/add_expense', methods = [ 'POST'])
def add_expense():
    date = request.form.get('date')
    category = request.form.get('category')
    description = request.form.get('description')
    amount = request.form.get('amount')


    # Save the payment voucher to the database (Example: Supabase)
    try:
        payment_voucher = {
            "date": date,
            "category": category,
            "amount": float(amount),
            "description": description,
        }

        # Insert into Supabase (assuming a table named 'payment_vouchers')
        result = supabase.table('expenses').insert(payment_voucher).execute()
        print(result)
        return redirect (url_for('accounting.expenses'))

        

    except Exception as e:
        print (e)
        return ({"error": str(e)}), 500
    

@accounting.route('/expenses')
def expenses():
    try:
        # Fetch all payment vouchers from the database (Example: Supabase)
        response = supabase.table('expenses').select('*').execute()
        print(response)
        if response:
            expenses = response.data  # This contains the payment voucher records
        else:
            expenses = []

        return render_template('accounts/expenses.html', expenses= expenses)

    except Exception as e:
        print(f"Error fetching payment vouchers: {str(e)}")
        return render_template('accounts/expenses.html', expenses=[])



@accounting.route('/submit_invoice', methods=['POST'])
# @login_required
def submit_invoice():
    date = request.form.get('date')
    invoice_number = request.form.get('invoice_number')
    customer = request.form.get('customer')
    type = request.form.get('type')
    category = request.form.get('category')
    description = request.form.get('description')
    quantity = float(request.form.get('quantity'))
    rate = float(request.form.get('rate'))
    total_amount = rate * quantity

    # Save the payment voucher to the database (Example: Supabase)
    try:
        invoices = {
            "date": date,
            "invoice_number": invoice_number,
            "customer": customer,
            "type": type,
            "category": category,
            "rate": rate,
            "description": description,
            "quantity": quantity,
            "total_amount": total_amount  # Use a string key here
        }

        # Insert into Supabase (assuming a table named 'invoices')
        result = supabase.table('invoices').insert(invoices).execute()
        print(result)
        return redirect(url_for('accounting.invoices'))  # Corrected route

    except Exception as e:
        print(e)
        return ({"error": str(e)}), 500

@accounting.route('/invoice')
def invoice():
    # Fetch all invoices from the database (Example: Supabase)
    try:
        response = supabase.table('invoices').select('*').execute()
        print(response)
        if response:
            invoices = response.data  # This contains the invoice records
        else:
            invoices = []

        return render_template('accounts/invoice.html', invoices=invoices)

    except Exception as e:
        print(f"Error fetching invoices: {str(e)}")
        return render_template('accounts/invoice.html', invoices=[])


@accounting.route('/get_customer')
@login_required
def get_customer():
    try:
        #fetch customer from the customers table
        result = supabase.table('customers').select('id, name').execute()
        customers = result.data
        return (customers)
        print(customers)
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500
    

@accounting.route('/sales', methods=['GET', 'POST'])
def sales():
    def safe_float(value):
        """Convert a value to float safely, returning None if invalid."""
        try:
            return float(value) if value else None
        except ValueError:
            return None

    if request.method == 'POST':
        # Retrieve and validate form data
        sale_type = request.form.get('sale_type')
        customer_id = request.form.get('customer_id')
        customer_name = request.form.get('customer_name')
        description = request.form.get('description')
        quantity = safe_float(request.form.get('quantity'))
        rate = safe_float(request.form.get('rate'))
        discount = safe_float(request.form.get('discount'))
        lengths = {key: safe_float(request.form.get(key)) for key in ['7m', '8m', '9m', '10m', '11m', '12m', '14m']}
        
        # Validate required fields
        missing_fields = []
        if not sale_type:
            missing_fields.append('Sale Type')
        if not customer_id:
            missing_fields.append('Customer')
        if not description:
            missing_fields.append('Description')
        if quantity is None:
            missing_fields.append('Quantity')
        if rate is None:
            missing_fields.append('Rate')

        if missing_fields:
            flash(f'Missing fields: {", ".join(missing_fields)}', 'danger')
            return redirect(url_for('accounting.sales'))

        # Calculate total amount
        total_amount = quantity * rate - (discount or 0)

        # Prepare sale data
        sale_data = {
            "sale_type": sale_type,
            "customer_id": int(customer_id),
            "customer_name": customer_name,
            "quantity": quantity,
            "rate": rate,
            "discount": discount,
            "total_amount": total_amount,
            "description": description,
            "date": request.form.get('date'),
            "receipt_number": request.form.get('receipt_number'),
            "status": request.form.get('status'),
            **lengths,  # Add lengths dynamically
        }

        # Insert sale into Supabase
        try:
            response = supabase.table('sales').insert(sale_data).execute()
            if response.data:
                flash('Sale created successfully!', 'success')
            else:
                flash('Failed to create sale. Please try again.', 'danger')
                print(f"Supabase Error: {response.error}")
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print(f"Error inserting sale: {str(e)}")

        return redirect(url_for('accounting.sales'))

    # Fetch customers and sales data for display
    try:
        customers = supabase.table('customers').select("id, full_name").execute().data or []
        sales = supabase.table('sales').select("*").order("date", desc=True).execute().data or []
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(f"Error fetching data: {str(e)}")
        customers, sales = [], []

    return render_template('accounts/add_sales.html', customers=customers, sales=sales)























@accounting.route('/inventory')
@login_required
def inventory():
    return render_template('accounts/inventory.html')


@accounting.route('/payroll')
@login_required
def payroll():
    return render_template('accounts/payroll.html')

@accounting.route('/reports')
@login_required
def reports():
    return render_template('accounts/reports.html')

@accounting.route('/taxes')
@login_required
def taxes():
    return render_template('accounts/taxes.html')




@accounting.route('/add_receipt', methods=['POST'])
def add_receipt():
    try:
        receipt_data = {
            "receipt_number": request.form.get('receipt_number'),
            "received_from": request.form.get('received_from'),
            "amount": float(request.form.get('amount')),
            "for_payment": request.form.get('for_payment'),
            "payment_method": request.form.get('payment_method'),
            "description": request.form.get('description'),
            "type": request.form.get('type'),
            "client_id": request.form.get('client_id')
        }

        result = supabase.table('receipts').insert(receipt_data).execute()
        print(result)
        return redirect(url_for('accounting.receipts'))

    except Exception as e:
        print(e)
        return {"error": str(e)}, 500

@accounting.route('/receipts')
def receipts():
    try:
        # Fetch receipts
        receipts_response = supabase.table('receipts').select('*').execute()
        receipts = receipts_response.data if receipts_response else []

        # Fetch clients
        clients_response = supabase.table('clients').select('*').execute()
        clients = clients_response.data if clients_response else []

        # Fetch customers
        customers_response = supabase.table('customers').select('*').execute()
        customers = customers_response.data if customers_response else []

        return render_template('accounts/receipts.html', 
                             receipts=receipts,
                             clients=clients,
                             customers=customers)

    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return render_template('accounts/receipts.html', 
                             receipts=[],
                             clients=[],
                             customers=[])
    


@accounting.route('/clients_ledger', methods=['GET'])
def clients_ledger():
    try:
        # Get client_id from query parameter
        client_id = request.args.get('client_id')
        
        # Fetch all clients for dropdown
        clients = supabase.table('clients').select('*').execute().data

        # If client_id is provided, fetch their ledger entries
        if client_id:
            ledger = supabase.table('clients_ledger')\
                .select('*, clients(name)')\
                .eq('client_id', client_id)\
                .order('transaction_date', desc=True)\
                .execute().data
        else:
            ledger = []

        return render_template('accounts/clients_ledger.html', 
                                clients=clients,
                                ledger=ledger,
                                selected_client=client_id)

    except Exception as e:
        print(f"Error fetching clients ledger: {str(e)}")
        # Initialize default values for clients and ledger
        clients = []
        ledger = []
        return render_template('accounts/clients_ledger.html', 
                                clients=clients,
                                ledger=ledger,
                                selected_client=None)
    





    
@accounting.route('/create_invoice', methods=['GET', 'POST'])
def create_invoice():
    if request.method == 'GET':
        return render_template('accounts/invoices.html')
    
    try:
        # Get form data
        data = {
            "date": request.form.get('date'),
            "invoice_number": float(request.form.get('invoice_number')),
            "customer": request.form.get('customer'),
            "type": request.form.get('type'),
            "category": request.form.get('category'),
            "description": request.form.get('description'),
            "quantity": float(request.form.get('quantity')),
            "rate": float(request.form.get('rate')),
            "total_amount": float(request.form.get('quantity')) * float(request.form.get('rate')),
            "status": "pending"
        }

        # Insert into Supabase
        result = supabase.table('invoices').insert(data).execute()
        
        if not result.data:
            raise Exception("Failed to create invoice")

        flash("Invoice created successfully", "success")
        return redirect(url_for('accounting.invoices'))

    except ValueError as e:
        flash("Please enter valid numeric values", "error")
        return redirect(url_for('accounting.create_invoice'))
    except Exception as e:
        flash(f"Error creating invoice: {str(e)}", "error")
        return redirect(url_for('accounting.create_invoice'))




@accounting.route('/invoices')
def invoices():
    try:
        response = supabase.table('invoices').select('*').order('created_at', desc=True).execute()
        invoices = response.data if response and response.data else []

        for invoice in invoices:
            if invoice.get('date'):
                invoice['date'] = datetime.strptime(invoice['date'], '%Y-%m-%d').strftime('%Y-%m-%d')
            if invoice.get('created_at'):
                invoice['created_at'] = datetime.strptime(invoice['created_at'].split('.')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
            if invoice.get('updated_at'):
                invoice['updated_at'] = datetime.strptime(invoice['updated_at'].split('.')[0], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')

        return render_template('accounts/invoice.html', invoices=invoices)

    except Exception as e:
        print(f"Error fetching invoices: {str(e)}")
        return render_template('accounts/invoice.html', invoices=[])






@accounting.route('/income_statement')
def income_statement():
    try:
        current_date = datetime.now()

        # Helper function to calculate totals for a given date range
        def calculate_totals(start_date):
            # Revenue (Sales)
            sales = supabase.table("sales").select("total_amount").gte("date", start_date).execute()
            total_sales = sum([sale['total_amount'] or 0 for sale in sales.data])

            # treatment income = sum all receipts whose type is treatment
            treatment_income = supabase.table("receipts").select("amount").eq("type", "treatment").gte("date", start_date).execute()
            total_treatment_income = sum([receipt['amount'] or 0 for receipt in treatment_income.data])

            #other income = sum all receipts whose type is sale
            other_income = supabase.table("receipts").select("amount").eq("type", "sale").gte("date", start_date).execute()
            total_other_income = sum([receipt['amount'] or 0 for receipt in other_income.data])

            # Expenses by category
            expenses = supabase.table("expenses").select("amount,category").gte("date", start_date).execute()
            expenses_by_category = {}
            for expense in expenses.data:
                category = expense['category']
                amount = expense['amount'] or 0
                expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            total_expenses = sum([amount for amount in expenses_by_category.values()])

            # Purchases (Cost of Goods Sold)
            purchases = supabase.table("purchases").select("total_amount").gte("date", start_date).execute()
            total_purchases = sum([purchase['total_amount'] or 0 for purchase in purchases.data])

            # Calculate gross profit and net income

            cost_of_goods = total_purchases
            gross_profit = total_sales + total_treatment_income + total_other_income - total_purchases
            net_income = gross_profit - total_expenses

            return {
                'revenue': total_sales,
                'treatment_income': total_treatment_income,
                'other_income': total_other_income,
                'cost_of_goods' : cost_of_goods,
                'gross_profit': gross_profit,
                'expenses': total_expenses,
                'expenses_by_category': expenses_by_category,
                'net_income': net_income
            }

        # Calculate for different periods
        daily = calculate_totals(current_date.date().isoformat())
        weekly = calculate_totals((current_date - timedelta(days=7)).date().isoformat())
        monthly = calculate_totals((current_date - timedelta(days=30)).date().isoformat())
        annual = calculate_totals((current_date - timedelta(days=365)).date().isoformat())

        return render_template('accounts/reports.html',
                            daily_statement=daily,
                            weekly_statement=weekly,
                            monthly_statement=monthly,
                            annual_statement=annual,
                            current_date=current_date.strftime('%Y-%m-%d'))

    except Exception as e:
        print(f"Error generating income statement: {str(e)}")
        return render_template('accounts/reports.html', 
                            error=str(e),
                            daily_statement={},
                            weekly_statement={},
                            monthly_statement={},
                            annual_statement={},
                            current_date=current_date.strftime('%Y-%m-%d'))


