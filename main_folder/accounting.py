from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint, send_file, jsonify
from flask_login import login_required, current_user
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime, timedelta
from flask_login import LoginManager, current_user, login_required
from main_folder.auth import role_required
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
        
        # Fetch notices that are currently active
        notices_response = supabase.table('notice').select('*').execute()
        print ('notices', notices_response)
        
        notices = notices_response.data[0]['content'] if notices_response.data else "No current notices"
        print("Active Notices:", notices)

        # Daily totals
        daily_sales = supabase.table("sales").select("total_amount").gte("created_at", current_date.date().isoformat()).execute()
        daily_sales_sum = sum([sale.get('total_amount', 0) for sale in (daily_sales.data or [])])
        print("Daily Sales Sum:", daily_sales_sum)

        daily_expenses = supabase.table("expenses").select("amount").gte("created_at", current_date.date().isoformat()).execute()
        daily_expenses_sum = sum([expense.get('amount', 0) for expense in (daily_expenses.data or [])])
        print("Daily Expenses Sum:", daily_expenses_sum)

        daily_purchases = supabase.table("purchases").select("total_amount").gte("created_at", current_date.date().isoformat()).execute()
        daily_purchases_sum = sum([purchase.get('total_amount', 0) for purchase in (daily_purchases.data or [])])
        print("Daily Purchases Sum:", daily_purchases_sum)

        daily_receipts = supabase.table("receipts").select("amount").gte("date", current_date.date().isoformat()).execute()
        daily_receipts_sum = sum([receipt.get('amount', 0) for receipt in (daily_receipts.data or [])])
        print("Daily Receipts Sum:", daily_receipts_sum) 

        # Weekly totals (last 7 days)
        week_ago = (current_date - timedelta(days=7)).date().isoformat()
        weekly_sales = supabase.table("sales").select("total_amount").gte("created_at", week_ago).execute()
        weekly_sales_sum = sum([sale.get('total_amount', 0) for sale in (weekly_sales.data or [])])
        print("Weekly Sales Sum:", weekly_sales_sum)

        weekly_expenses = supabase.table("expenses").select("amount").gte("created_at", week_ago).execute()
        weekly_expenses_sum = sum([expense.get('amount', 0) for expense in (weekly_expenses.data or [])])
        print("Weekly Expenses Sum:", weekly_expenses_sum)

        weekly_purchases = supabase.table("purchases").select("total_amount").gte("created_at", week_ago).execute()
        weekly_purchases_sum = sum([purchase.get('total_amount', 0) for purchase in (weekly_purchases.data or [])])
        print("Weekly Purchases Sum:", weekly_purchases_sum)



        weekly_receipts = supabase.table("receipts").select("amount").gte("date", week_ago).execute()
        weekly_receipts_sum = sum([receipt.get('amount', 0) for receipt in (weekly_receipts.data or [])])
        print("Weekly Receipts Sum:", weekly_receipts_sum)

        # Monthly totals (last 30 days)
        month_ago = (current_date - timedelta(days=30)).date().isoformat()
        monthly_sales = supabase.table("sales").select("total_amount").gte("created_at", month_ago).execute()
        monthly_sales_sum = sum([sale.get('total_amount', 0) for sale in (monthly_sales.data or [])])
        print("Monthly Sales Sum:", monthly_sales_sum)

        monthly_expenses = supabase.table("expenses").select("amount").gte("created_at", month_ago).execute()
        monthly_expenses_sum = sum([expense.get('amount', 0) for expense in (monthly_expenses.data or [])])
        print("Monthly Expenses Sum:", monthly_expenses_sum)

        monthly_purchases = supabase.table("purchases").select("total_amount").gte("created_at", month_ago).execute()
        monthly_purchases_sum = sum([purchase.get('total_amount', 0) for purchase in (monthly_purchases.data or [])])
        print("Monthly Purchases Sum:", monthly_purchases_sum)

        monthly_receipts = supabase.table("receipts").select("amount").gte("date", month_ago).execute()
        monthly_receipts_sum = sum([receipt.get('amount', 0) for receipt in (monthly_receipts.data or [])])
        print("Monthly Receipts Sum:", monthly_receipts_sum) 

        # Annual totals (last 365 days)
        year_ago = (current_date - timedelta(days=365)).date().isoformat()
        annual_sales = supabase.table("sales").select("total_amount").gte("created_at", year_ago).execute()
        annual_sales_sum = sum([sale.get('total_amount', 0) for sale in (annual_sales.data or [])])
        print("Annual Sales Sum:", annual_sales_sum)

        annual_expenses = supabase.table("expenses").select("amount").gte("created_at", year_ago).execute()
        annual_expenses_sum = sum([expense.get('amount', 0) for expense in (annual_expenses.data or [])])
        print("Annual Expenses Sum:", annual_expenses_sum)

        annual_purchases = supabase.table("purchases").select("total_amount").gte("created_at", year_ago).execute()
        annual_purchases_sum = sum([purchase.get('total_amount', 0) for purchase in (annual_purchases.data or [])])
        print("Annual Purchases Sum:", annual_purchases_sum)


        monthly_receipts = supabase.table("receipts").select("amount").gte("date", month_ago).execute()
        monthly_receipts_sum = sum([receipt.get('amount', 0) for receipt in (monthly_receipts.data or [])])
        print("Monthly Receipts Sum:", monthly_receipts_sum) 


        # Fetch recent transactions
        recent_sales = supabase.table('sales').select('*').order('created_at', desc="desc").limit(10).execute().data
        recent_expenses = supabase.table('expenses').select('*').order('date', desc="desc").limit(10).execute().data
        recent_invoices = supabase.table('invoices').select('*').order('created_at', desc="desc").limit(10).execute().data
        recent_payment_vouchers = supabase.table('payment_vouchers').select('*').order('date', desc="desc").limit(10).execute().data
        recent_receipts = supabase.table('receipts').select('*').order('date', desc="desc").limit(10).execute().data

        total_sales = sum([sale.get('total_amount', 0) for sale in (recent_sales or [])])
        print("Total Sales:", total_sales)
        total_expenses = sum([expense.get('amount', 0) for expense in (recent_expenses or [])])
        print("Total Expenses:", total_expenses)
        total_invoices = sum([invoice.get('total_amount', 0) for invoice in (recent_invoices or [])])
        print("Total Invoices:", total_invoices)
        total_payment_vouchers = sum([voucher.get('total_amount', 0) for voucher in (recent_payment_vouchers or [])])
        print("Total Payment Vouchers:", total_payment_vouchers)
        total_receipts = sum([receipt.get('amount', 0) for receipt in (recent_receipts or [])])
        print("Total Receipts:", total_receipts)
        total_purchases = sum([purchase.get('total_amount', 0) for purchase in (recent_payment_vouchers or [])])
        print("Total Purchases:", total_purchases)
        balance = total_sales + total_receipts - (total_expenses + total_payment_vouchers + total_purchases)


        return render_template('accounts/accounts_dashboard.html',
                            daily_sales=daily_sales_sum,
                            daily_expenses=daily_expenses_sum,
                            daily_purchases=daily_purchases_sum,
                            daily_receipts=daily_receipts_sum,
                            weekly_sales=weekly_sales_sum,
                            weekly_expenses=weekly_expenses_sum,
                            weekly_purchases=weekly_purchases_sum,
                            weekly_receipts=weekly_receipts_sum,
                            monthly_sales=monthly_sales_sum,
                            monthly_expenses=monthly_expenses_sum,
                            monthly_purchases=monthly_purchases_sum,
                            monthly_receipts=monthly_receipts_sum,
                            annual_sales=annual_sales_sum,
                            annual_expenses=annual_expenses_sum,
                            annual_purchases=annual_purchases_sum,
                            annual_receipts=monthly_receipts_sum,
                            recent_sales=recent_sales,
                            recent_expenses=recent_expenses,
                            recent_invoices=recent_invoices,
                            recent_payment_vouchers=recent_payment_vouchers,
                            recent_receipts=recent_receipts,
                            notices = notices,
                            balance=balance)


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
                            recent_payment_vouchers=[],
                            balance=0)









