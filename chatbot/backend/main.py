"""
NexusAI — FastAPI Backend
JWT Auth + SQLite + RAG Pipeline
Run: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

# Load environment variables from .env file
load_dotenv()

from auth import router as auth_router
from rag  import router as rag_router
from db   import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="NexusAI API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(rag_router,  prefix="/rag",  tags=["RAG"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "NexusAI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)