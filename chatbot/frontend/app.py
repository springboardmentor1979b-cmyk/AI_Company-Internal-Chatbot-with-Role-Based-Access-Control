import streamlit as st
import time
import os
import hashlib
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NexusAI — Enterprise Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Load CSS ────────────────────────────────────────────────────────────────
with open("styles.css", encoding="utf-8") as f: 
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Auth Config ─────────────────────────────────────────────────────────────
USERS = {
    "alice@nexus.com":    {"password": hashlib.sha256("Finance@123".encode()).hexdigest(), "role": "finance",     "name": "Alice Chen"},
    "bob@nexus.com":      {"password": hashlib.sha256("Market@123".encode()).hexdigest(),  "role": "marketing",   "name": "Bob Martinez"},
    "carol@nexus.com":    {"password": hashlib.sha256("HR@1234567".encode()).hexdigest(),  "role": "hr",          "name": "Carol Smith"},
    "dave@nexus.com":     {"password": hashlib.sha256("Eng@123456".encode()).hexdigest(),  "role": "engineering", "name": "Dave Patel"},
    "ceo@nexus.com":      {"password": hashlib.sha256("CEO@123456".encode()).hexdigest(),  "role": "c_level",     "name": "Frank CEO"},
}

ROLE_META = {
    "finance":     {"label": "Finance",     "icon": "💹", "color": "#4ade80"},
    "marketing":   {"label": "Marketing",   "icon": "📣", "color": "#f472b6"},
    "hr":          {"label": "HR",          "icon": "👥", "color": "#a78bfa"},
    "engineering": {"label": "Engineering", "icon": "⚙️", "color": "#38bdf8"},
    "c_level":     {"label": "C-Level",     "icon": "👑", "color": "#fbbf24"},
}

ROLE_SUGGESTIONS = {
    "finance":     ["Show Q3 revenue summary", "What is our latest budget allocation?", "Summarize quarterly spend"],
    "marketing":   ["Latest campaign performance?", "Show conversion metrics", "Summarize marketing strategy"],
    "hr":          ["What is the leave policy?", "List employee benefits", "Explain performance review process"],
    "engineering": ["Describe system architecture", "What are our tech stack choices?", "Explain deployment process"],
    "c_level":     ["Overall company performance?", "Summarize all departments", "Key KPIs across teams"],
}

