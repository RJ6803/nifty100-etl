import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql(
    """
    SELECT company_id, year, COUNT(*) AS cnt
    FROM financial_ratios
    GROUP BY company_id, year
    HAVING COUNT(*) > 1
    """,
    conn,
)

print(df)

print("\nDuplicate rows =", len(df))

conn.close()