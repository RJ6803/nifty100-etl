import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql(
    "SELECT * FROM financial_ratios LIMIT 5",
    conn
)

print(df.columns.tolist())

conn.close()