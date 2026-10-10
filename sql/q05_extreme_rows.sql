-- Sanity check: the 5 biggest and 5 smallest (most negative) transactions, with descriptions
(SELECT 'largest' AS kind, piid, mod_number, action_date, vendor_name, obligation, left(description, 80) AS description
 FROM explore.tx ORDER BY obligation DESC NULLS LAST LIMIT 5)
UNION ALL
(SELECT 'smallest', piid, mod_number, action_date, vendor_name, obligation, left(description, 80)
 FROM explore.tx ORDER BY obligation ASC NULLS LAST LIMIT 5)