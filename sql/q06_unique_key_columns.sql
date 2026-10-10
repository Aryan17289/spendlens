-- Which raw columns look like unique IDs for a transaction or an award?
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'raw' AND table_name = 'transactions'
  AND (column_name ILIKE '%unique_key%' OR column_name ILIKE '%unique_id%')
ORDER BY column_name