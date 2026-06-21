import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

tables = [
    "companies",
    "profit_loss",
    "balance_sheet",
    "cashflow",
    "stock_prices"
]

for table in tables:
    count = pd.read_sql(
        f"SELECT COUNT(*) AS rows FROM {table}",
        conn
    )

    print(table)
    print(count)
    

conn.close()