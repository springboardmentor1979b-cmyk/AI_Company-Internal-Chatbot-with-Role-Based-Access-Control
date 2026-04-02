# JWT Authentication Quick Reference Guide

## Installation & Setup

1. **Activate Virtual Environment**
   ```powershell
   .\rag_venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies** (if needed)
   ```bash
   pip install fastapi uvicorn sqlalchemy bcrypt pyjwt pydantic[email]
   ```

3. **Run Application**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

4. **Access API Documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## API Endpoints Reference

### 1. Register User
**Endpoint:** `POST /api/auth/register`
**Status:** 201 Created

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123",
  "role": "employee"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "role": "employee",
    "created_at": "2024-03-24T10:30:00"
  }
}
```

**Error Responses:**
- `400`: User already exists | Invalid role
- `422`: Validation error (invalid email format, password too short)

**Valid Roles:** `employee`, `engineering`, `marketing`, `finance`, `hr`, `c_level`

---

### 2. Login User
**Endpoint:** `POST /api/auth/login`
**Status:** 200 OK

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Responses:**
- `401`: Invalid email or password
- `403`: User account is inactive | `422`: Validation error

---

### 3. Get Current User Info
**Endpoint:** `GET /api/auth/me`
**Status:** 200 OK
**Required:** Authorization Bearer Token

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": 1,
  "email": "john@example.com",
  "role": "employee",
  "created_at": "2024-03-24T10:30:00"
}
```

**Error Responses:**
- `401`: Invalid or expired token

---

### 4. Chat with RAG (Protected)
**Endpoint:** `POST /api/chat`
**Status:** 200 OK
**Required:** Authorization Bearer Token

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Query Parameter:**
```
?question=What are our Q4 results?
```

**Response:**
```json
{
  "question": "What are our Q4 results?",
  "answer": "Based on your role, here are the Q4 results...",
  "user_role": "employee"
}
```

---

### 5. Logout
**Endpoint:** `POST /api/auth/logout`
**Status:** 200 OK
**Required:** Authorization Bearer Token

**Response:**
```json
{
  "message": "User logged out successfully",
  "user_id": 1
}
```

---

## Complete cURL Examples

### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@company.com",
    "password": "SecurePass123",
    "role": "engineering"
  }'
```

### Login and Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@company.com",
    "password": "SecurePass123"
  }'
```

### Use Token to Access Protected Endpoint
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/api/chat?question=What%20is%20engineering%20status?" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Current User Information
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## User Roles & Access

### Role Levels
```
Level 1: employee
Level 2: engineering, marketing, finance, hr
Level 3: c_level (executive)
```

### Role-Based Data Access
- **employee**: General documents only
- **engineering**: Engineering + General
- **marketing**: Marketing + General
- **finance**: Finance + General
- **hr**: HR + General
- **c_level**: All departments (Executive access)

---

## Token Information

- **Format:** JWT (JSON Web Token)
- **Algorithm:** HS256 (HMAC SHA256)
- **Default Expiration:** 60 minutes (3600 seconds)
- **Contains:** 
  - `user_id`: User's database ID
  - `email`: User's email
  - `role`: User's assigned role
  - `exp`: Token expiration timestamp
  - `iat`: Token issued at timestamp

---

## Common Issues & Solutions

### Issue: "Invalid or expired token"
**Solution:** 
1. Check token hasn't expired (default 60 minutes)
2. Ensure token format is correct: `Authorization: Bearer {token}`
3. Re-login to get new token

### Issue: "User already exists"
**Solution:** Use a different email or recover existing account

### Issue: "Invalid role"
**Solution:** Use one of the valid roles:
- employee
- engineering
- marketing
- finance
- hr
- c_level

### Issue: "User account is inactive"
**Solution:** Contact administrator to reactivate the account

### Issue: Database locked error
**Solution:** Restart the application (refreshes SQLite connection)

---

## Testing the System

### Test Scenario: Complete Authentication Flow
```bash
# 1. Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test1234", "role": "employee"}'

# 2. Login with credentials
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test1234"}')

# Extract token (example for Windows/PowerShell)
$TOKEN = ($RESPONSE | ConvertFrom-Json).access_token

# 3. Use token to access protected resource
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Logout
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## Password Requirements

- **Minimum Length:** 6 characters
- **Hashing:** bcrypt with salt
- **Storage:** Never stored in plaintext, only hash stored

---

## Security Best Practices

1. **In Production:**
   - Set `SECRET_KEY` environment variable (change from default)
   - Use HTTPS (not HTTP)
   - Set appropriate `TOKEN_EXPIRE_MINUTES`
   - Restrict CORS origins

2. **For Clients:**
   - Store tokens securely (not localStorage for sensitive apps)
   - Include token in Authorization header
   - Clear token on logout
   - Implement token refresh mechanism

3. **For Developers:**
   - Never commit real credentials
   - Use environment variables
   - Log authentication events
   - Monitor for suspicious activity

---

## Database Location

SQLite database file: `./users.db`

To reset the database:
```python
from backend.models.database import drop_tables, create_tables
drop_tables()
create_tables()
```

---

## Next Steps

1. ✅ Test authentication endpoints with Swagger UI (http://localhost:8000/docs)
2. ✅ Create test users with different roles
3. ✅ Test RAG endpoints with authentication
4. ✅ Verify role-based data access
5. ✅ Implement frontend integration
6. ✅ Add email verification (optional)
7. ✅ Add forgot password flow (optional)
8. ✅ Implement refresh tokens (optional)

---

## Troubleshooting

### Application won't start
- Check all imports are correct
- Verify dependencies installed: `pip install -r requirements.txt`
- Check PORT 8000 is not in use

### Authentication fails
- Verify correct email format
- Ensure password is at least 6 characters
- Check role is in valid list
- Verify token is not expired

### Database errors
- Delete `users.db` and restart (will recreate)
- Check file permissions
- Ensure no other process is accessing the database

---

## Support & Documentation

- **OpenAPI/Swagger:** http://localhost:8000/docs (after running app)
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **Full Implementation Guide:** See `AUTHENTICATION_IMPLEMENTATION.md`
