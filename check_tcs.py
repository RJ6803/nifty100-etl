import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql("""
SELECT
    id,
    company_name,
    roe_percentage,
    roce_percentage
FROM companies
WHERE id='TCS'
""", conn)

print(df)

conn.close()