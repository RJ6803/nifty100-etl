import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

# feature tables
pd.read_csv("src/features/company_kpis.csv").to_sql(
    "company_kpis", conn, if_exists="replace", index=False
)

pd.read_csv("src/features/company_growth.csv").to_sql(
    "company_growth", conn, if_exists="replace", index=False
)

pd.read_csv("src/features/final_company_features.csv").to_sql(
    "final_company_features", conn, if_exists="replace", index=False
)

# output tables
pd.read_csv("output/validation_failures.csv").to_sql(
    "validation_failures", conn, if_exists="replace", index=False
)

pd.read_csv("output/load_audit.csv").to_sql(
    "load_audit", conn, if_exists="replace", index=False
)

conn.close()

print("Extra tables added successfully!")