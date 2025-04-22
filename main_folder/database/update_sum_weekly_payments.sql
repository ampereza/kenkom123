CREATE OR REPLACE FUNCTION public.sum_weekly_payments()
RETURNS TABLE(worker_id BIGINT, total_pay NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT dw.worker_id, SUM(dw.total_pay)
    FROM public.daily_work dw
    GROUP BY dw.worker_id;
END;
$$ LANGUAGE plpgsql;
