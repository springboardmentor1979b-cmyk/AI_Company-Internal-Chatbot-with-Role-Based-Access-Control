import streamlit as st
import requests
import base64
import json
from datetime import datetime

API = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="DRAGON — Intelligence",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════
# DRAGON SVG LOGO
# ══════════════════════════════════════════
DRAGON_SVG = """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
  <defs>
    <linearGradient id="dg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#7c6af7"/>
      <stop offset="100%" style="stop-color:#4fc3f7"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Wings -->
  <path d="M50 55 Q20 30 8 45 Q15 55 30 52 Q20 65 25 75 Q38 62 50 65Z" fill="url(#dg)" opacity="0.9" filter="url(#glow)"/>
  <path d="M50 55 Q80 30 92 45 Q85 55 70 52 Q80 65 75 75 Q62 62 50 65Z" fill="url(#dg)" opacity="0.9" filter="url(#glow)"/>
  <!-- Body -->
  <ellipse cx="50" cy="60" rx="10" ry="18" fill="url(#dg)" filter="url(#glow)"/>
  <!-- Neck -->
  <path d="M44 45 Q50 25 56 45" fill="url(#dg)" filter="url(#glow)"/>
  <!-- Head -->
  <ellipse cx="50" cy="28" rx="9" ry="7" fill="url(#dg)" filter="url(#glow)"/>
  <!-- Snout -->
  <path d="M55 28 Q63 26 65 30 Q60 33 55 31Z" fill="url(#dg)" opacity="0.8"/>
  <!-- Eye -->
  <circle cx="53" cy="26" r="2" fill="#fff" opacity="0.95"/>
  <circle cx="53.5" cy="26" r="1" fill="#060608"/>
  <!-- Horn -->
  <path d="M47 22 Q45 14 49 18" stroke="url(#dg)" stroke-width="1.5" fill="none"/>
  <!-- Tail -->
  <path d="M50 78 Q42 88 46 95 Q52 90 54 82Z" fill="url(#dg)" opacity="0.7"/>
  <!-- Flame breath -->
  <path d="M65 30 Q72 27 76 22 Q70 24 68 20 Q73 18 74 14" stroke="#f97316" stroke-width="1.2" fill="none" opacity="0.7"/>
  <path d="M65 31 Q74 32 80 28" stroke="#fbbf24" stroke-width="0.8" fill="none" opacity="0.5"/>
</svg>
"""

# ══════════════════════════════════════════
# CSS
# ══════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400&display=swap');

:root {
  --bg:#04040a;
  --surface:#080810;
  --card:#0c0c18;
  --border:#1c1c2e;
  --border2:#252538;
  --text:#e8e8ff;
  --muted:#4a4a6a;
  --accent:#7c6af7;
  --blue:#4fc3f7;
  --green:#36d399;
  --orange:#f97316;
  --red:#ef4444;
  --yellow:#fbbf24;
  --purple:#c084fc;
}

*{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{
  font-family:'Rajdhani',sans-serif!important;
  background:var(--bg)!important;
  color:var(--text)!important;
}

/* hide chrome */
#MainMenu,footer,header,[data-testid="stToolbar"],
[data-testid="stDecoration"],[data-testid="stStatusWidget"]{
  visibility:hidden!important;display:none!important;
}

/* layout */
.block-container{
  padding:1.5rem 2.5rem 5rem!important;
  max-width:950px!important;
  margin:0 auto!important;
}

/* scrollbar */
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px;}

/* ── SIDEBAR ── */
[data-testid="stSidebar"]{
  background:var(--surface)!important;
  border-right:1px solid var(--border)!important;
}
[data-testid="stSidebar"]>div{padding:0!important;}

