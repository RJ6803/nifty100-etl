import sqlite3
import os
import pandas as pd

from src.analytics.cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr
)


# Connect Database

conn = sqlite3.connect("data/nifty100.db")

pl = pd.read_sql(
    "SELECT * FROM profit_loss",
    conn
)

conn.close()


# Prepare Year

pl["year"] = (
    pl["year"]
    .astype(str)
    .str.extract(r'(\d{4})')[0]
)

pl = pl.dropna(subset=["year"])

pl["year"] = pl["year"].astype(int)


# CAGR Helper

def calculate_window(group, column, years, cagr_function):

    group = group.sort_values("year")

    latest = group.iloc[-1]

    start_year = latest["year"] - years

    history = group[group["year"] <= start_year]

    if history.empty:
        return None, "INSUFFICIENT"

    first = history.iloc[-1]

    return cagr_function(
        first[column],
        latest[column],
        years
    )




# Build CAGR Dataset

records = []

for company_id, group in pl.groupby("company_id"):

    row = {
        "company_id": company_id
    }

    # Revenue CAGR

    value, flag = calculate_window(
    group,
    "sales",
    3,
    revenue_cagr
)
    row["revenue_cagr_3yr"] = value
    row["revenue_cagr_3yr_flag"] = flag

    value, flag = calculate_window(
        group,
        "sales",
        5,
        revenue_cagr
    )
    row["revenue_cagr_5yr"] = value
    row["revenue_cagr_5yr_flag"] = flag

    value, flag = calculate_window(
    group,
    "sales",
    10,
    revenue_cagr
)
    row["revenue_cagr_10yr"] = value
    row["revenue_cagr_10yr_flag"] = flag

    # PAT CAGR

    value, flag = calculate_window(group, "net_profit", 3, pat_cagr)
    row["pat_cagr_3yr"] = value
    row["pat_cagr_3yr_flag"] = flag

    value, flag = calculate_window(group, "net_profit", 5, pat_cagr)
    row["pat_cagr_5yr"] = value
    row["pat_cagr_5yr_flag"] = flag

    value, flag = calculate_window(group, "net_profit", 10, pat_cagr)
    row["pat_cagr_10yr"] = value
    row["pat_cagr_10yr_flag"] = flag

    # EPS CAGR

    value, flag = calculate_window(group, "eps", 3, eps_cagr)
    row["eps_cagr_3yr"] = value
    row["eps_cagr_3yr_flag"] = flag

    value, flag = calculate_window(group, "eps", 5, eps_cagr)
    row["eps_cagr_5yr"] = value
    row["eps_cagr_5yr_flag"] = flag

    value, flag = calculate_window(group, "eps", 10, eps_cagr)
    row["eps_cagr_10yr"] = value
    row["eps_cagr_10yr_flag"] = flag

    records.append(row)


# Create DataFrame

cagr_df = pd.DataFrame(records)



conn = sqlite3.connect("data/nifty100.db")

cagr_df.to_sql(
    "company_cagr",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("company_cagr table written to SQLite.")


# Save Output


os.makedirs("output", exist_ok=True)

cagr_df.to_csv(
    "output/company_cagr.csv",
    index=False
)

print(cagr_df.head())

print("\ncompany_cagr.csv created successfully!")