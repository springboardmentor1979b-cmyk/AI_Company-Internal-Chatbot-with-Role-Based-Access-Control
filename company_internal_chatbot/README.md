# Company Internal Chatbot with RAG & RBAC

Build a clean, minimal, fully working AI internal chatbot with Role-Based Access Control (RBAC) using Retrieval-Augmented Generation (RAG).

## Architecture overview
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Auth**: JWT via PyJWT, Password hashing via Passlib
- **Database (Users)**: SQLite (`users.db`)
- **Database (Vectors)**: ChromaDB (`vector_db/`)
- **Embeddings**: `sentence-transformers` (auto-managed via ChromaDB)

## Folder Structure
```
backend/
    main.py          # FastAPI application
    auth.py          # JWT authentication helpers
    rbac.py          # Dependencies to fetch JWT role
    rag.py           # ChromaDB search and initialization
    database.py      # SQLite Database initialization
frontend/
    app.py           # Streamlit clean UI
data/                # Dummy placeholder for explicit dataset folders
vector_db/           # ChromaDB persistence directory
requirements.txt
README.md
```

## Setup & Running

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Run Backend**
```bash
uvicorn backend.main:app --reload
```
*(The backend initializes the Mock SQLite and Vector Database automatically on the first startup.)*

**3. Run Frontend**
*(In a separate terminal)*
```bash
streamlit run frontend/app.py
```

## Pre-Generated Test Users
- username: `ceo`, password: `password` (Role: c_level)
- username: `alice`, password: `password` (Role: finance)
- username: `bob`, password: `password` (Role: marketing)
- username: `charlie`, password: `password` (Role: hr)
- username: `david`, password: `password` (Role: engineering)
- username: `eve`, password: `password` (Role: employee)

## API Endpoints
- `POST /login`: Receives `{username, password}` and returns a JWT `access_token`.
- `GET /me`: Requires `Authorization: Bearer <token>` and returns user details.
- `POST /chat`: Requires `Authorization: Bearer <token>` and `{query}`. Performs metadata-filtered Chroma search depending on the user's role and returns an LLM-like RAG answer.
