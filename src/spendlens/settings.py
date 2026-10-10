"""Project-wide paths and the mapping between our names and USAspending column names.

If a column in your downloaded file has a different name, change it HERE (one place)
and every script keeps working.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PARQUET_DIR = ROOT / "data" / "processed" / "transactions"
PARQUET_GLOB = PARQUET_DIR.as_posix() + "/**/*.parquet"
DB_PATH = ROOT / "data" / "spendlens.duckdb"
REPORT_PATH = ROOT / "docs" / "profile_report.md"

# our name -> column name in the USAspending contract transactions file
COLUMNS = {
    "piid": "award_id_piid",
    "mod": "modification_number",
    "action_date": "action_date",
    "vendor": "recipient_name",
    "uei": "recipient_uei",
    "parent_name": "recipient_parent_name",
    "parent_uei": "recipient_parent_uei",
    "description": "transaction_description",
    "naics": "naics_code",
    "psc": "product_or_service_code",
    "obligation": "federal_action_obligation",
    "total_value": "current_total_value_of_award",
    "competed": "extent_competed",
}