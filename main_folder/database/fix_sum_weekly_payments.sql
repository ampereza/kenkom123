CREATE OR REPLACE FUNCTION public.sum_weekly_payments()
RETURNS TABLE(worker_id INT, total_pay NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT dw.worker_id, SUM(dw.total_pay)
    FROM daily_work dw
    WHERE dw.date >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY dw.worker_id;
END;
$$ LANGUAGE plpgsql;
