from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW = (ROOT / "data" / "raw" / "fy2024" / "FY2024_075_Contracts_Full_20260909_1.csv").as_posix()

con = duckdb.connect()
source = f"read_csv('{RAW}', all_varchar=true, union_by_name=true)"

cols = con.sql(f"DESCRIBE SELECT * FROM {source}").df()["column_name"].tolist()
n = con.sql(f"SELECT COUNT(*) FROM {source}").fetchone()[0]

out = ROOT / "docs" / "columns.txt"
out.parent.mkdir(exist_ok=True)
out.write_text("\n".join(f"{i+1:3}. {c}" for i, c in enumerate(cols)), encoding="utf-8")
print(f"{n:,} rows, {len(cols)} columns. Full list saved to {out}")

wanted = [
    "action_date", "award_id_piid", "modification_number",
    "recipient_name", "recipient_uei", "recipient_parent_name", "recipient_parent_uei",
    "transaction_description", "naics_code", "product_or_service_code",
    "federal_action_obligation", "current_total_value_of_award",
    "extent_competed", "awarding_agency_name",
]
for c in wanted:
    print(("OK      " if c in cols else "MISSING ") + c)