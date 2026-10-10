-- Vendors (UEIs) recorded under more than one parent ID
SELECT uei,
       MODE(vendor_name)                                                    AS vendor_name,
       COUNT(DISTINCT parent_uei)                                           AS parent_ids,
       array_to_string(list_slice(list(DISTINCT parent_name), 1, 3), ' | ') AS parent_names,
       ROUND(SUM(obligation) / 1e6, 2)                                      AS net_millions,
       COUNT(*) OVER ()                                                     AS total_ueis_with_multiple_parents
FROM explore.tx
WHERE uei IS NOT NULL
GROUP BY uei
HAVING COUNT(DISTINCT parent_uei) > 1
ORDER BY net_millions DESC NULLS LAST
LIMIT 15