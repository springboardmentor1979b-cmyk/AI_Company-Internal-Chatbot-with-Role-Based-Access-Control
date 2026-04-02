# Application Setup & Verification Guide

## 1. Environment Setup

### Create .env file
Copy from `.env.example` and add your credentials:

```bash
cp .env.example .env
```

### Edit .env with required values:
```
SECRET_KEY=your_super_secret_key_here
GROQ_API_KEY=your_groq_api_key_from_console.groq.com
```

## 2. Get Groq API Key

1. Go to: https://console.groq.com/
2. Sign up or login
3. Navigate to API keys section
4. Create a new API key
5. Copy and paste into `.env` file

## 3. Verify All Components

### Backend Components:
✅ JWT Authentication (FastAPI)
✅ Database Models (SQLAlchemy)
✅ Password Hashing (bcrypt)
✅ Pydantic Validation
✅ RAG Pipeline (lazy-loaded)
✅ Groq LLM Client

### Frontend Components:
✅ Streamlit UI
✅ Login Page
✅ Register Page
✅ Chat Page
✅ Logout Button
✅ API Client

## 4. Running the Application

### Terminal 1: Start Backend
```bash
cd "a:\company_rag_project new"
.\rag_venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2: Start Frontend
```bash
cd "a:\company_rag_project new\frontend"
.\rag_venv\Scripts\Activate.ps1
streamlit run app.py
```

## 5. Testing the System

### Test 1: Register New User
1. Open http://localhost:8501 (Streamlit)
2. Click "📝 Create New Account"
3. Fill in:
   - Email: test@example.com
   - Password: test1234
   - Role: employee
4. Click "Create Account"

### Test 2: Login
1. Enter email: test@example.com
2. Enter password: test1234
3. Click "Login"
4. Should see chat interface

### Test 3: Chat with RAG
1. Ask: "What is the company structure?"
2. Should receive an answer from Groq LLM
3. Check sources if available

### Test 4: Logout
1. Click "🚪 Logout" button
2. Should return to login page

## 6. API Endpoints (For Testing)

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test1234",
    "role": "employee"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test1234"
  }'
```

### Chat (with token)
```bash
curl -X POST "http://localhost:8000/api/chat?question=What%20is%20this%20company?" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 7. API Documentation

Open: http://localhost:8000/docs (Swagger UI)
- View all endpoints
- Try endpoints directly
- See request/response schemas

## 8. Troubleshooting

### Issue: "Cannot connect to server"
- Ensure backend is running on port 8000
- Check firewall settings

### Issue: "GROQ_API_KEY not found"
- Add GROQ_API_KEY to .env file
- Restart backend server

### Issue: "Email validation failed"
- Email must be in format: user@domain.com
- Check for typos

### Issue: "User already exists"
- Use a different email address
- Or delete users.db and restart

### Issue: Streamlit not loading
- Run: pip install streamlit
- Use port 8501 (default)

## 9. Key Files

- `backend/main.py` - FastAPI app entry point
- `backend/auth/` - Authentication system
- `backend/api/auth_routes.py` - Auth endpoints
- `backend/api/rag_routes.py` - RAG endpoints
- `frontend/app.py` - Streamlit app entry point
- `frontend/login_page.py` - Login UI
- `frontend/register_page.py` - Register UI
- `frontend/chat_page.py` - Chat interface
- `.env` - Environment variables

## 10. Security Notes

- Never commit .env with real credentials
- Change SECRET_KEY in production
- Use HTTPS in production
- Implement rate limiting
- Add email verification
- Add password complexity requirements

## 11. Database

Location: `users.db` (SQLite)

To reset database:
```python
from backend.models.database import drop_tables, create_tables
drop_tables()
create_tables()
```

## 12. Default Roles

- employee: Basic access
- engineering: Engineering docs
- marketing: Marketing docs
- finance: Finance docs
- hr: HR docs
- c_level: Full access
