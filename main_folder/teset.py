from dotenv import load_dotenv
import os
from supabase import create_client, Client
from typing import Dict, Union
from flask import Blueprint, jsonify

# Initialize Flask Blueprint
teset = Blueprint('teset', __name__)

# Load environment variables
load_dotenv()

# Validate and load Supabase credentials
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise EnvironmentError("Supabase credentials are not properly set in the environment variables.")

# Initialize Supabase client
supabase: Client = create_client(supabase_url, supabase_key)

# Define mapping of table names to summation columns
TABLE_COLUMNS = {
    "expenses": "amount",
    "payment_vouchers": "total_amount",
    "purchases": "total_amount",
    "receipts": "amount",
    "salary_payments": "amount",
    "sales": "total_amount"
}

# Utility Functions
def fetch_table_sum(table_name: str) -> float:
    """
    Fetch and sum the specified column values from a Supabase table based on schema mapping.
    """
    try:
        column = TABLE_COLUMNS.get(table_name)
        if not column:
            raise KeyError(f"No summation column defined for table: {table_name}")

        response = supabase.table(table_name).select(column).execute()
        if response.data:
            return sum(record.get(column, 0.0) for record in response.data)
        return 0.0
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        return 0.0

def bal_brought_forward() -> float:
    """
    Fetch the balance brought forward from the database.
    """
    try:
        response = supabase.table("balance_brought_forward").select("balance").execute()
        if response.data:
            return response.data[0].get("balance", 0.0)
        return 0.0
    except Exception as e:
        print(f"Error fetching balance brought forward: {e}")
        return 0.0

def calculate_balances() -> Dict[str, Union[float, str]]:
    """
    Calculate financial balances using database data.
    """
    try:
        brought_forward = bal_brought_forward()
        sales = fetch_table_sum("sales")
        receipts = fetch_table_sum("receipts")
        payment_vouchers = fetch_table_sum("payment_vouchers")
        salary_payments = fetch_table_sum("salary_payments")
        purchases = fetch_table_sum("purchases")
        expenses = fetch_table_sum("expenses")

        brought_down = sales + receipts - (payment_vouchers + salary_payments + purchases + expenses)
        brought_forward += brought_down
        print (f"Calculated balances: Brought Forward: {brought_forward}, Brought Down: {brought_down}")

        return {
            "brought_forward": round(brought_forward, 2),
            
            "brought_down": round(brought_down, 2)
        }
    except KeyError as e:
        print(f"Key error: {e}")
        return {"brought_forward": "Error", "brought_down": "Error"}
    except TypeError as e:
        print(f"Type error: {e}")
        return {"brought_forward": "Error", "brought_down": "Error"}
    
    except Exception as e:
        print(f"Error calculating balances: {e}")
        return {"brought_forward": "Error", "brought_down": "Error"}

# Blueprint Routes
@teset.route('/balances', methods=['GET'])
def get_balances():
    """
    Endpoint to fetch calculated balances.
    """
    balances = calculate_balances()
    return (balances)
