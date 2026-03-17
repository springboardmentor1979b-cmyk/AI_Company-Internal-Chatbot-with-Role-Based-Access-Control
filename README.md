# 🐉 Dragon Intel — RBAC Intelligence Platform

> A secure, role-based enterprise chatbot with RAG pipeline, vector search, and local LLM.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-orange)
![Tests](https://img.shields.io/badge/Tests-26%20passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Overview

Dragon Intel is a full-stack enterprise chatbot that enforces **Role-Based Access Control (RBAC)** on internal company documents. Users can only retrieve information relevant to their department role — enforced at both the vector search and application layers.

### Key Features

- 🔐 **JWT Authentication** — bcrypt-hashed passwords, OAuth2 Bearer tokens
- 🛡️ **Multi-layer RBAC** — ChromaDB metadata filter + application-level guards
- 🧠 **RAG Pipeline** — Semantic search (ChromaDB + all-MiniLM-L6-v2) + TinyLlama LLM
- 🚫 **Smart Guards** — Off-topic, vague query, small talk, and role identity handlers
- 📊 **C-Level Dashboard** — Full audit log, query stats, user analytics
- 📁 **Document Upload** — Runtime document ingestion with department tagging
- ✅ **26 Integration Tests** — Full pytest suite with 100% pass rate

---

## 🏗️ Architecture

```
Browser (port 8502)
    │
    ▼
FastAPI Backend (port 8000)
    ├── /login     → JWT token
    ├── /chat      → RAG pipeline (RBAC filtered)
    ├── /history   → Chat history
    ├── /dashboard → Analytics (C-Level only)
    └── /upload    → Document ingestion
         │
         ├── SQLite (users, logs, history)
         │
         └── RAG Pipeline
              ├── Guard checks (off-topic, vague, role)
              ├── ChromaDB semantic search
              ├── RBAC filter (is_authorized)
              ├── Direct extraction (regex)
              └── TinyLlama LLM fallback
```

---

## 🚀 Quick Start

### 1. Clone & Install

```powershell
git clone https://github.com/yourusername/dragon-intel.git
cd dragon-intel
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Initialize Database & Embeddings

```powershell
python -m backend.init_users
python -m preprocessing.preprocess_all
python -m vector_db.embedding_engine
```

### 3. Start the System

```powershell
# Terminal 1 — Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
python -m http.server 8502
```

Open **http://localhost:8502** in your browser.

---

## 👤 Demo Credentials

| Username | Password | Role | Access Key |
|---|---|---|---|
| admin | admin123 | C-Level | CEO-2030 |
| ceo_user | ceo123 | C-Level | CEO-2030 |
| finance_user | finance123 | Finance | FIN-2030 |
| hr_user | hr123 | HR | HRM-2030 |
| marketing_user | marketing123 | Marketing | MKT-2030 |
| engineering_user | engineering123 | Engineering | ENG-2030 |
| employee_user | employee123 | Employee | EMP-2030 |

---

## 🛡️ RBAC Access Map

| Role | Finance | HR | Marketing | Engineering | Handbook |
|---|---|---|---|---|---|
| C-Level | ✅ | ✅ | ✅ | ✅ | ✅ |
| Finance | ✅ | ❌ | ❌ | ❌ | ❌ |
| HR | ❌ | ✅ | ❌ | ❌ | ✅ |
| Marketing | ❌ | ❌ | ✅ | ❌ | ❌ |
| Engineering | ❌ | ❌ | ❌ | ✅ | ❌ |
| Employee | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 📁 Project Structure

```
dragon-intel/
├── backend/
│   ├── main.py          # FastAPI app
│   ├── auth.py          # Login endpoint
│   ├── security.py      # JWT handling
│   ├── audit.py         # Query logging
│   ├── dashboard.py     # Analytics (C-Level)
│   ├── database.py      # SQLAlchemy setup
│   ├── models.py        # ORM models
│   ├── schemas.py       # Pydantic schemas
│   └── init_users.py    # DB seeding
├── frontend/
│   └── index.html       # Full SPA
├── preprocessing/
│   ├── parser.py        # File reader
│   ├── chunker.py       # Text chunking
│   ├── metadata.py      # RBAC tagging
│   ├── ingest.py        # Document processor
│   └── preprocess_all.py
├── vector_db/
│   ├── search_engine.py # RBAC search
│   └── embedding_engine.py
├── data/
│   ├── finance/
│   ├── hr/
│   ├── marketing/
│   ├── engineering/
│   └── general/
├── rag_pipeline.py      # RAG + guards
├── test_integration.py  # 26 pytest tests
└── requirements.txt
```

---

## 🧪 Running Tests

```powershell
pip install pytest requests
pytest test_integration.py -v
# Expected: 26 passed
```

---

## 📦 Requirements

```
fastapi
uvicorn
sqlalchemy
passlib[bcrypt]
python-jose[cryptography]
python-multipart
chromadb
sentence-transformers
transformers
torch
pytest
requests
```

---

## 📄 Documentation

| Document | Description |
|---|---|
| `docs/api_reference.docx` | Full API endpoint reference |
| `docs/integration_tests.docx` | Test suite documentation |
| `docs/system_architecture.docx` | System design & architecture |

---

## 🔒 Security Notes

- Change `SECRET_KEY` in `backend/security.py` before production deployment
- Access keys in `index.html` are for demo only — use environment variables in production
- TinyLlama runs locally — no data leaves your machine

---

## 📝 License

MIT License — see LICENSE file for details.
