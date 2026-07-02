import sqlite3

conn = sqlite3.connect("data/nifty100.db")

with open("sql/schema.sql", "r", encoding="utf-8") as f:
    conn.executescript(f.read())



conn.commit()
conn.close()

print("Schema created successfully!")