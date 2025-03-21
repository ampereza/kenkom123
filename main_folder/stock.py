from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint

stock = Blueprint('stock', __name__)

#templates for this blueprint are in the stock folder

#routes for this blueprint
#stock_dashboard
#recieve_stock
#stock_report
#sort_stock
#delivery_note
#stock_transfer
#recieveclientsstock
#stock_adjustment


@stock.route('/stock_dashboard')
def stock_dashboard():
    return render_template('stock/stock_dashboard.html')

@stock.route('/recieve_stock')
def recieve_stock():
    return render_template('stock/recieve_stock.html')

@stock.route('/stock_report')
def stock_report():
    return render_template('stock/stock_report.html')

@stock.route('/sort_stock')
def sort_stock():
    return render_template('stock/sort_stock.html')

@stock.route('/delivery_note')
def delivery_note():
    return render_template('stock/delivery_note.html')

@stock.route('/stock_transfer')
def stock_transfer():
    return render_template('stock/stock_transfer.html')

@stock.route('/recieveclientsstock')
def recieveclientsstock():
    return render_template('stock/recieveclientsstock.html')

@stock.route('/stock_adjustment')
def stock_adjustment():
    return render_template('stock/stock_adjustment.html')





