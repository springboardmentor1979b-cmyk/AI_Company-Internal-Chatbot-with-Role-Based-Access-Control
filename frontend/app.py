"""
app.py — Infobot | Infosys Internal Chatbot 
(Premium UI with Dashboard & Analytics)
"""

import streamlit as st
import requests
import pandas as pd
import altair as alt

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Infobot | Infosys Internal",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Infosys Blue Custom CSS ───────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
/* Avoid overriding material icons */
:not(i) { font-family: 'Inter', sans-serif; }

/* Deep midnight blue background */
.stApp {
    background: radial-gradient(circle at top left, #001f3f, #000000);
}

/* Hide Streamlit defaults, but KEEP the header so the sidebar toggle arrow works! */
#MainMenu, footer { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

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
    color: white;
}

/* Form submit button */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #007cc3 0%, #005a92 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
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
    background: transparent !important;
    color: white !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.95rem !important;
}
.stTextInput [data-baseweb="input"] {
    background: rgba(0, 124, 195, 0.08) !important;
    border: 1px solid rgba(0, 124, 195, 0.35) !important;
    border-radius: 10px !important;
}
.stTextInput [data-baseweb="input"]:focus-within {
    border-color: #007cc3 !important;
    box-shadow: 0 0 0 1px rgba(0, 124, 195, 0.5) !important;
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
[data-testid="stChatInput"] > div {
    background: rgba(0, 124, 195, 0.05) !important;
    border: 1px solid rgba(0, 124, 195, 0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: #007cc3 !important;
    box-shadow: 0 0 0 1px rgba(0,124,195,0.5) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
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
.streamlit-expanderHeader p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.88rem !important;
}

/* Divider */
hr { border-color: rgba(0, 124, 195, 0.25) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #007cc3; border-radius: 3px; }

/* Metric Cards */
[data-testid="stMetricValue"] {
    color: #007cc3 !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    font-weight: 600 !important;
}

/* Navigation Radio */
.stRadio > div { flex-direction: column !important; }
.stRadio > div > label > div { color: rgba(255,255,255,0.7) !important; font-size: 0.95rem !important; font-weight: 500 !important; padding: 0.5rem !important; }

/* Glass card */
.glass-card {
    background: rgba(0, 124, 195, 0.05);
    border: 1px solid rgba(0, 124, 195, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Success/error */
.stSuccess { background: rgba(0, 124, 195, 0.12) !important; border: 1px solid rgba(0, 124, 195, 0.3) !important; border-radius: 10px !important; }
.stError { background: rgba(229,57,53,0.12) !important; border: 1px solid rgba(229,57,53,0.3) !important; border-radius: 10px !important; }

/* Dataframes */
[data-testid="stDataFrame"] { border: 1px solid rgba(0, 124, 195, 0.3); border-radius: 8px;}
</style>
""", unsafe_allow_html=True)


# ── Role config ───────────────────────────────────────────────
ROLE_CONFIG = {
    "finance":     {"color": "#1E88E5", "icon": "💼", "label": "Finance"},
    "marketing":   {"color": "#E91E63", "icon": "📣", "label": "Marketing"},
    "hr":          {"color": "#43A047", "icon": "👥", "label": "Human Resources"},
    "engineering": {"color": "#FB8C00", "icon": "⚙️", "label": "Engineering"},
    "employees":   {"color": "#9C27B0", "icon": "📖", "label": "Employees"},
    "c_level":     {"color": "#007cc3", "icon": "👑", "label": "C-Level"},
}

# ── Session defaults ──────────────────────────────────────────
for key, default in [
    ("token", None), ("username", ""), ("role", ""),
    ("department", ""), ("history", []), ("current_page", "🤖 Infobot Chat")
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── API Calls ─────────────────────────────────────────────────
def api_login(username: str, password: str):
    try:
        r = requests.post(f"{BACKEND_URL}/auth/login",
                          json={"username": username, "password": password}, timeout=10)
        return (r.json(), None) if r.status_code == 200 else (None, r.json().get("detail", "Login failed."))
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend."

def api_query(question: str, top_k: int = 4):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        r = requests.post(f"{BACKEND_URL}/chat/query",
                          json={"question": question, "top_k": top_k}, headers=headers, timeout=90)
        if r.status_code == 200:
            return r.json(), None
        try:
            err = r.json().get("detail", f"Backend Error: {r.status_code}")
        except Exception:
            err = f"Backend Error: {r.status_code}"
        return None, err
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def api_get_history():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        r = requests.get(f"{BACKEND_URL}/chat/history", headers=headers, timeout=10)
        return (r.json().get("history", []), None) if r.status_code == 200 else ([], "Error loading history")
    except requests.ConnectionError:
        return [], "❌ Cannot reach backend."

def api_get_dashboard():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        r = requests.get(f"{BACKEND_URL}/admin/dashboard", headers=headers, timeout=10)
        return (r.json(), None) if r.status_code == 200 else (None, "Unauthorized Access")
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend."


# ── Sidebar & Navigation ──────────────────────────────────────
def render_sidebar():
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
        """, unsafe_allow_html=True)

        cfg = ROLE_CONFIG.get(st.session_state.role, {"color": "#007cc3", "icon": "👤", "label": st.session_state.role.upper()})

        st.markdown(f"""
        <div style="background:rgba(0,124,195,0.08);border:1px solid rgba(0,124,195,0.25);
        border-radius:14px;padding:1rem;margin-bottom:1.5rem;text-align:center">
            <div style="font-weight:700;font-size:1.05rem;color:white;margin:0.3rem 0">{st.session_state.username}</div>
            <span style="background:{cfg["color"]}22;color:{cfg["color"]};border:1px solid {cfg["color"]}44;
            padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:600;letter-spacing:0.05em">
            {cfg["icon"]} {cfg["label"]}</span>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown("<p style='color:rgba(255,255,255,0.4);font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem'>Navigation</p>", unsafe_allow_html=True)
        
        pages = ["🤖 Infobot Chat", "📜 Query History", "📂 Upload Documents", "📊 Analytics Dashboard"]
        st.session_state.current_page = st.radio("Go to:", pages, label_visibility="collapsed")
        
        st.markdown("<hr/>", unsafe_allow_html=True)
        
        if st.button("🚪 Sign Out"):
            for k in ["token", "username", "role", "department", "history"]:
                st.session_state[k] = "" if k != "history" else []
            st.session_state.token = None
            st.rerun()


# ── Views ─────────────────────────────────────────────────────

def show_login():
    with st.sidebar:
        # Infosys logo
        st.image(
            "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Infosys_logo.svg/1200px-Infosys_logo.svg.png",
            use_container_width=True,
        )
        st.markdown("""
        <div style="color:rgba(255,255,255,0.4);font-size:0.78rem;text-align:center;line-height:1.6">
            This portal uses Role-Based Access Control.<br>
            Login credentials are assigned by IT.
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("---")
        st.sidebar.caption("🚀 Infosys Springboard | Virtual Internship 6.0")

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 2.5rem">
            <div style="font-size:3.5rem;margin-bottom:0.75rem">🛡️</div>
            <div style="font-size:2.4rem;font-weight:700;color:#007cc3;letter-spacing:-0.02em">Infobot</div>
            <div style="color:rgba(255,255,255,0.45);font-size:0.95rem;margin-top:0.4rem;font-weight:300">
                Secure AI-Powered Internal Knowledge Assistant
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)

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
                    st.session_state.current_page = "🤖 Infobot Chat"
                    st.rerun()


def view_chat():
    cfg = ROLE_CONFIG.get(st.session_state.role, {"color": "#007cc3", "icon": "👤", "label": st.session_state.role.upper()})

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

    for msg in st.session_state.history:
        avatar_emoji = "👤" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar_emoji):
            st.markdown(msg["content"])


    if question := st.chat_input("Ask a question about company documents…"):
        with st.chat_message("user", avatar="👤"):
            st.markdown(question)
        st.session_state.history.append({"role": "user", "content": question})

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🔍 Searching documents… (Note: Initializing AI requires 30 seconds warmup)"):
                data, error = api_query(question, top_k=4)

            if error:
                st.error(error)
                answer, sources, chunks = error, [], []
            else:
                answer = data["answer"]
                sources = data["sources"]
                chunks = data.get("chunks", [])
                st.markdown(answer)
        
        st.session_state.history.append({
            "role": "assistant", "content": answer,
            "sources": sources, "chunks": chunks,
        })


def view_history():
    st.markdown("""
    <div style="border-bottom: 1px solid rgba(0,124,195,0.25); padding-bottom: 0.5rem; margin-bottom: 1.5rem;">
        <h2 style="margin:0; font-size:1.5rem; color:#E6F1FF;">Query History</h2>
        <p style="color:rgba(255,255,255,0.5); font-size:0.9rem;">View your previously searched questions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Loading history..."):
        history_logs, error = api_get_history()
    
    if error:
        st.error(error)
        return
        
    if not history_logs:
        st.info("No query logs found for your account.")
        return
        
    for log in history_logs:
        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem 1.5rem; margin-bottom: 0.8rem; border-left: 4px solid #007cc3;">
            <div style="color:white; font-weight:600; font-size: 1.05rem; margin-bottom:0.5rem;">"{log['query_text']}"</div>
            <div style="display:flex; justify-content:space-between; font-size:0.8rem; color:rgba(255,255,255,0.4);">
                <span>Event ID: {log['id']}</span>
                <span>Timestamp: {log['timestamp']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def view_upload():
    st.markdown("""
    <div style="border-bottom: 1px solid rgba(0,124,195,0.25); padding-bottom: 0.5rem; margin-bottom: 1.5rem;">
        <h2 style="margin:0; font-size:1.5rem; color:#E6F1FF;">Upload Documents</h2>
        <p style="color:rgba(255,255,255,0.5); font-size:0.9rem;">Add new knowledge base files directly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.warning("⚠️ Secure Upload deactivated in this UI prototype. Please use the backend `scripts/ingest_data.py` on the host machine to index new files securely.")
    st.file_uploader("Upload Internal Directives (PDF, MD, CSV)", disabled=True)


def view_dashboard():
    badge_text = "GLOBAL ACCESS" if st.session_state.role in ["c_level", "admin"] else f"{st.session_state.role.upper()} INSIGHTS"

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid rgba(0,124,195,0.25); padding-bottom: 0.5rem; margin-bottom: 1.5rem;">
        <div>
            <h2 style="margin:0; font-size:1.5rem; color:#E6F1FF;">Analytics Dashboard</h2>
            <p style="color:rgba(255,255,255,0.5); font-size:0.9rem; margin:0;">Real-time platform telemetry.</p>
        </div>
        <span style="background:rgba(229,57,53,0.15); color:#E53935; font-size:0.75rem; font-weight:700; letter-spacing:0.1em; border: 1px solid #E53935; padding: 4px 10px; border-radius: 4px;">{badge_text}</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Compiling system metrics..."):
        data, error = api_get_dashboard()
        
    if error:
        st.error(error)
        return
        
    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total User Queries", data["total_queries"])
    col2.metric("Registered Personnel", data["total_users"])
    col3.metric("System Database Health", "🟢 Optimal")
    
    st.markdown("<hr style='border-color: rgba(0,124,195,0.2)'>", unsafe_allow_html=True)
    
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown("<h3 style='font-size:1.1rem;color:white'>Queries by Clearance Level</h3>", unsafe_allow_html=True)
        if data["queries_by_role"]:
            df_role = pd.DataFrame(list(data["queries_by_role"].items()), columns=["Role", "Queries"])
            chart = alt.Chart(df_role).mark_bar(color="#007cc3", cornerRadiusTopRight=4, cornerRadiusBottomRight=4).encode(
                x='Queries:Q',
                y=alt.Y('Role:N', sort='-x'),
                tooltip=['Role', 'Queries']
            ).properties(height=300)
            
            # Make bg transparent
            chart = chart.configure(background='transparent')
            chart = chart.configure_axis(grid=False, domainColor="rgba(255,255,255,0.2)", tickColor="rgba(255,255,255,0.2)", labelColor="rgba(255,255,255,0.6)", titleColor="rgba(255,255,255,0.6)")
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No query data available.")
            
    with colB:
        st.markdown("<h3 style='font-size:1.1rem;color:white'>Top Inquiries</h3>", unsafe_allow_html=True)
        if data["top_queries"]:
            # Display as a clean table
            df_top = pd.DataFrame(data["top_queries"])
            df_top.columns = ["Query String", "Frequency"]
            st.dataframe(df_top, use_container_width=True, hide_index=True)
        else:
            st.info("No query data available.")


# ── Router ────────────────────────────────────────────────────
if st.session_state.token:
    render_sidebar()
    page = st.session_state.current_page
    
    if page == "🤖 Infobot Chat":
        view_chat()
    elif page == "📜 Query History":
        view_history()
    elif page == "📂 Upload Documents":
        view_upload()
    elif page == "📊 Analytics Dashboard":
        view_dashboard()
else:
    show_login()
