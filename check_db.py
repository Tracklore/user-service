import sqlite3

# Connect to the database
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in the database:")
for table in tables:
    print(table[0])

# Check if alembic_version table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version';")
alembic_table = cursor.fetchone()

if alembic_table:
    print("\nAlembic version table exists")
    cursor.execute("SELECT * FROM alembic_version;")
    version = cursor.fetchone()
    if version:
        print(f"Current version: {version[0]}")
else:
    print("\nAlembic version table does not exist")

conn.close()