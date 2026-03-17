"""
Run once to seed all users and create all tables.
Usage: python -m backend.init_users
"""
import sqlite3
import os
from passlib.context import CryptContext

DB_PATH     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(p: str) -> str:
    return pwd_context.hash(p)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # ── Users table ──────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    UNIQUE NOT NULL,
            password   TEXT    NOT NULL,
            role       TEXT    NOT NULL,
            is_active  INTEGER DEFAULT 1,
            created_at TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ── Query audit log ───────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT NOT NULL,
            role      TEXT NOT NULL,
            query     TEXT NOT NULL,
            status    TEXT NOT NULL,
            sources   TEXT,
            timestamp TEXT NOT NULL
        )
    """)

    # ── Per-user chat history ─────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            role       TEXT NOT NULL,
            query      TEXT NOT NULL,
            answer     TEXT NOT NULL,
            sources    TEXT,
            confidence REAL DEFAULT 0.0,
            timestamp  TEXT NOT NULL
        )
    """)

    conn.commit()

    # ── Default users ─────────────────────────────
    USERS = [
        ("admin",            hash_password("admin123"),       "C-Level"),
        ("ceo_user",         hash_password("ceo123"),         "C-Level"),
        ("finance_user",     hash_password("finance123"),     "Finance"),
        ("hr_user",          hash_password("hr123"),          "HR"),
        ("marketing_user",   hash_password("marketing123"),   "Marketing"),
        ("engineering_user", hash_password("engineering123"), "Engineering"),
        ("employee_user",    hash_password("employee123"),    "Employee"),
    ]

    inserted = 0
    for username, password, role in USERS:
        try:
            cur.execute(
                "INSERT INTO users (username, password, role) VALUES (?,?,?)",
                (username, password, role)
            )
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # already exists — skip

    conn.commit()
    conn.close()

    print(f"✅ Database ready at: {DB_PATH}")
    print(f"✅ Tables created: users, query_logs, chat_history")
    print(f"✅ {inserted} new users inserted (duplicates skipped)")
    print("\n── Login credentials ──────────────────────")
    print("  admin          / admin123       / C-Level  / CEO-2030")
    print("  ceo_user       / ceo123         / C-Level  / CEO-2030")
    print("  finance_user   / finance123     / Finance  / FIN-2030")
    print("  hr_user        / hr123          / HR       / HRM-2030")
    print("  marketing_user / marketing123   / Marketing/ MKT-2030")
    print("  engineering_user/engineering123 / Engineering/ENG-2030")
    print("  employee_user  / employee123    / Employee / EMP-2030")


if __name__ == "__main__":
    init_db()
