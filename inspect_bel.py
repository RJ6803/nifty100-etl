import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

df = pd.read_sql("""
SELECT *
FROM balance_sheet
WHERE company_id='BEL'
""", conn)

print(df)

conn.close()