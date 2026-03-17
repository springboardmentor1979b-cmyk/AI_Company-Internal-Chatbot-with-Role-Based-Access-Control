# 🐉 Dragon Intel — Complete Deployment Guide

## ✅ Run Locally (VS Code)

### Step 1 — Install dependencies
```powershell
cd D:\python\company-chatbot-rbac
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 2 — Seed DB + embed docs (run once)
```powershell
python -m backend.init_users
python -m preprocessing.preprocess_all
python -m vector_db.embedding_engine
```

### Step 3 — Start backend (Terminal 1)
```powershell
uvicorn backend.main:app --reload --port 8000
```

### Step 4 — Start frontend (Terminal 2)
```powershell
cd frontend
python -m http.server 8502
```

Open: **http://localhost:8502**

---

## 🚀 Deploy to Railway.app (FREE)

### Step 1 — Push to GitHub
```bash
cd D:\python\company-chatbot-rbac
git init
git add .
git commit -m "Dragon Intel v2.0"
git branch -M main
git remote add origin https://github.com/springboardmentor1979b-cmyk/AI_Company-Internal-Chatbot-with-Role-Based-Access-Control.git
git push -u origin main
```

### Step 2 — Deploy on Railway
1. Go to **https://railway.app**
2. Sign in with GitHub
3. Click **New Project → Deploy from GitHub repo**
4. Select your repo
5. Railway auto-detects Python and deploys

### Step 3 — Set Environment Variables on Railway
In Railway dashboard → Variables, add:
```
SECRET_KEY = dragon-rbac-supersecret-2030
PORT = 8000
```

### Step 4 — Update frontend API URL
After Railway gives you a URL (e.g. `https://dragon-intel.up.railway.app`),
update this line in `frontend/index.html`:
```javascript
const API = 'https://dragon-intel.up.railway.app';
```
Then push and redeploy.

---

## 👤 Login Credentials

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

## 🧪 Run Tests
```powershell
pytest test_integration.py -v
# Expected: 26 passed
```
