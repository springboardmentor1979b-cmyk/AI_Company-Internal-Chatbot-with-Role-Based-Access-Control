import sqlite3

DB_NAME = "rbac_users.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_user_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()