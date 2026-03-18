import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from . import auth, dashboard
from .audit import init_audit_table, log_query, save_chat_message, get_chat_history
from .schemas import QueryRequest, QueryResponse
from .security import get_current_user
from rag_pipeline import generate_response

# ── DB INIT ──────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dragon RBAC Intelligence", version="2.0")

app.add_middleware(
    CORSMiddleware,
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

UPLOAD_ALLOWED_ROLES = ["Finance", "HR", "Marketing", "Engineering", "C-Level", "Admin"]


# ── STARTUP ──────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    init_audit_table()
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

        status_flag = "Allowed" if result.get("sources") else "Denied"

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


# ── UPLOAD ───────────────────────────────────────────────
@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: str = "general",
    user=Depends(get_current_user)
):
    if user.role not in UPLOAD_ALLOWED_ROLES:
        raise HTTPException(status_code=403, detail="Upload not permitted for your role.")
    if not file.filename.endswith((".md", ".txt", ".csv")):
        raise HTTPException(status_code=400, detail="Only .md, .txt, .csv files allowed.")

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
        "note":    "Re-run ingestion pipeline to index the new document."
    }


# ── LIST UPLOADS ─────────────────────────────────────────
@app.get("/uploads")
def list_uploads(user=Depends(get_current_user)):
    if user.role not in ["C-Level", "Admin"]:
        raise HTTPException(status_code=403, detail="Access denied.")
    files = []
    if os.path.exists(UPLOAD_DIR):
        for dept in os.listdir(UPLOAD_DIR):
            dp = os.path.join(UPLOAD_DIR, dept)
            if os.path.isdir(dp):
                for fname in os.listdir(dp):
                    files.append({"department": dept, "filename": fname})
    return {"files": files}

@app.on_event("startup")
def startup_event():
    init_audit_table()
    
    # ✅ Run preprocessing + embedding here
    import subprocess
    subprocess.run(["python", "-m", "backend.init_users"])
    subprocess.run(["python", "-m", "preprocessing.preprocess_all"])
    subprocess.run(["python", "-m", "vector_db.embedding_engine"])