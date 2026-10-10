# SpendLens
Procurement spend intelligence with AI classification and a governed natural-language analyst.

## Problem
Procurement data is messy: vendors appear under many name variants and
line items are free-text descriptions. Without cleaning, teams can't
consolidate suppliers, spot tail spend or detect price anomalies.

## Question
Can we turn raw federal contract data into a trustworthy spend cube,
surface savings and risk signals, and let non-analysts query it in plain
English without the AI inventing metric definitions?

## Status
Work in progress. See roadmap below.

## Roadmap
- [ ] Data ingestion
- [ ] DuckDB + exploration
- [ ] dbt models
- [ ] Vendor entity resolution
- [ ] Spend classification
- [ ] Insights and anomalies
- [ ] Dashboards
- [ ] MCP analyst + evaluation
- [ ] Deployment and demo

## Data profile (USAspending, HHS contracts, FY2024)
- 66,806 transaction rows across 49,452 contracts, 8,867 vendor names and 9,026 vendor IDs; 1 Oct 2023 - 30 Sep 2024
- Keys: transaction key is unique on every row; PIID alone would undercount contracts by 27% (36,056 vs 49,452)
- Vendor finding: names are standardised per vendor ID (9,025 of 9,026 IDs have one name), but parent IDs change over time:
  989 vendor IDs (11.0%) appear under more than one parent ID, including Merck and ATI; the top 15 hold 35.1% of net spend.
  Grouping by parent ID would split these companies, so SpendLens tracks parent history and builds corporate families.