from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import sqlite3
import os
from collections import defaultdict
from .database import SessionLocal
from .models import User
from .security import get_current_user

router = APIRouter()
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_audit_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Total queries
    cur.execute("SELECT COUNT(*) FROM query_logs")
    total_queries = cur.fetchone()[0]

    # Denied attempts
    cur.execute("SELECT COUNT(*) FROM query_logs WHERE status='Denied'")
    denied = cur.fetchone()[0]

    # Queries by role
    cur.execute("SELECT role, COUNT(*) FROM query_logs GROUP BY role ORDER BY COUNT(*) DESC")
    queries_by_role = {r[0]: r[1] for r in cur.fetchall()}

    # Queries by hour (last 24h)
    cur.execute("""
        SELECT strftime('%H', timestamp) as hr, COUNT(*)
        FROM query_logs
        WHERE timestamp >= datetime('now', '-1 day')
        GROUP BY hr ORDER BY hr
    """)
    queries_by_hour = {r[0]: r[1] for r in cur.fetchall()}

    # Queries by day (last 7 days)
    cur.execute("""
        SELECT date(timestamp) as day, COUNT(*)
        FROM query_logs
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY day ORDER BY day
    """)
    queries_by_day = {r[0]: r[1] for r in cur.fetchall()}

    # Top queries
    cur.execute("""
        SELECT query, COUNT(*) as cnt
        FROM query_logs
        WHERE status != 'Uploaded'
        GROUP BY lower(query)
        ORDER BY cnt DESC LIMIT 5
    """)
    top_queries = [{"query": r[0], "count": r[1]} for r in cur.fetchall()]

    # Top denied queries
    cur.execute("""
        SELECT query, role, COUNT(*) as cnt
        FROM query_logs
        WHERE status='Denied'
        GROUP BY lower(query), role
        ORDER BY cnt DESC LIMIT 5
    """)
    top_denied = [{"query": r[0], "role": r[1], "count": r[2]} for r in cur.fetchall()]

    # Active users today
    cur.execute("""
        SELECT COUNT(DISTINCT username) FROM query_logs
        WHERE date(timestamp) = date('now')
    """)
    active_today = cur.fetchone()[0]

    # Total uploads
    cur.execute("SELECT COUNT(*) FROM query_logs WHERE status='Uploaded'")
    total_uploads = cur.fetchone()[0]

    # Recent logs (20)
    cur.execute("""
        SELECT username, role, query, status, sources, timestamp
        FROM query_logs
        ORDER BY timestamp DESC LIMIT 20
    """)
    recent_logs = [
        {"username": r[0], "role": r[1], "query": r[2],
         "status": r[3], "sources": r[4], "timestamp": r[5]}
        for r in cur.fetchall()
    ]

    # Login activity from chat_history
    cur.execute("""
        SELECT username, role, MIN(timestamp) as first_seen, MAX(timestamp) as last_seen, COUNT(*) as sessions
        FROM chat_history
        GROUP BY username ORDER BY last_seen DESC
    """)
    user_activity = [
        {"username": r[0], "role": r[1], "first_seen": r[2],
         "last_seen": r[3], "sessions": r[4]}
        for r in cur.fetchall()
    ]

    conn.close()
    return {
        "total_queries": total_queries,
        "denied": denied,
        "queries_by_role": queries_by_role,
        "queries_by_hour": queries_by_hour,
        "queries_by_day": queries_by_day,
        "top_queries": top_queries,
        "top_denied": top_denied,
        "active_today": active_today,
        "total_uploads": total_uploads,
        "recent_logs": recent_logs,
        "user_activity": user_activity,
    }


@router.get("/dashboard")
def dashboard(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role not in ["C-Level", "Admin"]:
        raise HTTPException(status_code=403, detail="Access Denied — C-Level only")
    total_users = db.query(User).count()
    stats = get_audit_stats()
    return {
        "total_users": total_users,
        "total_queries": stats["total_queries"],
        "unauthorized_attempts": stats["denied"],
        "queries_by_role": stats["queries_by_role"],
        "queries_by_hour": stats["queries_by_hour"],
        "queries_by_day": stats["queries_by_day"],
        "top_queries": stats["top_queries"],
        "top_denied": stats["top_denied"],
        "active_today": stats["active_today"],
        "total_uploads": stats["total_uploads"],
        "recent_logs": stats["recent_logs"],
        "user_activity": stats["user_activity"],
    }


@router.get("/dashboard/stats")
def dashboard_stats(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return dashboard(current_user=current_user, db=db)
