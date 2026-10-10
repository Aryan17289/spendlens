# Data profile report
_Generated 2026-10-08 10:57. 66,806 transaction rows. Produced by `src/spendlens/profile_data.py`._

## 1. Size and time range

**What to look for:** How big is it? A PIID is a contract number; one contract has many transaction rows (the original award plus modifications). If your real file has a unique award key column, prefer it over PIID.

| transaction_rows | distinct_piids | distinct_vendor_names | distinct_ueis | distinct_parent_ueis | first_action_date | last_action_date |
|---|---|---|---|---|---|---|
| 66,806 | 36,056 | 8,867 | 9,026 | 9,319 | 2023-10-01 | 2024-09-30 |

<details><summary>SQL</summary>

```sql
SELECT COUNT(*)                     AS transaction_rows,
       COUNT(DISTINCT piid)         AS distinct_piids,
       COUNT(DISTINCT vendor_name)  AS distinct_vendor_names,
       COUNT(DISTINCT uei)          AS distinct_ueis,
       COUNT(DISTINCT parent_uei)   AS distinct_parent_ueis,
       MIN(action_date)             AS first_action_date,
       MAX(action_date)             AS last_action_date
FROM explore.tx
```

</details>

## 2. Rows and money per fiscal year

**What to look for:** '(unknown)' means the action date was blank or unreadable. Note how many rows that is.

| fiscal_year | transaction_rows | net_obligation_millions |
|---|---|---|
| 2024 | 66,806 | 36,760.88 |

<details><summary>SQL</summary>

```sql
SELECT COALESCE(CAST(fiscal_year AS VARCHAR), '(unknown)') AS fiscal_year,
       COUNT(*)                          AS transaction_rows,
       ROUND(SUM(obligation) / 1e6, 2)   AS net_obligation_millions
FROM explore.tx
GROUP BY 1
ORDER BY 1
```

</details>

## 3. How much is missing, column by column

**What to look for:** Columns with high pct_missing limit what we can do. Missing parent_uei is normal (many vendors have no parent). Missing uei or description matters more.

| column_name | missing_rows | pct_missing |
|---|---|---|
| award_total_value | 5,145 | 7.70 |
| competed | 668 | 1.00 |
| parent_uei | 12 | 0.02 |
| parent_name | 7 | 0.01 |
| naics | 9 | 0.01 |
| mod_number | 0 | 0.00 |
| action_date | 0 | 0.00 |
| vendor_name | 1 | 0.00 |
| piid | 0 | 0.00 |
| uei | 0 | 0.00 |
| description | 0 | 0.00 |
| psc | 1 | 0.00 |
| obligation | 0 | 0.00 |

<details><summary>SQL</summary>

```sql
SELECT * FROM (
SELECT 'piid' AS column_name, COUNT(*) FILTER (WHERE piid IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE piid IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'mod_number' AS column_name, COUNT(*) FILTER (WHERE mod_number IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE mod_number IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'action_date' AS column_name, COUNT(*) FILTER (WHERE action_date IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE action_date IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'vendor_name' AS column_name, COUNT(*) FILTER (WHERE vendor_name IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE vendor_name IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'uei' AS column_name, COUNT(*) FILTER (WHERE uei IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE uei IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'parent_name' AS column_name, COUNT(*) FILTER (WHERE parent_name IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE parent_name IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'parent_uei' AS column_name, COUNT(*) FILTER (WHERE parent_uei IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE parent_uei IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'description' AS column_name, COUNT(*) FILTER (WHERE description IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE description IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'naics' AS column_name, COUNT(*) FILTER (WHERE naics IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE naics IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'psc' AS column_name, COUNT(*) FILTER (WHERE psc IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE psc IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'obligation' AS column_name, COUNT(*) FILTER (WHERE obligation IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE obligation IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'award_total_value' AS column_name, COUNT(*) FILTER (WHERE award_total_value IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE award_total_value IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
UNION ALL
SELECT 'competed' AS column_name, COUNT(*) FILTER (WHERE competed IS NULL) AS missing_rows, ROUND(100.0 * COUNT(*) FILTER (WHERE competed IS NULL) / COUNT(*), 2) AS pct_missing FROM explore.tx
) ORDER BY pct_missing DESC
```

</details>

## 4. Obligation values that could not be read as numbers

**What to look for:** Rows listed here are dropped from every sum. If the number is large, look at the examples and decide how to fix them in Part 4.

| unreadable_rows | examples |
|---|---|
| 0 |  |

<details><summary>SQL</summary>