@accounting.route('/accounting_purchases')
def accounting_purchases():
    try:
        # Fetch all purchase records from the Supabase table
        response = supabase.table('purchases').select('*').order('created_at', desc="desc").execute()
        purchases = response.data if response else []

        # Fetch all suppliers from the Supabase table
        suppliers_response = supabase.table('suppliers').select('*').execute()
        suppliers = suppliers_response.data if suppliers_response else []

        return render_template('accounts/purchases.html', purchases=purchases, suppliers=suppliers)

    except Exception as e:
        # In case of an error, return empty lists and log the error
        print(f"Error fetching purchases or suppliers: {str(e)}")
        return render_template('accounts/purchases.html', purchases=[], suppliers=[])



@accounting.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    if request.method == 'POST':
        try:
            # Retrieve form data
            supplier = request.form.get('supplier')  # Ensure this matches the form field name
            item = request.form.get('item')
            quantity = request.form.get('quantity')
            rate = request.form.get('rate')
            total_amount = request.form.get('total_amount')
            description = request.form.get('description')

            # Ensure mandatory fields are provided
            if not supplier:
                flash("Supplier is required. Please select a supplier.", "danger")
                return redirect(url_for('accounting.accounting_purchases'))
            if not all([item, quantity, rate, total_amount]):
                flash("Missing required fields: Item, Quantity, Rate, and Total Amount are mandatory.", "danger")
                return redirect(url_for('accounting.accounting_purchases'))

            # Convert inputs to floats and handle potential errors
            try:
                quantity = float(quantity)
                rate = float(rate)
                total_amount = float(total_amount)
            except ValueError:
                flash("Invalid numeric values for Quantity, Rate, or Total Amount.", "danger")
                return redirect(url_for('accounting.accounting_purchases'))

            # Prepare purchase data for insertion
            purchase_data = {
                "supplier": supplier,  # Ensure this matches the database field
                "item": item,
                "quantity": quantity,
                "rate": rate,
                "total_amount": total_amount,
                "description": description,
            }

            # Insert purchase into Supabase
            response = supabase.table('purchases').insert(purchase_data).execute()
            print(response)

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

