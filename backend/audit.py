from sqlalchemy.orm import Session
from datetime import datetime
from .database import SessionLocal, engine
from .models import Base, QueryLog, ChatHistory

def init_audit_table():
    """Create query_logs and chat_history tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def log_query(username: str, role: str, query: str, status: str, sources: list):
    with SessionLocal() as db:
        new_log = QueryLog(
            username=username,
            role=role,
            query=query,
            status=status,
            sources=", ".join(sources) if sources else "",
            timestamp=datetime.utcnow()
        )
        db.add(new_log)
        db.commit()

def save_chat_message(username: str, role: str, query: str, answer: str, sources: list, confidence: float):
    with SessionLocal() as db:
        new_msg = ChatHistory(
            username=username,
            role=role,
            query=query,
            answer=answer,
            sources=", ".join(sources) if sources else "",
            confidence=float(confidence),
            timestamp=datetime.utcnow()
        )
        db.add(new_msg)
        db.commit()

def get_chat_history(username: str, limit: int = 50) -> list:
    with SessionLocal() as db:
        rows = db.query(ChatHistory).filter(ChatHistory.username == username).order_by(ChatHistory.timestamp.desc()).limit(limit).all()
        return [
            {
                "query":      r.query,
                "answer":     r.answer,
                "sources":    [s.strip() for s in r.sources.split(",")] if r.sources else [],
                "confidence": r.confidence,
                "timestamp":  r.timestamp.isoformat(),
            }
            for r in rows
        ]
