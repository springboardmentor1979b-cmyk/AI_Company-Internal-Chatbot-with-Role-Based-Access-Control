import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def init_audit_table():
    """Create query_logs and chat_history tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

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
    conn.close()


def log_query(username: str, role: str, query: str,
              status: str, sources: list):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        """INSERT INTO query_logs
           (username, role, query, status, sources, timestamp)
           VALUES (?,?,?,?,?,?)""",
        (username, role, query, status,
         ", ".join(sources) if sources else "",
         datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def save_chat_message(username: str, role: str, query: str,
                      answer: str, sources: list, confidence: float):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        """INSERT INTO chat_history
           (username, role, query, answer, sources, confidence, timestamp)
           VALUES (?,?,?,?,?,?,?)""",
        (username, role, query, answer,
         ", ".join(sources) if sources else "",
         float(confidence),
         datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_chat_history(username: str, limit: int = 50) -> list:
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        """SELECT query, answer, sources, confidence, timestamp
           FROM chat_history
           WHERE username = ?
           ORDER BY timestamp DESC
           LIMIT ?""",
        (username, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "query":      r[0],
            "answer":     r[1],
            "sources":    [s.strip() for s in r[2].split(",")] if r[2] else [],
            "confidence": float(r[3] or 0),
            "timestamp":  r[4],
        }
        for r in rows
    ]
