"""
rag.py — RAG pipeline + search endpoint
POST /rag/query   → semantic search + role-filtered answer
GET  /rag/status  → index health
GET  /rag/debug   → show exactly what was indexed (no auth needed for debugging)
"""

import os
import time
import json
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import db
from auth import get_current_user

router = APIRouter()

# ─── Absolute path: always relative to this file, not cwd ────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "Fintech-data")

# ─── Role → file mapping  (filename only, no path) ───────────────────────────
# Every .csv / .md found while walking Fintech-data gets matched by filename.
# c_level gets access to ALL chunks automatically in the search step.
# ─── Updated Role → file mapping (rag.py) ───────────────────────────
ROLE_FILES = {
    "finance":     ["financial_summary.md", "quarterly_financial_report.md"],
    "marketing":   ["marketing_report_2024.md", "marketing_report_q1_2024.md", 
                    "marketing_report_q2_2024.md", "marketing_report_q3_2024.md", 
                    "market_report_q4_2024.md"],
    "hr":          ["employee_handbook.md", "hr_data.csv"],
    "engineering": ["engineering_master_doc.md"],
    "employees":   ["employee_handbook.md", "hr_data.csv"],
}
# c_level is NOT in ROLE_FILES — it is handled in the search filter instead.

ROLE_META = {
    "finance":     {"label": "Finance",     "color": "#4ade80"},
    "marketing":   {"label": "Marketing",   "color": "#f472b6"},
    "hr":          {"label": "HR",          "color": "#a78bfa"},
    "engineering": {"label": "Engineering", "color": "#38bdf8"},
    "employees":   {"label": "Employee",    "color": "#fb923c"},
    "c_level":     {"label": "C-Level",     "color": "#fbbf24"},
}

# ─── Schemas ──────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    answer:       str
    sources:      list
    result_count: int
    response_ms:  int
    role_label:   str

# ─── RAG singleton ────────────────────────────────────────────────────────────
_rag_state = {
    "collection": None, "model": None,
    "ready": False, "error": None,
    "doc_count": 0, "files_indexed": [],
}

# ─── Helpers ──────────────────────────────────────────────────────────────────
def _clean(text: str) -> str:
    return " ".join(str(text).replace("\n", " ").replace("\t", " ").strip().split())

def _chunk(text: str, size: int = 250) -> list[str]:
    """Split by words; fall back to split() if nltk unavailable."""
    try:
        import nltk
        nltk.download("punkt",     quiet=True)
        nltk.download("punkt_tab", quiet=True)
        from nltk.tokenize import word_tokenize
        words = word_tokenize(text)
    except Exception:
        words = text.split()
    chunks = []
    for i in range(0, len(words), size):
        c = " ".join(words[i : i + size]).strip()
        if c:
            chunks.append(c)
    return chunks

def _roles_for_file(fname: str) -> list[str]:
    """Return the list of roles that can access this filename."""
    roles = []
    for role, files in ROLE_FILES.items():
        if fname in files:
            roles.append(role)
    # c_level always gets access — handled in search, not stored per-chunk
    return roles  # may be empty if file not in any role list → skip it

# ─── Indexing ─────────────────────────────────────────────────────────────────
def init_rag():
    global _rag_state
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb

        print(f"[RAG] Looking for data in: {DATA_FOLDER}")
        if not os.path.isdir(DATA_FOLDER):
            raise FileNotFoundError(
                f"Fintech-data folder not found at {DATA_FOLDER}\n"
                "Place the Fintech-data folder inside the backend/ directory."
            )

        model  = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.Client()
        try: client.delete_collection("nexusai_docs")
        except: pass
        col = client.get_or_create_collection("nexusai_docs")

        chunks_meta  = []   # (text, fname, roles)
        files_indexed = []

        for root, _, files in os.walk(DATA_FOLDER):
            for fname in files:
                ext = fname.lower()
                if not (ext.endswith(".md") or ext.endswith(".csv")):
                    continue

                roles = _roles_for_file(fname)
                if not roles:
                    # Unknown file — index it and give it to all roles
                    # so c_level at minimum can access it
                    roles = ["hr", "employees"]  # safe default

                path = os.path.join(root, fname)
                print(f"[RAG]  Indexing {path}  →  roles={roles}")
                files_indexed.append(fname)

                try:
                    if fname.endswith(".md"):
                        raw = open(path, encoding="utf-8", errors="ignore").read()
                        for ch in _chunk(_clean(raw)):
                            chunks_meta.append((ch, fname, roles))

                    elif fname.endswith(".csv"):
                        df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
                        # Index every column: numeric as "col: value" pairs, text as-is
                        row_texts = []
                        for _, row in df.iterrows():
                            parts = []
                            for col_name, val in row.items():
                                if pd.notna(val):
                                    parts.append(f"{col_name}: {val}")
                            if parts:
                                row_texts.append(", ".join(parts))

                        full_text = " | ".join(row_texts)
                        for ch in _chunk(_clean(full_text)):
                            chunks_meta.append((ch, fname, roles))

                except Exception as e:
                    print(f"[RAG]  ⚠ Failed to read {fname}: {e}")

        if not chunks_meta:
            raise ValueError(
                f"No chunks created. Files found: {files_indexed}. "
                "Check that files are readable and not empty."
            )

        print(f"[RAG] Encoding {len(chunks_meta)} chunks…")
        texts = [c[0] for c in chunks_meta]
        embeddings = model.encode(texts, batch_size=32, show_progress_bar=True).tolist()

        col.add(
            ids=[f"c{i}" for i in range(len(chunks_meta))],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"source": c[1], "roles": json.dumps(c[2])} for c in chunks_meta],
        )

        _rag_state.update(
            collection=col, model=model,
            ready=True, error=None,
            doc_count=len(chunks_meta),
            files_indexed=files_indexed,
        )
        print(f"[RAG] ✓ Ready — {len(chunks_meta)} chunks from {len(files_indexed)} files.")

    except Exception as e:
        import traceback
        err = f"{e}\n{traceback.format_exc()}"
        print(f"[RAG] ✗ Init failed:\n{err}")
        _rag_state.update(ready=False, error=str(e))

