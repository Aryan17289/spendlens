from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[2]
src = (ROOT / "data" / "processed" / "transactions").as_posix() + "/**/*.parquet"
dst = (ROOT / "data" / "sample" / "transactions_sample.csv").as_posix()

duckdb.sql(f"""
    COPY (SELECT * FROM read_parquet('{src}', hive_partitioning=true) USING SAMPLE 5000 ROWS)
    TO '{dst}' (HEADER, DELIMITER ',')
""")
print("Sample written.")