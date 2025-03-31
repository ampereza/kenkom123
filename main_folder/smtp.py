# importing the requests library
from flask import Flask, request, jsonify, url_for, render_template, redirect, session, flash, Blueprint
import smtplib
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import json
import requests
import html


smtp = Blueprint('smtp', __name__)
load_dotenv()

# Initialize the Supabase client
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
secret_key = os.getenv("SECRET_KEY")


# The api url
url = "https://www.egosms.co/api/v1/plain/"

# The parameters to be sent to the ego sms api
password = "xKgWUPwD@QAs5"
username = "beampereza"
sender = "Egosms"
number = "256751057354"
message = "This is a message"



parameters = {
    'username': html.escape(username),
    'password': html.escape(password),
    'number': html.escape(number),
    'message': html.escape(message),
    'sender': html.escape(sender)
}

timeout = 5

# Check for the internet connection and make the request
try:
    # sending post request and saving response as response object
    r = requests.get(url=url, params=parameters, timeout=timeout)

    # extracting response text
    response = r.text

    print(response)

except(requests.ConnectionError, requests.Timeout) as exception:
    print("Check your internet connection")



