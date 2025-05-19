-- Function to update KDL treated poles totals
CREATE OR REPLACE FUNCTION public.update_total_kdl_treated_poles()
RETURNS TRIGGER AS $$
BEGIN
  -- Update the totals when delivering to customers (reducing from KDL stock)
  IF NEW.delivery_for = 'customer' THEN
    UPDATE public.kdl_treated_poles
    SET
      fencing_poles = GREATEST(0, COALESCE(kdl_treated_poles.fencing_poles, 0) - COALESCE(NEW.fencing_poles, 0)),
      timber = GREATEST(0, COALESCE(kdl_treated_poles.timber, 0) - COALESCE(NEW.timber, 0)),
      rafters = GREATEST(0, COALESCE(kdl_treated_poles.rafters, 0) - COALESCE(NEW.rafters, 0)),
      "7m" = GREATEST(0, COALESCE(kdl_treated_poles."7m", 0) - COALESCE(NEW."7m", 0)),
      "8m" = GREATEST(0, COALESCE(kdl_treated_poles."8m", 0) - COALESCE(NEW."8m", 0)),
      "9m" = GREATEST(0, COALESCE(kdl_treated_poles."9m", 0) - COALESCE(NEW."9m", 0)),
      "10m" = GREATEST(0, COALESCE(kdl_treated_poles."10m", 0) - COALESCE(NEW."10m", 0)),
      "11m" = GREATEST(0, COALESCE(kdl_treated_poles."11m", 0) - COALESCE(NEW."11m", 0)),
      "12m" = GREATEST(0, COALESCE(kdl_treated_poles."12m", 0) - COALESCE(NEW."12m", 0)),
      "14m" = GREATEST(0, COALESCE(kdl_treated_poles."14m", 0) - COALESCE(NEW."14m", 0)),
      "16m" = GREATEST(0, COALESCE(kdl_treated_poles."16m", 0) - COALESCE(NEW."16m", 0)),
      "9m_telecom" = GREATEST(0, COALESCE(kdl_treated_poles."9m_telecom", 0) - COALESCE(NEW."9m_telecom", 0)),
      "10m_telecom" = GREATEST(0, COALESCE(kdl_treated_poles."10m_telecom", 0) - COALESCE(NEW."10m_telecom", 0)),
      "12m_telecom" = GREATEST(0, COALESCE(kdl_treated_poles."12m_telecom", 0) - COALESCE(NEW."12m_telecom", 0))
    WHERE id = (
      SELECT id 
      FROM public.kdl_treated_poles 
      ORDER BY created_at DESC 
      LIMIT 1
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update client treated poles totals
CREATE OR REPLACE FUNCTION public.update_total_client_treated_poles()
RETURNS TRIGGER AS $$
BEGIN
  -- Update the totals when delivering to clients (reducing from client's stock)
  IF NEW.delivery_for = 'client' THEN
    UPDATE public.clients_treated_poles
    SET
      fencing_poles = GREATEST(0, COALESCE(clients_treated_poles.fencing_poles, 0) - COALESCE(NEW.fencing_poles, 0)),
      timber = GREATEST(0, COALESCE(clients_treated_poles.timber, 0) - COALESCE(NEW.timber, 0)),
      rafters = GREATEST(0, COALESCE(clients_treated_poles.rafters, 0) - COALESCE(NEW.rafters, 0)),
      "7m" = GREATEST(0, COALESCE(clients_treated_poles."7m", 0) - COALESCE(NEW."7m", 0)),
      "8m" = GREATEST(0, COALESCE(clients_treated_poles."8m", 0) - COALESCE(NEW."8m", 0)),
      "9m" = GREATEST(0, COALESCE(clients_treated_poles."9m", 0) - COALESCE(NEW."9m", 0)),
      "10m" = GREATEST(0, COALESCE(clients_treated_poles."10m", 0) - COALESCE(NEW."10m", 0)),
      "11m" = GREATEST(0, COALESCE(clients_treated_poles."11m", 0) - COALESCE(NEW."11m", 0)),
      "12m" = GREATEST(0, COALESCE(clients_treated_poles."12m", 0) - COALESCE(NEW."12m", 0)),
      "14m" = GREATEST(0, COALESCE(clients_treated_poles."14m", 0) - COALESCE(NEW."14m", 0)),
      "16m" = GREATEST(0, COALESCE(clients_treated_poles."16m", 0) - COALESCE(NEW."16m", 0)),
      "9m_telecom" = GREATEST(0, COALESCE(clients_treated_poles."9m_telecom", 0) - COALESCE(NEW."9m_telecom", 0)),
      "10m_telecom" = GREATEST(0, COALESCE(clients_treated_poles."10m_telecom", 0) - COALESCE(NEW."10m_telecom", 0)),
      "12m_telecom" = GREATEST(0, COALESCE(clients_treated_poles."12m_telecom", 0) - COALESCE(NEW."12m_telecom", 0))
    WHERE client_id = NEW.client_id
    AND id = (
      SELECT id 
      FROM public.clients_treated_poles 
      WHERE client_id = NEW.client_id
      ORDER BY created_at DESC 
      LIMIT 1
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to automatically update stock on delivery note creation
CREATE TRIGGER update_kdl_stock_on_delivery
  AFTER INSERT ON public.delivery_notes
  FOR EACH ROW
  EXECUTE FUNCTION public.update_total_kdl_treated_poles();

CREATE TRIGGER update_client_stock_on_delivery
  AFTER INSERT ON public.delivery_notes
  FOR EACH ROW
  EXECUTE FUNCTION public.update_total_client_treated_poles();
