import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_audit_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Query audit log
    cur.execute("""
    CREATE TABLE IF NOT EXISTS query_logs (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        username  TEXT,
        role      TEXT,
        query     TEXT,
        status    TEXT,
        sources   TEXT,
        timestamp TEXT
    )""")

    # Per-user chat history
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        username   TEXT,
        role       TEXT,
        query      TEXT,
        answer     TEXT,
        sources    TEXT,
        confidence REAL,
        timestamp  TEXT
    )""")

    conn.commit()
    conn.close()


def log_query(username, role, query, status, sources):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO query_logs (username,role,query,status,sources,timestamp) VALUES (?,?,?,?,?,?)",
        (username, role, query, status,
         ", ".join(sources) if sources else "None",
         datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def save_chat_message(username, role, query, answer, sources, confidence):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chat_history (username,role,query,answer,sources,confidence,timestamp) VALUES (?,?,?,?,?,?,?)",
        (username, role, query, answer,
         ", ".join(sources) if sources else "",
         confidence,
         datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_chat_history(username, limit=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT query, answer, sources, confidence, timestamp
        FROM chat_history
        WHERE username = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (username, limit))
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "query":      r[0],
            "answer":     r[1],
            "sources":    r[2].split(", ") if r[2] else [],
            "confidence": r[3],
            "timestamp":  r[4]
        }
        for r in rows
    ]