```sql
SELECT COUNT(*) FILTER (WHERE obligation_raw IS NOT NULL AND obligation IS NULL) AS unreadable_rows,
       array_to_string(list_slice(list(DISTINCT obligation_raw)
           FILTER (WHERE obligation_raw IS NOT NULL AND obligation IS NULL), 1, 5), ' | ') AS examples
FROM explore.tx
```

</details>

## 5. The money: positive, negative and zero obligations

**What to look for:** Negative obligations are normal: the government took money back from a contract (a de-obligation). Spend = the NET sum of obligations, so keep the negatives.

| positive_rows | negative_rows | zero_rows | gross_obligated_millions | deobligated_millions | net_millions | smallest_row | largest_row | median_row | p99_row |
|---|---|---|---|---|---|---|---|---|---|
| 37,037 | 12,628 | 17,141 | 41,022.43 | -4,261.56 | 36,760.88 | -654,561,465.17 | 686,683,980.61 | 9,732.50 | 8,623,512.16 |

<details><summary>SQL</summary>

```sql
SELECT COUNT(*) FILTER (WHERE obligation > 0)                          AS positive_rows,
       COUNT(*) FILTER (WHERE obligation < 0)                          AS negative_rows,
       COUNT(*) FILTER (WHERE obligation = 0)                          AS zero_rows,
       ROUND(SUM(obligation) FILTER (WHERE obligation > 0) / 1e6, 2)   AS gross_obligated_millions,
       ROUND(SUM(obligation) FILTER (WHERE obligation < 0) / 1e6, 2)   AS deobligated_millions,
       ROUND(SUM(obligation) / 1e6, 2)                                 AS net_millions,
       MIN(obligation)                                                 AS smallest_row,
       MAX(obligation)                                                 AS largest_row,
       ROUND(quantile_cont(CAST(obligation AS DOUBLE), 0.5), 2)        AS median_row,
       ROUND(quantile_cont(CAST(obligation AS DOUBLE), 0.99), 2)       AS p99_row
FROM explore.tx
```

</details>

## 6. The double-counting trap

**What to look for:** award_total_value is the whole contract's value, repeated on EVERY transaction row of that contract. Summing it per row inflates spend many times over. Use the obligation column for spend.

| spend_millions_correct | wrong_sum_of_total_value_per_row_millions | total_value_once_per_award_millions |
|---|---|---|
| 36,760.88 | 507,337.93 | 167,360.25 |

<details><summary>SQL</summary>

```sql
SELECT ROUND(SUM(obligation) / 1e6, 2) AS spend_millions_correct,
       ROUND((SELECT SUM(award_total_value) FROM explore.tx) / 1e6, 2) AS wrong_sum_of_total_value_per_row_millions,
       ROUND((SELECT SUM(v) FROM (SELECT MAX(award_total_value) AS v FROM explore.tx
                                  WHERE piid IS NOT NULL GROUP BY piid)) / 1e6, 2) AS total_value_once_per_award_millions
FROM explore.tx
```

</details>

## 7. The ten largest single transactions

**What to look for:** Outliers. Check whether they are real (big contracts exist) or data errors.

| piid | mod_number | action_date | vendor_name | obligation |
|---|---|---|---|---|
| 75D30123D16108 | P00003 | 2023-10-25 | MERCK SHARP & DOHME LLC | 686,683,980.61 |
| 75D30124D18656 | 0 | 2024-03-28 | MERCK SHARP & DOHME LLC | 679,068,171.01 |
| 75D30124D18658 | P00003 | 2024-08-20 | SANOFI VACCINES US INC. | 595,563,471.64 |
| 75A50123F61003 | P00001 | 2024-01-04 | ADVANCED TECHNOLOGY INTERNATIONAL | 523,524,000.00 |
| 75D30124D18656 | P00002 | 2024-06-03 | MERCK SHARP & DOHME LLC | 510,860,228.11 |
| 75D30124D18656 | P00003 | 2024-08-20 | MERCK SHARP & DOHME LLC | 494,662,515.03 |
| 75D30123D16108 | P00004 | 2024-02-05 | MERCK SHARP & DOHME LLC | 443,648,419.47 |
| 75A50123F61001 | P00002 | 2024-05-31 | ADVANCED TECHNOLOGY INTERNATIONAL | 400,000,000.00 |
| 75A50324F80002 | 0 | 2023-11-17 | GENENTECH USA, INC | 396,999,520.00 |
| 75A50123F61004 | P00001 | 2024-01-02 | ADVANCED TECHNOLOGY INTERNATIONAL | 389,473,000.00 |

