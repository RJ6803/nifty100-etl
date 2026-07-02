import sqlite3

conn = sqlite3.connect("data/nifty100.db")

cur = conn.cursor()

cur.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
AND name NOT LIKE 'sqlite_%'
""")

tables = cur.fetchall()

print("Number of tables =", len(tables))

for t in tables:
    print(t[0])

conn.close()