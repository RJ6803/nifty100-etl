import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_sql("""
SELECT *
FROM balance_sheet
WHERE company_id='BEL'
""", conn)

print(df)

conn.close()