@accounting.route('/delivery_notes')
def delivery_notes():
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
            "balance": float(request.form.get('balance')),
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

        # Initialize selected_client_name and total_balance
        selected_client_name = None
        total_balance = 0

        # If client_id is provided, fetch their ledger entries and name
        if client_id:
            ledger_response = supabase.table('clients_ledger')\
                .select('*, clients(name)')\
                .eq('client_id', client_id)\
                .order('transaction_date', desc=True)\
                .execute()
            ledger = ledger_response.data if ledger_response.data else []
            print(ledger)

            # Fetch the selected client's name
            client_response = supabase.table('clients').select('name').eq('id', client_id).execute()
            if client_response.data:
                selected_client_name = client_response.data[0]['name']

            # Compute running balance from top (most recent) to bottom
            balance = 0
            for entry in reversed(ledger):  # reverse to get oldest first
                transaction_type = entry.get('transaction_type')
                amount = entry.get('amount', 0)

                if transaction_type == 'payment':
                    balance += amount
                elif transaction_type == 'treatment':
                    balance -= amount

                entry['balance'] = balance  # inject into entry for frontend

            # Calculate total balance
            total_balance = sum(
                entry['amount'] if entry['transaction_type'] == 'payment' else -entry['amount']
                for entry in ledger
                if entry['transaction_type'] in ['payment', 'treatment']
            )
        else:
            ledger = []
            print

        return render_template('accounts/clients_ledger.html', 
                                clients=clients,
                                ledger=ledger,
                                selected_client=client_id,
                                selected_client_name=selected_client_name,
                                total_balance=total_balance)

    except Exception as e:
        print(f"Error fetching clients ledger: {str(e)}")
        # Initialize default values for clients and ledger
        clients = []
        ledger = []
        return render_template('accounts/clients_ledger.html', 
                                clients=clients,
                                ledger=ledger,
                                selected_client=None,
                                selected_client_name=None,
                                total_balance=0)
    





    
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






@accounting.route('/income_statements')
def income_statements():
    try:
        current_date = datetime.now()

        # Helper function to calculate totals for a given date range
        def calculate_totals(start_date):
            # Revenue (Sales)
            sales = supabase.table("sales").select("total_amount").gte("created_at", start_date).execute()
            total_sales = sum([sale['total_amount'] or 0 for sale in sales.data])

            # treatment income = sum all receipts whose type is treatment
            treatment_income = supabase.table("receipts").select("amount").eq("type", "treatment").gte("date", start_date).execute()
            total_treatment_income = sum([receipt['amount'] or 0 for receipt in treatment_income.data])

            #other income = sum all receipts whose type is sale
            other_income = supabase.table("receipts").select("amount").eq("type", "sale").gte("date", start_date).execute()
            total_other_income = sum([receipt['amount'] or 0 for receipt in other_income.data])
            print("Total Other Income:", total_other_income)

            # Expenses by category
            expenses = supabase.table("expenses").select("amount,category").gte("date", start_date).execute()
            expenses_by_category = {}
            for expense in expenses.data:
                category = expense['category']
                amount = expense['amount'] or 0
                expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
            total_expenses = sum([amount for amount in expenses_by_category.values()])

            # Purchases (Cost of Goods Sold)
            purchases = supabase.table("purchases").select("total_amount").gte("created_at", start_date).execute()
            total_purchases = sum([purchase['total_amount'] or 0 for purchase in purchases.data])

            #payment vouchers (expenses)
            payment_vouchers = supabase.table("payment_vouchers").select("total_amount").gte("date", start_date).execute()
            total_payment_vouchers = sum([voucher['total_amount'] or 0 for voucher in payment_vouchers.data])

            # Calculate gross profit and net income

            cost_of_goods = total_purchases + total_payment_vouchers
            gross_profit = total_sales + total_treatment_income + total_other_income - cost_of_goods
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



@accounting.route('/add_payroll', methods=['POST'])
def add_payroll():
    try:
        payroll_data = {
            "employee_id": request.form.get('employee_id'),
            "gross_salary": float(request.form.get('gross_salary')),
            "advance": float(request.form.get('advance')),
            "nssf": float(request.form.get('nssf')),
            "paye": float(request.form.get('paye')), 
            "local_tax": float(request.form.get('local_tax'))
        }

        result = supabase.table('payroll').insert(payroll_data).execute()
        print(result)
        return redirect(url_for('accounting.payroll'))

    except Exception as e:
        print(e)
        return redirect(url_for('accounting.payroll'))

@accounting.route('/payroll')
def payroll():
    try:
        # Fetch payroll records
        payroll_response = supabase.table('payroll').select('*, employee_id(name)').execute()
        payroll_records = payroll_response.data if payroll_response else []

        # Print payroll records for debugging
        print("Payroll Records:", payroll_records)

        # Calculate totals
        total_gross = sum(record['gross_salary'] for record in payroll_records)
        total_advance = sum(record['advance'] for record in payroll_records)
        total_nssf = sum(record['nssf'] for record in payroll_records)
        total_paye = sum(record['paye'] for record in payroll_records)
        total_local_tax = sum(record['local_tax'] for record in payroll_records)

        # Pass data to the template
        return render_template(
            'accounts/payroll.html',
            payroll_records=payroll_records,
            total_gross=total_gross,
            total_advance=total_advance,
            total_nssf=total_nssf,
            total_paye=total_paye,
            total_local_tax=total_local_tax
        )

    except Exception as e:
        print(f"Error fetching payroll data: {str(e)}")
        return render_template(
            'accounts/payroll.html',
            payroll_records=[],
            total_gross=0,
            total_advance=0,
            total_nssf=0,
            total_paye=0,
            total_local_tax=0
        )




