import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

tables = [
    "profit_loss",
    "balance_sheet",
    "cashflow"
]

for table in tables:

    print("\n====================")
    print(table)
    print("====================")

    df = pd.read_sql(f"""
        SELECT company_id,
               year,
               COUNT(*) AS cnt
        FROM {table}
        GROUP BY company_id, year
        HAVING COUNT(*) > 1
    """, conn)

    print(df)

    print("Duplicate rows =", len(df))

conn.close()