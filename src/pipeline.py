"""
pipeline.py
───────────
RAG pipeline:
  1. Retrieve role-filtered chunks from ChromaDB
  2. Build augmented prompt
  3. Call HuggingFace Inference API (free)
  4. Return answer + source citations
"""

import requests
from src.config import HF_API_TOKEN, HF_API_URL
from src.vector_db.vector_store import get_store


# ── Prompt builder ────────────────────────────────────────────

SYSTEM_PROMPT = """You are a helpful internal company assistant.
Answer ONLY using the provided context below.
If the context does not contain enough information, say:
"I don't have enough information in your accessible documents to answer that."
Always cite the source document(s) at the end of your answer.
"""


def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"\n[Source {i}: {chunk['source']}]\n{chunk['document']}\n"

    return (
        f"{SYSTEM_PROMPT}\n"
        f"---CONTEXT---\n{context_text}\n"
        f"---QUESTION---\n{question}\n"
        f"---ANSWER---\n"
    )


# ── LLM call ─────────────────────────────────────────────────

def call_llm(prompt: str) -> str:
    """
    Calls HuggingFace Inference API.
    Requires HF_API_TOKEN in .env (free account works).
    Falls back to a simple extractive summary if token is missing.
    """
    if not HF_API_TOKEN:
        # Fallback: return the most relevant chunk as the answer
        return "[LLM not configured] " + prompt.split("---CONTEXT---")[1].split("---QUESTION---")[0][:500]

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.3,
            "do_sample": False,
        },
        "options": {"wait_for_model": True},
    }

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        # Different models return different shapes
        if isinstance(data, list) and data:
            item = data[0]
            return item.get("generated_text", str(item)).strip()
        if isinstance(data, dict):
            return data.get("generated_text", str(data)).strip()
        return str(data)

    except requests.exceptions.Timeout:
        return "❌ LLM timed out. Please try again."
    except Exception as e:
        return f"❌ LLM error: {e}"


# ── Main pipeline ─────────────────────────────────────────────

def answer_query(question: str, user_role: str, top_k: int = 4) -> dict:
    """
    Full RAG pipeline.
    Returns {answer, sources, chunks_used, role}.
    """
    store = get_store()

    # Step 1: Retrieve
    chunks = store.search(query=question, user_role=user_role, top_k=top_k)

    if not chunks:
        return {
            "answer":      "No relevant documents found for your role and query.",
            "sources":     [],
            "chunks_used": 0,
            "role":        user_role,
        }

    # Step 2: Build prompt
    prompt = build_prompt(question, chunks)

    # Step 3: Generate
    answer = call_llm(prompt)

    # Strip the prompt echo if the model repeats it
    if "---ANSWER---" in answer:
        answer = answer.split("---ANSWER---")[-1].strip()

    # Step 4: Collect unique sources
    sources = list({c["source"] for c in chunks})

    return {
        "answer":      answer,
        "sources":     sources,
        "chunks_used": len(chunks),
        "role":        user_role,
        "chunks":      chunks,   # full chunks for debugging
    }
