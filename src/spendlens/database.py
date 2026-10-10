"""Open the SpendLens DuckDB file and (re)create the views we explore with.

Two views are created every time you connect:
  raw.transactions  - the Parquet files exactly as loaded in Part 2 (all text)
  explore.tx        - a cleaned, typed version used only for exploration
                      (blank -> NULL, text -> date / decimal). In Part 4, dbt will
                      replace it with proper, tested models.
"""
import difflib
import sys

import duckdb

from settings import COLUMNS, DB_PATH, PARQUET_DIR, PARQUET_GLOB


def _q(name: str) -> str:
    """Quote a column name so odd characters can't break the SQL."""
    return '"' + name.replace('"', '""') + '"'


def connect() -> duckdb.DuckDBPyConnection:
    if not any(PARQUET_DIR.glob("**/*.parquet")):
        sys.exit("No Parquet files found. Run Part 2 first: python src/spendlens/ingest.py")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        con = duckdb.connect(str(DB_PATH))
    except duckdb.IOException as e:
        sys.exit(f"Could not open {DB_PATH}. Is another terminal or program using it? Close it and retry.\n{e}")

    con.sql("CREATE SCHEMA IF NOT EXISTS raw")
    con.sql("CREATE SCHEMA IF NOT EXISTS explore")
    con.sql(
        f"CREATE OR REPLACE VIEW raw.transactions AS "
        f"SELECT * FROM read_parquet('{PARQUET_GLOB}', hive_partitioning=true)"
    )

    actual = con.sql("DESCRIBE raw.transactions").df()["column_name"].tolist()
    missing = {k: v for k, v in COLUMNS.items() if v not in actual}
    if missing:
        lines = ["These columns from settings.py were not found in your data:"]
        for ours, theirs in missing.items():
            close = difflib.get_close_matches(theirs, actual, n=3, cutoff=0.4)
            hint = f"  (similar columns: {', '.join(close)})" if close else ""
            lines.append(f"  - {ours}: '{theirs}'{hint}")
        lines.append("Open docs/columns.txt, find the right name, and fix it in src/spendlens/settings.py")
        sys.exit("\n".join(lines))
    if "fiscal_year" not in actual:
        sys.exit("Column 'fiscal_year' not found. Re-run Part 2: python src/spendlens/ingest.py")

    c = {k: _q(v) for k, v in COLUMNS.items()}

    def text(key: str) -> str:
        return f"NULLIF(TRIM({c[key]}), '')"

    con.sql(f"""
        CREATE OR REPLACE VIEW explore.tx AS
        SELECT
            {text('piid')}                                               AS piid,
            {text('mod')}                                                AS mod_number,
            TRY_CAST({text('action_date')} AS DATE)                      AS action_date,
            fiscal_year                                                  AS fiscal_year,
            {text('vendor')}                                             AS vendor_name,
            {text('uei')}                                                AS uei,
            {text('parent_name')}                                        AS parent_name,
            {text('parent_uei')}                                         AS parent_uei,
            {text('description')}                                        AS description,
            {text('naics')}                                              AS naics,
            {text('psc')}                                                AS psc,
            {text('obligation')}                                         AS obligation_raw,
            TRY_CAST({text('obligation')} AS DECIMAL(18,2))              AS obligation,
            TRY_CAST({text('total_value')} AS DECIMAL(18,2))             AS award_total_value,
            {text('competed')}                                           AS competed
        FROM raw.transactions
    """)
    return con