/* ── ANIMATED BG PARTICLES ── */
@keyframes float1{0%,100%{transform:translateY(0) translateX(0);}50%{transform:translateY(-30px) translateX(15px);}}
@keyframes float2{0%,100%{transform:translateY(0) translateX(0);}50%{transform:translateY(20px) translateX(-20px);}}
@keyframes float3{0%,100%{transform:translateY(0) translateX(0);}50%{transform:translateY(-15px) translateX(25px);}}
@keyframes pulse-glow{0%,100%{opacity:0.4;}50%{opacity:0.9;}}
@keyframes dragon-breathe{0%,100%{transform:scale(1);}50%{transform:scale(1.03);}}
@keyframes title-glow{0%,100%{text-shadow:0 0 20px rgba(124,106,247,0.5),0 0 40px rgba(79,195,247,0.3);}50%{text-shadow:0 0 35px rgba(124,106,247,0.9),0 0 70px rgba(79,195,247,0.6);}}
@keyframes border-flow{0%{border-color:rgba(124,106,247,0.3);}50%{border-color:rgba(79,195,247,0.6);}100%{border-color:rgba(124,106,247,0.3);}}
@keyframes fadeSlideUp{from{opacity:0;transform:translateY(20px);}to{opacity:1;transform:translateY(0);}}
@keyframes scanline{0%{transform:translateY(-100%);}100%{transform:translateY(100vh);}}
@keyframes spin-slow{from{transform:rotate(0deg);}to{transform:rotate(360deg);}}

/* ── LOGIN PAGE ── */
.login-bg{
  position:fixed;top:0;left:0;right:0;bottom:0;
  background:radial-gradient(ellipse at 20% 50%,rgba(124,106,247,0.12) 0%,transparent 60%),
             radial-gradient(ellipse at 80% 20%,rgba(79,195,247,0.08) 0%,transparent 50%),
             radial-gradient(ellipse at 60% 80%,rgba(192,132,252,0.06) 0%,transparent 50%),
             var(--bg);
  z-index:-1;
  pointer-events:none;
}
.orb{
  position:absolute;border-radius:50%;filter:blur(60px);pointer-events:none;
}
.orb1{width:400px;height:400px;background:rgba(124,106,247,0.08);top:-100px;left:-100px;animation:float1 8s ease-in-out infinite;}
.orb2{width:300px;height:300px;background:rgba(79,195,247,0.06);bottom:-80px;right:-80px;animation:float2 10s ease-in-out infinite;}
.orb3{width:200px;height:200px;background:rgba(192,132,252,0.07);top:40%;left:40%;animation:float3 7s ease-in-out infinite;}

.dragon-logo{
  animation:dragon-breathe 4s ease-in-out infinite;
  filter:drop-shadow(0 0 20px rgba(124,106,247,0.6)) drop-shadow(0 0 40px rgba(79,195,247,0.3));
  display:block;margin:0 auto;
}

.login-title{
  font-family:'Orbitron',sans-serif!important;
  font-size:2.2rem;font-weight:900;
  background:linear-gradient(135deg,#7c6af7 0%,#4fc3f7 50%,#c084fc 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:title-glow 3s ease-in-out infinite;
  letter-spacing:0.15em;text-align:center;
}
.login-sub{
  font-family:'JetBrains Mono',monospace!important;
  font-size:0.65rem;color:var(--muted);letter-spacing:0.25em;
  text-transform:uppercase;text-align:center;margin-top:0.4rem;
}

.login-card{
  background:rgba(8,8,16,0.85);
  border:1px solid var(--border);
  border-radius:16px;padding:2rem 2rem 1.5rem;
  backdrop-filter:blur(20px);
  animation:border-flow 4s ease-in-out infinite,fadeSlideUp 0.6s ease-out;
  box-shadow:0 0 60px rgba(124,106,247,0.08),inset 0 0 60px rgba(0,0,0,0.5);
}

/* ── INPUTS ── */
.stTextInput input,.stSelectbox>div>div{
  background:rgba(12,12,24,0.9)!important;
  border:1px solid var(--border2)!important;
  border-radius:8px!important;
  color:var(--text)!important;
  font-family:'Rajdhani',sans-serif!important;
  font-size:0.92rem!important;
  transition:all 0.3s ease!important;
}
.stTextInput input:focus{
  border-color:var(--accent)!important;
  box-shadow:0 0 0 2px rgba(124,106,247,0.2),0 0 15px rgba(124,106,247,0.1)!important;
  outline:none!important;
}
label,.stSelectbox label{
  font-size:0.65rem!important;color:var(--muted)!important;
  text-transform:uppercase!important;letter-spacing:0.12em!important;
  font-family:'JetBrains Mono',monospace!important;
}

/* ── BUTTONS ── */
.stButton>button{
  background:transparent!important;
  border:1px solid var(--border2)!important;
  color:var(--muted)!important;
  font-family:'Rajdhani',sans-serif!important;
  font-size:0.82rem!important;font-weight:500!important;
  border-radius:8px!important;padding:0.42rem 0.8rem!important;
  transition:all 0.25s ease!important;
  width:100%;text-align:left!important;
  white-space:nowrap!important;overflow:hidden!important;
  text-overflow:ellipsis!important;
}
.stButton>button:hover{
  border-color:var(--accent)!important;color:var(--text)!important;
  background:rgba(124,106,247,0.08)!important;
  box-shadow:0 0 12px rgba(124,106,247,0.15)!important;
}
.stButton>button[kind="primary"]{
  background:rgba(124,106,247,0.12)!important;
  border-color:var(--accent)!important;
  color:var(--accent)!important;font-weight:600!important;
}
.stButton>button[kind="primary"]:hover{
  background:rgba(124,106,247,0.2)!important;
}

/* ── LOGIN BUTTON special ── */
div[data-testid="column"] .stButton>button[kind="primary"],
.login-submit .stButton>button{
  background:linear-gradient(135deg,rgba(124,106,247,0.8),rgba(79,195,247,0.6))!important;
  border:none!important;color:#fff!important;
  font-family:'Orbitron',sans-serif!important;
  font-size:0.75rem!important;font-weight:700!important;
  letter-spacing:0.15em!important;
  border-radius:10px!important;padding:0.65rem!important;
  text-align:center!important;
  box-shadow:0 4px 20px rgba(124,106,247,0.4)!important;
  transition:all 0.3s ease!important;
}

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"]{
  background:transparent!important;border:none!important;
  padding:0.15rem 0!important;gap:0!important;
}
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"],
[data-baseweb="avatar"]{
  display:none!important;width:0!important;min-width:0!important;
  padding:0!important;margin:0!important;
}
[data-testid="stChatMessage"]>div:first-child{display:none!important;}
[data-testid="stChatMessage"] .stMarkdown p{
  font-family:'Rajdhani',sans-serif!important;
  font-size:0.92rem!important;line-height:1.65!important;color:var(--text)!important;
}

