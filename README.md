# 🤖 Infobot with RBAC
## Complete Setup Guide — VS Code to GitHub

---

## 📁 Project Structure

```
company-chatbot/
├── src/
│   ├── config.py                        ← All settings (paths, roles, LLM)
│   ├── data_processing/
│   │   └── preprocessor.py              ← Clean, chunk, tag documents
│   ├── vector_db/
│   │   └── vector_store.py              ← ChromaDB wrapper + RBAC search
│   ├── auth/
│   │   └── auth_handler.py              ← JWT, bcrypt, SQLite users
│   └── rag/
│       └── pipeline.py                  ← RAG + HuggingFace LLM
├── backend/
│   ├── main.py                          ← FastAPI app (REST API)
│   └── models.py                        ← Pydantic schemas
├── frontend/
│   └── app.py                           ← Streamlit UI
├── scripts/
│   └── ingest_data.py                   ← ONE-TIME: clone data + index
├── tests/
│   └── test_rbac.py                     ← Pytest test suite
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ✅ STEP 1 — Install Prerequisites

Before anything, install these on your PC:

| Tool | Download |
|------|----------|
| Python 3.10+ | https://python.org/downloads |
| Git | https://git-scm.com/downloads |
| VS Code | https://code.visualstudio.com |

After installing Python, verify:
```
python --version    # should show 3.10+
pip --version
git --version
```

---

## ✅ STEP 2 — Open Project in VS Code

1. Move the `company-chatbot` folder to wherever you keep projects  
   (e.g., `C:\Users\YourName\Projects\company-chatbot`)

2. Open VS Code → **File → Open Folder** → select `company-chatbot`

3. Install the **Python extension** in VS Code  
   (Extensions icon on left sidebar → search "Python" → Install)

---

## ✅ STEP 3 — Create Virtual Environment

Open the **VS Code Terminal** (`Ctrl + `` ` `` ` or **Terminal → New Terminal**):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

**Select the venv interpreter in VS Code:**  
`Ctrl+Shift+P` → "Python: Select Interpreter" → choose the one with `venv`

---

## ✅ STEP 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: FastAPI, Streamlit, ChromaDB, sentence-transformers, NLTK, bcrypt, PyJWT, SQLAlchemy, pandas.

---

## ✅ STEP 5 — Configure Environment

```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and fill in:

```env
JWT_SECRET_KEY=pick-any-long-random-string-here
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=8

# Get a FREE token at: https://huggingface.co → Settings → Access Tokens
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxx

