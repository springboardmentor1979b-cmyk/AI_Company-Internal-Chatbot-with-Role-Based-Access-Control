import re
import time
import torch
import json
import os
import threading
from transformers import AutoTokenizer, AutoModelForCausalLM
from vector_db.search_engine import secure_semantic_search, get_ef


MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = None
model = None

# ── PERSISTENT QUERY CACHE ───────────────────────────────
# Cache stores (role, query_lower) → result dict
# maxsize=256 means last 256 unique queries are cached per role
CACHE_MAX = 256
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(PROJECT_ROOT, "query_cache.json")
_cache = {}
_cache_lock = threading.Lock()


def _load_cache():
    global _cache
    with _cache_lock:
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r") as f:
                    _cache = json.load(f)
            except Exception:
                _cache = {}

def _save_cache():
    with _cache_lock:
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(_cache, f)
        except Exception:
            pass

_load_cache()


def _cache_key(role: str, query: str) -> str:
    return f"{role}||{query.lower().strip()}"


def _get_cache(role: str, query: str):
    with _cache_lock:
        return _cache.get(_cache_key(role, query))


def _set_cache(role: str, query: str, result: dict):
    key = _cache_key(role, query)
    with _cache_lock:
        if len(_cache) >= CACHE_MAX:
            # Remove oldest entry
            oldest = next(iter(_cache))
            del _cache[oldest]
        _cache[key] = result
    _save_cache()


def clear_cache():
    """Call this after new documents are embedded."""
    global _cache
    with _cache_lock:
        _cache.clear()
    _save_cache()
    print("🔄 Query cache cleared.")


# ── WARMUP — pre-load everything at startup ───────────────
def warmup():
    """
    Pre-loads the embedding model at startup so the first
    user query is instant. LLM is lazy-loaded (too large).
    """
    print("🔥 Warming up embedding model...")
    # Actually initialize the embedding function so it downloads models
    _ = get_ef()
    print("✅ Embedding model ready — searches will be fast.")


# ── LOAD LLM ─────────────────────────────────────────────
def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("Loading TinyLlama LLM...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        # Load in float16 to save memory and speed up inference
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, 
            torch_dtype=torch.float16, 
            device_map="auto",
            low_cpu_mem_usage=True
        )
        print("✅ LLM loaded.")


# ── BUILD CONTEXT ─────────────────────────────────────────
def build_context(docs):
    return "\n\n".join(
        f"[Source: {d['metadata']['source']}]\n{d['document']}"
        for d in docs
    )