@accounting.route('/search', methods=['GET'])
def search():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Both start_date and end_date are required'}), 400

        # Search sales
        sales = supabase.table('sales')\
            .select('*')\
            .gte('created_at', start_date)\
            .lte('created_at', end_date)\
            .execute()

        # Search receipts
        receipts = supabase.table('receipts')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()

        # Search purchases
        # Ensure these fields exist in the table
        purchases = supabase.table('purchases')\
            .select('created_at, item, description, total_amount, supplier')\
            .gte('created_at', start_date)\
            .lte('created_at', end_date)\
            .execute()

        if not purchases.data:
            print("No purchases found for the given date range.")
        else:
            print(f"Purchases retrieved: {len(purchases.data)} records")
        
        # Search payment vouchers
        payment_vouchers = supabase.table('payment_vouchers')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()
        
        #expenses
        expenses = supabase.table('expenses')\
            .select('*')\
            .gte('date', start_date)\
            .lte('date', end_date)\
            .execute()


        results = {
            'sales': sales.data if sales else [],
            'receipts': receipts.data if receipts else [],
            'purchases': purchases.data if purchases else [],
            'payment_vouchers': payment_vouchers.data if payment_vouchers else [],
            'expenses':expenses.data if expenses else[]
        }

        return render_template('accounts/acc_search_results.html', 
                                results=results,
                                start_date=start_date,
                                end_date=end_date)

    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': str(e)}), 500



@accounting.route('/to_pay')
def to_pay():
    try:
        authorizations = supabase.table('expense_authorizations').select('*').execute().data
        print(authorizations)
        return render_template('accounts/to_pay.html', authorizations=authorizations)
    except Exception as e:
        print(f"Error fetching expense authorizations: {str(e)}")
        return render_template('accounts/to_pay.html')


