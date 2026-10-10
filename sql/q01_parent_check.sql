-- Is parent_uei a useful answer key? How often is the parent just the vendor itself?
SELECT COUNT(*)                                                     AS total_rows,
       COUNT(*) FILTER (WHERE parent_uei = uei)                     AS parent_is_self,
       COUNT(*) FILTER (WHERE parent_uei <> uei)                    AS parent_is_different,
       COUNT(*) FILTER (WHERE UPPER(parent_name) = UPPER(vendor_name)) AS parent_name_same_as_vendor_name
FROM explore.tx