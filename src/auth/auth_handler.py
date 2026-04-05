"""
auth_handler.py
───────────────
• SQLite user store (SQLAlchemy core)
• Telemetry queries table tracking
• bcrypt password hashing
• JWT issue / verify
• Role-based permission check
"""

import datetime
import jwt
import bcrypt
from sqlalchemy import create_engine, Column, String, Integer, DateTime, MetaData, Table, select, func, desc

from src.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRY_HOURS,
    SQLITE_DB_PATH,
    ROLES,
)

# ── Database setup ────────────────────────────────────────────

engine = create_engine(f"sqlite:///{SQLITE_DB_PATH}", echo=False)
metadata = MetaData()

users_table = Table(
    "users",
    metadata,
    Column("username", String, primary_key=True),
    Column("password_hash", String, nullable=False),
    Column("role", String, nullable=False),
    Column("department", String, nullable=True),
)

queries_table = Table(
    "queries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("username", String, nullable=False),
    Column("role", String, nullable=False),
    Column("query_text", String, nullable=False),
    Column("timestamp", DateTime, default=datetime.datetime.utcnow),
)

metadata.create_all(engine)


# ── Password helpers ──────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── User CRUD ─────────────────────────────────────────────────

def create_user(username: str, password: str, role: str, department: str = "") -> bool:
    if role not in ROLES:
        raise ValueError(f"Invalid role '{role}'. Choose from: {ROLES}")
    with engine.connect() as conn:
        existing = conn.execute(
            select(users_table).where(users_table.c.username == username)
        ).fetchone()
        if existing:
            return False   # user already exists
        conn.execute(users_table.insert().values(
            username=username,
            password_hash=hash_password(password),
            role=role,
            department=department,
        ))
        conn.commit()
    return True


def get_user(username: str) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(
            select(users_table).where(users_table.c.username == username)
        ).fetchone()
    if row:
        return {"username": row.username, "role": row.role, "department": row.department}
    return None


def authenticate(username: str, password: str) -> dict | None:
    """Returns user dict on success, None on failure."""
    with engine.connect() as conn:
        row = conn.execute(
            select(users_table).where(users_table.c.username == username)
        ).fetchone()
    if row and verify_password(password, row.password_hash):
        return {"username": row.username, "role": row.role, "department": row.department}
    return None


# ── JWT ───────────────────────────────────────────────────────

def create_token(user: dict) -> str:
    payload = {
        **user,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure."""
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


# ── Telemetry & Analytics ─────────────────────────────────────

def log_query(username: str, role: str, query_text: str):
    """Logs an incoming chat query for the analytics dashboard."""
    with engine.connect() as conn:
        conn.execute(queries_table.insert().values(
            username=username,
            role=role,
            query_text=query_text,
            timestamp=datetime.datetime.utcnow()
        ))
        conn.commit()

def get_user_history(username: str, limit: int = 50) -> list[dict]:
    """Fetch the query history for a specific user."""
    with engine.connect() as conn:
        rows = conn.execute(
            select(queries_table)
            .where(queries_table.c.username == username)
            .order_by(desc(queries_table.c.timestamp))
            .limit(limit)
        ).fetchall()
    
    return [
        {
            "id": r.id, 
            "query_text": r.query_text, 
            "timestamp": r.timestamp.isoformat()
        } for r in rows
    ]

def get_dashboard_metrics(role_filter: str = "c_level") -> dict:
    """Compiles analytics stats. If role_filter is not c_level/admin, filters only for that role."""
    with engine.connect() as conn:
        # Base query block
        is_global = role_filter in ["c_level", "admin"]
            
        # Total queries
        q_count = select(func.count(queries_table.c.id))
        u_count = select(func.count(users_table.c.username))
        
        if not is_global:
            q_count = q_count.where(queries_table.c.role == role_filter)
            u_count = u_count.where(users_table.c.role == role_filter)

        total_queries = conn.execute(q_count).scalar() or 0
        total_users = conn.execute(u_count).scalar() or 0
        
        # Queries by Role
        r_dist = select(queries_table.c.role, func.count('*').label('count')).group_by(queries_table.c.role)
        if not is_global:
            r_dist = r_dist.where(queries_table.c.role == role_filter)
            
        role_counts = conn.execute(r_dist).fetchall()
        queries_by_role = {r[0]: r[1] for r in role_counts}
        
        # Top Queries list
        t_queries = select(queries_table.c.query_text, func.count('*').label('count')).group_by(queries_table.c.query_text).order_by(desc('count')).limit(10)
        if not is_global:
            t_queries = t_queries.where(queries_table.c.role == role_filter)
            
        top_queries = conn.execute(t_queries).fetchall()
        top_queries_list = [{"text": r[0], "count": r[1]} for r in top_queries]
        
    return {
        "total_queries": total_queries,
        "total_users": total_users,
        "queries_by_role": queries_by_role,
        "top_queries": top_queries_list,
    }


# ── Seed demo accounts ────────────────────────────────────────

DEMO_USERS = [
    ("alice",   "alice123",   "finance",     "Finance"),
    ("bob",     "bob123",     "marketing",   "Marketing"),
    ("carol",   "carol123",   "hr",          "Human Resources"),
    ("dave",    "dave123",    "engineering", "Engineering"),
    ("eve",     "eve123",     "employees",   "General"),
    ("frank",   "frank123",   "c_level",     "Executive"),
]

def seed_demo_users():
    created = 0
    for username, password, role, dept in DEMO_USERS:
        if create_user(username, password, role, dept):
            created += 1
    print(f"✅ Demo users seeded ({created} new accounts created).")
    print("   Accounts: alice/finance, bob/marketing, carol/hr,")
    print("             dave/engineering, eve/employees, frank/c_level")


if __name__ == "__main__":
    seed_demo_users()
