# 🤖 AI Company Internal Chatbot with RBAC

> A secure, intelligent chatbot that provides department-specific information using **Role-Based Access Control (RBAC)** and **Retrieval-Augmented Generation (RAG)**.

---

## ✨ Key Features

* 🔐 Secure Authentication using JWT
* 🧑‍💼 Role-Based Access Control (RBAC)
* 🧠 RAG Pipeline for intelligent responses
* 📂 Department-wise data access
* ⚡ FastAPI backend + Streamlit frontend

---

## 🏗️ Project Structure

```
company_internal_chatbot/
│
├── backend/        # FastAPI backend (auth, RBAC, RAG)
├── frontend/       # Streamlit UI
├── data/           # Department-wise documents
│   ├── finance/
│   ├── hr/
│   ├── marketing/
│   ├── engineering/
│   └── general/
│
├── README.md
├── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```
git clone <your-repo-url>
cd company_internal_chatbot
```

---

### 2️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 3️⃣ Create Environment File (.env)

Create a `.env` file in the root folder:

```
JWT_SECRET_KEY=your_secret_key
HF_API_TOKEN=your_huggingface_token
```

---

## 🤗 How to Generate Hugging Face Token

1. Go to 👉 https://huggingface.co
2. Sign up / Login
3. Click your profile icon → **Settings**
4. Go to **Access Tokens**
5. Click **New Token**
6. Select:

   * Role: **Read**
7. Click **Generate**
8. Copy the token

👉 Paste it inside `.env`:

```
HF_API_TOKEN=hf_xxxxxxxxxxxxxx
```

---

## 🚀 Run the Project

### ▶️ Start Backend (FastAPI)

```
python -m backend.main
```

👉 Open: http://localhost:8000/docs

---

### ▶️ Start Frontend (Streamlit)

```
streamlit run frontend/app.py
```

👉 Open: http://localhost:8501

---

## 🔐 Roles Supported

* Finance
* HR
* Marketing
* Engineering
* Employees
* C-Level (Full Access)

---

## 🧠 How It Works

1. User logs in → receives JWT token
2. User sends query
3. RBAC checks access permissions
4. Relevant documents retrieved
5. RAG generates response
6. Answer displayed in UI

---

## 🧰 Tech Stack

| Component | Technology  |
| --------- | ----------- |
| Backend   | FastAPI     |
| Frontend  | Streamlit   |
| Auth      | JWT         |
| Vector DB | ChromaDB    |
| Database  | SQLite      |
| AI Model  | HuggingFace |

---

## ⚠️ Important Notes

* Do NOT upload `.env` file to GitHub
* Keep your Hugging Face token private
* First run may take time (model loading)

---

## 🚀 Future Improvements

* UI enhancements
* Chat history support
* Deployment on cloud
* Advanced role hierarchy

---

## 👩‍💻 Author

**Driti**

---

## ⭐ Conclusion

This project demonstrates how **AI + RBAC + RAG** can be combined to build secure and intelligent enterprise chatbot systems.
