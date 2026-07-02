import sqlite3

conn = sqlite3.connect("data/nifty100.db")

cursor = conn.cursor()

cursor.execute("""
SELECT sql
FROM sqlite_master
WHERE type='table'
AND name != 'sqlite_sequence'
""")

tables = cursor.fetchall()

with open("sql/schema.sql", "w", encoding="utf-8") as f:
    for table in tables:
        if table[0]:
            f.write(table[0] + ";\n\n")

conn.close()

print("schema.sql exported successfully!")