/* ── CHAT INPUT ── */
[data-testid="stChatInput"]{
  background:var(--surface)!important;
  border:1px solid var(--border2)!important;
  border-radius:12px!important;
  transition:border-color 0.3s!important;
}
[data-testid="stChatInput"]:focus-within{
  border-color:var(--accent)!important;
  box-shadow:0 0 0 2px rgba(124,106,247,0.15),0 0 20px rgba(124,106,247,0.08)!important;
}
[data-testid="stChatInput"] textarea{
  font-family:'Rajdhani',sans-serif!important;
  font-size:0.9rem!important;color:var(--text)!important;background:transparent!important;
}

/* ── METRICS ── */
[data-testid="stMetric"]{
  background:var(--card)!important;border:1px solid var(--border)!important;
  border-radius:12px!important;padding:1rem 1.1rem!important;
  transition:border-color 0.3s!important;
}
[data-testid="stMetric"]:hover{border-color:var(--border2)!important;}
[data-testid="stMetricLabel"]{
  font-family:'JetBrains Mono',monospace!important;
  font-size:0.6rem!important;color:var(--muted)!important;
  text-transform:uppercase!important;letter-spacing:0.1em!important;
}
[data-testid="stMetricValue"]{
  font-family:'Orbitron',sans-serif!important;
  font-size:1.5rem!important;font-weight:700!important;color:var(--text)!important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"]{
  border:1px solid var(--border)!important;border-radius:10px!important;overflow:hidden!important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"]{
  background:var(--card)!important;
  border:1px dashed var(--border2)!important;
  border-radius:12px!important;
}
[data-testid="stFileUploader"]:hover{border-color:var(--accent)!important;}

/* ── SELECTBOX ── */
.stSelectbox>div>div{cursor:pointer!important;}

/* divider */
hr{border-color:var(--border)!important;margin:0.75rem 0!important;}

/* spinner */
.stSpinner>div{border-top-color:var(--accent)!important;}

/* role key input */
.stTextInput.role-key input{
  font-family:'Orbitron',sans-serif!important;
  letter-spacing:0.2em!important;text-align:center!important;
}

