import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Internal Chatbot", page_icon="🤖", layout="wide")

def login():
    st.subheader("Login to AI Chatbot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        with st.spinner("Authenticating..."):
            response = requests.post(f"{API_BASE_URL}/login", data={"username": username, "password": password})
            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state["token"] = token
                
                # Fetch user info
                user_info = requests.get(f"{API_BASE_URL}/me", headers={"Authorization": f"Bearer {token}"})
                if user_info.status_code == 200:
                    st.session_state["username"] = user_info.json()["username"]
                    st.session_state["role"] = user_info.json()["role"]
                    st.session_state["messages"] = []
                    st.rerun()
                else:
                    st.error("Failed to fetch user info")
            else:
                st.error("Invalid credentials")

def chat_interface():
    st.sidebar.title("User Profile")
    st.sidebar.write(f"**Username:** {st.session_state['username']}")
    st.sidebar.write(f"**Role:** {st.session_state['role']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
        
    st.title("Company Documents Chatbot")
    
    # Display message history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("sources"):
                with st.expander("Sources"):
                    for src in msg["sources"]:
                        st.markdown(f"- {src}")
                        
    # Chat input
    if prompt := st.chat_input("Ask about company documents..."):
        # Display user message
        st.session_state["messages"].append({"role": "user", "content": prompt, "sources": []})
        with st.chat_message("user"):
            st.write(prompt)
            
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                response = requests.post(
                    f"{API_BASE_URL}/query", 
                    json={"query": prompt},
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer found.")
                    sources = data.get("sources", [])
                    
                    st.write(answer)
                    if sources:
                        with st.expander("Sources"):
                            for src in sources:
                                st.markdown(f"- {src}")
                                
                    st.session_state["messages"].append({"role": "assistant", "content": answer, "sources": sources})
                else:
                    st.error(f"Error {response.status_code}: {response.text}")

if "token" not in st.session_state:
    login()
else:
    chat_interface()
