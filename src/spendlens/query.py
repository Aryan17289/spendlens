"""Run SQL against the SpendLens database from the terminal.

Pass either a SQL string or the path to a .sql file:
    python src/spendlens/query.py "SELECT COUNT(*) AS n FROM explore.tx"
    python src/spendlens/query.py sql/q01_parent_check.sql
"""
import sys
from pathlib import Path

import pandas as pd

from database import connect


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    arg = sys.argv[1]
    if arg.lower().endswith(".sql"):
        path = Path(arg)
        if not path.exists():
            sys.exit(f"SQL file not found: {path.resolve()}  (run this from the project root)")
        sql = path.read_text(encoding="utf-8")
    else:
        sql = arg

    con = connect()
    df = con.sql(sql).df()
    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_colwidth", 70)
    print(df.to_string(index=False))
    print(f"\n({len(df)} rows)")


if __name__ == "__main__":
    main()