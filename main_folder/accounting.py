from flask import Flask, render_template, request, redirect, url_for, flash, session, Blueprint
from flask_login import login_required, current_user
import uuid
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

import os
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
#@login_required
def accounting_dashboard():
    return render_template('accounts/accounts_dashboard.html')





@accounting.route('/receipts', methods=['GET', 'POST'])
def receipts():
    if request.method == 'POST':
        # Retrieve and validate form data
        receipt_type = request.form.get('receipt_type')
        client_id = request.form.get('client_id')
        customer_id = request.form.get('customer_id')
        amount = request.form.get('amount')
        description = request.form.get('description')
        
        if not receipt_type or not client_id or not customer_id or not amount or not description:
            flash('All fields are required.', 'danger')
            return redirect(url_for('accounting.receipts'))

        try:
            amount = float(amount)
        except ValueError:
            flash('Amount must be a valid number.', 'danger')
            return redirect(url_for('accounting.receipts'))

        # Generate receipt data
        receipt_id = str(uuid.uuid4())
        receipt_number = f"REC-{uuid.uuid4().hex[:8].upper()}"
        date_created = datetime.utcnow().isoformat()
        
        # Prepare receipt data for insertion
        receipt_data = {
            "id": receipt_id,
 #           "user_id": current_user.id,
            "type": receipt_type,
            "client_id": client_id,
            "customer_id": customer_id,
            "amount": amount,
            "description": description,
            "receipt_number": receipt_number,
            "date": date_created
        }
        
        # Insert receipt into Supabase
        try:
            response = supabase.table('receipts').insert(receipt_data).execute()
            if response.status_code == 201:
                flash(f'Receipt {receipt_number} created successfully!', 'success')
                print(response.data)  # Log the response data for debugging
            else:
                flash('Failed to create receipt. Please try again.', 'danger')
                print(response.error)  # Log the error for debugging
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print(f'Error: {str(e)}')

        return redirect(url_for('accounting.receipts'))

    # Fetch clients, customers, and receipts
    try:
        clients = supabase.table('clients').select("id, name").execute().data
        print(clients)

        customers = supabase.table('customers').select("id, full_name").execute().data
        print(customers)

        receipts = supabase.table('receipts').select("*", "client_id(name)", "customer_id(full_name)").order("date", desc=True).execute().data
    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(f'Error: {str(e)}')
        clients = customers = receipts = []

    return render_template('accounts/receipts.html', clients=clients, customers=customers, receipts=receipts)



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



@accounting.route('/create_invoice', methods=['POST'])
# @login_required
def create_invoice():
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

    

@accounting.route('/invoices')
def invoices():
    try:
        # Fetch all payment vouchers from the database (Example: Supabase)
        response = supabase.table('invoices').select('*').execute()
        print(response)
        if response:
            invoices = response.data  # This contains the payment voucher records
        else:
            invoices = []

        return render_template('accounts/invoices.html', invoices= invoices)

    except Exception as e:
        print(f"Error fetching payment vouchers: {str(e)}")
        return render_template('accounts/invoices.html', invoices=[])



@accounting.route('/get_customer')
#@login_required
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
    if request.method == 'POST':
        # Retrieve and validate form data
        sale_type = request.form.get('sale_type')
        client_id = request.form.get('client_id')
        customer_id = request.form.get('customer_id')
        amount = request.form.get('amount')
        description = request.form.get('description')

        # Check for missing fields
        missing_fields = []
        if not sale_type:
            missing_fields.append('Sale Type')
        if not client_id:
            missing_fields.append('Client ID')
        if not customer_id:
            missing_fields.append('Customer ID')
        if not amount:
            missing_fields.append('Amount')
        if not description:
            missing_fields.append('Description')

        if missing_fields:
            flash(f'Missing fields: {", ".join(missing_fields)}', 'danger')
            return redirect(url_for('accounting.sales'))

        try:
            amount = float(amount)
            client_id = int(client_id)
            customer_id = int(customer_id)
        except ValueError:
            flash('Amount, Client ID, and Customer ID must be valid numbers.', 'danger')
            return redirect(url_for('accounting.sales'))

        # Generate receipt data
        date_created = datetime.utcnow().isoformat()
        quantity = float(request.form.get('quantity'))
        rate = float(request.form.get('unit_price'))
        total_amount = rate * quantity

        receipt_data = {
            "sale_type": sale_type,
            "client_id": client_id,
            "customer_id": customer_id,
            "total_amount": total_amount,
            "description": description,
            "date": date_created,
            "quantity": quantity,
            "rate": rate
        }

        # Insert receipt into Supabase
        try:
            response = supabase.table('sales').insert(receipt_data).execute()
            if response:
                print(f"Inserted data: {response.data}")
                flash('Sale created successfully!', 'success')
            else:
                flash('Failed to create receipt. Please try again.', 'danger')
                print(f"Error: {response.error}")
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            print(f'Error: {str(e)}')

        return redirect(url_for('accounting.sales'))

    # Fetch clients, customers, and sales
    try:
        clients = supabase.table('clients').select("id, name").execute().data
       # print(f"client_id: {client_id}, type: {type(client_id)}")

        customers = supabase.table('customers').select("id, full_name").execute().data
        #print(f"customer_id: {customer_id}, type: {type(customer_id)}")

        sales = supabase.table('sales').select("*", "client_id(name)", "customer_id(full_name)").order("date", desc=True).execute().data
        print(f"Sales: {sales}")
        # Validate fetched data
        if not all(isinstance(client['id'], int) for client in clients):
            flash('Invalid client data fetched.', 'danger')
            print(f"Clients: {clients}")
            clients = []

        if not all(isinstance(customer['id'], int) for customer in customers):
            flash('Invalid customer data fetched.', 'danger')
            print(f"Customers: {customers}")
            customers = []

    except Exception as e:
        flash(f'Error fetching data: {str(e)}', 'danger')
        print(f'Error: {str(e)}')
        clients = customers = sales = []

    return render_template('accounts/add_sales.html', clients=clients, customers=customers, sales=sales)





