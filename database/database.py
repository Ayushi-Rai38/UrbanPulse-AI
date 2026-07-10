import sqlite3

conn = sqlite3.connect(
    "database/complaints.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS complaints(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    issue_type TEXT,

    confidence REAL,

    location TEXT,

    image_path TEXT,

    status TEXT,

    date TEXT,

    ai_summary TEXT,

    latitude REAL,

    longitude REAL

)
""")

conn.commit()