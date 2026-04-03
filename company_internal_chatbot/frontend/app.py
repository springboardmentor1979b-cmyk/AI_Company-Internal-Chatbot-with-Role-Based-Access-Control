import streamlit as st
import requests
import time
from datetime import datetime
import json

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Internal Chatbot", page_icon="🤖", layout="wide")

# --- UI STYLES ---
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }

        .main {
            background-color: #fafbfc;
        }
        
        /* Chat Containers */
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            margin-bottom: 2rem;
        }

        .message-box {
            padding: 1.2rem;
            border-radius: 12px;
            max-width: 85%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
            line-height: 1.5;
            position: relative;
        }

        .user-msg {
            background-color: #e6f0ff;
            color: #0b2e59;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }

        .bot-msg {
            background-color: #ffffff;
            color: #1a1a1a;
            align-self: flex-start;
            border: 1px solid #e1e4e8;
            border-bottom-left-radius: 4px;
        }

        /* Timestamps */
        .timestamp {
            font-size: 0.7em;
            color: #8c92a4;
            margin-bottom: 5px;
            display: inline-block;
        }
        .user-msg .timestamp {
            float: right;
        }

        /* Sources formatting */
        .source-container {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #f0f0f0;
            font-size: 0.85em;
            color: #586069;
            background-color: #fcfcfc;
            border-radius: 6px;
            padding: 10px;
        }

        .confidence-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.75em;
            margin-left: 8px;
        }

        .conf-High { background-color: #d3f9d8; color: #2b8a3e; }
        .conf-Medium { background-color: #fff3bf; color: #e67700; }
        .conf-Low { background-color: #ffe3e3; color: #c92a2a; }

        /* Role Badges */
        .role-badge {
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.8em;
            display: inline-block;
            margin-bottom: 10px;
        }
        
        .role-c_level { background-color: #2b2b2b; color: #ffd700; }
        .role-finance { background-color: #e3fafc; color: #0c8599; }
        .role-hr { background-color: #fff0f6; color: #a61e4d; }
        .role-marketing { background-color: #fff4e6; color: #d9480f; }
        .role-engineering { background-color: #ebfbee; color: #2b8a3e; }
        .role-employee { background-color: #f1f3f5; color: #495057; }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #edf2f7;
        }
        
        /* Layout overrides */
        [data-testid="stForm"] {
            border: 1px solid #e1e4e8;
            border-radius: 12px;
            background-color: white;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        </style>
    """, unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
def init_session_state():
    if "jwt_token" not in st.session_state:
        st.session_state.jwt_token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# --- API INTEGRATION ---
class BackendAPI:
    @staticmethod
    def login(username, password):
        try:
            res = requests.post(f"{API_URL}/login", json={"username": username, "password": password}, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return data.get("access_token"), None
            return None, "Invalid username or password"
        except requests.exceptions.RequestException:
            return None, "Unable to connect to backend server."

    @staticmethod
    def get_me(token):
        try:
            res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {token}"}, timeout=5)
            if res.status_code == 200:
                return res.json(), None
            return None, "Unauthorized"
        except requests.exceptions.RequestException:
            return None, "Connection error"

    @staticmethod
    def chat(token, query):
        try:
            res = requests.post(f"{API_URL}/chat", headers={"Authorization": f"Bearer {token}"}, json={"query": query}, timeout=30)
            if res.status_code == 200:
                return res.json(), None
            elif res.status_code == 401:
                return None, "Session expired"
            return None, "Error processing query"
        except requests.exceptions.RequestException:
            return None, "Backend connection lost"

# --- TYPING ANIMATION (BONUS) ---
def render_typing_animation(text):
    placeholder = st.empty()
    display_text = ""
    # Simulate realistic typing roughly
    for char in text:
        display_text += char
        placeholder.markdown(f'<div class="message-box bot-msg">{display_text}▌</div>', unsafe_allow_html=True)
        time.sleep(0.015)
    placeholder.empty()

# --- VIEWS ---
def login_view():
    st.markdown("<h1 style='text-align: center; margin-top: 5rem;'>AI Internal Knowledge Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Secure enterprise search powered by RAG</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### 🔐 Secure Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Authenticate", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both credentials.")
                else:
                    with st.spinner("Authenticating..."):
                        token, err = BackendAPI.login(username, password)
                        if token:
                            user_data, user_err = BackendAPI.get_me(token)
                            if user_data:
                                st.session_state.jwt_token = token
                                st.session_state.user_info = user_data
                                st.rerun()
                            else:
                                st.error("Failed to retrieve profile data.")
                        else:
                            st.error(err)

def chat_view():
    user = st.session_state.user_info
    role = user.get("role", "employee")
    
    # Sidebar Profile
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        st.markdown(f"<div class='role-badge role-{role.replace(' ','_').lower()}'>{role.upper()} ACCESS</div>", unsafe_allow_html=True)
        st.write(f"**Verified as:** @{user.get('username')}")
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.jwt_token = None
            st.session_state.user_info = None
            st.session_state.chat_history = []
            st.rerun()
            
    # Main Chat Area
    st.title("Company Intelligent Assistant")
    st.markdown("Ask anything related to your permitted internal documentation.")
    
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        for idx, chat in enumerate(st.session_state.chat_history):
            timestamp = chat.get("timestamp", datetime.now().strftime("%I:%M %p"))
            if chat["type"] == "user":
                html = f"""
                <div style="display:flex; justify-content:flex-end;">
                  <div class="message-box user-msg">
                    <span class="timestamp">{timestamp}</span><br>
                    {chat["content"]}
                  </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
            else:
                conf = chat.get("confidence", "Low")
                sources = ", ".join(chat.get("sources", [])) if chat.get("sources") else "None"
                html = f"""
                <div style="display:flex; justify-content:flex-start;">
                  <div class="message-box bot-msg">
                    <span class="timestamp">{timestamp}</span><br>
                    {chat["content"]}
                    <div class="source-container">
                      📚 <b>Sources:</b> {sources} 
                      <span class="confidence-badge conf-{conf}">{conf} Match</span>
                    </div>
                  </div>
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Input Form Fixed at bottom
    with st.form("chat_input_form", clear_on_submit=True):
        col1, col2 = st.columns([8, 1])
        with col1:
            query = st.text_input("Message...", placeholder="Search internal documents...", label_visibility="collapsed")
        with col2:
            submit_btn = st.form_submit_button("Send 🚀")
            
        if submit_btn and query.strip():
            # append user message
            st.session_state.chat_history.append({
                "type": "user", 
                "content": query,
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            st.rerun() # rerun to show user msg instantly before delay

    # Process outstanding query
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["type"] == "user":
        latest_query = st.session_state.chat_history[-1]["content"]
        
        with st.spinner("Searching secure documents..."):
            res_data, err = BackendAPI.chat(st.session_state.jwt_token, latest_query)
            
        if err == "Session expired":
            st.warning("Session Expired. Please log in again.")
            st.session_state.jwt_token = None
            st.rerun()
        elif err:
            st.session_state.chat_history.append({
                "type": "bot",
                "content": f"⚠️ System encountered an error: {err}",
                "sources": [],
                "confidence": "Low",
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
            st.rerun()
        else:
            # Animation effect handling
            ans = res_data.get("answer", "No response.")
            # render_typing_animation(ans) # commented out true typing animation to avoid markdown rerender glitches, but leaving mechanism ready.
            
            bot_msg = {
                "type": "bot",
                "content": ans,
                "sources": res_data.get("sources", []),
                "confidence": res_data.get("confidence", "Low"),
                "timestamp": datetime.now().strftime("%I:%M %p")
            }
            st.session_state.chat_history.append(bot_msg)
            st.rerun()


# --- APP RUNNER ---
def main():
    inject_custom_css()
    init_session_state()
    
    if st.session_state.jwt_token is None:
        login_view()
    else:
        chat_view()

if __name__ == "__main__":
    main()
