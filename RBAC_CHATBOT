# 🛡️ Internal Enterprise Chatbot (RBAC & RAG Integration)

A highly secure, production-ready internal chatbot engineered to retrieve insights from private company knowledge bases dynamically based on an employee's authorized access level.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?logo=streamlit&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Flan_T5-FFD21E?logo=huggingface&logoColor=black)

---

## 🌟 Key Features

- **Retrieval Augmented Generation (RAG)**: Synthesizes responses strictly from internal Markdown and CSV datasheets.
- **Role-Based Access Control (RBAC)**: Deep-level JWT permissioning limits Vector Database queries precisely to user roles (Finance, Marketing, HR, Engineering, etc.)
- **Security First Local Inference**: Leverages lightweight, zero-cost `google/flan-t5` models and `all-MiniLM-L6-v2` embeddings—ensuring highly confidential enterprise data never hits public LLM APIs like OpenAI.
- **Source Citations**: Transparently cites the exact backend CSV/Markdown references underpinning the generated logic.
- **Chroma Database**: Robust local AI vector architecture enabling instantaneous semantic contextual search.

---

## 🎨 UI & Design Aesthetic
The application leverages a beautiful **pastel-crafted user interface** constructed with custom Streamlit injections. It optimizes aesthetics and reduces cognitive load by separating chat messages dynamically with contrasting color maps seamlessly bridged with clear Markdown rendering rules.

---

## 🚀 Quick Setup & Installation

### 1. Clone the Source
```bash
git clone https://github.com/your-username/Company-Internal-Chatbot.git
cd Company-Internal-Chatbot
```

### 2. Configure Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Provide Environment Secrets
```bash
cp .env.example .env
```
*(Open the `.env` file and define your custom `JWT_SECRET` key).*

---

## 💻 Running the Application

The infrastructure relies on a decoupled architecture. You must spawn both the backend API and the frontend client simultaneously.

### » Spin up the FastAPI Backend
```bash
cd backend
uvicorn main:app --reload
```
*(Initializes Chroma collections, loads local AI model weight tensors, and exposes JWT endpoints universally on `http://127.0.0.1:8000`)*

### » Launch the Streamlit Frontend
In a **new terminal tab**:
```bash
cd frontend
streamlit run app.py
```
*(Exposes the UI on `http://localhost:8501`)*

---

## 🔒 Implemented Roles & Security Bounds

| Role Identifier | Accessible Data Scopes               | Overall Clearance |
|-----------------|--------------------------------------|-------------------|
| `finance`       | Financial Reports, Quarterly Summaries| Restricted        |
| `hr`            | Employee Databases, Privacy Policies | Restricted        |
| `engineering`   | Tech Specs, System Architectures     | Restricted        |
| `marketing`     | Campaign Analytics, Analysis         | Restricted        |
| `employee`      | General Global Handbooks             | Restricted        |
| `c_level`       | **Unrestricted Global Clearance**    | Administrative    |
