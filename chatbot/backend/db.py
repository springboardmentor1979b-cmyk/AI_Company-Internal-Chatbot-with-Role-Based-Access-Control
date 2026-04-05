"""
db.py — SQLite database layer
Tables: users, sessions, query_logs
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = "nexusai.db"

# ─────────────────────────────────────────
#  Schema
# ─────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    email        TEXT    UNIQUE NOT NULL,
    name         TEXT    NOT NULL,
    password     TEXT    NOT NULL,   -- SHA-256 hex
    role         TEXT    NOT NULL,
    department   TEXT    NOT NULL,
    avatar_initials TEXT NOT NULL,
    is_active    INTEGER DEFAULT 1,
    created_at   TEXT    DEFAULT (datetime('now')),
    last_login   TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    jti          TEXT    UNIQUE NOT NULL,  -- JWT ID
    created_at   TEXT    DEFAULT (datetime('now')),
    expires_at   TEXT    NOT NULL,
    revoked      INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS query_logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    query        TEXT    NOT NULL,
    role         TEXT    NOT NULL,
    sources      TEXT,                     -- JSON list
    result_count INTEGER DEFAULT 0,
    response_ms  INTEGER DEFAULT 0,
    created_at   TEXT    DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""

# ─────────────────────────────────────────
#  Seed users
# ─────────────────────────────────────────
SEED_USERS = [
    ("alice@nexus.com",   "Alice Chen",       "Finance@123",  "finance",     "Finance",     "AC"),
    ("bob@nexus.com",     "Bob Martinez",     "Market@123",   "marketing",   "Marketing",   "BM"),
    ("carol@nexus.com",   "Carol Smith",      "HR@12345678",  "hr",          "HR",          "CS"),
    ("dave@nexus.com",    "Dave Patel",       "Eng@12345678", "engineering", "Engineering", "DP"),
    ("emma@nexus.com",    "Emma Johnson",     "Emp@12345678", "employees",   "General",     "EJ"),
    ("frank@nexus.com",   "Frank CEO",        "CEO@1234567",  "c_level",     "Executive",   "FC"),
]

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    # seed only if empty
    cur = conn.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO users (email, name, password, role, department, avatar_initials) VALUES (?,?,?,?,?,?)",
            [(e, n, _hash(p), r, d, a) for e, n, p, r, d, a in SEED_USERS],
        )
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
#  User helpers
# ─────────────────────────────────────────
def get_user_by_email(email: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=? AND is_active=1", (email.lower(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(email: str, name: str, password: str, role: str, department: str, avatar_initials: str):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (email, name, password, role, department, avatar_initials) VALUES (?,?,?,?,?,?)",
            (email.lower(), name, _hash(password), role, department, avatar_initials),
        )
        conn.commit()
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        return user_id
    except sqlite3.IntegrityError:
        return None  # email already exists
    finally:
        conn.close()

def update_last_login(user_id: int):
    conn = get_conn()
    conn.execute("UPDATE users SET last_login=? WHERE id=?", (datetime.utcnow().isoformat(), user_id))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
#  Session helpers
# ─────────────────────────────────────────
def create_session(user_id: int, jti: str, expires_at: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO sessions (user_id, jti, expires_at) VALUES (?,?,?)",
        (user_id, jti, expires_at),
    )
    conn.commit()
    conn.close()

def is_session_valid(jti: str) -> bool:
    conn = get_conn()
    row = conn.execute(
        "SELECT revoked FROM sessions WHERE jti=? AND expires_at > datetime('now')",
        (jti,),
    ).fetchone()
    conn.close()
    return bool(row) and row["revoked"] == 0

def revoke_session(jti: str):
    conn = get_conn()
    conn.execute("UPDATE sessions SET revoked=1 WHERE jti=?", (jti,))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────
#  Query log helpers
# ─────────────────────────────────────────
def log_query(user_id: int, query: str, role: str, sources: list, result_count: int, response_ms: int):
    import json
    conn = get_conn()
    conn.execute(
        "INSERT INTO query_logs (user_id, query, role, sources, result_count, response_ms) VALUES (?,?,?,?,?,?)",
        (user_id, query, role, json.dumps(sources), result_count, response_ms),
    )
    conn.commit()
    conn.close()

def get_user_stats(user_id: int) -> dict:
    conn = get_conn()
    today = datetime.utcnow().date().isoformat()
    total    = conn.execute("SELECT COUNT(*) FROM query_logs WHERE user_id=?", (user_id,)).fetchone()[0]
    today_c  = conn.execute("SELECT COUNT(*) FROM query_logs WHERE user_id=? AND DATE(created_at)=?", (user_id, today)).fetchone()[0]
    avg_ms   = conn.execute("SELECT AVG(response_ms) FROM query_logs WHERE user_id=?", (user_id,)).fetchone()[0]
    recent   = conn.execute(
        "SELECT query, result_count, response_ms, created_at FROM query_logs WHERE user_id=? ORDER BY created_at DESC LIMIT 5",
        (user_id,),
    ).fetchall()
    conn.close()
    return {
        "total_queries":   total,
        "today_queries":   today_c,
        "avg_response_ms": round(avg_ms or 0),
        "recent_queries":  [dict(r) for r in recent],
    }