import sqlite3

# Connect to the database
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Check the current version
cursor.execute("SELECT * FROM alembic_version;")
version = cursor.fetchone()
if version:
    print(f"Current version: {version[0]}")
else:
    print("No version recorded")

conn.close()