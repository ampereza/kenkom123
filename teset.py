@accounting.route('/accounts_dashboard')
def accounts_dashboard():
    try:
        # Get current date
        current_date = datetime.now()

        # Daily totals
        daily_sales = supabase.table('sales').select('sum(total_amount)').eq('date', current_date.date().isoformat()).execute().data[0]['sum']
        daily_expenses = supabase.table('expenses').select('sum(amount)').eq('date', current_date.date().isoformat()).execute().data[0]['sum'] 
        daily_purchases = supabase.table('purchases').select('sum(total_amount)').eq('date', current_date.date().isoformat()).execute().data[0]['sum']

        # Weekly totals (last 7 days)
        week_ago = (current_date - timedelta(days=7)).date().isoformat()
        weekly_sales = supabase.table('sales').select('sum(total_amount)').gte('date', week_ago).execute().data[0]['sum']
        weekly_expenses = supabase.table('expenses').select('sum(amount)').gte('date', week_ago).execute().data[0]['sum']
        weekly_purchases = supabase.table('purchases').select('sum(total_amount)').gte('date', week_ago).execute().data[0]['sum']

        # Monthly totals (last 30 days)
        month_ago = (current_date - timedelta(days=30)).date().isoformat()
        monthly_sales = supabase.table('sales').select('sum(total_amount)').gte('date', month_ago).execute().data[0]['sum']
        monthly_expenses = supabase.table('expenses').select('sum(amount)').gte('date', month_ago).execute().data[0]['sum']
        monthly_purchases = supabase.table('purchases').select('sum(total_amount)').gte('date', month_ago).execute().data[0]['sum']

        # Annual totals (last 365 days)
        year_ago = (current_date - timedelta(days=365)).date().isoformat()
        annual_sales = supabase.table('sales').select('sum(total_amount)').gte('date', year_ago).execute().data[0]['sum']
        annual_expenses = supabase.table('expenses').select('sum(amount)').gte('date', year_ago).execute().data[0]['sum']
        annual_purchases = supabase.table('purchases').select('sum(total_amount)').gte('date', year_ago).execute().data[0]['sum']

        return render_template('accounts/accounts_dashboard.html', 
                               daily_totals={
                                   'sales': daily_sales or 0,
                                   'expenses': daily_expenses or 0,
                                   'purchases': daily_purchases or 0
                               },
                               weekly_totals={
                                   'sales': weekly_sales or 0,
                                   'expenses': weekly_expenses or 0, 
                                   'purchases': weekly_purchases or 0
                               },
                               monthly_totals={
                                   'sales': monthly_sales or 0,
                                   'expenses': monthly_expenses or 0,
                                   'purchases': monthly_purchases or 0
                               },
                               annual_totals={
                                   'sales': annual_sales or 0,
                                   'expenses': annual_expenses or 0,
                                   'purchases': annual_purchases or 0
                               })

    except Exception as e:
        print(f"Error getting totals: {str(e)}")
        return {'error': str(e)}, 500
