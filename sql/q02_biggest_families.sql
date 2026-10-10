-- Corporate families: one parent_uei covering several vendor registrations (UEIs)
SELECT parent_uei,
       MODE(parent_name)                                                      AS parent_name,
       COUNT(DISTINCT uei)                                                    AS ueis,
       COUNT(DISTINCT vendor_name)                                            AS names,
       array_to_string(list_slice(list(DISTINCT vendor_name), 1, 5), ' | ')   AS example_names,
       ROUND(SUM(obligation) / 1e6, 2)                                        AS net_millions
FROM explore.tx
WHERE parent_uei IS NOT NULL
GROUP BY parent_uei
HAVING COUNT(DISTINCT uei) > 1
ORDER BY ueis DESC, net_millions DESC NULLS LAST
LIMIT 10