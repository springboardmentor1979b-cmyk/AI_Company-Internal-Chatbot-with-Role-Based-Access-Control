from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, unique=True, index=True, nullable=False)
    password   = Column(String, nullable=False)
    role       = Column(String, nullable=False)
    is_active  = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class QueryLog(Base):
    __tablename__ = "query_logs"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, index=True, nullable=False)
    role       = Column(String, nullable=False)
    query      = Column(String, nullable=False)
    status     = Column(String, nullable=False)
    sources    = Column(String, nullable=True)
    timestamp  = Column(DateTime, server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String, index=True, nullable=False)
    role       = Column(String, nullable=False)
    query      = Column(String, nullable=False)
    answer     = Column(String, nullable=False)
    sources    = Column(String, nullable=True)
    confidence = Column(Float, default=0.0)
    timestamp  = Column(DateTime, server_default=func.now())