<details><summary>SQL</summary>

```sql
SELECT piid, mod_number, action_date, vendor_name, obligation
FROM explore.tx
ORDER BY obligation DESC NULLS LAST
LIMIT 10
```

</details>

## 8. Vendor identifiers: how many rows have them

**What to look for:** UEI is the government's unique vendor ID. These IDs are our 'answer key' for testing vendor matching in Part 5. Rows with neither ID cannot be scored, so we want this to be small.

| pct_rows_with_uei | pct_rows_with_parent_uei | pct_rows_with_neither | pct_spend_with_neither |
|---|---|---|---|
| 100.00 | 99.98 | 0.00 |  |

<details><summary>SQL</summary>

```sql
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE uei IS NOT NULL) / COUNT(*), 2)                              AS pct_rows_with_uei,
       ROUND(100.0 * COUNT(*) FILTER (WHERE parent_uei IS NOT NULL) / COUNT(*), 2)                       AS pct_rows_with_parent_uei,
       ROUND(100.0 * COUNT(*) FILTER (WHERE uei IS NULL AND parent_uei IS NULL) / COUNT(*), 2)           AS pct_rows_with_neither,
       ROUND(100.0 * SUM(obligation) FILTER (WHERE uei IS NULL AND parent_uei IS NULL)
             / NULLIF(SUM(obligation), 0), 2)                                                            AS pct_spend_with_neither
FROM explore.tx
```

</details>

## 9. How many different names does one vendor ID have?

**What to look for:** This is the problem SpendLens solves. Every vendor above '1' is a vendor that spend reports would split into several lines.

| name_variants_per_uei | vendors |
|---|---|
| 3-5 | 1 |
| 1 | 9,025 |

<details><summary>SQL</summary>

```sql
WITH per_uei AS (
    SELECT uei, COUNT(DISTINCT vendor_name) AS name_variants
    FROM explore.tx
    WHERE uei IS NOT NULL
    GROUP BY uei
)
SELECT CASE WHEN name_variants = 1 THEN '1'
            WHEN name_variants = 2 THEN '2'
            WHEN name_variants <= 5 THEN '3-5'
            ELSE '6+' END          AS name_variants_per_uei,
       COUNT(*)                    AS vendors
FROM per_uei
GROUP BY 1
ORDER BY MIN(name_variants)
```

</details>

## 10. Worst examples of one vendor under many names

**What to look for:** Screenshot or copy 2-3 of these into your README. Concrete examples make the problem real to a recruiter.

| uei | name_variants | example_names |
|---|---|---|
| NPFUUDHHMJY1 | 1 | CECIL & CECIL ENTERPRISES INC |
| SGNAA4AGG933 | 1 | NITOR TECHNOLOGIES INC |
| M9RJXA9M7L68 | 1 | MIMETAS OPERATIONS US, CO. |
| NACNDU85S2Q2 | 1 | JBS INTERNATIONAL, INC. |
| Y7YJFTG997E7 | 1 | RMF ENGINEERING, INC., P.C. |
| CGTPPXXEB987 | 1 | SYNERGY GROUP JV, LLC |
| EATLJWKP3RE4 | 1 | EKIN SOLUTIONS INC. |
| CE11R34E5PA9 | 1 | VISTA STAFFING SOLUTIONS, INC. |

<details><summary>SQL</summary>

```sql
SELECT uei,
       COUNT(DISTINCT vendor_name) AS name_variants,
       array_to_string(list_slice(list(DISTINCT vendor_name), 1, 5), ' | ') AS example_names
FROM explore.tx
WHERE uei IS NOT NULL
GROUP BY uei
ORDER BY name_variants DESC
LIMIT 8
```

</details>

## 11. Vendor names vs real vendors (baseline)

**What to look for:** The last number is the best estimate of the true vendor count. The gap between it and the others is what Part 5 must close. Simple cleaning alone will not close it.

| raw_name_strings | after_upper_and_trim | after_removing_punctuation | entities_by_parent_or_own_uei |
|---|---|---|---|
| 8,867 | 8,867 | 8,826 | 9,325 |

<details><summary>SQL</summary>

```sql
SELECT COUNT(DISTINCT vendor_name)                                                   AS raw_name_strings,
       COUNT(DISTINCT UPPER(TRIM(vendor_name)))                                      AS after_upper_and_trim,
       COUNT(DISTINCT regexp_replace(UPPER(vendor_name), '[^A-Z0-9 ]', '', 'g'))     AS after_removing_punctuation,
       COUNT(DISTINCT COALESCE(parent_uei, uei))                                     AS entities_by_parent_or_own_uei
FROM explore.tx
```

