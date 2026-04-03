import sqlite3
import os

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)
    
    # Check if we need to insert dummy data
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Passwords will be "password" for all users for simplicity in this demo.
        # We will use passlib for hashing in auth, but for simplicity here we assume the hash is generated from "password".
        # We will import the hasher from auth module to ensure it aligns.
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        dummy_hash = pwd_context.hash("password")
        
        users = [
            ("ceo", dummy_hash, "c_level"),
            ("alice", dummy_hash, "finance"),
            ("bob", dummy_hash, "marketing"),
            ("charlie", dummy_hash, "hr"),
            ("david", dummy_hash, "engineering"),
            ("eve", dummy_hash, "employee"),
        ]
        
        cursor.executemany("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", users)
        conn.commit()
    
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