@accounting.route('/mark_authorization_paid/<authorization_id>', methods=['POST'])
def mark_authorization_paid(authorization_id):
    try:
        supabase.table('expense_authorizations').update({"status": "paid"}).eq("id", authorization_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error marking authorization as paid: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
    



@accounting.route('/purchases_ledger', methods=['GET', 'POST'])
def purchases_ledger():
    try:
        if request.method == 'POST':
            # Fetch supplier name based on supplier_id
            supplier_id = request.form.get('supplier_id')
            supplier_name = None
            if supplier_id:
                supplier_response = supabase.table('suppliers').select('name').eq('id', supplier_id).execute()
                if supplier_response.data:
                    supplier_name = supplier_response.data[0]['name']

            # Add new purchase entry
            new_purchase = {
                'supplier_id': supplier_id,
                'supplier_name': supplier_name,  # Automatically populate supplier name
                'invoice_number': request.form.get('invoice_number'),
                'invoice_date': request.form.get('invoice_date'),
                'description': request.form.get('description'),
                'item': request.form.get('item'),
                'amount': float(request.form.get('amount')),
                'total_paid': float(request.form.get('initial_payment', 0))
            }
            
            # Insert into purchases_ledger
            result = supabase.table('purchases_ledger').insert(new_purchase).execute()
            
            # If there's an initial payment, record it in payment history
            if float(request.form.get('initial_payment', 0)) > 0:
                payment = {
                    'invoice_id': result.data[0]['id'],
                    'payment_date': request.form.get('invoice_date'),
                    'payment_amount': float(request.form.get('initial_payment')),
                    'payment_method': request.form.get('payment_method'),
                    'remarks': 'Initial payment'
                }
                supabase.table('payment_history').insert(payment).execute()

            flash('Purchase entry added successfully', 'success')
            return redirect(url_for('accounting.purchases_ledger'))

        # GET request - fetch data
        suppliers = supabase.table('suppliers').select('*').execute().data
        purchases = supabase.table('purchases_ledger').select('*').execute().data
        payment_history = supabase.table('payment_history').select('*').execute().data

        # Calculate totals
        total_amount = sum(float(p.get('amount', 0)) for p in purchases)
        total_paid = sum(float(p.get('total_paid', 0)) for p in purchases)
        total_outstanding = total_amount - total_paid

        return render_template('accounts/purchases_ledger.html',
                            suppliers=suppliers,
                            purchases=purchases,
                            payment_history=payment_history,
                            total_amount=total_amount,
                            total_paid=total_paid,
                            total_outstanding=total_outstanding)

    except Exception as e:
        print(f"Error in purchases_ledger: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return render_template('accounts/purchases_ledger.html', 
                            suppliers=[],
                            purchases=[],
                            payment_history=[],
                            total_amount=0,
                            total_paid=0,
                            total_outstanding=0)

@accounting.route('/add_payment/<int:invoice_id>', methods=['POST'])
def add_payment():
    try:
        payment_data = {
            'invoice_id': request.form.get('invoice_id'),
            'payment_date': request.form.get('payment_date'),
            'payment_amount': float(request.form.get('payment_amount')),
            'payment_method': request.form.get('payment_method'),
            'remarks': request.form.get('remarks')
        }

        # Insert payment record
        supabase.table('payment_history').insert(payment_data).execute()

        # Update total_paid in purchases_ledger
        invoice = supabase.table('purchases_ledger')\
            .select('total_paid')\
            .eq('id', payment_data['invoice_id'])\
            .execute()\
            .data[0]

        new_total_paid = float(invoice['total_paid']) + payment_data['payment_amount']
        
        supabase.table('purchases_ledger')\
            .update({'total_paid': new_total_paid})\
            .eq('id', payment_data['invoice_id'])\
            .execute()

        flash('Payment recorded successfully', 'success')
        return redirect(url_for('accounting.purchases_ledger'))

    except Exception as e:
        print(f"Error adding payment: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('accounting.purchases_ledger'))




@accounting.route('/pay_workers', methods=['GET', 'POST'])
def pay_workers():
    if request.method == 'POST':
        worker_id = request.form.get('worker_id')
        amount_paid = float(request.form.get('amount_paid', 0))
        is_advance = request.form.get('is_advance') == 'true'  # Convert to boolean

        # Insert payment record
        payment_data = {
            'workers_id': worker_id,  # Changed to workers_id
            'amount': amount_paid,
            'is_advance': is_advance,  # Ensure this is a boolean
            'payment_date': 'now()'
        }
        supabase.table('worker_payments').insert(payment_data).execute()
        
        if not is_advance:
            # Mark corresponding daily_work records as paid (numeric comparison for non-boolean fields)
            supabase.table('daily_work')\
                .update({'paid': 1})\
                .eq('worker_id', worker_id)\
                .eq('paid', 0)\
                .execute()
            print("Daily work records marked as paid.")
        else:
            # Mark corresponding daily_work records as advance
            supabase.table('daily_work')\
                .update({'advance': 1})\
                .eq('worker_id', worker_id)\
                .eq('advance', 0)\
                .execute()
            print("Daily work records marked as advance.")

        # If full amount is paid, mark summed total_pay as paid
        if not is_advance and amount_paid >= sum(
            record['total_pay'] for record in supabase.table('daily_work')
            .select('total_pay')
            .eq('worker_id', worker_id)
            .eq('paid', 0)
            .execute().data
        ):
            supabase.table('daily_work')\
                .update({'paid': 1})\
                .eq('worker_id', worker_id)\
                .eq('paid', 0)\
                .execute()
            print("Full amount paid. All unpaid records marked as paid.")

    try:
        # Call the custom Postgres function to calculate total_pay and amount for the current week
        weekly_payments = supabase.rpc('sum_weekly_payments').execute()
        weekly_payments_data = weekly_payments.data  # Access the data attribute directly
        print(f"Weekly payments data: {weekly_payments_data}")  # Debugging output

        # Log if no data is returned
        if not weekly_payments_data:
            print("No weekly payments data found. Check the daily_work and worker_payments tables for matching records.")
    except Exception as e:
        # Log the error and set weekly_payments_data to an empty list
        print(f"Error calculating weekly payments: {e}")
        weekly_payments_data = []

    # Get advance payments
    advance_payments = supabase.table('worker_payments')\
        .select('workers_id, amount, is_advance, payment_date')\
        .eq('is_advance', True)\
        .execute()

    # Group advance payments by workers_id
    advances_dict = {}
    for payment in advance_payments.data:
        worker_id = payment['workers_id']  # Changed to workers_id
        advances_dict[worker_id] = advances_dict.get(worker_id, 0) + payment['amount']

    # Get worker details
    workers = supabase.table('cusual_workers').select('*').execute()
    workers_dict = {w['id']: w for w in workers.data}

    # Combine payment data with worker details and advances
    payment_records = []
    for payment in weekly_payments_data:
        if payment['worker_id'] in workers_dict:  # worker_id remains as it refers to the daily_work table
            payment['worker'] = workers_dict[payment['worker_id']]
            payment['advance'] = advances_dict.get(payment['worker_id'], 0)
            # Calculate net_due as total_pay - advance
            payment['net_due'] = payment['total_pay'] - payment['advance']
            payment_records.append(payment)

    return render_template('accounts/pay_workers.html', payments=payment_records)


@accounting.route('/inventory_status', methods=['GET'])
def inventory_status():
    total_workers = supabase.table('cusual_workers').select('*').execute()
    total_workers_sum = len(total_workers.data)
    total_items = supabase.table('inventory').select('*').execute()
    # Get total chemicals from inventory
    chemical_items = supabase.table('inventory').select('quantity').eq('item', 'chemical').execute()
    total_chemicals = sum(item['quantity'] for item in chemical_items.data)

    #get Total endplates from inventory
    endplates_items = supabase.table('inventory').select('quantity').eq('item', 'endplates').execute()
    total_endplates = sum(item['quantity'] for item in endplates_items.data)
    total_endplates_used = supabase.table('inventory_use').select('quantity').eq('item', 'endplates').execute()
    total_endplates_used = sum(item['quantity'] for item in total_endplates_used.data)
    balance_endplates = total_endplates - total_endplates_used

    #get total fuel from inventory
    fuel_items = supabase.table('inventory').select('quantity').eq('item', 'Fuel').execute()
    total_fuel = sum(item['quantity'] for item in fuel_items.data)
    fuel_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'Fuel').execute()
    total_fuel_used = sum(item['quantity'] for item in fuel_items_used.data)
    balance_fuel = total_fuel - total_fuel_used

    #get total paint from inventory
    paint_items = supabase.table('inventory').select('quantity').eq('item', 'paint').execute()
    total_paint = sum(item['quantity'] for item in paint_items.data)
    paint_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'paint').execute()
    total_paint_used = sum(item['quantity'] for item in paint_items_used.data)
    balance_paint = total_paint - total_paint_used

    #get total nails from inventory
    nails_items = supabase.table('inventory').select('quantity').eq('item', 'unails').execute()
    total_nails = sum(item['quantity'] for item in nails_items.data)
    nails_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'unails').execute()
    total_nails_used = sum(item['quantity'] for item in nails_items_used.data)
    balance_nails = total_nails - total_nails_used

    #label_nails
    label_nails_items = supabase.table('inventory').select('quantity').eq('item', 'label_nails').execute()
    total_label_nails = sum(item['quantity'] for item in label_nails_items.data)
    label_nails_items_used = supabase.table('inventory_use').select('quantity').eq('item', 'label_nails').execute()
    total_label_nails_used = sum(item['quantity'] for item in label_nails_items_used.data)
    balance_label_nails = total_label_nails - total_label_nails_used

    #chemicals
    chemicals_items = supabase.table('inventory').select('quantity').eq('item', 'chemical').execute()
    total_chemicals = sum(item['quantity'] for item in chemicals_items.data)
    total_chemicals_used = supabase.table('inventory_use').select('quantity').eq('item', 'chemical').execute()
    total_chemicals_used = sum(item['quantity'] for item in total_chemicals_used.data)
    balance_chemicals = total_chemicals - total_chemicals_used 

    return render_template('accounts/inventory_status.html', 
                           total_workers=total_workers_sum, 
                           total_items=len(total_items.data),
                           total_chemicals=total_chemicals,
                           total_endplates=total_endplates,
                            total_endplates_used=total_endplates_used,
                            balance_endplates=balance_endplates,
                            total_fuel=total_fuel,
                            total_paint=total_paint,
                            total_nails=total_nails,
                            total_fuel_used=total_fuel_used,
                            total_paint_used=total_paint_used,
                            total_nails_used=total_nails_used,
                            total_label_nails=total_label_nails,
                            total_label_nails_used=total_label_nails_used,
                            balance_fuel=balance_fuel,
                            balance_paint=balance_paint,
                            balance_nails=balance_nails,
                            balance_label_nails=balance_label_nails,
                            balance_chemicals=balance_chemicals,
                            total_chemicals_used=total_chemicals_used,
                           )



