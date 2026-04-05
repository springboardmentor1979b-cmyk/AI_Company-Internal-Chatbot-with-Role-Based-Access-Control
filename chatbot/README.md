# NexusAI — Enterprise Intelligence Platform

A secure, role-based AI chatbot for enterprise knowledge management, built with FastAPI backend and Streamlit frontend.

## Features

- **Role-Based Access**: Finance, Marketing, HR, Engineering, C-Level with tailored knowledge bases
- **RAG Pipeline**: Semantic search over company documents using Sentence Transformers and ChromaDB
- **ChatGPT-like UI**: Modern, responsive chat interface with multi-turn conversations
- **JWT Authentication**: Secure login with session management
- **Analytics Dashboard**: Query metrics, user activity, and access controls
- **Document Upload**: Add new knowledge via file uploads
- **OpenAI Integration**: Optional GPT fallback for enhanced responses

## Architecture

```
frontend/ (Streamlit)
├── app.py          # Main UI with chat, dashboard, auth
├── styles.css      # Dark theme styling
└── __pycache__/

backend/ (FastAPI)
├── main.py         # App entry point
├── auth.py         # JWT auth endpoints
├── rag.py          # RAG search & indexing
├── db.py           # SQLite database layer
├── Fintech-data/   # Knowledge base documents
└── __pycache__/

tests/              # Pytest suite
├── test_auth.py
├── test_rag.py
└── __init__.py
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit 1.32+ | Web UI framework |
| **Backend** | FastAPI 0.104+ | REST API framework |
| **Database** | SQLite 3 | User & session storage |
| **Vector DB** | ChromaDB | Semantic search storage |
| **Embeddings** | Sentence-Transformers | Document embeddings |
| **Authentication** | JWT (PyJWT) | Token-based auth |
| **Config** | python-dotenv | Environment management |
| **Testing** | Pytest | Unit & integration tests |
| **Optional AI** | OpenAI API | GPT-3.5 fallback |

## Setup

### Prerequisites

- Python 3.9+ ([Install Python](https://www.python.org/downloads/))
- Git
- SQLite (built-in)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/nexusai.git
   cd nexusai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your settings (especially JWT_SECRET_KEY)
   ```

5. **Initialize the database**
   ```bash
   cd backend
   python -c "from db import init_db; init_db()"
   cd ..
   ```

### Quick Start

1. Start the backend (Terminal 1):
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start the frontend (Terminal 2):
   ```bash
   cd frontend
   streamlit run app.py
   ```

3. Open **http://localhost:8501** in your browser and log in with demo credentials.

### Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Finance | alice@nexus.com | Finance@123 |
| Marketing | bob@nexus.com | Market@123 |
| HR | carol@nexus.com | HR@1234567 |
| Engineering | dave@nexus.com | Eng@123456 |
| C-Level | ceo@nexus.com | CEO@123456 |

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Secret key for JWT signing ⚠️ **CHANGE FOR PRODUCTION** | `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `BACKEND_URL` | Frontend's backend API URL | `http://localhost:8000` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:8501` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | From [OpenAI Dashboard](https://platform.openai.com/account/api-keys) |
| `ENVIRONMENT` | Deployment environment | `development` / `production` |

**⚠️ Security Note**: Always generate a new `JWT_SECRET_KEY` for production:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Knowledge Base

Documents are stored in `backend/Fintech-data/` with subfolders:
- `engineering/`
- `Finance/`
- `general/`
- `HR/`
- `marketing/`

Supported formats: `.md` (Markdown), `.csv`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Revoke session
- `GET /auth/me` - Get current user info

### RAG
- `POST /rag/query` - Semantic search with role filtering
- `GET /rag/status` - Index health and stats
- `GET /rag/debug` - Debug indexing info

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

## Troubleshooting

### Backend won't start on port 8000
```bash
# Check if port is already in use (Windows)
netstat -ano | findstr :8000

# Kill the process using the port
taskkill /PID <PID> /F

# Or use a different port
uvicorn main:app --port 8001
```

### Frontend shows "Connection refused" error
- Ensure backend is running on `http://localhost:8000`
- Check `BACKEND_URL` in `.env` matches your setup
- Verify CORS is configured correctly in `backend/main.py`

### Database errors
```bash
# Reinitialize database
cd backend
rm nexusai.db
python -c "from db import init_db; init_db()"
```

### Login issues
- Verify credentials match demo accounts in README table
- Check JWT_SECRET_KEY is set in `.env`
- Clear browser cookies and try again

### RAG queries return no results
- Ensure documents exist in `backend/Fintech-data/`
- Verify role-document mappings in `backend/rag.py`
- Check that your user role has access to documents
- Rebuild ChromaDB index:
  ```bash
  cd frontend
  python -c "from app import search_docs; search_docs('test', 'finance')"
  ```

### Streamlit performance issues
- Increase `client.maxMessageSize` in `.streamlit/config.toml`
- Disable `logger.level` for faster startup
- Use `--logger.level=error` flag

## Development

### Project Structure
```
nexusai/
├── backend/
│   ├── main.py           # FastAPI app initialization
│   ├── auth.py           # JWT authentication
│   ├── rag.py            # RAG pipeline & semantic search
│   ├── db.py             # Database layer (SQLite)
│   ├── Fintech-data/     # Knowledge base documents
│   └── nexusai.db        # SQLite database (generated)
├── frontend/
│   ├── app.py            # Streamlit main app
│   └── styles.css        # UI theming
├── tests/                # Pytest test suite
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
└── setup.py              # Project setup
```

### Adding New Roles

1. Add role to seed users in `backend/db.py`
2. Update `ROLE_META` in `frontend/app.py`
3. Add role-document mappings in `backend/rag.py`
4. Update `ROLE_SUGGESTIONS` UI hints in `frontend/app.py`

### Customizing UI

Edit `frontend/styles.css` for theme and layout changes.

### Extending RAG

Modify `backend/rag.py` to:
- Switch embedding models (default: `all-MiniLM-L6-v2`)
- Use different vector databases (default: ChromaDB)
- Add document preprocessing pipelines

## Security

- Passwords: SHA-256 hashing
- Authentication: JWT tokens with expiration
- Authorization: Role-based access control (RBAC)
- Sessions: Revocable with JTI claims
- CORS: Configurable origins
- Secrets: Environment variable management

**Production Checklist:**
- [ ] Set `ENVIRONMENT=production`
- [ ] Generate new `JWT_SECRET_KEY`
- [ ] Use HTTPS for all connections
- [ ] Set strong database encryption
- [ ] Run security audit: `pip-audit`
- [ ] Implement rate limiting
- [ ] Set up logging/monitoring

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes and test: `pytest tests/ -v`
4. Commit with clear messages: `git commit -m "Add: your feature description"`
5. Push to branch: `git push origin feature/your-feature`
6. Submit a Pull Request with description

### Code Standards
- Follow PEP 8 style guide
- Write tests for new features
- Update documentation
- Keep commits atomic and descriptive

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 **Documentation**: Check README and code comments
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/nexusai/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/nexusai/discussions)

## Authors

- Your Name ([@yourgithub](https://github.com/yourgithub))

## Acknowledgments

- FastAPI team for excellent framework
- Streamlit team for rapid UI development
- ChromaDB for vector database capabilities
