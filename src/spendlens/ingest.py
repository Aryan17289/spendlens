"""Convert raw USAspending contract CSVs into partitioned Parquet files."""
import shutil
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RAW = (ROOT / "data" / "raw" / "fy2024" / "FY2024_075_Contracts_Full_20260909_1.csv").as_posix()
OUT = ROOT / "data" / "processed" / "transactions"


def main() -> None:
    if not list((ROOT / "data" / "raw").glob("fy2024/FY2024_075_Contracts_Full_20260909_1.csv")):
        sys.exit("No CSVs found. Expected files like data/raw/fy2024/FY2024_075_Contracts_Full_20260909_1.csv")

    con = duckdb.connect()
    con.sql("SET memory_limit='4GB'")          # lower this to '2GB' on a small laptop
    con.sql("SET preserve_insertion_order=false")  # uses less memory

    source = f"read_csv('{RAW}', all_varchar=true, union_by_name=true)"
    cols = con.sql(f"DESCRIBE SELECT * FROM {source}").df()["column_name"].tolist()
    if "action_date" not in cols:
        sys.exit("Column 'action_date' not found. Check docs/columns.txt.")

    if OUT.exists():
        shutil.rmtree(OUT)  # start clean so old files never mix with new ones

    con.sql(f"""
        COPY (
            SELECT *,
                   year(try_cast(action_date AS DATE))
                   + (month(try_cast(action_date AS DATE)) >= 10)::INTEGER AS fiscal_year
            FROM {source}
        )
        TO '{OUT.as_posix()}' (FORMAT PARQUET, PARTITION_BY (fiscal_year))
    """)

    n = con.sql(
        f"SELECT COUNT(*) FROM read_parquet('{OUT.as_posix()}/**/*.parquet', hive_partitioning=true)"
    ).fetchone()[0]
    print(f"Done. Parquet rows: {n:,}")


if __name__ == "__main__":
    main()