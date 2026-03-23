# 🔐 AI Company Internal Chatbot with Role-Based Access Control (RBAC)

---

## 📌 Overview

This project is a **secure AI-powered internal chatbot** designed for organizations to safely access internal data using natural language queries.

It ensures that users can only view information **based on their role**, preventing unauthorized access and data leakage.

---

## 🚀 Key Features

- 🔑 JWT-based Authentication  
- 🔐 Role-Based Access Control (RBAC)  
- 🧠 Semantic Search using Embeddings (RAG)  
- 📂 Secure Document Retrieval  
- 💬 Interactive Chat Interface (Streamlit)  
- ⚡ High-performance FastAPI Backend  

---

## 🧠 How It Works

1. User logs in with credentials  
2. System generates a secure JWT token  
3. User submits a query  
4. Query is converted into embeddings  
5. Similar documents are retrieved from vector database  
6. RBAC filter checks user permissions  
7. Only authorized data is returned  

---

## 🏗️ Architecture

User (Streamlit UI)
        ↓
FastAPI Backend
        ↓
Embedding Model (Sentence Transformers)
        ↓
Vector Database (ChromaDB)
        ↓
RBAC Filtering
        ↓
Secure Response

---

## 👥 User Roles & Access

| Role        | Access |
|------------|--------|
| Finance     | Financial data |
| HR          | HR policies |
| C-Level     | Full access |

---

## 🔐 Security Features

- JWT-based authentication  
- Role-level access control  
- Prevention of unauthorized data exposure  
- Secure API communication  

---

## 🛠️ Tech Stack

- Backend: FastAPI  
- Frontend: Streamlit  
- Database: ChromaDB (Vector DB)  
- Embeddings: Sentence Transformers (MiniLM)  
- Authentication: JWT  

---

## 🧪 Example Scenarios

Finance User → "financial report" → ✅ Allowed  
HR User → "financial report" → ❌ Blocked  
CEO User → "financial report" → ✅ Full Access  

---

## 🚀 How to Run

1. Install dependencies  
pip install -r requirements.txt  

2. Run backend  
uvicorn main:app --reload  

3. Run frontend  
streamlit run app.py  

---

## 🌟 Highlights

✔ Secure AI system  
✔ Real-world enterprise use case  
✔ Prevents data leakage  
✔ Clean and scalable architecture  
✔ Role-based intelligent retrieval  

---

## 👨‍💻 Author

Kevin Harry  

---

## 🎯 Conclusion

This project demonstrates how to build a **secure and intelligent AI system** by combining:

- AI (RAG)
- Security (RBAC)
- Backend APIs
- Interactive UI

---

⭐ Building secure AI systems is the future — this project is a step toward it.
