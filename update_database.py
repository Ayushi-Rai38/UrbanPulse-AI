import sqlite3

conn = sqlite3.connect("database/complaints.db")
cursor = conn.cursor()

columns = [
    ("ai_summary", "TEXT"),
    ("latitude", "REAL"),
    ("longitude", "REAL")
]

for name, datatype in columns:
    try:
        cursor.execute(
            "ALTER TABLE complaints ADD COLUMN {} {}".format(name, datatype)
        )
        print("{} added.".format(name))
    except sqlite3.OperationalError:
        print("{} already exists.".format(name))

conn.commit()
conn.close()

print("Database Updated Successfully.")