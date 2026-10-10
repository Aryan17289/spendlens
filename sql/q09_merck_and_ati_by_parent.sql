-- Why do Merck and Advanced Technology International each appear twice in the top 10?
SELECT vendor_name, uei, parent_uei, parent_name,
       COUNT(*)                        AS rows,
       ROUND(SUM(obligation) / 1e6, 2) AS net_millions,
       MIN(action_date)                AS first_action,
       MAX(action_date)                AS last_action
FROM explore.tx
WHERE vendor_name IN ('MERCK SHARP & DOHME LLC', 'ADVANCED TECHNOLOGY INTERNATIONAL')
GROUP BY ALL
ORDER BY vendor_name, net_millions DESC NULLS LAST