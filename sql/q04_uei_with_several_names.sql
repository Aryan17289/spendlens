-- The only UEI(s) that appear under more than one name
SELECT uei, vendor_name, COUNT(*) AS rows, ROUND(SUM(obligation) / 1e6, 2) AS net_millions
FROM explore.tx
WHERE uei IN (SELECT uei FROM explore.tx WHERE uei IS NOT NULL GROUP BY uei HAVING COUNT(DISTINCT vendor_name) > 1)
GROUP BY uei, vendor_name
ORDER BY uei, rows DESC