# ─── Session State Init ──────────────────────────────────────────────────────
for key, val in [
    ("authenticated", False),
    ("user_email", None),
    ("user_role", None),
    ("user_name", None),
    ("access_token", None),
    ("messages", []),
    ("login_error", ""),
    ("login_attempts", 0),
    ("denied_queries", 0),
    ("page", "Dashboard"),
    ("session_day", datetime.now(timezone.utc).strftime('%Y-%m-%d')),
    ("daily_activity", []),
    ("mode", "login"),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─── Auth Helpers ─────────────────────────────────────────────────────────────
def authenticate(email, password):
    user = USERS.get(email.lower().strip())
    if not user:
        return False
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return hashed == user["password"]


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def backend_request(path, method="post", json_data=None, headers=None, timeout=5):
    try:
        import requests
        url = f"{BACKEND_URL}{path}"
        func = getattr(requests, method.lower())
        resp = func(url, json=json_data, headers=headers or {}, timeout=timeout)
        if resp.status_code >= 400:
            detail = None
            try:
                detail = resp.json().get("detail")
            except Exception:
                detail = resp.text or f"HTTP {resp.status_code}"
            return None, detail
        return resp.json(), None
    except Exception as e:
        return None, f"Backend unreachable: {e}"


def backend_login(email, password):
    return backend_request("/auth/login", method="post", json_data={"email": email, "password": password})


def login(email, password):
    if st.session_state.login_attempts >= 5:
        st.session_state.login_error = "Account locked — too many failed attempts."
        return

    data, err = backend_login(email, password)
    if data:
        st.session_state.authenticated = True
        st.session_state.user_email = data["user"]["email"]
        st.session_state.user_role = data["user"]["role"]
        st.session_state.user_name = data["user"]["name"]
        st.session_state.access_token = data["access_token"]
        st.session_state.login_error = ""
        st.session_state.login_attempts = 0
        st.session_state.messages = []
        return

    # fallback to local in-memory demo users
    if authenticate(email, password):
        u = USERS[email.lower().strip()]
        st.session_state.authenticated = True
        st.session_state.user_email = email.lower().strip()
        st.session_state.user_role = u["role"]
        st.session_state.user_name = u["name"]
        st.session_state.access_token = None
        st.session_state.login_error = ""
        st.session_state.login_attempts = 0
        st.session_state.messages = []
        return

    st.session_state.login_attempts += 1
    remaining = 5 - st.session_state.login_attempts
    st.session_state.login_error = err or f"Invalid credentials. {remaining} attempt(s) remaining."

def logout():
    for k in ["authenticated","user_email","user_role","user_name","messages"]:
        st.session_state[k] = False if k == "authenticated" else ([] if k == "messages" else None)

# ─── RAG Backend ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_rag():
    """Load the RAG pipeline — cached so it only runs once."""
    try:
        import os, pandas as pd
        from sentence_transformers import SentenceTransformer
        import chromadb

        def clean_text(text):
            return " ".join(str(text).replace("\n"," ").replace("\t"," ").strip().split())

        def chunk_text(text, chunk_size=300):
            from nltk.tokenize import word_tokenize
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            words = word_tokenize(text)
            return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

        role_mapping = {
            "finance":     ["financial_summary.md", "quarterly_financial_report.md"],
            "marketing":   ["marketing_report_2024.md", "marketing_report_q1_2024.md", "marketing_report_q2_2024.md", "marketing_report_q3_2024.md", "market_report_q4_2024.md"],
            "hr":          ["employee_handbook.md", "hr_data.csv"],
            "engineering": ["engineering_master_doc.md"],
            "c_level":     "all",
        }

        def assign_metadata(file_name, chunk, role_mapping):
            roles = []
            for role, files in role_mapping.items():
                if files == "all" or file_name in files:
                    roles.append(role)
            return {"source_file": file_name, "chunk_text": chunk, "roles": roles}

        model  = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.Client()
        try: client.delete_collection("company_docs")
        except: pass
        collection = client.get_or_create_collection("company_docs")

        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.normpath(os.path.join(base_dir, "..", "backend", "Fintech-data"))
        all_chunks = []

        if not os.path.isdir(folder):
            folder = os.path.normpath(os.path.join(base_dir, "..", "Fintech-data"))

        if os.path.isdir(folder):
            for root, _, files in os.walk(folder):
                for fname in files:
                    path = os.path.join(root, fname)
                    if fname.endswith(".md"):
                        raw = open(path, encoding="utf-8").read()
                        for chunk in chunk_text(clean_text(raw)):
                            all_chunks.append(assign_metadata(fname, chunk, role_mapping))
                    elif fname.endswith(".csv"):
                        df = pd.read_csv(path)
                        for col in df.select_dtypes(include="object").columns:
                            text = " ".join(df[col].dropna().astype(str).tolist())
                            for chunk in chunk_text(clean_text(text)):
                                all_chunks.append(assign_metadata(fname, chunk, role_mapping))

            for i, item in enumerate(all_chunks):
                collection.add(
                    ids=[f"chunk_{i}"],
                    embeddings=[model.encode(item["chunk_text"]).tolist()],
                    documents=[item["chunk_text"]],
                    metadatas=[{"roles": str(item["roles"]), "source": item["source_file"]}],
                )

        return collection, model, True
    except Exception as e:
        return None, None, str(e)

def search_docs(query, user_role, top_k=4):
    collection, model, status = load_rag()
    if not isinstance(status, bool) or not status:
        return [], f"RAG not loaded: {status}"

    results = collection.query(query_texts=[query], n_results=top_k * 3)
    docs = []
    if results and results["documents"] and results["documents"][0]:
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            try:
                roles_str = meta.get("roles", "[]")
                # Handle both JSON strings and direct Python list representations
                if isinstance(roles_str, str):
                    roles = json.loads(roles_str)
                else:
                    roles = roles_str if isinstance(roles_str, list) else []
            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, default to empty list (access denied)
                roles = []
            
            # c_level sees everything; others must be in the chunk's role list
            allowed = (user_role == "c_level") or (user_role in roles)
            if allowed:
                docs.append({"text": doc, "source": meta.get("source", "unknown")})
            if len(docs) >= top_k:
                break
    return docs, None

def build_answer(query, docs, user_name, user_role):
    """Simple but smart answer builder from retrieved context."""
    if not docs:
        suggested = ROLE_SUGGESTIONS.get(user_role, [])
        suggestions_text = "\n\n".join([f"- {s}" for s in suggested[:3]]) if suggested else "No quick suggestions available."
        return (
            f"❌ **Access Denied** — No documents accessible for your role.\n\n"
            f"**Your Role**: {ROLE_META[user_role]['label']}\n"
            f"**Query**: \"{query}\"\n\n"
            "This information may require higher access permissions. Try asking about topics related to your role:\n\n"
            f"{suggestions_text}"
        )

    sources = list({d['source'] for d in docs})
    summary_lines = []
    for d in docs:
        snippet = d['text'].replace("\n", " ").strip()
        if len(snippet) > 220:
            snippet = snippet[:220].rsplit(" ", 1)[0] + "…"
        summary_lines.append(f"- From {d['source']}: {snippet}")

    return (
        f"✅ Here's a concise summary based on your accessible documents:\n\n"
        f"{chr(10).join(summary_lines)}\n\n"
        f"If you want, I can provide deeper detail from a specific document or focus on a particular metric (revenue, cash flow, margins, vendor payment delays, etc.).\n\n"
        f"Sources: {', '.join(sources)}"
    )

# ─── LOGIN/REGISTER PAGE ───────────────────────────────────────────────────────────────
def render_login():
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("""
        <div class="login-card">
            <div class="login-logo">⬡</div>
            <h1 class="login-title">NexusAI</h1>
            <p class="login-subtitle">Enterprise Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)

        # Toggle between login and register
        if st.button("Switch to Register" if st.session_state.mode == "login" else "Switch to Login"):
            st.session_state.mode = "register" if st.session_state.mode == "login" else "login"
            st.rerun()

        if st.session_state.mode == "login":
            # Login form
            email = st.text_input("Email", placeholder="you@company.com", label_visibility="collapsed")
            password = st.text_input("Password", placeholder="Password", type="password", label_visibility="collapsed")

            if st.button("Login"):
                login(email, password)
                if st.session_state.authenticated:
                    st.success(f"Welcome, {st.session_state.user_name}!")
                else:
                    st.error(st.session_state.login_error)
        else:
            # Register form
            name = st.text_input("Full Name", placeholder="Your Full Name", label_visibility="collapsed")
            email = st.text_input("Email", placeholder="you@company.com", label_visibility="collapsed")
            password = st.text_input("Password", placeholder="Password (min 6 chars)", type="password", label_visibility="collapsed")
            role = st.selectbox("Role", ["finance", "marketing", "hr", "engineering", "c_level"], label_visibility="collapsed")

            if st.button("Register"):
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif not name or not email:
                    st.error("Name and email are required")
                else:
                    data, err = backend_request(
                        "/auth/register",
                        method="post",
                        json_data={
                            "email": email,
                            "name": name,
                            "password": password,
                            "role": role,
                        },
                    )
                    if data:
                        st.success("Registration successful! Please login.")
                        st.session_state.mode = "login"
                        st.rerun()
                    else:
                        st.error(err or "Registration failed")

        if st.session_state.login_error:
            st.markdown(f'<div class="error-msg">⚠ {st.session_state.login_error}</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="demo-accounts">
            <p class="demo-title">Demo Accounts</p>
            <div class="demo-grid">
                <div class="demo-item"><span class="demo-role">💹 Finance</span><br>alice@nexus.com<br>Finance@123</div>
                <div class="demo-item"><span class="demo-role">📣 Marketing</span><br>bob@nexus.com<br>Market@123</div>
                <div class="demo-item"><span class="demo-role">👥 HR</span><br>carol@nexus.com<br>HR@1234567</div>
                <div class="demo-item"><span class="demo-role">👑 C-Level</span><br>ceo@nexus.com<br>CEO@123456</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── OPENAI + AGENT HELPERS ───────────────────────────────────────────────────
def get_openai_answer(query, user_role, docs):
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openai_key:
        return None
    try:
        import openai  # type: ignore
    except ImportError:
        return None

    openai.api_key = openai_key
    system_prompt = (
        "You are NexusAI, an enterprise assistant. "
        "Use the internal knowledge base snippets when available and keep answers concise, helpful, and secure."
    )

    context = ""
    if docs:
        context = "\n\n".join([f"{d['source']}: {d['text']}" for d in docs[:4]])

    chat_history = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        if msg["role"] in ["user", "assistant"]:
            chat_history.append({"role": msg["role"], "content": msg["content"]})

    prompt = f"Role: {user_role}\nQuery: {query}\n\nContext:\n{context if context else 'No direct relevant context found.'}"
    chat_history.append({"role": "user", "content": prompt})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=chat_history,
            temperature=0.2,
            max_tokens=450,
            top_p=1,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def backend_query(question: str):
    if not st.session_state.access_token:
        return None, "No backend token available"
    data, err = backend_request(
        "/rag/query",
        method="post",
        json_data={"query": question, "top_k": 5},
        headers={"Authorization": f"Bearer {st.session_state.access_token}"},
    )
    if err or not data:
        return None, err
    sources = data.get("sources", [])
    docs = [{"source": src, "text": ""} for src in sources]
    return data.get("answer", ""), docs


def query_agent(question: str):
    role = st.session_state.user_role

    if st.session_state.access_token:
        answer, docs = backend_query(question)
        if answer:
            return answer, docs

    docs, err = search_docs(question, role)
    if not docs:
        st.session_state.denied_queries += 1

    openai_resp = get_openai_answer(question, role, docs)
    if openai_resp:
        return openai_resp, docs

    return build_answer(question, docs, st.session_state.user_name, role), docs


def set_page(page_name: str):
    """Helper to switch pages in sidebar navigation."""
    st.session_state.page = page_name


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def render_sidebar():
    role = st.session_state.user_role
    meta = ROLE_META[role]

    with st.sidebar:
        st.markdown(f"""
        <div class='sidebar-profile'>
            <div class='avatar'>{meta['icon']}</div>
            <div>
                <div class='profile-name'>{st.session_state.user_name}</div>
                <div class='profile-role'>{meta['label']} Access</div>
                <div class='profile-email'>{st.session_state.user_email or ''}</div>
            </div>
        </div>
        <div class='sidebar-divider'></div>
        """, unsafe_allow_html=True)

        # Navigation buttons in a grid
        col1, col2 = st.columns(2)
        with col1:
            st.button("💬 Chat", on_click=set_page, args=("Chat",), use_container_width=True)
            st.button("📊 Dashboard", on_click=set_page, args=("Dashboard",), use_container_width=True)
        with col2:
            st.button("📜 History", on_click=set_page, args=("History",), use_container_width=True)
            st.button("📄 Upload", on_click=set_page, args=("Upload Docs",), use_container_width=True)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<p class="sidebar-section">Quick Queries</p>', unsafe_allow_html=True)

        for suggestion in ROLE_SUGGESTIONS[role]:
            if st.button(f"→ {suggestion}", key=f"sug_{suggestion}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": suggestion, "timestamp": datetime.now(timezone.utc).isoformat()})
                with st.spinner("Searching knowledge base..."):
                    docs, err = search_docs(suggestion, role)
                    answer = build_answer(suggestion, docs, st.session_state.user_name, role)
                st.session_state.messages.append({"role": "assistant", "content": answer, "timestamp": datetime.now(timezone.utc).isoformat()})
                st.rerun()

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        denied_count = st.session_state.denied_queries
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        today_queries = len([m for m in st.session_state.messages if m["role"] == "user" and m.get("timestamp", "").startswith(today)])

        st.markdown(f"""
        <div class="sidebar-stats">
            <div class="stat-item">
                <span class="stat-label">Today's Queries</span>
                <span class="stat-value">{today_queries}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Total Queries</span>
                <span class="stat-value">{msg_count}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Access Denied</span>
                <span class="stat-value">{denied_count}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Role Access</span>
                <span class="stat-value">{meta['label']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("🔒 Sign Out", use_container_width=True, key="logout_btn"):
            logout()
            st.rerun()
# ─── DASHBOARD + PAGES ──────────────────────────────────────────────────────
def render_dashboard():
    role = st.session_state.user_role
    meta = ROLE_META[role]
    total_queries = len([m for m in st.session_state.messages if m["role"] == "user"])
    active_users = 1
    access_denied = st.session_state.denied_queries
    total_users = 7

    st.markdown("""
    <div class='dashboard-header'>
        <div>
            <h1>Analytics Dashboard</h1>
            <p>Role: <strong style='color:{role_color};'>{role_label}</strong> | Active session for {user}</p>
        </div>
        <div class='dashboard-pill'>Live</div>
    </div>
    """.format(role_color=meta["color"], role_label=meta["label"], user=st.session_state.user_name), unsafe_allow_html=True)

    # Top metrics cards
    col1, col2, col3, col4 = st.columns(4, gap="small")
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_queries}</div>
            <div class='metric-label'>Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{total_users}</div>
            <div class='metric-label'>Total Users</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{access_denied}</div>
            <div class='metric-label'>Access Denied</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{active_users}</div>
            <div class='metric-label'>Active Today</div>
        </div>
        """, unsafe_allow_html=True)

    # Charts and panels in grid
    st.markdown("<div class='dashboard-grid'>", unsafe_allow_html=True)
    chart1, chart2 = st.columns(2, gap="small")

    with chart1:
        st.markdown("<div class='dashboard-panel'><h3>Queries by Role</h3></div>", unsafe_allow_html=True)
        role_counts = {
            "Finance": sum(1 for m in st.session_state.messages if m.get("role") == "finance"),
            "Marketing": sum(1 for m in st.session_state.messages if m.get("role") == "marketing"),
            "HR": sum(1 for m in st.session_state.messages if m.get("role") == "hr"),
            "Engineering": sum(1 for m in st.session_state.messages if m.get("role") == "engineering"),
            "C-Level": sum(1 for m in st.session_state.messages if m.get("role") == "c_level"),
        }
        st.bar_chart(role_counts)

    with chart2:
        st.markdown("<div class='dashboard-panel'><h3>Activity - last 7 days</h3></div>", unsafe_allow_html=True)
        history = st.session_state.daily_activity[-7:] if st.session_state.daily_activity else [1, 2, 0, 0, 1, 1, total_queries]
        st.line_chart(history)

    st.markdown("</div>", unsafe_allow_html=True)

    # Bottom panels in grid
    panel1, panel2 = st.columns(2, gap="small")
    with panel1:
        st.markdown("<div class='dashboard-panel'><h3>Top Queries</h3></div>", unsafe_allow_html=True)
        top_queries = ["What is our Q3 revenue?", "Show marketing budget", "Employee handbook summary", "Latest financial report"]
        for q in top_queries:
            st.markdown(f"<div class='dashboard-item'>▶ {q}</div>", unsafe_allow_html=True)

    with panel2:
        st.markdown("<div class='dashboard-panel'><h3>Top Denied Queries</h3></div>", unsafe_allow_html=True)
        denied = ["Confidential data request", "Unauthorized access attempt", "Outside role scope"] if access_denied > 0 else ["No denied queries yet"]
        for d in denied:
            st.markdown(f"<div class='dashboard-item'>⚠ {d}</div>", unsafe_allow_html=True)

    # User activity table
    st.markdown("<h3>User Login Activity</h3>", unsafe_allow_html=True)
    login_data = [
        {"User": "Alice Chen", "Role": "Finance", "Last Login": "2026-04-03 10:30", "Queries": 5},
        {"User": "Bob Martinez", "Role": "Marketing", "Last Login": "2026-04-03 09:15", "Queries": 3},
        {"User": "Carol Smith", "Role": "HR", "Last Login": "2026-04-02 16:45", "Queries": 2},
        {"User": "Dave Patel", "Role": "Engineering", "Last Login": "2026-04-03 11:00", "Queries": 1},
    ]
    st.table(login_data)


def render_history():
    st.header("📜 Conversation History")
    if not st.session_state.messages:
        st.info("No chat history yet. Start a conversation in Chat mode.")
        return
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"**You:** {m['content']}")
        else:
            st.markdown(f"**NEXUS AI:** {m['content']}")


def render_upload_docs():
    st.header("📄 Upload Documents")
    st.write("Drop markdown or CSV files to add to your private knowledge base.")
    uploaded = st.file_uploader("Choose files", accept_multiple_files=True, type=["md", "csv"])
    if uploaded:
        for f in uploaded:
            target_dir = os.path.join(os.path.dirname(__file__), "..", "backend", "Fintech-data")
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, f.name)
            with open(target_path, "wb") as out:
                out.write(f.getbuffer())
        st.success(f"Saved {len(uploaded)} file(s). Restart backend to refresh RAG index.")

# ─── CHAT PAGE ────────────────────────────────────────────────────────────────
def render_chat():
    role = st.session_state.user_role
    meta = ROLE_META[role]

    st.markdown(f"""
    <div class="chat-header">
        <div class="chat-header-left">
            <span class="chat-logo">⬡</span>
            <div>
                <h2 class="chat-title">NexusAI Intelligence</h2>
                <p class="chat-subtitle">Searching <span style="color:{meta['color']}">{meta['label']}</span> knowledge base</p>
            </div>
        </div>
        <div class="chat-badge" style="background:{meta['color']}20;border:1px solid {meta['color']}40;color:{meta['color']}">
            {meta['icon']} {meta['label']} Access
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.messages:
        st.chat_message("assistant").write(f"Welcome, {st.session_state.user_name.split()[0]}! I'm your AI assistant. Ask me anything.")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    user_input = st.chat_input("Ask anything within your access level…")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input, "timestamp": datetime.now(timezone.utc).isoformat()})
        st.session_state.daily_activity.append(1)

        with st.chat_message("assistant"):
            st.write("Typing...")

        with st.spinner("💬 Generating response…"):
            answer, docs = query_agent(user_input)
            time.sleep(0.3)

        st.session_state.messages.append({"role": "assistant", "content": answer, "timestamp": datetime.now(timezone.utc).isoformat()})
        st.rerun()

    if st.button("🗑 Clear chat", key="clear_chat"):
        st.session_state.messages = []
        st.rerun()

# ─── SYSTEM HEADER ───────────────────────────────────────────────────────────
def render_system_header():
    st.markdown("""
    <div class='system-bar'>
      <span>NEXUS AI Intelligence Platform</span>
      <span class='system-indicator'><span class='system-dot'></span> SYSTEM ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

# ─── ROUTER ──────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    render_login()
else:
    render_system_header()
    render_sidebar()
    if st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Chat":
        render_chat()
    elif st.session_state.page == "History":
        render_history()
    elif st.session_state.page == "Upload Docs":
        render_upload_docs()
    else:
        render_dashboard()
