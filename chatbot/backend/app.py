"""
app.py — NexusAI Streamlit Frontend
Talks to FastAPI backend via JWT-authenticated HTTP
Run: streamlit run app.py
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────────
API = "http://localhost:8000"

st.set_page_config(
    page_title="NexusAI",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Role palette ─────────────────────────────────────────────────────────────
ROLE_META = {
    "finance":     {"icon": "💹", "color": "#4ade80",  "label": "Finance"},
    "marketing":   {"icon": "📣", "color": "#f472b6",  "label": "Marketing"},
    "hr":          {"icon": "👥", "color": "#a78bfa",  "label": "HR"},
    "engineering": {"icon": "⚙️", "color": "#38bdf8",  "label": "Engineering"},
    "employees":   {"icon": "🏢", "color": "#fb923c",  "label": "Employee"},
    "c_level":     {"icon": "👑", "color": "#fbbf24",  "label": "C-Level"},
}

SUGGESTIONS = {
    "finance":     ["Q3 revenue summary", "Latest budget allocation", "Quarterly spend breakdown"],
    "marketing":   ["Campaign performance metrics", "Conversion rate analysis", "Marketing strategy overview"],
    "hr":          ["Leave policy details", "Performance review process", "Employee benefits summary"],
    "engineering": ["System architecture overview", "Tech stack summary", "Deployment process"],
    "employees":   ["Company handbook highlights", "Remote work policy", "Employee perks"],
    "c_level":     ["Overall company performance", "Department KPI summary", "Strategic objectives"],
}

# ─── Session state ────────────────────────────────────────────────────────────
DEFAULTS = {
    "access_token":  None,
    "refresh_token": None,
    "user":          None,
    "stats":         None,
    "messages":      [],
    "page":          "chat",   # "chat" | "dashboard"
    "login_error":   "",
    "login_attempts": 0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─── API helpers ──────────────────────────────────────────────────────────────
def _headers():
    return {"Authorization": f"Bearer {st.session_state.access_token}"}

def api_login(email: str, password: str) -> bool:
    try:
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": password}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            st.session_state.access_token  = data["access_token"]
            st.session_state.refresh_token = data["refresh_token"]
            st.session_state.user          = data["user"]
            st.session_state.login_error   = ""
            st.session_state.login_attempts = 0
            _refresh_stats()
            return True
        st.session_state.login_error = r.json().get("detail", "Login failed")
        st.session_state.login_attempts += 1
        return False
    except requests.exceptions.ConnectionError:
        st.session_state.login_error = "Cannot reach API server — is the backend running?"
        return False

def api_logout():
    try:
        requests.post(
            f"{API}/auth/logout",
            headers=_headers(),
            json={"refresh_token": st.session_state.refresh_token},
            timeout=5,
        )
    except Exception:
        pass
    for k, v in DEFAULTS.items():
        st.session_state[k] = v

def api_query(query: str) -> dict | None:
    try:
        r = requests.post(
            f"{API}/rag/query",
            headers=_headers(),
            json={"query": query, "top_k": 4},
            timeout=30,
        )
        if r.status_code == 401:
            # Try token refresh
            rr = requests.post(f"{API}/auth/refresh", json={"refresh_token": st.session_state.refresh_token}, timeout=10)
            if rr.status_code == 200:
                st.session_state.access_token = rr.json()["access_token"]
                r = requests.post(f"{API}/rag/query", headers=_headers(), json={"query": query, "top_k": 4}, timeout=30)
            else:
                api_logout()
                st.rerun()
        if r.status_code == 200:
            _refresh_stats()
            return r.json()
        return {"answer": f"Error: {r.json().get('detail','Unknown error')}", "sources": [], "result_count": 0, "response_ms": 0, "role_label": ""}
    except requests.exceptions.ConnectionError:
        return {"answer": "⚠ Cannot reach API server. Make sure the backend is running.", "sources": [], "result_count": 0, "response_ms": 0, "role_label": ""}

def _refresh_stats():
    try:
        r = requests.get(f"{API}/auth/me", headers=_headers(), timeout=5)
        if r.status_code == 200:
            st.session_state.stats = r.json()["stats"]
    except Exception:
        pass

def api_rag_status() -> dict:
    try:
        r = requests.get(f"{API}/rag/status", headers=_headers(), timeout=5)
        return r.json() if r.status_code == 200 else {}
    except Exception:
        return {}

# ─── LOGIN PAGE ───────────────────────────────────────────────────────────────
def render_login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-brand">
                <span class="brand-hex">⬡</span>
                <h1 class="brand-name">NexusAI</h1>
                <p class="brand-sub">Enterprise Intelligence Platform</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login", clear_on_submit=False):
            email    = st.text_input("", placeholder="Corporate email", label_visibility="collapsed")
            password = st.text_input("", placeholder="Password", type="password", label_visibility="collapsed")
            go       = st.form_submit_button("Sign In  →", use_container_width=True)
            if go:
                if st.session_state.login_attempts >= 5:
                    st.session_state.login_error = "Account locked — contact your administrator."
                else:
                    with st.spinner("Authenticating…"):
                        if api_login(email, password):
                            st.rerun()

        if st.session_state.login_error:
            st.markdown(f'<div class="err-box">⚠ {st.session_state.login_error}</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="creds-panel">
          <div class="creds-title">TEST CREDENTIALS</div>
          <div class="creds-grid">
            <div class="cred"><b>💹 Finance</b><br>alice@nexus.com<br>Finance@123</div>
            <div class="cred"><b>📣 Marketing</b><br>bob@nexus.com<br>Market@123</div>
            <div class="cred"><b>👥 HR</b><br>carol@nexus.com<br>HR@12345678</div>
            <div class="cred"><b>👑 C-Level</b><br>frank@nexus.com<br>CEO@1234567</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def render_sidebar():
    user  = st.session_state.user
    stats = st.session_state.stats or {}
    role  = user["role"]
    meta  = ROLE_META[role]

    with st.sidebar:
        # Profile
        st.markdown(f"""
        <div class="sb-profile">
          <div class="sb-avatar" style="background:linear-gradient(135deg,{meta['color']}30,{meta['color']}10);
               border:1.5px solid {meta['color']}50">{user['avatar_initials']}</div>
          <div class="sb-info">
            <div class="sb-name">{user['name']}</div>
            <div class="sb-role" style="color:{meta['color']}">{meta['icon']} {meta['label']}</div>
            <div class="sb-dept">{user['department']}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Nav
        st.markdown('<div class="sb-divider"></div><p class="sb-section">NAVIGATION</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💬 Chat", use_container_width=True,
                         type="primary" if st.session_state.page == "chat" else "secondary"):
                st.session_state.page = "chat"; st.rerun()
        with c2:
            if st.button("📊 Dashboard", use_container_width=True,
                         type="primary" if st.session_state.page == "dashboard" else "secondary"):
                st.session_state.page = "dashboard"; st.rerun()

        # Stats strip
        st.markdown('<div class="sb-divider"></div><p class="sb-section">ACTIVITY</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stat-strip">
          <div class="stat-tile">
            <div class="stat-num" style="color:{meta['color']}">{stats.get('today_queries',0)}</div>
            <div class="stat-lbl">Today</div>
          </div>
          <div class="stat-tile">
            <div class="stat-num" style="color:{meta['color']}">{stats.get('total_queries',0)}</div>
            <div class="stat-lbl">Total</div>
          </div>
          <div class="stat-tile">
            <div class="stat-num" style="color:{meta['color']}">{stats.get('avg_response_ms',0)}ms</div>
            <div class="stat-lbl">Avg Speed</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick queries
        st.markdown('<div class="sb-divider"></div><p class="sb-section">QUICK QUERIES</p>', unsafe_allow_html=True)
        for s in SUGGESTIONS[role]:
            if st.button(f"↗ {s}", key=f"qq_{s}", use_container_width=True):
                st.session_state.page = "chat"
                _send_message(s)
                st.rerun()

        # Logout
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)
        if st.button("🔒  Sign Out", use_container_width=True, key="logout"):
            api_logout(); st.rerun()

