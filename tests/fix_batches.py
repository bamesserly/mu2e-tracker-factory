from guis.common.getresources import GetLocalDatabasePath
import sqlite3
import re

# Connect to the SQLite database
conn = sqlite3.connect(GetLocalDatabasePath())
cursor = conn.cursor()

# Fetch rows that need cleaning
cursor.execute("SELECT id, batch FROM straw WHERE batch GLOB '*[^0-9A-Za-z]*'")
rows = cursor.fetchall()

# Clean and update each row
for row in rows:
    id, batch = row
    cleaned_batch = re.sub(r'[^0-9A-Za-z]', '', batch)  # Remove non-alphanumeric characters
    cursor.execute("UPDATE straw SET batch = ? WHERE id = ?", (cleaned_batch, id))

# Commit the changes and close the connection
conn.commit()
conn.close()

