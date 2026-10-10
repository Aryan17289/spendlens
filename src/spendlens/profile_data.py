"""Profile the raw contract data and write docs/profile_report.md.

Run from the project root:
    python src/spendlens/profile_data.py

Every section has the SQL, the result, and a note on what to look for.
Read the report, then write your findings into the README.
"""
from datetime import datetime
from decimal import Decimal
from numbers import Integral

import pandas as pd

from database import connect
from settings import REPORT_PATH

CHECK_COLUMNS = [
    "piid", "mod_number", "action_date", "vendor_name", "uei", "parent_name", "parent_uei",
    "description", "naics", "psc", "obligation", "award_total_value", "competed",
]

COMPLETENESS_SQL = "SELECT * FROM (\n" + "\nUNION ALL\n".join(
    f"SELECT '{c}' AS column_name, "
    f"COUNT(*) FILTER (WHERE {c} IS NULL) AS missing_rows, "
    f"ROUND(100.0 * COUNT(*) FILTER (WHERE {c} IS NULL) / COUNT(*), 2) AS pct_missing "
    f"FROM explore.tx"
    for c in CHECK_COLUMNS
) + "\n) ORDER BY pct_missing DESC"

SECTIONS = [
    ("1. Size and time range", """
SELECT COUNT(*)                     AS transaction_rows,
       COUNT(DISTINCT piid)         AS distinct_piids,
       COUNT(DISTINCT vendor_name)  AS distinct_vendor_names,
       COUNT(DISTINCT uei)          AS distinct_ueis,
       COUNT(DISTINCT parent_uei)   AS distinct_parent_ueis,
       MIN(action_date)             AS first_action_date,
       MAX(action_date)             AS last_action_date
FROM explore.tx
""", "How big is it? A PIID is a contract number; one contract has many transaction rows (the original award plus modifications). "
     "If your real file has a unique award key column, prefer it over PIID."),

    ("2. Rows and money per fiscal year", """
SELECT COALESCE(CAST(fiscal_year AS VARCHAR), '(unknown)') AS fiscal_year,
       COUNT(*)                          AS transaction_rows,
       ROUND(SUM(obligation) / 1e6, 2)   AS net_obligation_millions
FROM explore.tx
GROUP BY 1
ORDER BY 1
""", "'(unknown)' means the action date was blank or unreadable. Note how many rows that is."),

    ("3. How much is missing, column by column", COMPLETENESS_SQL,
     "Columns with high pct_missing limit what we can do. Missing parent_uei is normal (many vendors have no parent). "
     "Missing uei or description matters more."),

    ("4. Obligation values that could not be read as numbers", """
SELECT COUNT(*) FILTER (WHERE obligation_raw IS NOT NULL AND obligation IS NULL) AS unreadable_rows,
       array_to_string(list_slice(list(DISTINCT obligation_raw)
           FILTER (WHERE obligation_raw IS NOT NULL AND obligation IS NULL), 1, 5), ' | ') AS examples
FROM explore.tx
""", "Rows listed here are dropped from every sum. If the number is large, look at the examples and decide how to fix them in Part 4."),

    ("5. The money: positive, negative and zero obligations", """
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
""", "Negative obligations are normal: the government took money back from a contract (a de-obligation). "
     "Spend = the NET sum of obligations, so keep the negatives."),

    ("6. The double-counting trap", """
SELECT ROUND(SUM(obligation) / 1e6, 2) AS spend_millions_correct,
       ROUND((SELECT SUM(award_total_value) FROM explore.tx) / 1e6, 2) AS wrong_sum_of_total_value_per_row_millions,
       ROUND((SELECT SUM(v) FROM (SELECT MAX(award_total_value) AS v FROM explore.tx
                                  WHERE piid IS NOT NULL GROUP BY piid)) / 1e6, 2) AS total_value_once_per_award_millions
FROM explore.tx
""", "award_total_value is the whole contract's value, repeated on EVERY transaction row of that contract. "
     "Summing it per row inflates spend many times over. Use the obligation column for spend."),

    ("7. The ten largest single transactions", """
SELECT piid, mod_number, action_date, vendor_name, obligation
FROM explore.tx
ORDER BY obligation DESC NULLS LAST
LIMIT 10
""", "Outliers. Check whether they are real (big contracts exist) or data errors."),

    ("8. Vendor identifiers: how many rows have them", """
SELECT ROUND(100.0 * COUNT(*) FILTER (WHERE uei IS NOT NULL) / COUNT(*), 2)                              AS pct_rows_with_uei,
       ROUND(100.0 * COUNT(*) FILTER (WHERE parent_uei IS NOT NULL) / COUNT(*), 2)                       AS pct_rows_with_parent_uei,
       ROUND(100.0 * COUNT(*) FILTER (WHERE uei IS NULL AND parent_uei IS NULL) / COUNT(*), 2)           AS pct_rows_with_neither,
       ROUND(100.0 * SUM(obligation) FILTER (WHERE uei IS NULL AND parent_uei IS NULL)
             / NULLIF(SUM(obligation), 0), 2)                                                            AS pct_spend_with_neither
FROM explore.tx
""", "UEI is the government's unique vendor ID. These IDs are our 'answer key' for testing vendor matching in Part 5. "
     "Rows with neither ID cannot be scored, so we want this to be small."),

    ("9. How many different names does one vendor ID have?", """
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
""", "This is the problem SpendLens solves. Every vendor above '1' is a vendor that spend reports would split into several lines."),

    ("10. Worst examples of one vendor under many names", """
SELECT uei,
       COUNT(DISTINCT vendor_name) AS name_variants,
       array_to_string(list_slice(list(DISTINCT vendor_name), 1, 5), ' | ') AS example_names
FROM explore.tx
WHERE uei IS NOT NULL
GROUP BY uei
ORDER BY name_variants DESC
LIMIT 8
""", "Screenshot or copy 2-3 of these into your README. Concrete examples make the problem real to a recruiter."),

    ("11. Vendor names vs real vendors (baseline)", """
SELECT COUNT(DISTINCT vendor_name)                                                   AS raw_name_strings,
       COUNT(DISTINCT UPPER(TRIM(vendor_name)))                                      AS after_upper_and_trim,
       COUNT(DISTINCT regexp_replace(UPPER(vendor_name), '[^A-Z0-9 ]', '', 'g'))     AS after_removing_punctuation,
       COUNT(DISTINCT COALESCE(parent_uei, uei))                                     AS entities_by_parent_or_own_uei
FROM explore.tx
""", "The last number is the best estimate of the true vendor count. The gap between it and the others is what Part 5 must close. "
     "Simple cleaning alone will not close it."),

    ("12. Top ten vendors by net spend (grouped by parent or own UEI)", """
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
""", "A first look at vendor concentration, which we measure properly in Part 7. "
     "'UNKNOWN' groups every row that has no vendor ID at all, so it is not a real vendor."),

    ("13. Competition", """
SELECT COALESCE(competed, '(missing)') AS extent_competed,
       COUNT(*)                        AS transaction_rows,
       ROUND(SUM(obligation) / 1e6, 2) AS net_millions,
       ROUND(100.0 * SUM(obligation) / SUM(SUM(obligation)) OVER (), 2) AS pct_of_spend
FROM explore.tx
GROUP BY 1
ORDER BY net_millions DESC NULLS LAST
""", "How much spend was competed vs given without competition. Read the data dictionary for what each label means before drawing conclusions."),

    ("14. NAICS codes", """
SELECT COALESCE(CAST(length(naics) AS VARCHAR), '(missing)') AS naics_length,
       COUNT(*)                                              AS transaction_rows
FROM explore.tx
GROUP BY 1
ORDER BY 1
""", "A NAICS industry code should be 6 digits. Other lengths are data problems."),

    ("15. Top ten NAICS codes by spend", """
SELECT naics,
       COUNT(*)                        AS transaction_rows,
       ROUND(SUM(obligation) / 1e6, 2) AS net_millions
FROM explore.tx
WHERE naics IS NOT NULL
GROUP BY naics
ORDER BY net_millions DESC NULLS LAST
LIMIT 10
""", "Look up two or three codes at census.gov/naics to see what they mean."),

    ("16. Descriptions: how useful are they?", """
SELECT COUNT(*) FILTER (WHERE description IS NULL)   AS missing_descriptions,
       COUNT(DISTINCT description)                   AS distinct_descriptions,
       ROUND(quantile_cont(length(description), 0.5), 0) AS median_length,
       MAX(length(description))                      AS longest
FROM explore.tx
""", "Descriptions are the raw material for AI classification in Part 6. Many distinct, informative descriptions = good. "
     "Mostly missing or mostly codes = harder."),

    ("17. Fifteen most common descriptions", """
SELECT description, COUNT(*) AS transaction_rows
FROM explore.tx
WHERE description IS NOT NULL
GROUP BY description
ORDER BY transaction_rows DESC
LIMIT 15
""", "Short code-like or generic descriptions give a classifier almost nothing to work with. Note how many you see."),

    ("18. Possible duplicate rows", """
WITH d AS (
    SELECT COUNT(*) AS c
    FROM explore.tx
    GROUP BY piid, mod_number, action_date, obligation, vendor_name, description
    HAVING COUNT(*) > 1
)
SELECT COUNT(*) AS duplicated_groups, CAST(COALESCE(SUM(c - 1), 0) AS BIGINT) AS extra_rows FROM d
""", "Possible, not proven: a contract can legitimately have two identical-looking lines. "
     "Investigate before deleting anything."),

    ("19. Contract-and-modification pairs that appear more than once", """
SELECT COUNT(*) AS piid_mod_pairs_seen_more_than_once
FROM (SELECT 1 FROM explore.tx GROUP BY piid, mod_number HAVING COUNT(*) > 1)
""", "Related to the section above. Tells us how carefully we must define what one row of fact data means in Part 4."),
]


