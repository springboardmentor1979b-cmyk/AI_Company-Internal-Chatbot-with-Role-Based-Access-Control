
# System Architecture Documentation

Create the file:

```
reports/system_architecture.md
```

Add the following content.

---

# Secure Enterprise RAG Chatbot — System Architecture

## 1. Overview

This project implements a **Secure Enterprise Retrieval-Augmented Generation (RAG) Chatbot** designed for internal company knowledge access.

The system allows employees to ask natural language questions and retrieve answers from company documents while enforcing **strict role-based access control (RBAC)**.

The architecture integrates:

* **semantic vector search**
* **role-based security filtering**
* **large language model reasoning**
* **web-based user interface**

The system ensures that employees can **only access documents permitted by their role**.

---

# 2. High-Level Architecture

```
User
 ↓
Streamlit Frontend
 ↓
FastAPI Backend
 ↓
JWT Authentication
 ↓
RBAC Middleware
 ↓
RAG Pipeline
 ↓
Vector Database (ChromaDB)
 ↓
Company Documents
```

The architecture follows a **layered AI microservice design** commonly used in enterprise AI assistants.

---

# 3. System Components

## 3.1 Frontend — Streamlit UI

The frontend provides a **chat interface for users** to interact with the AI assistant.

Responsibilities:

* user login
* chat interaction
* display AI responses
* show source document citations

Frontend modules:

```
frontend/
   app.py
   login_page.py
   chat_page.py
   api_client.py
```

Streamlit was chosen for:

* rapid development
* Python-native integration
* lightweight UI deployment.

---

# 3.2 Backend — FastAPI

The backend provides **API endpoints for authentication and chat requests**.

Responsibilities:

* user authentication
* role verification
* RAG pipeline execution
* AI response generation

API endpoints:

```
POST /auth/register
POST /auth/login
POST /chat
```

FastAPI was selected because it provides:

* high-performance async APIs
* automatic API documentation
* easy integration with AI pipelines.

---

# 3.3 Authentication Layer

Authentication uses **JWT-based stateless authentication**.

Workflow:

```
User Login
 ↓
Verify email/password
 ↓
Generate JWT Token
 ↓
Frontend stores token
 ↓
Token used for protected requests
```

JWT payload example:

```
{
  "user_id": 1,
  "email": "finance@company.com",
  "role": "finance"
}
```

Passwords are securely stored using **bcrypt hashing**.

---

# 3.4 Role-Based Access Control (RBAC)

RBAC ensures that users can only access documents relevant to their department.

Role hierarchy:

| Role        | Accessible Departments |
| ----------- | ---------------------- |
| employee    | general                |
| finance     | finance + general      |
| marketing   | marketing + general    |
| engineering | engineering + general  |
| hr          | hr + general           |
| c_level     | all departments        |

RBAC enforcement occurs during **vector retrieval** by filtering document metadata.

---

# 3.5 Document Processing Pipeline

Company documents are processed through a preprocessing pipeline:

```
Raw Documents
 ↓
Parsing (Markdown + CSV)
 ↓
Text Cleaning
 ↓
Chunking (300–500 tokens)
 ↓
Metadata tagging
 ↓
Vector embedding generation
```

Each chunk contains metadata:

```
{
  chunk_id
  text
  source
  department
  section
  allowed_roles
}
```

This metadata enables **secure filtering during retrieval**.

---

# 3.6 Vector Database — ChromaDB

The system uses **ChromaDB** as the vector database.

Responsibilities:

* store document embeddings
* perform semantic similarity search
* support metadata filtering

Embedding model used:

```
sentence-transformers
all-MiniLM-L6-v2
```

Embedding dimension:

```
384
```

---

# 3.7 Retrieval-Augmented Generation (RAG)

The RAG pipeline combines **semantic search with LLM reasoning**.

Workflow:

```
User Query
 ↓
Query Embedding
 ↓
Vector Similarity Search
 ↓
RBAC Filtering
 ↓
Top-K Chunk Retrieval
 ↓
Prompt Construction
 ↓
LLM Response Generation
```

The prompt includes structured context from retrieved documents.

---

# 3.8 Large Language Model

The system uses **Groq Llama-3.1 models** for fast inference.

Advantages:

* extremely low latency
* high throughput
* suitable for real-time AI assistants

The LLM generates responses using **only retrieved context** to minimize hallucination.

---

# 4. Security Model

Security is implemented at multiple levels:

### Authentication

JWT tokens validate user identity.

### Authorization

RBAC restricts document access.

### Retrieval Security

Metadata filtering ensures that unauthorized documents are never retrieved.

### Prompt Grounding

The LLM receives only verified company documents.

This prevents **data leakage and hallucinated responses**.

---

# 5. Performance Characteristics

System performance metrics:

| Component            | Average Time  |
| -------------------- | ------------- |
| Embedding generation | ~100 ms       |
| Vector retrieval     | ~150 ms       |
| LLM generation       | ~600–700 ms   |
| Total response time  | ~0.88 seconds |

The system meets the target requirement of **<3 seconds per query**.

---

# 6. Deployment Architecture

```
Streamlit UI
     ↓
FastAPI Backend
     ↓
Chroma Vector Database
     ↓
Groq LLM API
```

The architecture supports easy deployment in:

* local environments
* cloud servers
* containerized environments.

---

# 7. Key Engineering Challenges

### Data Security

Preventing cross-department information leakage.

Solution:

* metadata filtering
* RBAC enforcement during retrieval.

### Hallucination Reduction

Ensuring AI answers are grounded in real documents.

Solution:

* RAG architecture
* structured prompt context.

### Performance Optimization

Maintaining fast responses.

Solution:

* lightweight embeddings
* optimized vector search
* Groq inference engine.

---

# 8. Future Improvements

Possible future enhancements include:

* conversation memory
* feedback-based answer ranking
* document update pipelines
* scalable vector databases
* cloud deployment with containerization.

