-- Are the file's own unique keys really unique? (needed for the Part 4 table design)
SELECT COUNT(*)                                         AS rows,
       COUNT(DISTINCT contract_transaction_unique_key)  AS distinct_transaction_keys,
       COUNT(DISTINCT contract_award_unique_key)        AS distinct_award_keys,
       COUNT(DISTINCT award_id_piid)                     AS distinct_piids
FROM raw.transactions