import sqlite3

from src.etl.loader import (
    load_companies,
    load_profitandloss,
    load_balancesheet,
    load_cashflow,
    load_stock_prices,
)

DB = "data/nifty100.db"

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = OFF")

companies = load_companies()
profit_loss = load_profitandloss()
balance_sheet = load_balancesheet()
cashflow = load_cashflow()
stock_prices = load_stock_prices()

# -------------------------
# Clean Companies
# -------------------------

companies = companies[
    [
        "id",
        "company_name",
        "face_value",
        "book_value",
        "roce_percentage",
        "roe_percentage",
    ]
]

companies = companies.drop_duplicates(subset=["id"])

# -------------------------
# Clean Profit Loss
# -------------------------

profit_loss = profit_loss.drop_duplicates(
    subset=["company_id", "year"]
)

# -------------------------
# Clean Balance Sheet
# -------------------------

balance_sheet = balance_sheet.drop_duplicates(
    subset=["company_id", "year"]
)

# -------------------------
# Clean Cashflow
# -------------------------

cashflow = cashflow.drop_duplicates(
    subset=["company_id", "year"]
)

# -------------------------
# Clean Stock Prices
# -------------------------

stock_prices.columns = [
    "id",
    "company_id",
    "date",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume",
    "adjusted_close",
]

stock_prices = stock_prices.drop(columns=["id"])

stock_prices = stock_prices.drop_duplicates(
    subset=["company_id", "date"]
)

# -------------------------
# Delete existing rows
# -------------------------

conn.execute("DELETE FROM stock_prices")
conn.execute("DELETE FROM cashflow")
conn.execute("DELETE FROM balance_sheet")
conn.execute("DELETE FROM profit_loss")
conn.execute("DELETE FROM companies")

# -------------------------
# Insert data
# -------------------------

companies.to_sql(
    "companies",
    conn,
    if_exists="append",
    index=False,
)

profit_loss.to_sql(
    "profit_loss",
    conn,
    if_exists="append",
    index=False,
)

balance_sheet.to_sql(
    "balance_sheet",
    conn,
    if_exists="append",
    index=False,
)

cashflow.to_sql(
    "cashflow",
    conn,
    if_exists="append",
    index=False,
)

stock_prices.to_sql(
    "stock_prices",
    conn,
    if_exists="append",
    index=False,
)

conn.commit()

conn.execute("PRAGMA foreign_keys = ON")

conn.close()

print("Database loaded successfully.")