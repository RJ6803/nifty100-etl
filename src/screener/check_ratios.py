import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql("""
SELECT
company_id,
year,
return_on_equity_pct
FROM financial_ratios
WHERE company_id='TCS'
ORDER BY year
""", conn)

print(df)

conn.close()