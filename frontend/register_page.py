import streamlit as st
from api_client import register_user


def show_register():
    """Display registration page."""
    st.title("📝 Create Account")
    
    with st.form("register_form", clear_on_submit=True):
        email = st.text_input("Email Address", key="reg_email")
        password = st.text_input("Password", type="password", help="Minimum 6 characters", key="reg_password")
        password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        role = st.selectbox(
            "Select Your Role",
            ["employee", "engineering", "marketing", "finance", "hr", "c_level"],
            help="Choose your department/role",
            key="reg_role"
        )
        
        submitted = st.form_submit_button("Create Account", type="primary")
    
    if submitted:
        # Validate inputs
        if not email:
            st.error("Email is required")
            return
        elif not password:
            st.error("Password is required")
            return
        elif len(password) < 6:
            st.error("Password must be at least 6 characters")
            return
        elif password != password_confirm:
            st.error("Passwords do not match")
            return
        else:
            # Call registration API
            with st.spinner("Creating account..."):
                result = register_user(email, password, role)
            
            if result["success"]:
                st.success("✅ Account created successfully! Please login.")
                st.session_state["current_page"] = "login"
                st.rerun()
            else:
                st.error(f"❌ Registration failed: {result['message']}")
    
    # Link to login
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Back to Login", key="back_to_login"):
            st.session_state["current_page"] = "login"
            st.rerun()
