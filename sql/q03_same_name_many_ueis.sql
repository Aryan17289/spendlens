-- Same vendor name, more than one UEI (e.g. the Merck and Advanced Technology International cases)
SELECT vendor_name,
       COUNT(DISTINCT uei)             AS ueis,
       COUNT(DISTINCT parent_uei)      AS parents,
       ROUND(SUM(obligation) / 1e6, 2) AS net_millions
FROM explore.tx
GROUP BY vendor_name
HAVING COUNT(DISTINCT uei) > 1
ORDER BY net_millions DESC NULLS LAST
LIMIT 15