</details>

## 12. Top ten vendors by net spend (grouped by parent or own UEI)

**What to look for:** A first look at vendor concentration, which we measure properly in Part 7. 'UNKNOWN' groups every row that has no vendor ID at all, so it is not a real vendor.

| entity | typical_name | net_millions | pct_of_total |
|---|---|---|---|
| GYXFTAF6L3W4 | MERCK SHARP & DOHME LLC | 2,200.19 | 5.99 |
| MEHNDWCSBKD5 | ADVANCED TECHNOLOGY INTERNATIONAL | 1,379.73 | 3.75 |
| MHBQULRMEEJ5 | PFIZER INC | 1,363.70 | 3.71 |
| JHSBM7A72GU5 | SANOFI VACCINES US INC. | 1,282.20 | 3.49 |
| LDMMF472BB93 | ADVANCED TECHNOLOGY INTERNATIONAL | 1,208.62 | 3.29 |
| ZL41ERXMPAR3 | LEIDOS BIOMEDICAL RESEARCH INC | 1,044.17 | 2.84 |
| CR4UZS5SKL15 | GLAXOSMITHKLINE, LLC | 913.62 | 2.49 |
| TREKW6J3QSF5 | MAXIMUS FEDERAL SERVICES, INC. | 758.37 | 2.06 |
| FAZSFFE6CST9 | GENERAL DYNAMICS INFORMATION TECHNOLOGY, INC. | 714.32 | 1.94 |
| DGEELN7LRBZ9 | MERCK SHARP & DOHME LLC | 691.37 | 1.88 |

<details><summary>SQL</summary>

```sql
WITH v AS (
    SELECT COALESCE(parent_uei, uei, 'UNKNOWN') AS entity,
           MODE(vendor_name)                    AS typical_name,
           SUM(obligation)                      AS net
    FROM explore.tx
    GROUP BY 1
)
SELECT entity, typical_name,
       ROUND(net / 1e6, 2)                      AS net_millions,
       ROUND(100.0 * net / SUM(net) OVER (), 2) AS pct_of_total
FROM v
ORDER BY net DESC NULLS LAST
LIMIT 10
```

</details>

## 13. Competition

**What to look for:** How much spend was competed vs given without competition. Read the data dictionary for what each label means before drawing conclusions.

| extent_competed | transaction_rows | net_millions | pct_of_spend |
|---|---|---|---|
| FULL AND OPEN COMPETITION | 29,806 | 30,918.36 | 84.11 |
| FULL AND OPEN COMPETITION AFTER EXCLUSION OF SOURCES | 6,735 | 2,352.10 | 6.40 |
| NOT AVAILABLE FOR COMPETITION | 3,888 | 1,228.83 | 3.34 |
| NOT COMPETED | 5,068 | 1,104.60 | 3.00 |
| COMPETED UNDER SAP | 13,835 | 743.55 | 2.02 |
| NOT COMPETED UNDER SAP | 6,781 | 430.44 | 1.17 |
| (missing) | 668 | 0.00 | 0.00 |
| NON-COMPETITIVE DELIVERY ORDER | 6 | -7.86 | -0.02 |
| COMPETITIVE DELIVERY ORDER | 19 | -9.15 | -0.02 |

<details><summary>SQL</summary>

```sql
SELECT COALESCE(competed, '(missing)') AS extent_competed,
       COUNT(*)                        AS transaction_rows,
       ROUND(SUM(obligation) / 1e6, 2) AS net_millions,
       ROUND(100.0 * SUM(obligation) / SUM(SUM(obligation)) OVER (), 2) AS pct_of_spend
FROM explore.tx
GROUP BY 1
ORDER BY net_millions DESC NULLS LAST
```

</details>

## 14. NAICS codes

**What to look for:** A NAICS industry code should be 6 digits. Other lengths are data problems.

| naics_length | transaction_rows |
|---|---|
| (missing) | 9 |
| 6 | 66,797 |

<details><summary>SQL</summary>

```sql
SELECT COALESCE(CAST(length(naics) AS VARCHAR), '(missing)') AS naics_length,
       COUNT(*)                                              AS transaction_rows
FROM explore.tx
GROUP BY 1
ORDER BY 1
```

</details>

## 15. Top ten NAICS codes by spend

**What to look for:** Look up two or three codes at census.gov/naics to see what they mean.

