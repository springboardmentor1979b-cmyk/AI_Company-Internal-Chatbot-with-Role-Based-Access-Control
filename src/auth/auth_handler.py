"""
auth_handler.py
───────────────
• SQLite user store (SQLAlchemy core)
• bcrypt password hashing
• JWT issue / verify
• Role-based permission check
"""

import datetime
import jwt
import bcrypt
from sqlalchemy import create_engine, Column, String, MetaData, Table, select

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
