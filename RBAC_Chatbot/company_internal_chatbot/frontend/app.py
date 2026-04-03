import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Internal Chatbot", layout="centered")

# Custom CSS for Pastel Theme
st.markdown("""
    <style>
        .stApp {
            background-color: #f7f9fc;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .stButton>button {
            background-color: #a2d2ff;
            color: #fff;
            border-radius: 10px;
            border: none;
            padding: 10px 20px;
        }
        .stButton>button:hover {
            background-color: #bde0fe;
            color: #fff;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
            border: 1px solid #cdb4db;
        }
        .chat-bubble-user {
            background-color: #ffafcc;
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            color: #fff;
        }
        .chat-bubble-bot {
            background-color: #ffc8dd;
            padding: 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            color: #2c3e50;
        }
        .source-box {
            background-color: #e0fbfc;
            border-left: 4px solid #98c1d9;
            padding: 10px;
            margin-top: 10px;
            font-size: 0.9em;
            color: #3d5a80;
        }
    </style>
""", unsafe_allow_html=True)


if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.messages = []

def login():
    st.title("Welcome to Internal Chatbot")
    st.subheader("Login")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post(f"{API_URL}/login", data={"username": username, "password": password})
            if res.status_code == 200:
                st.session_state.token = res.json().get("access_token")
                user_res = requests.get(f"{API_URL}/me", headers={"Authorization": f"Bearer {st.session_state.token}"})
                st.session_state.user = user_res.json()
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        reg_username = st.text_input("Username", key="reg_user")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_role = st.selectbox("Role", ["Finance", "HR", "Marketing", "Engineering", "Employee", "C_Level"])
        if st.button("Register"):
            res = requests.post(f"{API_URL}/register", json={"username": reg_username, "password": reg_password, "role": reg_role})
            if res.status_code == 201:
                st.success("Registered successfully. Please login.")
            else:
                st.error("Error registering user")

def chat_interface():
    st.sidebar.title("App Settings")
    st.sidebar.write(f"Logged in as: **{st.session_state.user['username']}**")
    st.sidebar.write(f"Role: **{st.session_state.user['role'].capitalize()}**")
    
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()
    
    st.title(f"Internal Chatbot ({st.session_state.user['role'].capitalize()})")
    
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {content}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-bot"><b>Bot:</b> {content}</div>', unsafe_allow_html=True)
            if "sources" in msg and msg["sources"]:
                for idx, src in enumerate(msg["sources"]):
                    st.markdown(f'<div class="source-box"><b>Source {idx+1}: {src["source"]}</b><br>{src["document"][:200]}...</div>', unsafe_allow_html=True)

    query = st.chat_input("Ask a question about internal docs...")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {query}</div>', unsafe_allow_html=True)

        with st.spinner("Searching and generating response..."):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            res = requests.post(f"{API_URL}/chat", json={"query": query}, headers=headers)
            
            if res.status_code == 200:
                data = res.json()
                answer = data["answer"]
                sources = data["sources"]
                st.session_state.messages.append({"role": "bot", "content": answer, "sources": sources})
                st.markdown(f'<div class="chat-bubble-bot"><b>Bot:</b> {answer}</div>', unsafe_allow_html=True)
                for idx, src in enumerate(sources):
                    st.markdown(f'<div class="source-box"><b>Source {idx+1}: {src["source"]}</b><br>{src["document"][:200]}...</div>', unsafe_allow_html=True)
            else:
                st.error("Error connecting to backend.")

if st.session_state.token is None:
    login()
else:
    chat_interface()
