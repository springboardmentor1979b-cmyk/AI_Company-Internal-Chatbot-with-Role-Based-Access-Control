import streamlit as st
from api_client import login_user


def show_login():
    """Display login page."""
    
    st.title("🔐 Company AI Assistant Login")
    
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email Address", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login", type="primary")
    
    if submitted:
        if not email or not password:
            st.error("Email and password are required")
        else:
            with st.spinner("Logging in..."):
                result = login_user(email, password)
            
            if result["success"]:
                st.session_state["token"] = result["token"]
                st.session_state["user_email"] = email
                st.session_state["logged_in"] = True
                st.session_state["current_page"] = "chat"
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error(f"❌ Login failed: {result['message']}")
    
    # Register link
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("📝 Create New Account", use_container_width=True):
            st.session_state["current_page"] = "register"
            st.rerun()
