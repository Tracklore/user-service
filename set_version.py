import sqlite3

# Connect to the database
conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# Insert the current version (2 based on our migration files)
cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('2');")
conn.commit()

print("Inserted version 2 into alembic_version table")

conn.close()