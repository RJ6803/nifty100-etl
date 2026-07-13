import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql("""
SELECT
company_id,
year,
equity_capital,
reserves
FROM balance_sheet
WHERE company_id='TCS'
ORDER BY year
""", conn)

print(df.tail())

conn.close()