import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from .database import engine, Base, SessionLocal
from . import auth, dashboard
from .audit import init_audit_table, log_query, save_chat_message, get_chat_history
from .schemas import QueryRequest, QueryResponse
from .security import get_current_user
from .models import User
from rag_pipeline import generate_response, warmup

# ── DB INIT ──────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dragon RBAC Intelligence", version="2.0")

app.add_middleware(
    CORSMiddleware,
    # In production, this should be restricted to the frontend origin
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(dashboard.router)

UPLOAD_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "uploads"
)
os.makedirs(UPLOAD_DIR, exist_ok=True)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Employee role shouldn't be created via Admin typically, but available
VALID_ROLES = ["C-Level", "Finance", "HR", "Marketing", "Engineering", "Employee"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── STARTUP — pre-load embedding + LLM ───────────────────
@app.on_event("startup")
def startup_event():
    init_audit_table()
    warmup()  # pre-load embedding model for fast first query
    print("✅ Dragon Intelligence API v2.0 — all tables ready.")


# ── ROOT ─────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "Dragon RBAC Intelligence API v2.0", "version": "2.0"}


# ── CHAT ─────────────────────────────────────────────────
@app.post("/chat", response_model=QueryResponse)
def chat(request: QueryRequest, user=Depends(get_current_user)):
    try:
        result = generate_response(query=request.query, user_role=user.role)
        status_flag = "Allowed" if result.get("documents_used", 0) > 0 else "Denied"
        log_query(
            username=user.username,
            role=user.role,
            query=request.query,
            status=status_flag,
            sources=result.get("sources", [])
        )
        save_chat_message(
            username=user.username,
            role=user.role,
            query=request.query,
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# ── CHAT HISTORY ─────────────────────────────────────────
@app.get("/history")
def history(limit: int = 50, user=Depends(get_current_user)):
    return {
        "username": user.username,
        "role":     user.role,
        "history":  get_chat_history(user.username, limit)
    }


# ── UPLOAD — C-Level only ─────────────────────────────────
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = "general",
    user=Depends(get_current_user)
):
    if user.role != "C-Level":
        raise HTTPException(status_code=403, detail="Only C-Level administrators can upload documents.")
    if not file.filename.endswith((".md", ".txt", ".csv", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .md, .txt, .csv, .pdf files allowed.")

    dept_dir  = os.path.join(UPLOAD_DIR, department.lower())
    os.makedirs(dept_dir, exist_ok=True)
    file_path = os.path.join(dept_dir, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    log_query(
        username=user.username,
        role=user.role,
        query=f"[UPLOAD] {file.filename} → {department}",
        status="Uploaded",
        sources=[file.filename]
    )
    return {
        "message": f"'{file.filename}' uploaded to '{department}'.",
        "note": "Re-run ingestion pipeline to index the new document."
    }


# ── LIST UPLOADS — Restricted ────────────────────────────
@app.get("/uploads")
def list_uploads(user=Depends(get_current_user)):
    # Restrict to C-Level / Admin instead of public
    if user.role not in ["C-Level", "Admin"]:
         raise HTTPException(status_code=403, detail="Not authorized to view uploads.")
    files = []
    if os.path.exists(UPLOAD_DIR):
        for dept in os.listdir(UPLOAD_DIR):
            dp = os.path.join(UPLOAD_DIR, dept)
            if os.path.isdir(dp):
                for fname in os.listdir(dp):
                    files.append({"department": dept, "filename": fname})
    return {"files": files}


# ── INGEST — C-Level only ────────────────────────────────
@app.post("/admin/ingest")
def trigger_ingestion(user=Depends(get_current_user)):
    if user.role != "C-Level":
         raise HTTPException(status_code=403, detail="Not authorized to trigger ingestion.")
    
    try:
        from preprocessing.preprocess_all import process_documents, export_to_json
        from vector_db.embedding_engine import embed_documents
        from rag_pipeline import clear_cache
        
        docs = process_documents()
        if docs:
            export_to_json(docs)
            embed_documents()
            clear_cache()
            return {"message": "Ingestion completed successfully."}
        return {"message": "No documents processed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── USER MANAGEMENT — C-Level only ───────────────────────

@app.get("/admin/users")
def list_users(user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != "C-Level":
        raise HTTPException(status_code=403, detail="Admin access required.")
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": u.id, 
                "username": u.username, 
                "role": u.role,
                "is_active": getattr(u, "is_active", True)
            }
            for u in users
        ]
    }


@app.post("/admin/users")
def add_user(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "C-Level":
        raise HTTPException(status_code=403, detail="Admin access required.")
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {VALID_ROLES}")

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Username '{username}' already exists.")

    hashed = pwd_context.hash(password)
    new_user = User(username=username, password=hashed, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_query(
        username=user.username,
        role=user.role,
        query=f"[ADD USER] {username} → {role}",
        status="Admin",
        sources=[]
    )
    return {"message": f"User '{username}' created with role '{role}'."}


@app.delete("/admin/users/{username}")
def delete_user(
    username: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "C-Level":
        raise HTTPException(status_code=403, detail="Admin access required.")
    if username == user.username:
        raise HTTPException(status_code=400, detail="Cannot delete your own account.")

    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")

    db.delete(target)
    db.commit()
    log_query(
        username=user.username,
        role=user.role,
        query=f"[DELETE USER] {username}",
        status="Admin",
        sources=[]
    )
    return {"message": f"User '{username}' deleted."}


@app.put("/admin/users/{username}/role")
def update_user_role(
    username: str,
    role: str = Form(...),
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.role != "C-Level":
        raise HTTPException(status_code=403, detail="Admin access required.")
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role.")

    target = db.query(User).filter(User.username == username).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found.")

    target.role = role
    db.commit()
    return {"message": f"User '{username}' role updated to '{role}'."}
