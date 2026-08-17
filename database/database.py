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

DB_PATH = "database/complaints.db"


def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    conn.commit()
    conn.close()

def create_default_users():
    conn = get_connection()
    cursor = conn.cursor()

    users = [
        ("Admin", "admin@urbanpulse.ai", "admin123", "admin"),
        ("Ayushi", "ayushi@gmail.com", "user123", "user")
    ]

    for user in users:
        try:
            cursor.execute("""
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            """, user)
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()

create_users_table()
create_default_users()