# Company Internal Chatbot (RAG + RBAC) - Project Context & Setup

## Overview

This project implements a secure internal chatbot system for a company. It processes natural language queries and retrieves department-specific company information using Retrieval-Augmented Generation (RAG). The system authenticates users, assigns roles (Finance, Marketing, HR, Engineering, C-Level, Employees), and ensures role-based access control (RBAC) when querying the vector database.

## System Architecture

The ecosystem relies on three main decoupled parts:
1. **Frontend (Streamlit)**: A chat interface (`frontend/app.py`).
2. **Backend (FastAPI)**: REST endpoints for auth and semantic search (`backend/main.py`).
3. **Core Application (`src/`)**: Holds the business logic, security middleware, and integration with the Vector DB (Chroma) and LLM.

### Project Structure
```text
company-chatbot/
│
├── src/                        # Core Python Logic
│   ├── data_processing/        # Cleans and chunks Markdown/CSV documents
│   ├── vector_db/              # Wraps ChromaDB and embeds queries using SentenceTransformers
│   ├── auth/                   # JWT creation, BCrypt hashing, and SQLite DB connection
│   └── rag/                    # Links Vector search results to a HuggingFace Inference API call
│
├── backend/                    # FastAPI Server
│   ├── main.py                 # Endpoints: /auth/login, /chat/query
│   └── models.py               # Pydantic schemas for request/response payloads
│
├── frontend/                   # Streamlit UI
│   └── app.py                  # Interfaces with backend over HTTP (port 8000)
│
├── scripts/
│   └── ingest_data.py          # Data Pipeline: Clones Github data, processes text, fills Vector DB
│
├── tests/
│   └── test_rbac.py            # Pytest test-suite to assert security limits (e.g. Finance cannot view HR docs)
│
├── requirements.txt            # Python dependencies
├── .env                        # Secrets and API tokens (Do not commit to Github!)
└── README.md                   # Setup instructions
```

## Data Flow (RAG Pipeline)

1. **User Query**: Employee logs in and typed a question. The token identifies them (e.g., `role: finance`).
2. **Retrieve**: The query is embedded. We query ChromaDB but immediately drop any results that lack the `"finance"` tag (unless the user is `c_level`).
3. **Augment**: The matched document chunks are packaged into context for our underlying Prompt.
4. **Generate**: The prompt is passed to the LLM. *Note: If a HuggingFace Token is missing, an extractive fallback mode triggers to safely test querying.*

## Role Permissions (RBAC)

- **Finance**: Accessible matching documents `["finance_report.md", "quarterly_summary.csv", ...]`
- **Marketing**: Accessible matching documents `["marketing_analysis.md", "campaign_data.csv", ...]`
- **HR**: Accessible matching documents `["employee_data.csv", ...]`
- **Engineering**: Accessible matching documents `["tech_docs.md", ...]`
- **Employees**: General handbook and general policies.
- **C-Level**: Grants implicit override to *all* documents.

## Local VS Code Execution

1. **Activate Virtual Environment**
   ```ps1
   venv\Scripts\activate
   ```
2. **(One-Time) Ingest Data**
   ```ps1
   python scripts/ingest_data.py
   ```
3. **Run Services Simultaneously**
   - **Terminal 1** (Backend): 
     ```bash
     python -m backend.main
     ```
   - **Terminal 2** (Frontend): 
     ```bash
     venv\Scripts\activate
     streamlit run frontend/app.py
     ```

## GitHub Integration

Ensure that you have initialized Git, linked the repository, and checked in the files while ignoring sensitive elements like the local Vector DB and python cache.

```bash
git init
git add .
git commit -m "Initial commit for RBAC Chatbot"
git branch -M U_Akhila
git push -u origin U_Akhila
```
