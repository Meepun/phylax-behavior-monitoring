import sqlite3

DB_NAME = "phylax.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Delete all data from tables
tables = ["state_transitions", "violations", "messages", "sessions", "users"]

for table in tables:
    cursor.execute(f"DELETE FROM {table};")
    # Reset AUTOINCREMENT counters (for INTEGER PRIMARY KEY)
    if table in ["sessions", "violations", "state_transitions"]:
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")

conn.commit()
conn.close()
print("Database cleared successfully!")