# ─── DASHBOARD ───────────────────────────────────────────────────────────────
def render_dashboard():
    user  = st.session_state.user
    stats = st.session_state.stats or {}
    role  = user["role"]
    meta  = ROLE_META[role]

    # Header
    st.markdown(f"""
    <div class="page-header">
      <div>
        <h2 class="page-title">Analytics Dashboard</h2>
        <p class="page-sub">Your activity overview · <span style="color:{meta['color']}">{meta['label']} Access</span></p>
      </div>
      <div class="page-badge" style="background:{meta['color']}18;border:1px solid {meta['color']}40;color:{meta['color']}">
        {meta['icon']} {user['name']}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI cards
    rag = api_rag_status()
    last = user.get("last_login","")
    if last:
        try:
            last = datetime.fromisoformat(last).strftime("%d %b, %H:%M")
        except: pass

    k1, k2, k3, k4 = st.columns(4)
    for col, num, lbl, sub, color in [
        (k1, stats.get("today_queries",0),   "Queries Today",    "Questions asked",              meta["color"]),
        (k2, stats.get("total_queries",0),   "Total Queries",    "All time",                     meta["color"]),
        (k3, f"{stats.get('avg_response_ms',0)}ms", "Avg Response", "Search latency",            meta["color"]),
        (k4, rag.get("doc_count","—"),        "Indexed Docs",    "Chunks in knowledge base",     meta["color"]),
    ]:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-num" style="color:{color}">{num}</div>
              <div class="kpi-label">{lbl}</div>
              <div class="kpi-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two columns: recent queries + info
    c1, c2 = st.columns([1.6, 1])

    with c1:
        st.markdown('<h3 class="section-title">Recent Queries</h3>', unsafe_allow_html=True)
        recent = stats.get("recent_queries", [])
        if recent:
            for q in recent:
                ts = q.get("created_at","")
                try: ts = datetime.fromisoformat(ts).strftime("%d %b %H:%M")
                except: pass
                st.markdown(f"""
                <div class="query-row">
                  <div class="query-text">"{q['query']}"</div>
                  <div class="query-meta">
                    <span class="qm-chip">{q['result_count']} sources</span>
                    <span class="qm-chip">{q['response_ms']}ms</span>
                    <span class="qm-time">{ts}</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">No queries yet — start chatting!</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<h3 class="section-title">Account Info</h3>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-card">
          <div class="info-row"><span class="info-lbl">Name</span><span class="info-val">{user['name']}</span></div>
          <div class="info-row"><span class="info-lbl">Email</span><span class="info-val">{user['email']}</span></div>
          <div class="info-row"><span class="info-lbl">Role</span><span class="info-val" style="color:{meta['color']}">{meta['label']}</span></div>
          <div class="info-row"><span class="info-lbl">Department</span><span class="info-val">{user['department']}</span></div>
          <div class="info-row"><span class="info-lbl">Last Login</span><span class="info-val">{last or '—'}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<h3 class="section-title" style="margin-top:20px">Knowledge Base</h3>', unsafe_allow_html=True)
        accessible = {
            "finance":     ["finance_report.md", "quarterly_summary.csv"],
            "marketing":   ["marketing_analysis.md", "campaign_data.csv"],
            "hr":          ["employee_data.csv", "hr_policies.md"],
            "engineering": ["tech_docs.md", "system_architecture.md"],
            "employees":   ["general_handbook.md"],
            "c_level":     ["All files"],
        }
        files = accessible.get(role, [])
        chips = "".join(f'<span class="file-chip">{f}</span>' for f in files)
        status_dot = "🟢" if rag.get("ready") else "🔴"
        st.markdown(f"""
        <div class="info-card">
          <div class="info-row"><span class="info-lbl">Status</span><span class="info-val">{status_dot} {'Ready' if rag.get('ready') else 'Offline'}</span></div>
          <div class="info-row"><span class="info-lbl">Your files</span></div>
          <div class="file-chips">{chips}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── CHAT PAGE ────────────────────────────────────────────────────────────────
def _send_message(text: str):
    st.session_state.messages.append({"role": "user", "content": text, "ts": datetime.now().strftime("%H:%M")})
    result = api_query(text)
    if result:
        meta_info = f"*{result['result_count']} sources · {result['response_ms']}ms*" if result["result_count"] else ""
        st.session_state.messages.append({
            "role":    "assistant",
            "content": result["answer"],
            "meta":    meta_info,
            "ts":      datetime.now().strftime("%H:%M"),
        })

def render_chat():
    user = st.session_state.user
    role = user["role"]
    meta = ROLE_META[role]

    # Header
    st.markdown(f"""
    <div class="page-header">
      <div style="display:flex;align-items:center;gap:14px">
        <span class="brand-hex-sm">⬡</span>
        <div>
          <h2 class="page-title">NexusAI Chat</h2>
          <p class="page-sub">Searching <span style="color:{meta['color']}">{meta['label']}</span> knowledge base</p>
        </div>
      </div>
      <div class="page-badge" style="background:{meta['color']}18;border:1px solid {meta['color']}40;color:{meta['color']}">
        {meta['icon']} {meta['label']} Access
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-area">
          <div class="welcome-icon">{meta['icon']}</div>
          <h3 class="welcome-h">Hi, {user['name'].split()[0]}!</h3>
          <p class="welcome-p">I have access to your <strong>{meta['label']}</strong> documents.<br>Ask anything or pick a quick query from the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="msg-wrap user-wrap">
                  <div class="msg-bubble user-bub">{msg['content']}</div>
                  <div class="msg-av user-av" style="background:{meta['color']}20;border:1px solid {meta['color']}40;color:{meta['color']}">{user['avatar_initials']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                meta_line = f'<div class="msg-meta">{msg.get("meta","")}</div>' if msg.get("meta") else ""
                st.markdown(f"""
                <div class="msg-wrap bot-wrap">
                  <div class="msg-av bot-av">⬡</div>
                  <div>
                    <div class="msg-bubble bot-bub">{msg['content']}</div>
                    {meta_line}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:90px'></div>", unsafe_allow_html=True)

    # Input
    col1, col2 = st.columns([1, 8])
    with col2:
        if st.session_state.messages:
            if st.button("🗑 Clear", key="clr"):
                st.session_state.messages = []; st.rerun()

    prompt = st.chat_input("Ask about your company data…")
    if prompt:
        with st.spinner("Searching…"):
            _send_message(prompt)
        st.rerun()

# ─── ROUTER ──────────────────────────────────────────────────────────────────
if not st.session_state.access_token:
    render_login()
else:
    render_sidebar()
    if st.session_state.page == "dashboard":
        render_dashboard()
    else:
        render_chat()