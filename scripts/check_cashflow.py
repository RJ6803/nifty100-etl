import sqlite3
import pandas as pd

conn = sqlite3.connect("data/nifty100.db")

cf = pd.read_sql("SELECT * FROM cashflow", conn)

print(cf.columns)

conn.close()