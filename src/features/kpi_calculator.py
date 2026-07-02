import sqlite3
import pandas as pd

# Connect database
conn = sqlite3.connect("data/nifty100.db")

# Load tables
pl = pd.read_sql("SELECT * FROM profit_loss", conn)
bs = pd.read_sql("SELECT * FROM balance_sheet", conn)
companies = pd.read_sql("SELECT * FROM companies", conn)

conn.close()

pl["year_num"] = (
    pl["year"]
    .astype(str)
    .str.extract(r'(\d{4})')[0]
)

# Convert to numeric
pl["year_num"] = pd.to_numeric(
    pl["year_num"],
    errors="coerce"
)



# Remove rows where year could not be extracted
pl = pl.dropna(subset=["year_num"])

# -------------------------
# Normalize balance_sheet year
# -------------------------

bs["year_num"] = (
    bs["year"]
      .astype(str)
      .str.extract(r'(\d{4})')[0]
)

bs["year_num"] = pd.to_numeric(
    bs["year_num"],
    errors="coerce"
)

bs = bs.dropna(subset=["year_num"])

bs["year_num"] = bs["year_num"].astype(int)

# Convert to integer
pl["year_num"] = pl["year_num"].astype(int)

# Latest year record per company
latest_pl = (
    pl.sort_values("year_num")
      .groupby("company_id")
      .tail(1)
)

latest_bs = (
    bs.sort_values("year_num")
      .groupby("company_id")
      .tail(1)
)

# Merge
kpi_df = latest_pl.merge(
    latest_bs,
    on="company_id",
    suffixes=("_pl", "_bs")
)

# Net Profit Margin
kpi_df["net_profit_margin"] = (
    kpi_df["net_profit"] /
    kpi_df["sales"]
) * 100

# Debt Ratio
kpi_df["debt_ratio"] = (
    kpi_df["borrowings"] /
    kpi_df["total_assets"]
) * 100

# Asset Turnover Ratio
kpi_df["asset_turnover"] = (
    kpi_df["sales"] /
    kpi_df["total_assets"]
)

# Select useful columns
kpi_df = kpi_df[
[
    "company_id",
    "sales",
    "net_profit",
    "eps",
    "opm_percentage",
    "net_profit_margin",
    "borrowings",
    "total_assets",
    "debt_ratio",
    "asset_turnover"
]
]

# Save CSV
conn = sqlite3.connect("data/nifty100.db")

kpi_df.to_sql(
    "company_kpis",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("company_kpis table written to SQLite.")

print(kpi_df.head())
print("\ncompany_kpis.csv created successfully!")