DATA_FOLDER=Fintech-data
CHROMA_DB_PATH=./chroma_db
```

> **HuggingFace token** is optional but recommended.  
> Without it, the chatbot returns the raw retrieved text instead of a generated answer.  
> Sign up free at huggingface.co → Settings → Access Tokens → New Token (read permission).

---

## ✅ STEP 6 — Run Data Ingestion (ONE TIME ONLY)

```bash
python scripts/ingest_data.py
```

This will:
- Clone the GitHub data repo into `Fintech-data/`
- Parse all `.md` and `.csv` files
- Generate vector embeddings
- Index everything into ChromaDB (saved in `chroma_db/`)
- Create demo user accounts in `users.db`

**Expected output:**
```
✅ Repository cloned successfully.
✅ Total chunks loaded: 120
✅ Indexing complete. Total in DB: 120
✅ Demo users seeded (6 new accounts created).
```

---

## ✅ STEP 7 — Start the Backend (FastAPI)

Open a **new terminal** (keep it running):

```bash
python -m backend.main
```

You'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it: open your browser → http://localhost:8000/docs  
(Interactive API documentation — you can test endpoints here!)

---

## ✅ STEP 8 — Start the Frontend (Streamlit)

Open **another new terminal**:

```bash
streamlit run frontend/app.py
```

Browser opens automatically at http://localhost:8501

**Demo login credentials:**

| Username | Password | Role |
|----------|----------|------|
| alice | alice123 | Finance |
| bob | bob123 | Marketing |
| carol | carol123 | HR |
| dave | dave123 | Engineering |
| eve | eve123 | Employees |
| 👑 frank | frank123 | C-Level (all access) |

---

## 🧪 Evaluator Testing Guide (RBAC Validation)

To completely verify the strict Role-Based Access Control, evaluators should log in using different accounts and test cross-departmental queries. 

Here are exact test cases to validate the security model:

### 1. The "Finance Exclusive" Test
**Log in as `alice` (Finance)**:
- **Ask:** *"What are the Q4 earnings or financial metrics?"*
- **Expected Result:** Alice **receives** the detailed financial answer (Access Granted).
- **Ask:** *"What is the current marketing campaign strategy?"*
- **Expected Result:** Alice receives a generic fallback answer (e.g., "I could not find an answer in your authorized documents"). She is **BLOCKED** from Marketing data.

### 2. The "Marketing Exclusive" Test
**Log in as `bob` (Marketing)**:
- **Ask:** *"What is our social media marketing strategy?"*
- **Expected Result:** Bob **receives** the marketing strategy details.
- **Ask:** *"What are the Q4 earnings?"*
- **Expected Result:** Bob is **BLOCKED** from Finance data and cannot see the earnings.

### 3. The "General Employee" Test
**Log in as `eve` (Employees)**:
- **Ask:** *"What is the general company holiday schedule?"*
- **Expected Result:** Eve **receives** this information because it is publicly tagged for all `employees`.
- **Ask:** *"What are the engineering backend architectures?"*
- **Expected Result:** Eve is **BLOCKED** from Engineering documentation.

### 4. The "C-Level Superuser" Test
**Log in as `frank` (C-Level)**:
- **Ask:** *"What are the Q4 earnings AND the marketing strategy?"*
- **Expected Result:** Frank **receives** answers to both. C-Level bypasses all departmental locks and has global workspace access.

### 5. Testing the Secure File Ingestion Prototype
- Log in as any department (e.g., `bob` for Marketing).
- Navigate to the **Upload Documents** tab.
- Upload a new dummy `.md` or `.csv` file.
- **Result:** The Python backend immediately parses and securely indexes it into ChromaDB. Log out and try to access its internal contents using an account from a *different* department to prove the file is securely locked to Marketing!

---

## ✅ STEP 9 — Run Tests

```bash
pip install pytest
pytest tests/test_rbac.py -v
```

---

## ✅ STEP 10 — Push to GitHub

### 10a. Create a GitHub Repository

1. Go to https://github.com → click **"New repository"**
2. Name it: `company-chatbot-rbac`
3. Set to **Private** (your project data is internal!)
4. **Do NOT** check "Add README" (we have one)
5. Click **Create repository**

### 10b. Initialize Git and Push

In your VS Code terminal (make sure you're in the project folder):

```bash
git init
git add .
git commit -m "Initial commit: Company chatbot with RBAC"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/company-chatbot-rbac.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

### 10c. Add Your Mentor as Collaborator

1. Go to your GitHub repo page
2. Click **Settings** → **Collaborators** → **Add people**
3. Enter your mentor's GitHub username or email
4. They'll get an email invitation — they accept and can now push/pull

---

## 🔄 Daily Workflow (after first setup)

Each time you work on the project:

```bash
# Activate virtual environment
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Terminal 1 — Backend
python -m backend.main

# Terminal 2 — Frontend
streamlit run frontend/app.py
```

---

## 🐛 Fixing the Colab Error (ChromaDB metadata bug)

Your mentor's Colab code had this error because ChromaDB **does not accept Python lists** in metadata:

```python
# ❌ This FAILS in ChromaDB:
metadatas=[{"roles": ["finance", "c_level"]}]

# ✅ This WORKS — use comma-separated string:
metadatas=[{"roles": "finance,c_level"}]
```

This is already fixed in `src/vector_db/vector_store.py` and `src/data_processing/preprocessor.py`.

---

## 📡 API Reference

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/auth/login` | No | Get JWT token |
| GET | `/auth/me` | Yes | Current user info |
| POST | `/chat/query` | Yes | Ask a question (RAG) |
| POST | `/admin/create-user` | Yes (C-Level) | Create new user |
| GET | `/health` | No | Liveness check |

Full interactive docs: http://localhost:8000/docs

---

## 🏗️ Architecture Summary

```
User (Streamlit)
     ↓  login
FastAPI /auth/login  →  SQLite (users)  →  JWT token
     ↓  query + JWT
FastAPI /chat/query
     ↓
RBAC check (role from JWT)
     ↓
ChromaDB semantic search (role-filtered)
     ↓
HuggingFace LLM (generates answer)
     ↓
Response with answer + source citations
     ↑  rendered in Streamlit chat
```

---

## 📦 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Vector DB | ChromaDB (persistent) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| LLM | HuggingFace (google/flan-t5-large) |
| Auth | PyJWT + bcrypt |
| User DB | SQLite + SQLAlchemy |
| Version Control | Git + GitHub |
