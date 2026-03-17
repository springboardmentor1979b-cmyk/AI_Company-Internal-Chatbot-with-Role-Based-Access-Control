# 🔧 Bug Fixes & Setup Guide

## Bugs Fixed

### 1. `backend/security.py` — Wrong SECRET_KEY + wrong return type (CRITICAL)
- **Problem:** `security.py` used `"super_secret_rbac_key_change_this"` but `auth.py` signed tokens with `"supersecretkey"` → every `/chat` request failed with 401.
- **Also:** `get_current_user` returned a plain dict `{"username":..., "role":...}` but `main.py` accessed `.username` and `.role` as object attributes → `AttributeError` on every chat call.
- **Fix:** Unified SECRET_KEY to `"supersecretkey"`, made `get_current_user` return the SQLAlchemy ORM `User` object.

### 2. `backend/init_users.py` — Plain-text passwords (CRITICAL)
- **Problem:** Seeded users stored plain-text passwords (`"finance123"`), but `auth.py` uses bcrypt to verify → login always failed.
- **Fix:** Passwords are now hashed with bcrypt before inserting. Re-run `init_users.py` to rehash existing users.

### 3. `frontend/app.py` — Missing Chat page entirely
- **Problem:** The frontend had Login, Register, and Admin Dashboard, but **no Chat page** — the core feature was missing.
- **Fix:** Full chat interface built with `st.chat_input`, message history, source display, and confidence metrics.

### 4. `vector_db/search_engine.py` — RBAC always returned empty results
- **Problem:** ChromaDB stores list metadata (like `allowed_roles`) as comma-separated **strings**, but the code compared them as Python lists → RBAC filter never matched any document.
- **Fix:** Added string parsing: `[r.strip() for r in raw_roles.split(",")]`

### 5. `backend/dashboard.py` — Hardcoded stats + missing `/dashboard/stats` endpoint
- **Problem:** Stats were hardcoded (`total_queries: 120`). `admin_dashboard.py` called `/dashboard/stats` which didn't exist.
- **Fix:** Stats now read live from the `query_logs` audit table. Added `/dashboard/stats` as an alias endpoint.

### 6. `preprocessing/preprocess_all.py` — Broken imports
- **Problem:** `from parser import ...` fails when run from project root.
- **Fix:** Changed to `from preprocessing.parser import ...`

### 7. `requirements.txt` — Completely empty
- **Fix:** Filled with all required packages.

---

## Setup Instructions

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Re-seed users with hashed passwords
```bash
# From project root
python -c "
import sys; sys.path.insert(0, '.')
from backend.init_users import init_users
init_users()
"
```

### Step 3 — Start the FastAPI backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4 — Start the Streamlit frontend
```bash
streamlit run frontend/app.py
```

---

## Demo Credentials

| Username | Password | Role |
|---|---|---|
| finance_user | finance123 | Finance |
| hr_user | hr123 | HR |
| marketing_user | marketing123 | Marketing |
| engineering_user | engineering123 | Engineering |
| employee_user | employee123 | Employee |
| ceo_user | ceo123 | C-Level |
| admin | admin123 | C-Level |

---

## Files Changed
- `backend/security.py` — unified secret key, returns ORM user object
- `backend/init_users.py` — bcrypt password hashing
- `backend/dashboard.py` — live audit stats, added `/dashboard/stats`
- `vector_db/search_engine.py` — fixed `allowed_roles` string parsing
- `preprocessing/preprocess_all.py` — fixed imports
- `frontend/app.py` — complete rewrite with Chat page
- `requirements.txt` — filled in
