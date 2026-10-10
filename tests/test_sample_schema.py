"""Sanity checks on the committed sample file. They fail early if the data shape changes."""
import csv

import duckdb
import pytest

from settings import COLUMNS, ROOT

SAMPLE = ROOT / "data" / "sample" / "transactions_sample.csv"

pytestmark = pytest.mark.skipif(not SAMPLE.exists(), reason="sample file not created yet (Part 2, step 7)")


def test_sample_has_all_required_columns():
    with open(SAMPLE, newline="", encoding="utf-8") as fh:
        header = next(csv.reader(fh))
    missing = [name for name in COLUMNS.values() if name not in header]
    assert not missing, f"Columns missing from the sample file: {missing}"


def test_obligation_is_mostly_numeric():
    col = COLUMNS["obligation"]
    total, readable = duckdb.sql(
        f"""
        SELECT COUNT(*),
               COUNT(TRY_CAST(NULLIF(TRIM("{col}"), '') AS DECIMAL(18,2)))
        FROM read_csv('{SAMPLE.as_posix()}', all_varchar=true)
        """
    ).fetchone()
    assert total > 0
    assert readable / total >= 0.90, f"Only {readable}/{total} obligation values could be read as numbers"


def test_action_date_is_mostly_a_valid_date():
    col = COLUMNS["action_date"]
    total, readable = duckdb.sql(
        f"""
        SELECT COUNT(*),
               COUNT(TRY_CAST(NULLIF(TRIM("{col}"), '') AS DATE))
        FROM read_csv('{SAMPLE.as_posix()}', all_varchar=true)
        """
    ).fetchone()
    assert readable / total >= 0.90, f"Only {readable}/{total} action dates could be read as dates"