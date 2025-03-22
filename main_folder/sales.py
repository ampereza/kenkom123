from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from datetime import datetime

sales = Blueprint('sales', __name__)

# Load environment variables from .env file
load_dotenv()

# Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
SECRET_KEY = os.getenv("SECRET_KEY")


@sales.route('/add_sale', methods=['POST'])
def add_sale():
    data = request.json

    # Extract sale details
    product_id = data.get('category_id')  # Changed from 'item_id' to 'category_id'
    customer_id = data.get('customer_id')  # Optional, can be None
    quantity = data.get('quantity')
    discount = data.get('discount', 0)  # Default to 0 if no discount is provided

    # Validate input
    if not product_id or not quantity:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Fetch price details from the pricing config
        price_config = supabase.table('pricing_config').select("*").eq("id", product_id).single().execute()
        
        if not price_config.data:
            return jsonify({"error": "Item not found"}), 404

        # Extract pricing details
        unit_price = price_config.data.get('sale_price', 0)

        # Calculate total amount with discount
        total_amount = (unit_price * quantity) - discount

        # Ensure total_amount is not negative
        total_amount = max(total_amount, 0)

        sale_date = datetime.now()  # Automatically set the sale date

        # Prepare sale data to insert into sales table
        sale = {
            "product_id": product_id,
            "customer_id": customer_id,
            "quantity": quantity,
            "total_amount": total_amount,
            "sale_date": sale_date.isoformat()
        }

        # Insert the sale into Supabase
        result = supabase.table('sales').insert(sale).execute()

        if result.status_code == 201:
            return jsonify({"message": "Sale added successfully", "sale": result.data}), 201
        else:
            return jsonify({"error": result.error_message}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sales.route('/get_price_config', methods=['GET'])
def get_price_config():
    category_id = request.args.get('category_id')  # Changed from 'item_id' to 'category_id'

    if not category_id:
        return jsonify({"error": "Category ID is required"}), 400
        print(category_id) # Added to debug

    try:
        # Fetch the category's price config from Supabase
        price_config = supabase.table('pricing_config').select("*").eq("category_id", category_id).single().execute()  # Updated to filter by 'category_id'

        if not price_config.data:
            return jsonify({"error": "Category not found"}), 404
        print (price_config.data) # Added to debug

        return jsonify({"price_config": price_config.data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    print(error)


@sales.route('/calculate_total', methods=['POST'])
def calculate_total():
    data = request.json
    item_id = data.get('item_id')
    quantity = data.get('quantity', 0)
    discount = data.get('discount', 0)

    if not item_id or quantity <= 0:
        return jsonify({"error": "Invalid item ID or quantity"}), 400

    try:
        # Fetch the item's price config from Supabase
        price_config = supabase.table('pricing_config').select("*").eq("id", item_id).single().execute()

        if not price_config.data:
            return jsonify({"error": "Item not found"}), 404

        # Extract pricing details
        unit_price = price_config.data.get('sale_price', 0)

        total_discount = discount * quantity

        # Calculate total with discount applied
        total_price = (unit_price * quantity) - total_discount

        # Ensure total price is not negative
        total_price = max(total_price, 0)

        return jsonify({"total_price": total_price}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sales.route('/sales', methods=['GET']) 
def sales_page():
    price = supabase.table('pricing_config').select('*').execute()
    customers = supabase.table('customers').select('*').execute()

    return render_template('sales/sales.html', price=price.data, customers=customers.data)

@sales.route('/sales_report', methods=['GET'])
def sales_report():
    return render_template('sales/sales_report.html')