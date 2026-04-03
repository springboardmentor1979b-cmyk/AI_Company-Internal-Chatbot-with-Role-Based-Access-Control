"""
app.py — Infobot | Infosys Internal Chatbot (Premium UI)
"""

import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Infobot | Infosys Internal",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — Infosys Blue Branding ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }

/* Deep midnight blue background */
.stApp {
    background: radial-gradient(circle at top left, #001f3f, #000000);
}

/* Hide Streamlit defaults */
#MainMenu, footer, header { visibility: hidden; }

/* Glass login form */
[data-testid="stForm"] {
    border: 1px solid #007cc3;
    border-radius: 20px;
    background-color: rgba(0, 124, 195, 0.05);
    padding: 40px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}

/* Infosys Blue button */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #007cc3 0%, #005a92 100%);
    color: white;
    border: none;
    border-radius: 10px;
    width: 100%;
    height: 3em;
    font-weight: bold;
    font-size: 1rem;
    letter-spacing: 0.03em;
    transition: all 0.2s ease;
}
div.stButton > button:first-child:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 124, 195, 0.5);
    opacity: 0.95;
}

/* Form submit button */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #007cc3 0%, #005a92 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    width: 100% !important;
    height: 3em !important;
    font-weight: bold !important;
    font-size: 1rem !important;
    margin-top: 0.5rem;
}
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 124, 195, 0.5) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #00162d !important;
    border-right: 1px solid #007cc3 !important;
}
[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }

/* Input fields */
.stTextInput > div > div > input {
    background: rgba(0, 124, 195, 0.08) !important;
    border: 1px solid rgba(0, 124, 195, 0.35) !important;
    border-radius: 10px !important;
    color: white !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #007cc3 !important;
    box-shadow: 0 0 0 2px rgba(0, 124, 195, 0.25) !important;
}
.stTextInput > div > div > input::placeholder { color: rgba(255,255,255,0.3) !important; }

/* Labels */
.stTextInput label, .stSlider label, label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(0, 124, 195, 0.05) !important;
    border: 1px solid rgba(0, 124, 195, 0.15) !important;
    border-radius: 14px !important;
    padding: 1rem 1.2rem !important;
    margin-bottom: 0.75rem !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    background: rgba(0, 124, 195, 0.07) !important;
    border: 1px solid rgba(0, 124, 195, 0.3) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* Expander — clean readable text */
details summary {
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    background: rgba(0,124,195,0.08) !important;
    border: 1px solid rgba(0,124,195,0.25) !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
}
details summary:hover {
    background: rgba(0,124,195,0.15) !important;
    color: white !important;
}
details[open] summary {
    border-radius: 10px 10px 0 0 !important;
}
details > div {
    background: rgba(0,124,195,0.05) !important;
    border: 1px solid rgba(0,124,195,0.2) !important;
    border-top: none !important;
    border-radius: 0 0 10px 10px !important;
    padding: 0.75rem !important;
}
.streamlit-expanderHeader {
    background: transparent !important;
    border: none !important;
    color: rgba(255,255,255,0.75) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}
.streamlit-expanderHeader p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.88rem !important;
}
[data-testid="stExpander"] {
    border: 1px solid rgba(0,124,195,0.25) !important;
    border-radius: 10px !important;
    background: rgba(0,124,195,0.05) !important;
}
[data-testid="stExpander"] summary {
    color: white !important;
}


