# Deployment Guide

Create the file:

```text
reports/deployment_guide.md
```

Add the following **professional deployment documentation**.

---

# Secure Enterprise RAG Chatbot — Deployment Guide

## 1. Overview

This guide explains how to set up and run the **Secure Enterprise RAG Chatbot** locally.

The system consists of:

* Streamlit frontend
* FastAPI backend
* ChromaDB vector database
* Groq LLM API
* SQLite user database

The deployment process includes:

1. cloning the repository
2. installing dependencies
3. configuring environment variables
4. running backend services
5. launching the frontend interface

---

# 2. System Requirements

Minimum requirements:

| Component | Requirement           |
| --------- | --------------------- |
| Python    | 3.10+                 |
| RAM       | 8 GB recommended      |
| Disk      | 2 GB free             |
| OS        | Windows / Linux / Mac |

Recommended tools:

* Python 3.10
* Git
* VS Code

---

# 3. Clone the Repository

Clone the project repository:

```bash
git clone <repository_url>
cd company_rag_project
```

Example:

```bash
git clone https://github.com/username/company_rag_project.git
cd company_rag_project
```

---

# 4. Create Python Virtual Environment

Create a virtual environment:

```bash
python -m venv rag_env
```

Activate it:

### Windows

```bash
rag_env\Scripts\activate
```

### Mac/Linux

```bash
source rag_env/bin/activate
```

---

# 5. Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

This installs:

* FastAPI
* Streamlit
* Sentence Transformers
* ChromaDB
* LangChain
* SQLAlchemy
* JWT libraries
* Groq API client

---

# 6. Configure Environment Variables

Create a file in the project root:

```text
.env
```

Add the following configuration:

```text
GROQ_API_KEY=your_groq_api_key_here
JWT_SECRET_KEY=super_secure_secret_key
```

The **Groq API key** is required for LLM responses.

You can obtain it from:

```text
https://console.groq.com
```

---

# 7. Prepare Vector Database

Ensure the vector database is built.

If not already created, run:

```bash
python -m backend.rag.index_chunks
```

This will:

* load processed document chunks
* generate embeddings
* store them in ChromaDB

Expected output:

```
Indexing complete.
Total vectors in database: 457
```

---

# 8. Start the Backend Server

Run the FastAPI backend:

```bash
uvicorn backend.main:app --reload
```

Server will start at:

```text
http://127.0.0.1:8000
```

You can view the API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# 9. Start the Streamlit Frontend

Open a new terminal and activate the environment.

Run:

```bash
streamlit run frontend/app.py
```

The UI will launch at:

```text
http://localhost:8501
```

---

# 10. Using the System

### Step 1 — Register a User

Example:

```
finance@company.com
securepassword123
role: finance
```

---

### Step 2 — Login

Enter credentials in the login page.

The system will authenticate the user and generate a **JWT token**.

---

### Step 3 — Ask Questions

Example queries:

```
What was the revenue growth in Q3?
```

```
What marketing strategies were used in Q2?
```

```
Explain the engineering architecture overview.
```

The system will return:

* AI-generated answer
* source documents used

---

# 11. Role-Based Access Control

Users can only access documents allowed by their role.

Example:

| Role        | Accessible Documents   |
| ----------- | ---------------------- |
| employee    | handbook               |
| finance     | finance + handbook     |
| marketing   | marketing + handbook   |
| engineering | engineering + handbook |
| hr          | hr + handbook          |
| c_level     | all documents          |

Unauthorized documents will **not appear in retrieval results**.

---

# 12. Troubleshooting

### Backend fails to start

Check:

```
.env file exists
GROQ_API_KEY is set
dependencies installed
```

---

### Vector database empty

Run:

```bash
python -m backend.rag.index_chunks
```

---

### Login fails

Check that:

* user is registered
* database `users.db` exists

---

# 13. System Shutdown

Stop services with:

```
CTRL + C
```

in the terminal running:

* FastAPI
* Streamlit

---

# 14. Project Structure

```
company_rag_project/
│
├── backend/
│   ├── api/
│   ├── auth/
│   ├── rag/
│
├── frontend/
│
├── data/
│   ├── raw/
│   ├── processed/
│
├── vector_store/
│
├── reports/
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

# 15. Deployment Extensions

Future deployment options include:

* Docker containers
* cloud hosting (AWS / GCP)
* Kubernetes scaling
* CI/CD pipelines