#return stock totals
@accounting.route('/bank_expenses', methods=['GET', 'POST'])
def bank_expenses():
    if request.method == 'POST':
        try:
            data = {
                'date': request.form.get('date'),
                'description': request.form.get('description'),
                'amount': float(request.form.get('amount'))
            }
            supabase.table('bank_expenses').insert(data).execute()
            flash('Expense added successfully', 'success')
            return redirect(url_for('accounting.bank_expenses'))
        except Exception as e:
            flash(f'Error adding expense: {str(e)}', 'error')

    try:
        expenses = supabase.table('bank_expenses').select('*').order('date', desc=True).execute().data
        total = sum(expense['amount'] for expense in expenses if expense['amount'])
        return render_template('accounts/bank_expenses.html', expenses=expenses, total=total)
    except Exception as e:
        print(f"Error fetching expenses: {str(e)}")
        return render_template('accounts/bank_expenses.html', expenses=[], total=0)

@accounting.route('/edit_bank_expense/<int:id>', methods=['POST'])
def edit_bank_expense(id):
    try:
        data = {
            'date': request.form.get('date'),
            'description': request.form.get('description'),
            'amount': float(request.form.get('amount'))
        }
        supabase.table('bank_expenses').update(data).eq('id', id).execute()
        flash('Expense updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating expense: {str(e)}', 'error')
    return redirect(url_for('accounting.bank_expenses'))