init_rag()

# ─── Search ───────────────────────────────────────────────────────────────────
def semantic_search(query: str, user_role: str, top_k: int = 5) -> list[dict]:
    if not _rag_state["ready"]:
        return []

    col   = _rag_state["collection"]
    model = _rag_state["model"]

    # Fetch more candidates than needed so filtering doesn't starve results
    n_candidates = min(top_k * 5, 50)
    results = col.query(query_texts=[query], n_results=n_candidates)

    if not (results and results["documents"] and results["documents"][0]):
        return []

    docs = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        try:
            roles_str = meta.get("roles", "[]")
            if isinstance(roles_str, str):
                roles = json.loads(roles_str)
            else:
                roles = roles_str if isinstance(roles_str, list) else []
        except (json.JSONDecodeError, ValueError, TypeError):
            # If parsing fails, default to empty list (access denied)
            roles = []

        # c_level sees everything; others must be in the chunk's role list
        allowed = (user_role == "c_level") or (user_role in roles)
        if not allowed:
            continue

        # Cosine distance → relevance % (chromadb returns L2 by default;
        # clamp to [0,100] to be safe)
        relevance = max(0.0, min(100.0, round((1 - dist) * 100, 1)))

        docs.append({
            "text":      text,
            "source":    meta.get("source", "unknown"),
            "relevance": relevance,
        })
        if len(docs) >= top_k:
            break

    return docs

# ─── Answer builder ───────────────────────────────────────────────────────────
def build_clean_answer(query: str, docs: list[dict], role: str) -> str:
    if not docs:
        return (
            f"❌ **Access Denied** — No documents accessible for your role.\n\n"
            f"**Your Role**: {ROLE_META.get(role, {}).get('label', role)}\n"
            f"**Query**: \"{query}\"\n\n"
            "This information may require higher access permissions. "
            "Contact your administrator if you believe this is an error."
        )

    by_source: dict[str, list] = {}
    for d in docs:
        by_source.setdefault(d["source"], []).append(d)

    lines = []
    for src, chunks in by_source.items():
        combined  = " ".join(c["text"] for c in chunks)
        if len(combined) > 700:
            combined = combined[:700].rsplit(" ", 1)[0] + "…"
        relevance = max(c["relevance"] for c in chunks)
        lines.append(f"**📄 {src}** *(relevance: {relevance}%)*\n\n{combined}")

    body         = "\n\n---\n\n".join(lines)
    sources_list = ", ".join(f"`{s}`" for s in by_source)

    return (
        f"{body}\n\n"
        f"---\n"
        f"*Sources: {sources_list} · Role: {ROLE_META[role]['label']}*"
    )

# ─── Routes ───────────────────────────────────────────────────────────────────
@router.post("/query", response_model=QueryResponse)
def query_rag(req: QueryRequest, user=Depends(get_current_user)):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    t0   = time.time()
    docs = semantic_search(req.query, user["role"], req.top_k)
    ms   = int((time.time() - t0) * 1000)

    answer  = build_clean_answer(req.query, docs, user["role"])
    sources = list({d["source"] for d in docs})

    db.log_query(
        user_id=user["id"],
        query=req.query,
        role=user["role"],
        sources=sources,
        result_count=len(docs),
        response_ms=ms,
    )

    return QueryResponse(
        answer=answer,
        sources=sources,
        result_count=len(docs),
        response_ms=ms,
        role_label=ROLE_META[user["role"]]["label"],
    )

@router.get("/status")
def rag_status(user=Depends(get_current_user)):
    return {
        "ready":         _rag_state["ready"],
        "doc_count":     _rag_state["doc_count"],
        "files_indexed": _rag_state["files_indexed"],
        "data_folder":   DATA_FOLDER,
        "error":         _rag_state["error"],
    }

@router.get("/debug")
def rag_debug():
    """No auth — call this from browser to see what's indexed."""
    return {
        "ready":         _rag_state["ready"],
        "doc_count":     _rag_state["doc_count"],
        "files_indexed": _rag_state["files_indexed"],
        "data_folder":   DATA_FOLDER,
        "folder_exists": os.path.isdir(DATA_FOLDER),
        "error":         _rag_state["error"],
    }
