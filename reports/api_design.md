API Endpoints
POST /auth/register
POST /auth/login
POST /chat
Authentication Flow
Register → Login → JWT Token → Protected Endpoints
RAG Pipeline
Query
 ↓
Embedding
 ↓
Vector Retrieval
 ↓
RBAC Filter
 ↓
LLM Generation