# ── CLEAN LLM OUTPUT ──────────────────────────────────────
def clean_llm_output(text: str) -> str:
    lines = text.split("\n")
    cleaned = [l for l in lines
               if not l.startswith("[Source:") and not l.strip().startswith("<|")]
    text = " ".join(cleaned)
    text = re.sub(r"Answer:", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ── MAIN RESPONSE ─────────────────────────────────────────
def generate_response(query: str, user_role: str) -> dict:
    start = time.perf_counter()
    clean_query = query.lower().strip()

    def ms():
        return round((time.perf_counter() - start) * 1000, 2)

    def resp(answer, sources=None, confidence=1.0, docs=0):
        return {
            "answer": answer,
            "sources": sources or [],
            "confidence": confidence,
            "documents_used": docs,
            "response_time_ms": ms()
        }

    # ── 1. SMALL TALK ─────────────────────────────────────
    small_talk = {
        "hi":             "Hello! How can I assist you today?",
        "hello":          "Hi there! Ask me about company reports or policies.",
        "hey":            "Hello! Ask me about your company documents.",
        "who are you":    "I am Dragon Intel, a secure RBAC assistant for internal company documents.",
        "what can you do": f"As a {user_role}, I can answer questions about your permitted company documents.",
        "help":           "Try asking about revenue, HR policies, leave days, or your department reports.",
    }
    stripped_query = clean_query.rstrip("?.!")
    if stripped_query in small_talk:
        return resp(small_talk[stripped_query], confidence=1.0)

    # ── 2. ROLE IDENTITY ──────────────────────────────────
    role_triggers = ["my role", "what is my role", "say my role",
                     "who am i", "what role", "tell me my role"]
    if any(t == stripped_query for t in role_triggers) or stripped_query in role_triggers:
        return resp(f"Your current role is **{user_role}**.", confidence=1.0)

    # ── 3. OFF-TOPIC GUARD ────────────────────────────────
    company_keywords = [
        "revenue", "profit", "cost", "expense", "loss", "budget", "forecast",
        "leave", "policy", "remote", "salary", "hire", "hiring", "headcount",
        "handbook", "attendance", "marketing", "engineering", "hr", "finance",
        "report", "quarter", "annual", "employee", "team", "project", "sprint",
        "campaign", "nps", "kpi", "metric", "insurance", "allowance", "bonus",
        "department", "company", "document", "data", "access", "role",
        "training", "onboard", "performance", "review", "holiday", "benefit",
        "capital", "investment", "strategy", "roadmap"
    ]
    has_company_kw = any(kw in clean_query for kw in company_keywords)

    off_topic = [
        r"\bweather\b", r"\bjokes?\b", r"\bpoems?\b", r"\bsongs?\b",
        r"\blyrics?\b", r"\bstory\b", r"\bcook\b", r"\brecipes?\b",
        r"\bsports?\b", r"\bfootball\b", r"\bcricket\b", r"\bnews\b",
        r"\bpolitics\b", r"\bmovies?\b", r"\bgames?\b",
        r"\bwrite me a\b", r"\btell me a\b", r"\bgive me a\b",
        r"\bexplain quantum\b", r"\bmeaning of life\b",
    ]
    if any(re.search(p, clean_query) for p in off_topic) and not has_company_kw:
        return resp("I can only answer questions related to company documents, policies, and reports.", confidence=1.0)

    # ── 4. VAGUE GUARD ────────────────────────────────────
    vague_exact = [
        "ok", "okay", "yes", "no", "maybe", "sure", "please", "thanks",
        "thank you", "cool", "nice", "great", "good", "bad", "test",
        "do you know", "can you", "are you", "do you",
    ]
    if stripped_query in vague_exact or (len(stripped_query.split()) <= 2 and not has_company_kw):
        return resp("Please ask a specific question — e.g. 'What is the Q2 revenue?' or 'What is the HR leave policy?'", confidence=1.0)

    # ── 5. CACHE CHECK ────────────────────────────────────
    cached = _get_cache(user_role, clean_query)
    if cached:
        # Return cached result with fresh timing
        cached_copy = cached.copy()
        cached_copy["response_time_ms"] = ms()
        cached_copy["cached"] = True
        return cached_copy

    # ── 6. RBAC SEARCH ────────────────────────────────────
    docs = secure_semantic_search(query=query, user_role=user_role, top_k=3)
    doc_count = len(docs)
    confidence = round(
        sum(d["similarity_score"] or 0 for d in docs) / doc_count, 3
    ) if doc_count > 0 else 0.0
    sources = [d["metadata"]["source"] for d in docs]

    if doc_count == 0:
        result = resp(
            f"As a {user_role} user, you do not have access to this information or it doesn't exist.",
            confidence=0.0
        )
        return result

    context = build_context(docs)

    # ── 7. DIRECT EXTRACTION (sub-10ms) ──────────────────
    result = None

    if "revenue" in clean_query:
        m = re.search(r"(?:USD|EUR|GBP|₹|\$)\s*[\d,]+(?:\.\d+)?(?:K|M|B|m|b)?|[\d,]+(?:\.\d+)?\s*(?:USD|EUR|GBP|₹|\$|million|billion)", context, re.IGNORECASE)
        if m:
            result = resp(f"The reported revenue is {m.group()}.", sources, confidence, doc_count)

    elif "profit" in clean_query or "margin" in clean_query:
        m = re.search(r"\d+(\.\d+)?\s*%", context)
        if m:
            result = resp(f"The reported profit margin is {m.group()}.", sources, confidence, doc_count)

    elif "expense" in clean_query or "cost" in clean_query:
        m = re.search(r"(?:USD|EUR|GBP|₹|\$)\s*[\d,]+(?:\.\d+)?(?:K|M|B|m|b)?|[\d,]+(?:\.\d+)?\s*(?:USD|EUR|GBP|₹|\$|million|billion)", context, re.IGNORECASE)
        if m:
            result = resp(f"The reported operational expense is {m.group()}.", sources, confidence, doc_count)

    elif "leave" in clean_query:
        m = re.search(r"\d+\s*(?:casual|paid|sick|annual)?\s+leave\s+(?:days?)?", context, re.IGNORECASE)
        if m:
            result = resp(f"Leave policy: {m.group().capitalize()}.", sources, confidence, doc_count)

    elif "remote" in clean_query or "work from home" in clean_query or "wfh" in clean_query:
        if "remote" in context.lower() or "home" in context.lower():
            result = resp("Employees may generally work remotely as per company policy, but please refer to the context for specifics.", sources, confidence, doc_count)

    elif "engineer" in clean_query and any(w in clean_query for w in ["how many", "count", "number", "total"]):
        m = re.search(r"\d+\s*(?:software\s+)?engineers?", context, re.IGNORECASE)
        if m:
            result = resp(f"There are {m.group()} in the engineering department.", sources, confidence, doc_count)

    elif "nps" in clean_query or "net promoter" in clean_query:
        m = re.search(r"NPS.*?(?:is|of|\:)?\s*(\d+)", context, re.IGNORECASE)
        if m:
            result = resp(f"The Net Promoter Score (NPS) is {m.group(1)}.", sources, confidence, doc_count)

    # ── 8. LLM FALLBACK ───────────────────────────────────
    if result is None:
        load_model()
        messages = [
            {"role": "system", "content": (
                "You are an internal enterprise assistant. "
                "Answer ONLY using the Context provided below. "
                "Be concise — answer in 1-3 sentences only. "
                "Do NOT repeat context or source tags. "
                "If the answer is not in the context, say 'I cannot find the answer in the provided documents.'"
            )},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"}
        ]
        
        enc = tokenizer.apply_chat_template(messages, return_tensors="pt")
        enc = {k: v.to(model.device) for k, v in enc.items()}
        input_len = enc["input_ids"].shape[1]

        with torch.no_grad():
            outputs = model.generate(
                **enc,
                max_new_tokens=150,
                do_sample=False,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        new_tokens = outputs[0][input_len:]
        answer = clean_llm_output(tokenizer.decode(new_tokens, skip_special_tokens=True))
        if not answer or len(answer) < 5:
            answer = "I found relevant documents but could not generate a clear answer."
        result = resp(answer, sources, confidence, doc_count)

    # ── 9. CACHE THE RESULT ───────────────────────────────
    _set_cache(user_role, clean_query, result)
    return result