@accounting.route('/clients_ledger')
def clients_ledger():
    try:
        # Fetch all clients from the database
        clients = supabase.table('clients').select('*').execute().data

        # Fetch all treatment prices from the treatment_price table
        prices = supabase.table('treatment_price').select('*').execute().data
        # Create a dictionary mapping treatment category names to prices
        price_dict = {}
        for p in prices:
            if 'category' in p and 'price' in p:
                price_dict[p['category']] = p['price']

        # Fetch client names for display
        client_names = supabase.table('clients').select('name').execute().data
        client_list = [client['name'] for client in client_names]
        print(f"Available clients: {client_list}")

        # Define the treatment categories (i.e., columns in clients_treated_poles)
        treatment_categories = ['telecom_poles', '9m', '10m', '11m', '12m', '14m', '16m', '7m', '8m']

        ledger_entries = []

        # Process each client's data
        for client in clients:
            total_charge = 0
            poles_by_category = {}

            # Get all treated poles for the current client
            poles = supabase.table('clients_treated_poles').select('*').eq('client_id', client['id']).execute().data

            # Iterate over each record and each treatment category column
            for pole in poles:
                for category in treatment_categories:
                    # Convert the value to an integer (defaulting to 0 if missing)
                    try:
                        count = int(pole.get(category, 0))
                    except ValueError:
                        count = 0
                    if count:
                        poles_by_category[category] = poles_by_category.get(category, 0) + count

            # Calculate total charge by summing each category's count multiplied by its price
            for category, count in poles_by_category.items():
                unit_price = price_dict.get(category, 0)
                total_charge += count * unit_price

            # Calculate total payments made by the client
            payments = supabase.table('receipts').select('amount').eq('client_id', client['id']).execute().data
            total_paid = sum(payment['amount'] for payment in payments)

            # Calculate remaining balance
            balance = total_charge - total_paid

            # Create a ledger entry for the client
            ledger_entry = {
                'client_name': client['name'],
                'poles_by_category': poles_by_category,
                'total_poles': sum(poles_by_category.values()),
                'total_charge': total_charge,
                'total_paid': total_paid,
                'balance': balance
            }
            ledger_entries.append(ledger_entry)

        # Render the ledger template with the collected data
        return render_template('accounts/clients_ledger.html', 
                               price_dict = price_dict,
                               ledger_entries=ledger_entries,
                               categories=price_dict.keys(),
                               client_list=client_list)

    except Exception as e:
        print(f"Error generating ledger: {str(e)}")
        return render_template('accounts/clients_ledger.html', 
                                 price_dict = price_dict,
                               ledger_entries=[], 
                               categories=[],
                               clients=[])





















@accounting.route('/inventory')
#@login_required
def inventory():
    return render_template('accounts/inventory.html')

@accounting.route('/invoice')
#@login_required
def invoice():
    return render_template('accounts/invoice.html')

@accounting.route('/ledgers')
#@login_required
def ledgers():
    return render_template('accounts/ledgers.html')

@accounting.route('/payroll')
#@login_required
def payroll():
    return render_template('accounts/payroll.html')

@accounting.route('/reports')
#@login_required
def reports():
    return render_template('accounts/reports.html')

@accounting.route('/taxes')
#@login_required
def taxes():
    return render_template('accounts/taxes.html')