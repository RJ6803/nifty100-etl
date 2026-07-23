import sqlite3

conn = sqlite3.connect("data/nifty100.db")
cur = conn.cursor()

print("=" * 60)
print("TABLES")
print("=" * 60)

tables = cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
).fetchall()

for table in tables:
    table_name = table[0]
    print(f"\nTABLE: {table_name}")

    cols = cur.execute(f"PRAGMA table_info({table_name});").fetchall()

    for col in cols:
        print("   ", col[1])

conn.close()