/* section header */
.sec-header{
  padding-bottom:0.9rem;margin-bottom:1.4rem;
  border-bottom:1px solid var(--border);
}
.sec-label{
  font-family:'JetBrains Mono',monospace;font-size:0.6rem;
  color:var(--muted);text-transform:uppercase;letter-spacing:0.15em;margin-bottom:4px;
}
.sec-title{
  font-family:'Orbitron',sans-serif;font-size:1rem;
  font-weight:700;color:var(--text);letter-spacing:0.05em;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════
# ROLE CONFIG
# ══════════════════════════════════════════
ROLES = ["Finance","HR","Marketing","Engineering","Employee","C-Level"]
ROLE_KEYS = {
    "Finance":"FIN-2030","HR":"HRM-2030","Marketing":"MKT-2030",
    "Engineering":"ENG-2030","Employee":"EMP-2030","C-Level":"CEO-2030"
}
ROLE_COLORS = {
    "Finance":"#36d399","HR":"#f97316","Marketing":"#c084fc",
    "Engineering":"#4fc3f7","Employee":"#94a3b8","C-Level":"#fbbf24","Admin":"#fbbf24"
}
ROLE_ICONS = {
    "Finance":"💹","HR":"👥","Marketing":"📣","Engineering":"⚙️",
    "Employee":"🪪","C-Level":"👑","Admin":"🛡️"
}

def rc(role): return ROLE_COLORS.get(role,"#94a3b8")
def ri(role): return ROLE_ICONS.get(role,"●")

def decode_role(token):
    try:
        p=token.split(".")[1]; p+="="*(4-len(p)%4)
        return json.loads(base64.b64decode(p)).get("role","Employee")
    except: return "Employee"

def hdrs(): return {"Authorization":f"Bearer {st.session_state['token']}"}

def fmt_time(ts):
    try: return datetime.fromisoformat(ts).strftime("%b %d · %H:%M")
    except: return ts

def chips(confidence, docs, ms):
    st.markdown(f"""
    <div style="display:flex;gap:6px;margin:6px 0 4px;flex-wrap:wrap;">
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:2px 9px;
        border-radius:4px;background:#0a1f12;color:#36d399;border:1px solid #1a3a22;">
        ↑ {confidence:.0%}
      </span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:2px 9px;
        border-radius:4px;background:#0a1525;color:#4fc3f7;border:1px solid #1a2a48;">
        {docs} doc{"s" if docs!=1 else ""}
      </span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:2px 9px;
        border-radius:4px;background:#1a1008;color:#f97316;border:1px solid #3a2010;">
        {ms:.0f}ms
      </span>
    </div>""", unsafe_allow_html=True)

def src_row(sources):
    if not sources: return
    tags="".join(f'<span style="font-family:JetBrains Mono,monospace;font-size:0.6rem;padding:2px 9px;border-radius:4px;background:#0d0d18;color:#4a4a6a;border:1px solid #1c1c2e;margin:2px;">◈ {s}</span>' for s in sources)
    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:3px;margin:4px 0;">{tags}</div>', unsafe_allow_html=True)

def sec_header(label, title):
    st.markdown(f'<div class="sec-header"><div class="sec-label">{label}</div><div class="sec-title">{title}</div></div>', unsafe_allow_html=True)

# session state
for k,v in [("token",None),("username",None),("role",None),("chat_history",[]),("page","chat"),("login_step",1),("sel_role","Finance")]:
    if k not in st.session_state: st.session_state[k]=v

# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    # Dragon brand
    st.markdown("""
    <div style="padding:1.2rem 1rem 0.8rem;border-bottom:1px solid #1c1c2e;
      display:flex;align-items:center;gap:10px;">
      <div style="font-size:1.8rem;line-height:1;
        filter:drop-shadow(0 0 8px rgba(124,106,247,0.8));">&#x1F409;</div>
      <div>
        <div style="font-family:'Orbitron',sans-serif;font-size:0.75rem;font-weight:900;
          background:linear-gradient(135deg,#7c6af7,#4fc3f7);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;
          letter-spacing:0.08em;">DRAGON</div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:0.5rem;
          color:#2a2a40;letter-spacing:0.2em;text-transform:uppercase;margin-top:1px;">
          Intelligence · RBAC</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state["token"]:
        role=st.session_state["role"]; color=rc(role)
        st.markdown(f"""
        <div style="margin:0.8rem 0.8rem 0.5rem;padding:0.8rem 0.9rem;
          background:var(--card);border:1px solid var(--border);
          border-radius:10px;border-left:3px solid {color};">
          <div style="font-size:0.55rem;color:#2a2a40;font-family:'JetBrains Mono',monospace;
            text-transform:uppercase;letter-spacing:0.12em;margin-bottom:3px;">Active Session</div>
          <div style="font-weight:600;font-size:0.88rem;color:var(--text);
            font-family:'Orbitron',sans-serif;font-size:0.7rem;letter-spacing:0.05em;">
            {st.session_state['username']}
          </div>
          <div style="font-size:0.68rem;color:{color};margin-top:3px;
            font-family:'JetBrains Mono',monospace;">
            {ri(role)} {role}
          </div>
        </div>
        """, unsafe_allow_html=True)

        pages=[("💬","chat","Chat"),("📜","history","Chat History")]
        if role in ["C-Level","Admin"]:
            pages+=[("📊","dashboard","Dashboard"),("📋","logs","Query Logs")]
        pages.append(("📁","upload","Upload Docs"))

        st.markdown('<div style="padding:0 0.6rem;">', unsafe_allow_html=True)
        for icon,pid,label in pages:
            active=st.session_state["page"]==pid
            if st.button(f"{icon}  {label}",key=f"nav_{pid}",type="primary" if active else "secondary"):
                st.session_state["page"]=pid; st.rerun()
        st.divider()
        if st.button("🗑️  Clear Chat"):
            st.session_state["chat_history"]=[]; st.rerun()
        if st.button("← Logout"):
            for k in ["token","username","role","chat_history"]:
                st.session_state[k]=None if k!="chat_history" else []
            st.session_state.update({"page":"chat","login_step":1}); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        pass  # not logged in — sidebar empty

# ══════════════════════════════════════════
# ① LOGIN PAGE — animated, role+passkey flow
# ══════════════════════════════════════════
if not st.session_state["token"]:

    # dragon vars not needed - using emoji

    # Animated background
    st.markdown("""
    <div class="login-bg">
      <div class="orb orb1"></div>
      <div class="orb orb2"></div>
      <div class="orb orb3"></div>
    </div>
    """, unsafe_allow_html=True)

    # Dragon logo + title
    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0 1.5rem;animation:fadeSlideUp 0.8s ease-out;">
      <div style="font-size:5rem;line-height:1;text-align:center;filter:drop-shadow(0 0 25px rgba(124,106,247,0.9)) drop-shadow(0 0 50px rgba(79,195,247,0.5));animation:dragon-breathe 4s ease-in-out infinite;margin-bottom:0.5rem;">&#x1F409;</div>
      <div class="login-title">DRAGON INTEL</div>
      <div class="login-sub">Secure Internal Knowledge System</div>
    </div>
    """, unsafe_allow_html=True)

    _,col,_ = st.columns([0.8, 1.4, 0.8])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        if st.session_state["login_step"] == 1:
            # Step 1: credentials + role
            st.markdown("""
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#3a3a5a;
              letter-spacing:0.2em;text-transform:uppercase;margin-bottom:1.2rem;text-align:center;">
              ── Step 1 of 2 · Identity ──
            </div>""", unsafe_allow_html=True)

            username = st.text_input("Username", placeholder="your_username", key="li_user")
            password = st.text_input("Password", type="password", placeholder="••••••••••", key="li_pass")
            role_sel = st.selectbox("Your Role", ROLES, key="li_role")
            st.session_state["sel_role"] = role_sel

            st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
            if st.button("Continue →", type="primary", use_container_width=True, key="step1_btn"):
                if not username or not password:
                    st.error("Username and password required.")
                else:
                    # verify credentials with backend
                    try:
                        r = requests.post(f"{API}/login", data={"username": username, "password": password})
                        if r.status_code == 200:
                            token = r.json()["access_token"]
                            actual_role = decode_role(token)
                            if actual_role.lower() != role_sel.lower():
                                st.error(f"⚠ Role mismatch. Your account role is **{actual_role}**.")
                            else:
                                st.session_state["_temp_token"] = token
                                st.session_state["_temp_user"] = username
                                st.session_state["_temp_role"] = actual_role
                                st.session_state["login_step"] = 2
                                st.rerun()
                        else:
                            st.error("⚠ Invalid credentials.")
                    except:
                        st.error("⚠ Cannot reach API server.")

        else:
            # Step 2: passkey confirmation
            sel_role = st.session_state.get("_temp_role","Finance")
            color = rc(sel_role)
            st.markdown(f"""
            <div style="text-align:center;margin-bottom:1.2rem;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#3a3a5a;
                letter-spacing:0.2em;text-transform:uppercase;margin-bottom:0.8rem;">
                ── Step 2 of 2 · Access Key ──
              </div>
              <div style="display:inline-block;background:var(--card);border:1px solid {color}33;
                border-radius:8px;padding:0.5rem 1.2rem;">
                <span style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:{color};">
                  {ri(sel_role)} {sel_role} Role Detected
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            passkey = st.text_input(
                "Role Access Key",
                type="password",
                placeholder="Enter your role key",
                key="li_key",
                help=f"Hint: {sel_role[:3].upper()}-2030"
            )

            st.markdown('<div style="height:0.4rem;"></div>', unsafe_allow_html=True)
            col_back, col_enter = st.columns([1,2])
            with col_back:
                if st.button("← Back", key="back_btn"):
                    st.session_state["login_step"] = 1
                    st.rerun()
            with col_enter:
                if st.button("🐉 Enter System", type="primary", use_container_width=True, key="step2_btn"):
                    expected = ROLE_KEYS.get(sel_role,"")
                    if passkey != expected:
                        st.error(f"⚠ Invalid access key for {sel_role}.")
                    else:
                        st.session_state.update({
                            "token": st.session_state["_temp_token"],
                            "username": st.session_state["_temp_user"],
                            "role": st.session_state["_temp_role"],
                            "login_step": 1,
                            "page": "chat"
                        })
                        st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Role keys hint table
    st.markdown("""
    <div style="max-width:540px;margin:1.5rem auto 0;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.55rem;color:#1e1e32;
        letter-spacing:0.2em;text-transform:uppercase;text-align:center;margin-bottom:0.75rem;">
        Role Access Keys
      </div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;">
    """, unsafe_allow_html=True)

    key_cards = ""
    for role_name, key in ROLE_KEYS.items():
        color = rc(role_name)
        key_cards += f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;
          padding:0.55rem 0.75rem;border-top:2px solid {color}22;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;
            color:var(--text);">{ri(role_name)} {role_name}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;
            color:{color};margin-top:3px;letter-spacing:0.1em;">{key}</div>
        </div>"""
    st.markdown(key_cards + "</div></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════
# ② CHAT
# ══════════════════════════════════════════
elif st.session_state["page"] == "chat":
    color = rc(st.session_state["role"])
    st.markdown(f"""
    <div class="sec-header" style="display:flex;align-items:center;gap:10px;">
      <div style="width:8px;height:8px;border-radius:50%;background:{color};
        box-shadow:0 0 10px {color};flex-shrink:0;
        animation:pulse-glow 2s ease-in-out infinite;"></div>
      <div>
        <div class="sec-label">Intelligence Interface</div>
        <div style="font-family:'Orbitron',sans-serif;font-size:0.85rem;font-weight:700;
          color:var(--text);letter-spacing:0.05em;">
          {ri(st.session_state['role'])} {st.session_state['role']} Access Channel
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Empty state
    if not st.session_state["chat_history"]:
        st.markdown(f"""
        <div style="text-align:center;padding:3rem 0;animation:fadeSlideUp 0.6s ease-out;">
          <div style="font-size:3.5rem;line-height:1;filter:drop-shadow(0 0 15px rgba(124,106,247,0.5));display:inline-block;margin-bottom:1rem;animation:dragon-breathe 4s ease-in-out infinite;">&#x1F409;</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:0.75rem;color:#2a2a40;
            letter-spacing:0.15em;text-transform:uppercase;">
            Ask me anything within your access scope
          </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                src_row(msg.get("sources",[]))
                if msg.get("meta"):
                    m=msg["meta"]; chips(m["confidence"],m["documents_used"],m["response_time_ms"])

    if prompt := st.chat_input("Query the intelligence system…"):
        st.session_state["chat_history"].append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(""):
                try:
                    r = requests.post(f"{API}/chat", json={"query":prompt}, headers=hdrs())
                    if r.status_code == 200:
                        d=r.json(); answer=d["answer"]; srcs=d.get("sources",[])
                        meta={"confidence":d.get("confidence",0),"documents_used":d.get("documents_used",0),"response_time_ms":d.get("response_time_ms",0)}
                        st.markdown(answer); src_row(srcs); chips(meta["confidence"],meta["documents_used"],meta["response_time_ms"])
                        st.session_state["chat_history"].append({"role":"assistant","content":answer,"sources":srcs,"meta":meta})
                    elif r.status_code == 401:
                        st.error("Session expired."); st.session_state["token"]=None
                    else: st.error(r.json().get("detail","Error."))
                except Exception as e: st.error(f"Connection error: {e}")


# ══════════════════════════════════════════
# ③ CHAT HISTORY
# ══════════════════════════════════════════
elif st.session_state["page"] == "history":
    sec_header("Persistent Memory", "Chat History")
    try:
        r = requests.get(f"{API}/history?limit=50", headers=hdrs())
        if r.status_code == 200:
            history = r.json().get("history",[])
            if not history:
                st.markdown('<div style="text-align:center;padding:3rem;color:#2a2a40;font-family:JetBrains Mono,monospace;font-size:0.75rem;">No history yet.</div>', unsafe_allow_html=True)
            else:
                for item in history:
                    ts=fmt_time(item.get("timestamp","")); conf=item.get("confidence",0)
                    srcs=item.get("sources",[])
                    src_html = f'<div style="margin-top:0.4rem;font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#2a2a40;">◈ {" · ".join(srcs)}</div>' if srcs else ""
                    st.markdown(f"""
                    <div style="background:var(--card);border:1px solid var(--border);border-radius:10px;
                      padding:0.9rem 1rem;margin-bottom:0.5rem;animation:fadeSlideUp 0.4s ease-out;">
                      <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#2a2a40;">{ts}</span>
                        <span style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#36d399;
                          background:#0a1f12;padding:1px 7px;border-radius:3px;border:1px solid #1a3a22;">{conf:.0%}</span>
                      </div>
                      <div style="font-family:'Orbitron',sans-serif;font-size:0.65rem;color:var(--accent);
                        margin-bottom:0.4rem;letter-spacing:0.03em;">Q: {item['query']}</div>
                      <div style="font-family:'Rajdhani',sans-serif;font-size:0.88rem;color:#b8b8d8;line-height:1.5;">
                        {item['answer'][:220]}{"…" if len(item["answer"])>220 else ""}
                      </div>
                      {src_html}
                    </div>""", unsafe_allow_html=True)
        else: st.error("Failed to load history.")
    except Exception as e: st.error(f"Connection error: {e}")


# ══════════════════════════════════════════
# ④ DASHBOARD
# ══════════════════════════════════════════
elif st.session_state["page"] == "dashboard":
    sec_header("C-Level Access", "System Analytics")
    try:
        r = requests.get(f"{API}/dashboard/stats", headers=hdrs())
        if r.status_code == 200:
            data=r.json()
            c1,c2,c3,c4=st.columns(4)
            c1.metric("Total Users", data["total_users"])
            c2.metric("Queries", data["total_queries"])
            c3.metric("Denied", data["unauthorized_attempts"])
            allowed=data["total_queries"]-data["unauthorized_attempts"]
            c4.metric("Access Rate", f"{(allowed/max(data['total_queries'],1))*100:.0f}%")

            st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)
            col_a,col_b=st.columns([1.3,1])
            with col_a:
                if data.get("queries_by_role"):
                    import pandas as pd
                    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:#2a2a40;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.5rem;">Queries by Role</div>', unsafe_allow_html=True)
                    df=pd.DataFrame(list(data["queries_by_role"].items()),columns=["Role","Queries"])
                    st.bar_chart(df.set_index("Role"),height=220,color="#7c6af7")
            with col_b:
                st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.6rem;color:#2a2a40;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.75rem;">Role Breakdown</div>', unsafe_allow_html=True)
                if data.get("queries_by_role"):
                    total=sum(data["queries_by_role"].values())
                    for role,count in sorted(data["queries_by_role"].items(),key=lambda x:-x[1]):
                        color=rc(role); pct=count/max(total,1)
                        st.markdown(f"""
                        <div style="margin-bottom:10px;">
                          <div style="display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--text);margin-bottom:3px;">
                            <span>{ri(role)} {role}</span><span style="color:{color};">{count}</span>
                          </div>
                          <div style="background:var(--border);border-radius:3px;height:3px;">
                            <div style="background:{color};width:{pct*100:.0f}%;height:100%;border-radius:3px;transition:width 1s ease;"></div>
                          </div>
                        </div>""", unsafe_allow_html=True)

            if data.get("recent_logs"):
                st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)
                sec_header("Audit Trail", "Recent Activity")
                import pandas as pd
                df_logs=pd.DataFrame(data["recent_logs"])[["username","role","query","status","timestamp"]]
                st.dataframe(df_logs,use_container_width=True,height=260,hide_index=True)
        elif r.status_code==403: st.error("🚫 C-Level access required.")
        else: st.error("Failed to load.")
    except Exception as e: st.error(f"Connection error: {e}")


# ══════════════════════════════════════════
# ⑤ QUERY LOGS
# ══════════════════════════════════════════
elif st.session_state["page"] == "logs":
    sec_header("Audit Trail", "Query Logs")
    try:
        r = requests.get(f"{API}/dashboard/stats", headers=hdrs())
        if r.status_code == 200:
            logs=r.json().get("recent_logs",[])
            if not logs: st.info("No queries logged yet.")
            else:
                cf1,cf2=st.columns(2)
                with cf1: f_role=st.selectbox("Role",["All"]+list({l["role"] for l in logs}))
                with cf2: f_status=st.selectbox("Status",["All","Allowed","Denied"])
                filtered=[l for l in logs if(f_role=="All" or l["role"]==f_role) and(f_status=="All" or l["status"]==f_status)]
                st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:0.58rem;color:#2a2a40;margin:0.5rem 0;">{len(filtered)} records</div>', unsafe_allow_html=True)
                for log in filtered:
                    sc="#36d399" if log["status"]=="Allowed" else "#ef4444"
                    color=rc(log.get("role","")); ts=fmt_time(log.get("timestamp",""))
                    st.markdown(f"""
                    <div style="display:grid;grid-template-columns:120px 1fr 110px 72px;gap:10px;
                      align-items:center;padding:0.6rem 0.9rem;background:var(--card);
                      border:1px solid var(--border);border-radius:8px;margin-bottom:4px;
                      transition:border-color 0.2s;" onmouseover="this.style.borderColor='#252538'" onmouseout="this.style.borderColor='#1c1c2e'">
                      <span style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:#2a2a40;white-space:nowrap;">{ts}</span>
                      <span style="font-family:'Rajdhani',sans-serif;font-size:0.82rem;color:#b8b8d8;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{log['query']}</span>
                      <span style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:{color};white-space:nowrap;">{log['role']}</span>
                      <span style="font-family:'JetBrains Mono',monospace;font-size:0.58rem;color:{sc};
                        background:{'#0a1f12' if log['status']=='Allowed' else '#1a0808'};
                        padding:2px 8px;border-radius:4px;text-align:center;white-space:nowrap;">{log['status']}</span>
                    </div>""", unsafe_allow_html=True)
        else: st.error("Access denied.")
    except Exception as e: st.error(f"Connection error: {e}")


# ══════════════════════════════════════════
# ⑥ UPLOAD
# ══════════════════════════════════════════
elif st.session_state["page"] == "upload":
    sec_header("Knowledge Base", "Upload Documents")
    role=st.session_state["role"]
    dept_map={"C-Level":["finance","hr","marketing","engineering","general"],"Admin":["finance","hr","marketing","engineering","general"],"Finance":["finance"],"HR":["hr"],"Marketing":["marketing"],"Engineering":["engineering"],"Employee":["general"]}
    dept_options=dept_map.get(role,["general"])
    col1,col2=st.columns([1.5,1])
    with col1:
        department=st.selectbox("Target Department",dept_options)
        uploaded_file=st.file_uploader("Drop document here",type=["md","txt","csv"])
        if uploaded_file and st.button("Upload Document →",type="primary"):
            try:
                files={"file":(uploaded_file.name,uploaded_file.getvalue(),uploaded_file.type)}
                r=requests.post(f"{API}/upload?department={department}",files=files,headers=hdrs())
                if r.status_code==200:
                    st.success(f"✅ {r.json()['message']}")
                    st.info("💡 Re-run ingestion pipeline to index the new document.")
                else: st.error(r.json().get("detail","Upload failed."))
            except Exception as e: st.error(f"Error: {e}")
    with col2:
        color=rc(role)
        st.markdown(f"""
        <div style="background:var(--card);border:1px solid var(--border);border-radius:12px;
          padding:1.2rem;margin-top:1.6rem;border-left:3px solid {color}22;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:#2a2a40;
            text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.75rem;">Your Access</div>
          <div style="font-family:'Orbitron',sans-serif;font-size:0.72rem;color:{color};
            font-weight:600;margin-bottom:0.6rem;">{ri(role)} {role}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:#2a2a40;line-height:2.2;">
            Depts: {', '.join(dept_options)}<br>
            Formats: .md · .txt · .csv<br>Max: 10 MB
          </div>
        </div>
        """, unsafe_allow_html=True)