def fmt(v) -> str:
    if v is None or (not isinstance(v, (list, tuple)) and pd.isna(v)):
        return ""
    if hasattr(v, "strftime"):          # dates and timestamps -> 2024-09-30
        return v.strftime("%Y-%m-%d")
    if isinstance(v, Decimal):
        v = float(v)
    if isinstance(v, Integral):
        return f"{int(v):,}"
    if isinstance(v, float):
        return f"{v:,.2f}"
    return str(v).replace("|", "/").replace("\n", " ")[:90]


def md_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_no rows_"
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(v) for v in row) + " |")
    return "\n".join(lines)


def main() -> None:
    con = connect()
    total = con.sql("SELECT COUNT(*) FROM explore.tx").fetchone()[0]
    if total == 0:
        raise SystemExit("explore.tx has 0 rows. Re-run Part 2: python src/spendlens/ingest.py")

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 60)

    out = [
        "# Data profile report",
        f"_Generated {datetime.now():%Y-%m-%d %H:%M}. {total:,} transaction rows. "
        "Produced by `src/spendlens/profile_data.py`._",
        "",
    ]
    for title, sql, note in SECTIONS:
        df = con.sql(sql).df()
        print(f"\n=== {title} ===")
        print(df.to_string(index=False))
        out += [f"## {title}", "", f"**What to look for:** {note}", "", md_table(df), "",
                "<details><summary>SQL</summary>", "", "```sql", sql.strip(), "```", "", "</details>", ""]

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"\nReport written to {REPORT_PATH}")


if __name__ == "__main__":
    main()