/* Divider */
hr { border-color: rgba(0, 124, 195, 0.25) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #007cc3; border-radius: 3px; }

/* Glass card */
.glass-card {
    background: rgba(0, 124, 195, 0.05);
    border: 1px solid rgba(0, 124, 195, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Stat card */
.stat-card {
    background: rgba(0, 124, 195, 0.08);
    border: 1px solid rgba(0, 124, 195, 0.25);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
}
.stat-label { color: rgba(255,255,255,0.4); font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; }
.stat-value { color: #007cc3; font-size: 1.6rem; font-weight: 700; margin-top: 0.2rem; }

/* Role badge */
.role-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Success/error */
.stSuccess { background: rgba(0, 124, 195, 0.12) !important; border: 1px solid rgba(0, 124, 195, 0.3) !important; border-radius: 10px !important; }
.stError { background: rgba(229,57,53,0.12) !important; border: 1px solid rgba(229,57,53,0.3) !important; border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ── Session defaults ──────────────────────────────────────────
for key, default in [
    ("token", None), ("username", ""), ("role", ""),
    ("department", ""), ("history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── API helpers ───────────────────────────────────────────────
def api_login(username: str, password: str):
    try:
        r = requests.post(f"{BACKEND_URL}/auth/login",
                          json={"username": username, "password": password}, timeout=10)
        return (r.json(), None) if r.status_code == 200 else (None, r.json().get("detail", "Login failed"))
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend. Is it running?"

def api_query(question: str, top_k: int = 4):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        r = requests.post(f"{BACKEND_URL}/chat/query",
                          json={"question": question, "top_k": top_k}, headers=headers, timeout=90)
        return (r.json(), None) if r.status_code == 200 else (None, r.json().get("detail", "Query failed"))
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend."


# ── Role config ───────────────────────────────────────────────
ROLE_CONFIG = {
    "finance":     {"color": "#1E88E5", "icon": "💼", "label": "Finance"},
    "marketing":   {"color": "#E91E63", "icon": "📣", "label": "Marketing"},
    "hr":          {"color": "#43A047", "icon": "👥", "label": "Human Resources"},
    "engineering": {"color": "#FB8C00", "icon": "⚙️", "label": "Engineering"},
    "employees":   {"color": "#8E24AA", "icon": "📖", "label": "Employees"},
    "c_level":     {"color": "#007cc3", "icon": "👑", "label": "C-Level"},
}

DEMO_ACCOUNTS = [
    ("alice",  "alice123",  "Finance",      "💼"),
    ("bob",    "bob123",    "Marketing",    "📣"),
    ("carol",  "carol123",  "HR",           "👥"),
    ("dave",   "dave123",   "Engineering",  "⚙️"),
    ("eve",    "eve123",    "Employees",    "📖"),
    ("frank",  "frank123",  "C-Level",      "👑"),
]


# ── Sidebar branding (always visible) ─────────────────────────
def render_sidebar_branding():
    with st.sidebar:
        # Infosys logo
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Infosys_logo.svg/1200px-Infosys_logo.svg.png",
            use_container_width=True,
        )
        st.markdown("""
        <div style="text-align:center;margin:0.5rem 0 1rem">
            <span style="background:rgba(0,124,195,0.15);color:#007cc3;border:1px solid #007cc3;
            padding:4px 14px;border-radius:20px;font-size:0.75rem;font-weight:600;letter-spacing:0.05em">
            🔒 SECURE INTERNAL PORTAL</span>
        </div>
        <hr style="border-color:rgba(0,124,195,0.25);margin:0.75rem 0"/>
        """, unsafe_allow_html=True)


# ── Login page ────────────────────────────────────────────────
def show_login():
    render_sidebar_branding()
    with st.sidebar:
        st.markdown("""
        <div style="color:rgba(255,255,255,0.4);font-size:0.78rem;text-align:center;line-height:1.6">
            This portal uses Role-Based Access Control.<br>
            Login credentials are assigned by IT.
        </div>
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # Header
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 2.5rem">
            <div style="font-size:3.5rem;margin-bottom:0.75rem">🛡️</div>
            <div style="font-size:2.4rem;font-weight:700;color:#007cc3;letter-spacing:-0.02em">Infobot</div>
            <div style="color:rgba(255,255,255,0.45);font-size:0.95rem;margin-top:0.4rem;font-weight:300">
                Secure AI-Powered Internal Knowledge Assistant
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🔐  Sign In", use_container_width=True)

        if submitted:
            if not username or not password:
                st.warning("⚠️ Please enter both username and password.")
            else:
                with st.spinner("Authenticating…"):
                    data, error = api_login(username, password)
                if error:
                    st.error(error)
                else:
                    st.session_state.token      = data["access_token"]
                    st.session_state.username   = data["username"]
                    st.session_state.role       = data["role"]
                    st.session_state.department = data["department"]
                    st.session_state.history    = []
                    st.success(f"✅ Welcome, {username}! Redirecting…")
                    st.rerun()

        # Demo accounts collapsed inside expander
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        with st.expander("🛠️ Developer Access (Demo Accounts)"):
            for user, pwd, dept, icon in DEMO_ACCOUNTS:
                st.markdown(f"""
                <div style="background:rgba(0,124,195,0.07);border:1px solid rgba(0,124,195,0.2);
                border-radius:8px;padding:0.5rem 0.85rem;margin-bottom:0.4rem;
                display:flex;justify-content:space-between;font-size:0.85rem">
                    <span style="color:#007cc3">{icon} {dept}</span>
                    <span style="color:rgba(255,255,255,0.65);font-family:monospace">{user} / {pwd}</span>
                </div>
                """, unsafe_allow_html=True)


# ── Chat page ─────────────────────────────────────────────────
def show_chat():
    role = st.session_state.role
    cfg  = ROLE_CONFIG.get(role, {"color": "#007cc3", "icon": "👤", "label": role.upper()})

    render_sidebar_branding()
    with st.sidebar:
        # User profile card
        st.markdown(f"""
        <div style="background:rgba(0,124,195,0.08);border:1px solid rgba(0,124,195,0.25);
        border-radius:14px;padding:1.25rem;margin-bottom:1rem;text-align:center">
            <div style="font-size:2.2rem">{cfg["icon"]}</div>
            <div style="font-weight:700;font-size:1.05rem;color:white;margin:0.3rem 0">{st.session_state.username}</div>
            <span style="background:{cfg["color"]}22;color:{cfg["color"]};border:1px solid {cfg["color"]}44;
            padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;letter-spacing:0.05em">
            {cfg["icon"]} {cfg["label"]}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='color:rgba(255,255,255,0.4);font-size:0.72rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem'>Settings</p>", unsafe_allow_html=True)
        top_k = st.slider("Chunks to retrieve", 1, 8, 4)
        show_sources = st.checkbox("Show source chunks", value=False)
        st.markdown("<hr/>", unsafe_allow_html=True)

        total_messages = len([m for m in st.session_state.history if m["role"] == "user"])
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Queries This Session</div>
            <div class="stat-value">{total_messages}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", use_container_width=True):
            for k in ["token", "username", "role", "department", "history"]:
                st.session_state[k] = "" if k != "history" else []
            st.session_state.token = None
            st.rerun()

    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;
    border-bottom:1px solid rgba(0,124,195,0.25);padding-bottom:1.25rem;margin-bottom:1.5rem">
        <div style="font-size:2.8rem">🛡️</div>
        <div>
            <div style="font-size:2rem;font-weight:700;color:#007cc3;letter-spacing:-0.02em">Infobot</div>
            <div style="color:rgba(255,255,255,0.4);font-size:0.85rem;margin-top:0.15rem">
                Secure AI-Powered Internal Knowledge Assistant &nbsp;·&nbsp;
                <span style="color:{cfg["color"]};font-weight:600">{cfg["icon"]} {cfg["label"]} Access</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome card if first visit
    if not st.session_state.history:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;padding:2rem">
            <div style="font-size:2.5rem;margin-bottom:0.75rem">👋</div>
            <div style="font-size:1.1rem;font-weight:600;color:white;margin-bottom:0.4rem">
                Hello, {st.session_state.username}!
            </div>
            <div style="color:rgba(255,255,255,0.4);max-width:420px;margin:0 auto;font-size:0.9rem">
                Ask me anything about your Company's internal documents.
                Your results are restricted to <strong style="color:{cfg["color"]}">{cfg["label"]}</strong> permissions.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat history
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📄 Sources"):
                    for s in msg["sources"]:
                        st.markdown(f"- `{s}`")
            if show_sources and msg.get("chunks"):
                with st.expander("🔍 Retrieved Chunks"):
                    for i, chunk in enumerate(msg["chunks"], 1):
                        st.markdown(f"**Chunk {i}** | `{chunk['source']}` | score: {chunk['score']}")
                        st.text(chunk["document"][:300])

    # Chat input
    if question := st.chat_input("Ask a question about company documents…"):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.history.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching documents…"):
                data, error = api_query(question, top_k)

            if error:
                st.error(error)
                answer, sources, chunks = error, [], []
            else:
                answer  = data["answer"]
                sources = data["sources"]
                chunks  = data.get("chunks", [])
                st.markdown(answer)
                if sources:
                    with st.expander("📄 Sources"):
                        for s in sources:
                            st.markdown(f"- `{s}`")
                if show_sources and chunks:
                    with st.expander("🔍 Retrieved Chunks"):
                        for i, chunk in enumerate(chunks, 1):
                            st.markdown(f"**Chunk {i}** | `{chunk['source']}` | score: {chunk['score']}")
                            st.text(chunk["document"][:300])

        st.session_state.history.append({
            "role": "assistant", "content": answer,
            "sources": sources, "chunks": chunks,
        })


# ── Router ────────────────────────────────────────────────────
if st.session_state.token:
    show_chat()
else:
    show_login()