| naics | transaction_rows | net_millions |
|---|---|---|
| 325412 | 570 | 6,756.02 |
| 541512 | 3,491 | 3,450.47 |
| 541714 | 1,433 | 3,230.09 |
| 541611 | 5,501 | 2,298.38 |
| 541519 | 4,233 | 2,168.62 |
| 541715 | 2,168 | 2,153.09 |
| 541511 | 1,642 | 1,730.32 |
| 325414 | 666 | 1,583.19 |
| 541990 | 3,608 | 1,557.40 |
| 524114 | 293 | 1,201.16 |

<details><summary>SQL</summary>

```sql
SELECT naics,
       COUNT(*)                        AS transaction_rows,
       ROUND(SUM(obligation) / 1e6, 2) AS net_millions
FROM explore.tx
WHERE naics IS NOT NULL
GROUP BY naics
ORDER BY net_millions DESC NULLS LAST
LIMIT 10
```

</details>

## 16. Descriptions: how useful are they?

**What to look for:** Descriptions are the raw material for AI classification in Part 6. Many distinct, informative descriptions = good. Mostly missing or mostly codes = harder.

| missing_descriptions | distinct_descriptions | median_length | longest |
|---|---|---|---|
| 0 | 43,101 | 57.00 | 630 |

<details><summary>SQL</summary>

```sql
SELECT COUNT(*) FILTER (WHERE description IS NULL)   AS missing_descriptions,
       COUNT(DISTINCT description)                   AS distinct_descriptions,
       ROUND(quantile_cont(length(description), 0.5), 0) AS median_length,
       MAX(length(description))                      AS longest
FROM explore.tx
```

</details>

## 17. Fifteen most common descriptions

**What to look for:** Short code-like or generic descriptions give a classifier almost nothing to work with. Note how many you see.

| description | transaction_rows |
|---|---|
| LODGING, MEETING, AND AV EXPENSES FOR PEER REVIEW | 454 |
| CLOSE OUT | 450 |
| CLOSE OUT FAR 4.804-1 | 333 |
| THE PURPOSE OF THIS MODIFICATION IS TO EXTEND THE ORDERING PERIOD OF PERFORMANCE OF THE CO | 254 |
| DEOBLIGATE AND CLOSE OUT | 216 |
| TO DE-OBLIGATE FUNDS FROM FY2019 EXPIRING LINES IN ACCORDANCE WITH NIH OALM COMMUNICATION | 176 |
| DE-OBLIGATE AND CLOSE OUT | 167 |
| MEDICAL EXPERT SERVICES VICP. | 160 |
| SUPPLEMENTAL AGREEMENT FOR WORK WITHIN SCOPE | 158 |
| FY 19 EXPIRING LINES | 147 |
| DEOB AND CLOSEOUT | 147 |
| MODIFICATION TO ADMINISTRATIVELY CLOSE AND DE-OBLIGATE EXCESS FUNDS | 122 |
| EXTEND THE ORDERING PERIOD OF PERFORMANCE FROM APRIL 29, 2024 THROUGH OCTOBER 29, 2024. YE | 117 |
| LODGING, MEETING, AND AV EXPENSES FOR PEER REVIEW. | 112 |
| LAB SUPPLIES | 104 |

<details><summary>SQL</summary>

```sql
SELECT description, COUNT(*) AS transaction_rows
FROM explore.tx
WHERE description IS NOT NULL
GROUP BY description
ORDER BY transaction_rows DESC
LIMIT 15
```

</details>

## 18. Possible duplicate rows

**What to look for:** Possible, not proven: a contract can legitimately have two identical-looking lines. Investigate before deleting anything.

| duplicated_groups | extra_rows |
|---|---|
| 28 | 28 |

<details><summary>SQL</summary>

```sql
WITH d AS (
    SELECT COUNT(*) AS c
    FROM explore.tx
    GROUP BY piid, mod_number, action_date, obligation, vendor_name, description
    HAVING COUNT(*) > 1
)
SELECT COUNT(*) AS duplicated_groups, CAST(COALESCE(SUM(c - 1), 0) AS BIGINT) AS extra_rows FROM d
```

</details>

## 19. Contract-and-modification pairs that appear more than once

**What to look for:** Related to the section above. Tells us how carefully we must define what one row of fact data means in Part 4.

| piid_mod_pairs_seen_more_than_once |
|---|
| 3,576 |

<details><summary>SQL</summary>

```sql
SELECT COUNT(*) AS piid_mod_pairs_seen_more_than_once
FROM (SELECT 1 FROM explore.tx GROUP BY piid, mod_number HAVING COUNT(*) > 1)
```

</details>
