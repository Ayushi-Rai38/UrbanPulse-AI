import sqlite3

conn = sqlite3.connect("database/complaints.db")
cursor = conn.cursor()

try:

    cursor.execute("""
    ALTER TABLE complaints
    ADD COLUMN complaint_id TEXT
    """)

    print("Complaint ID column added.")

except Exception as e:

    print(e)

conn.commit()
conn.close()