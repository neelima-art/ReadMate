import sqlite3

conn = sqlite3.connect("readmate.db")

cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
)

tables = cursor.fetchall()

print("\nTables in ReadMate database:\n")

for table in tables:
    print(table[0])

conn.close()