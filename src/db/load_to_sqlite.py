import sqlite3

from src.etl.loader import (
    load_companies,
    load_profitandloss,
    load_balancesheet,
    load_cashflow,
    load_stock_prices
)


conn = sqlite3.connect("data/nifty100.db")


companies = load_companies()
profit_loss = load_profitandloss()
balance_sheet = load_balancesheet()
cashflow = load_cashflow()
stock_prices = load_stock_prices()



companies = companies[
    [
        "id",
        "company_name",
        "face_value",
        "book_value",
        "roce_percentage",
        "roe_percentage"
    ]
]



stock_prices.columns = [
    "id",
    "company_id",
    "date",
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume",
    "adjusted_close"
]

stock_prices = stock_prices.drop(columns=["id"])



companies.to_sql(
    "companies",
    conn,
    if_exists="replace",
    index=False
)

profit_loss.to_sql(
    "profit_loss",
    conn,
    if_exists="replace",
    index=False
)

balance_sheet.to_sql(
    "balance_sheet",
    conn,
    if_exists="replace",
    index=False
)

cashflow.to_sql(
    "cashflow",
    conn,
    if_exists="replace",
    index=False
)

stock_prices.to_sql(
    "stock_prices",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("All tables loaded successfully!")