ALTER TABLE public.kdl_untreated_stock
ALTER COLUMN id SET NOT NULL;

-- Ensure the `id` column is auto-incremented
CREATE SEQUENCE IF NOT EXISTS kdl_untreated_stock_id_seq;

ALTER TABLE public.kdl_untreated_stock
ALTER COLUMN id SET DEFAULT nextval('kdl_untreated_stock_id_seq');

-- Populate `id` for existing rows if any are NULL
UPDATE public.kdl_untreated_stock
SET id = nextval('kdl_untreated_stock_id_seq')
WHERE id IS NULL;