@accounting.route('/delete_bank_expense/<int:id>', methods=['POST'])
def delete_bank_expense(id):
    try:
        supabase.table('bank_expenses').delete().eq('id', id).execute()
        flash('Expense deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'error')
    return redirect(url_for('accounting.bank_expenses'))



@accounting.route('/poles_summary')
def poles_summary():
    try:
        # Get all rows from the table
        response = supabase.table('kdl_treated_poles').select('*').execute()
        rows = response.data

        # Initialize sums dictionary
        summary = {
            'Rafters': 0,
            'Timber': 0,
            'Fencing Poles': 0,
            'Telecom Poles': 0,
            '7m Poles': 0,
            '8m Poles': 0,
            '9m Poles': 0,
            '10m Poles': 0,
            '11m Poles': 0,
            '12m Poles': 0,
            '14m Poles': 0,
            '16m Poles': 0,
            'Stubs': 0,
            '9m Telecom': 0,
            '10m Telecom': 0,
            '12m Telecom': 0
        }

        # Sum values row by row
        for row in rows:
            summary['Rafters'] += float(row.get('rafters') or 0)
            summary['Timber'] += float(row.get('timber') or 0)
            summary['Fencing Poles'] += float(row.get('fencing_poles') or 0)
            summary['Telecom Poles'] += float(row.get('telecom_poles') or 0)
            summary['7m Poles'] += float(row.get('7m') or 0)
            summary['8m Poles'] += float(row.get('8m') or 0)
            summary['9m Poles'] += float(row.get('9m') or 0)
            summary['10m Poles'] += float(row.get('10m') or 0)
            summary['11m Poles'] += float(row.get('11m') or 0)
            summary['12m Poles'] += float(row.get('12m') or 0)
            summary['14m Poles'] += float(row.get('14m') or 0)
            summary['16m Poles'] += float(row.get('16m') or 0)
            summary['Stubs'] += float(row.get('stubs') or 0)
            summary['9m Telecom'] += float(row.get('9m_telecom') or 0)
            summary['10m Telecom'] += float(row.get('10m_telecom') or 0)
            summary['12m Telecom'] += float(row.get('12m_telecom') or 0)

        return render_template('accounts/poles_summary.html', summary=summary)

    except Exception as e:
        print(f"Error getting poles summary: {str(e)}")
        return render_template('accounts/poles_summary.html', summary={})
    



def calculate_treatment_summary(treatments):
    """Calculate summary statistics from treatment data"""
    summary = {
        'total_liters': 0.0,
        'total_kegs': 0,
        'total_poles': 0,
        'total_treatments': len(treatments) if treatments else 0
    }

    if not treatments:
        return summary

    for treatment in treatments:
        # Sum up liters_added
        summary['total_liters'] += float(treatment.get('liters_added', 0) or 0)
        
        # Sum up kegs_added
        summary['total_kegs'] += float(treatment.get('kegs_added', 0) or 0)
        
        # Sum up all pole types
        pole_types = ['fencing_poles', 'rafters', 'timber', 'stubs', 
                     '7m', '8m', '9m', '9m_telecom', '10m', '10m_telecom',
                     '11m', '12m', '12m_telecom', '14m', '16m']
        
        for pole_type in pole_types:
            summary['total_poles'] += float(treatment.get(pole_type, 0) or 0)

    return summary

@accounting.route('/treatment_stats')
def treatment_stats():
    try:
        # Fetch treatments with client information using foreign key relationship
        treatments = supabase.from_('treatment_log')\
            .select('''
                *,
                client:clients(id, name)
            ''')\
            .order('date', desc=True)\
            .execute()

        # Calculate summary with default values
        treatment_summary = calculate_treatment_summary(treatments.data)

        return render_template('accounts/treatment_stats.html',
                             treatments=treatments.data,
                             treatment_summary=treatment_summary)
    except Exception as e:
        print(f"Error: {str(e)}")
        # Return empty summary with default values on error
        return render_template('accounts/treatment_stats.html',
                             treatments=[],
                             treatment_summary={
                                 'total_liters': 0.0,
                                 'total_kegs': 0,
                                 'total_poles': 0,
                                 'total_treatments': 0
                             })
    





@accounting.route('/sorted_data', methods=['GET', 'POST'])
def sorted_data():
    try:
        if request.method == 'POST':
            # Get payment details 
            supplier_id = request.form.get('supplier_id')
            sorted_data_id = request.form.get('sorted_data_id')
            amount = float(request.form.get('amount'))
            
            # Get sorted data record
            sorted_record = supabase.table('sorted_data').select('*').eq('id', sorted_data_id).execute().data[0]
            print(f"Sorted Record: {sorted_record}")
            
            # Update amount_paid in sorted_data
            new_amount_paid = float(sorted_record['amount_paid'] or 0) + amount
            supabase.table('sorted_data').update({
                'amount_paid': new_amount_paid,
                'payment_status': 'paid' if new_amount_paid >= float(sorted_record['total_pay'] or 0) else 'partial'
            }).eq('id', sorted_data_id).execute()

            # Create description by checking which columns have values
            pole_columns = ['fencing_poles', '7m', '8m', '9m', '9m_telecom', '10m', '10m_telecom', 
                            '11m', '12m', '12m_telecom', '14m', '16m', 'rafters', 'timber', 
                            'telecom_poles', 'stubs']
            
            descriptions = []
            for col in pole_columns:
                if sorted_record.get(col) and float(sorted_record[col] or 0) > 0:
                    descriptions.append(f"{col}: {sorted_record[col]}")
            
            description = "Purchase of poles - " + ", ".join(descriptions)

            # Insert into purchases table
            purchase_data = {
                'supplier': supplier_id,
                'total_amount': amount,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            supabase.table('purchases').insert(purchase_data).execute()

            flash('Payment recorded successfully', 'success')
            return redirect(url_for('accounting.sorted_data'))

        # GET request - fetch data
        selected_supplier = request.args.get('supplier_id')
        suppliers = supabase.table('suppliers').select('*').execute().data

        # Fetch sorted records based on supplier selection
        if selected_supplier:
            sorted_records = supabase.table('sorted_data')\
                .select('*')\
                .eq('supplier_id', selected_supplier)\
                .execute()\
                .data
        else:
            sorted_records = supabase.table('sorted_data').select('*').execute().data

        # Calculate totals for the filtered records
        total_amount = sum(float(record.get('total_pay', 0) or 0) for record in sorted_records)
        total_paid = sum(float(record.get('amount_paid', 0) or 0) for record in sorted_records)
        total_outstanding = total_amount - total_paid

        return render_template('accounts/pay_suppliers.html', 
                            sorted_records=sorted_records,
                            suppliers=suppliers,
                            selected_supplier=selected_supplier,
                            total_amount=total_amount,
                            total_paid=total_paid,
                            total_outstanding=total_outstanding)

    except Exception as e:
        print(f"Error in sorted_data: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return render_template('accounts/pay_suppliers.html', 
                            sorted_records=[],
                            suppliers=[],
                            selected_supplier=None,
                            total_amount=0,
                            total_paid=0,
                            total_outstanding=0)
    


# Get client details
@accounting.route('/savanna')
def savanna():
    try:
        # Fetch stock from all 3 tables for client_id 18
        untreated = supabase.table('client_untreated_stock').select("*").eq('client_id', 18).execute().data
        treated = supabase.table('clients_treated_poles').select("*").eq('client_id', 18).execute().data 
        unsorted = supabase.table('clients_unsorted').select("*").eq('client_id', 18).execute().data

        # Get client details
        client = supabase.table('clients').select("*").eq('id', 18).execute().data[0]

        return render_template('accounts/savanna.html',
                            untreated=untreated,
                            treated=treated, 
                            unsorted=unsorted,
                            client=client)

    except Exception as e:
        flash(f'Error fetching client stock: {str(e)}', 'danger')
        return render_template('accounts/savanna.html',
                            untreated=[],
                            treated=[],
                            unsorted=[],
                            client=None)
    


@accounting.route('/purchase_orders', methods=['GET', 'POST'])
def purchase_orders():
    if request.method == 'POST':
        try:
            # Get form data
            order_data = {
                'customer_id': request.form.get('customer_id'),
                'lpo_number': request.form.get('lpo_number'),
                '7m': request.form.get('7m'),
                '8m': request.form.get('8m'), 
                '9m': request.form.get('9m'),
                '10m': request.form.get('10m'),
                '12m': request.form.get('12m'),
                '14m': request.form.get('14m'),
                'notes': request.form.get('notes')
            }

            # Insert purchase order
            result = supabase.table('purchase_order').insert(order_data).execute()
            
            # If dispatch details provided, create dispatch order
            if request.form.get('dispatch_to'):
                dispatch_data = {
                    'purchases_order_id': result.data[0]['id'],
                    'dispatch_to': request.form.get('dispatch_to'),
                    '7m': request.form.get('7m'),
                    '8m': request.form.get('8m'),
                    '9m': request.form.get('9m'), 
                    '10m': request.form.get('10m'),
                    '12m': request.form.get('12m'),
                    '14m': request.form.get('14m'),
                    'deadline': request.form.get('deadline'),
                    'location': request.form.get('location')
                }
                supabase.table('dispatch_order').insert(dispatch_data).execute()

            flash('Order created successfully', 'success')
            return redirect(url_for('accounting.purchase_orders'))

        except Exception as e:
            flash(f'Error creating order: {str(e)}', 'error')
            return redirect(url_for('accounting.purchase_orders'))

    # GET - fetch orders and customers
    try:
        orders = supabase.table('purchase_order')\
            .select('*, customers(id, full_name), dispatch_order(*)')\
            .order('created_at', desc=True)\
            .execute()
        
        customers = supabase.table('customers').select('id, full_name').execute()

        return render_template('accounts/purchase_orders.html',
                            orders=orders.data,
                            customers=customers.data)

    except Exception as e:
        flash(f'Error fetching orders: {str(e)}', 'error')
        return render_template('accounts/purchase_orders.html',
                            orders=[],
                            customers=[])

@accounting.route('/dispatch_orders', methods=['GET', 'POST'])
def dispatch_orders():
    if request.method == 'POST':
        try:
            dispatch_data = {
                'purchases_order_id': request.form.get('purchase_order_id'),
                'dispatch_to': request.form.get('dispatch_to'),
                '7m': request.form.get('7m'),
                '8m': request.form.get('8m'),
                '9m': request.form.get('9m'),
                '10m': request.form.get('10m'),
                '12m': request.form.get('12m'),
                '14m': request.form.get('14m'),
                'deadline': request.form.get('deadline'),
                'location': request.form.get('location')
            }
            result = supabase.table('dispatch_order').insert(dispatch_data).execute()
            flash('Dispatch order created successfully', 'success')
            return redirect(url_for('accounting.dispatch_orders'))
        except Exception as e:
            flash(f'Error creating dispatch order: {str(e)}', 'error')
            return redirect(url_for('accounting.dispatch_orders'))

    try:
        dispatch_orders = supabase.table('dispatch_order')\
            .select('''*, purchase_order:purchase_order(id, customer_id, notes, created_at, customers(id, full_name))''')\
            .order('created_at', desc=True)\
            .execute()
        
        purchase_orders = supabase.table('purchase_order')\
            .select('*, customers(id, full_name)')\
            .order('created_at', desc=True)\
            .execute()

        return render_template('accounts/dispatch_orders.html',
                            dispatch_orders=dispatch_orders.data,
                            purchase_orders=purchase_orders.data)
    except Exception as e:
        flash(f'Error fetching dispatch orders: {str(e)}', 'error')
        return render_template('accounts/dispatch_orders.html',
                            dispatch_orders=[],
                            purchase_orders=[])
    


@accounting.route('/quotations', methods=['GET', 'POST'])
def quotation():
    if request.method == 'POST':
        try:            # Get pole quantities and calculate total
            pole_types = ['7m', '8m', '9m', '10m', '11m', '12m', '14m', '16m', 
                         'fencing_poles', 'rafters', 'timber', 'telecom_poles', 'stubs']
            
            total_qty = 0
            quotation_data = {
                'customer_id': request.form.get('customer_id'),
                'details': request.form.get('details'),
                'rate': float(request.form.get('rate', 0))
            }
            
            # Add each pole type quantity to the data and calculate total
            for pole_type in pole_types:
                qty = float(request.form.get(pole_type, 0) or 0)
                quotation_data[pole_type] = qty
                total_qty += qty
            
            # Calculate amounts
            amount = quotation_data['rate'] * total_qty
            vat = amount * 0.18
            
            # Add calculated fields
            quotation_data.update({
                'total_amount': amount + vat,
                'vat_18percent': vat
            })

            # Insert quotation
            result = supabase.table('quotations').insert(quotation_data).execute()
            flash('Quotation created successfully', 'success')
            return redirect(url_for('accounting.quotations'))

        except Exception as e:
            flash(f'Error creating quotation: {str(e)}', 'error')
            return redirect(url_for('accounting.quotations'))

    try:        # Fetch quotations with customer details
        quotations = supabase.table('quotations')\
            .select('*, customers(id, full_name)')\
            .order('created_at', desc=True)\
            .execute()

        # Fetch customers for dropdown
        customers = supabase.table('customers').select('id, full_name').execute()

        # Convert quotation data to regular dictionaries to avoid dict.items() method issue
        quotations_data = []
        for q in quotations.data:
            q_dict = dict(q)  # Convert to regular dictionary
            q_dict['items'] = q.get('items', '')  # Get items value directly
            quotations_data.append(q_dict)

        return render_template('accounts/quotations.html',
                            quotations=quotations_data,
                            customers=customers.data)

    except Exception as e:
        flash(f'Error fetching quotations: {str(e)}', 'error')
        return render_template('accounts/quotations.html',
                            quotations=[],
                            customers=[])