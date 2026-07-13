import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

print("----- financial_ratios -----")
print(pd.read_sql("""
SELECT company_id,
year,
return_on_equity_pct
FROM financial_ratios
WHERE company_id='HAL'
ORDER BY year DESC
LIMIT 5
""", conn))

print("\n----- companies -----")
print(pd.read_sql("""
SELECT
id,
company_name,
roe_percentage
FROM companies
WHERE id='HAL'
""", conn))

conn.close()