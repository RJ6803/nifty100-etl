import sqlite3

conn = sqlite3.connect("data/nifty100.db")

result = conn.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
AND name='company_screening'
""").fetchall()

conn.close()

print(result)