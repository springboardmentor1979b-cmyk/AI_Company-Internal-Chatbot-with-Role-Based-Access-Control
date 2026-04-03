"""
app.py — Streamlit Frontend
────────────────────────────
Pages:
  • Login
  • Chat (with source attribution)
  • My Profile
"""

import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Infobot",
    page_icon="🤖",
    layout="wide",
)

# ── Session defaults ──────────────────────────────────────────

for key, default in [
    ("token", None),
    ("username", ""),
    ("role", ""),
    ("department", ""),
    ("history", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── API helpers ───────────────────────────────────────────────

def api_login(username: str, password: str):
    try:
        r = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Login failed")
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend. Is it running? (`python -m backend.main`)"


def api_query(question: str, top_k: int = 4):
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        r = requests.post(
            f"{BACKEND_URL}/chat/query",
            json={"question": question, "top_k": top_k},
            headers=headers,
            timeout=90,
        )
        if r.status_code == 200:
            return r.json(), None
        return None, r.json().get("detail", "Query failed")
    except requests.ConnectionError:
        return None, "❌ Cannot reach backend."


# ── Role badge colours ────────────────────────────────────────

ROLE_COLOURS = {
    "finance":     "#1E88E5",
    "marketing":   "#E91E63",
    "hr":          "#43A047",
    "engineering": "#FB8C00",
    "employees":   "#8E24AA",
    "c_level":     "#E53935",
}


def role_badge(role: str) -> str:
    colour = ROLE_COLOURS.get(role, "#607D8B")
    return f'<span style="background:{colour};color:white;padding:2px 10px;border-radius:12px;font-size:0.8em">{role.upper()}</span>'


# ── Login page ────────────────────────────────────────────────

def show_login():
    st.title("🔐 Infobot")
    st.markdown("#### Login to your account")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not username or not password:
            st.warning("Please enter both username and password.")
            return

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
            st.success(f"Welcome, {username}!")
            st.rerun()

    st.markdown("---")
    st.markdown("**Demo accounts:**")
    demo = {
        "alice / alice123": "Finance",
        "bob / bob123":     "Marketing",
        "carol / carol123": "HR",
        "dave / dave123":   "Engineering",
        "eve / eve123":     "Employees",
        "frank / frank123": "C-Level (all access)",
    }
    for creds, dept in demo.items():
        st.code(f"{creds}  →  {dept}", language=None)


# ── Chat page ─────────────────────────────────────────────────

def show_chat():
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(role_badge(st.session_state.role), unsafe_allow_html=True)
        st.markdown(f"**Dept:** {st.session_state.department}")
        st.divider()

        top_k = st.slider("Chunks to retrieve", 1, 8, 4)
        show_sources = st.checkbox("Show source chunks", value=False)
        st.divider()

        if st.button("🚪 Logout", use_container_width=True):
            for k in ["token", "username", "role", "department", "history"]:
                st.session_state[k] = "" if k != "history" else []
            st.session_state.token = None
            st.rerun()

    st.title("🤖 Infobot")
    st.caption(f"Role: **{st.session_state.role}** | You can only access documents permitted for your role.")

    # Render history
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📄 Sources"):
                    for s in msg["sources"]:
                        st.markdown(f"- `{s}`")
            if show_sources and msg.get("chunks"):
                with st.expander("🔍 Retrieved chunks"):
                    for i, chunk in enumerate(msg["chunks"], 1):
                        st.markdown(f"**Chunk {i}** | `{chunk['source']}` | score: {chunk['score']}")
                        st.text(chunk["document"][:300])

    # Input
    if question := st.chat_input("Ask a question about company documents…"):
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.history.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer…"):
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
                    with st.expander("🔍 Retrieved chunks"):
                        for i, chunk in enumerate(chunks, 1):
                            st.markdown(f"**Chunk {i}** | `{chunk['source']}` | score: {chunk['score']}")
                            st.text(chunk["document"][:300])

        st.session_state.history.append({
            "role":    "assistant",
            "content": answer,
            "sources": sources,
            "chunks":  chunks,
        })


# ── Router ────────────────────────────────────────────────────

if st.session_state.token:
    show_chat()
else:
    show_login()
