import streamlit as st
from api_client import ask_question


def show_chat():
    """Display chat interface for authenticated users."""
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🤖 Company AI Assistant")
    with col2:
        if st.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["token"] = None
            st.session_state["user_email"] = None
            st.session_state["chat_history"] = []
            st.rerun()
    
    # Display user info
    st.caption(f"📧 Logged in as: {st.session_state.get('user_email', 'Unknown')}")
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.chat_message("user").write(chat["message"])
        else:
            st.chat_message("assistant").write(chat["message"])
            
            if "sources" in chat and chat["sources"]:
                with st.expander("📚 Sources"):
                    for src in chat["sources"]:
                        st.write(f"- {src}")
    
    # Chat input
    user_input = st.chat_input("Ask a question about company data...")
    
    if user_input:
        # Display user message
        st.chat_message("user").write(user_input)
        
        st.session_state.chat_history.append({
            "role": "user",
            "message": user_input
        })
        
        # Get token
        token = st.session_state.get("token")
        
        if not token:
            st.error("Session expired. Please login again.")
            return
        
        # Call backend RAG API
        with st.spinner("🔍 Searching knowledge base..."):
            response = ask_question(user_input, token)
        
        # Ensure response is a dictionary
        if isinstance(response, str):
            try:
                import json
                response = json.loads(response)
            except:
                response = {"answer": response, "sources": []}
        
        answer = response.get("answer", "No answer returned.")
        sources = response.get("sources", [])
        
        # Display AI response
        st.chat_message("assistant").write(answer)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "message": answer,
            "sources": sources
        })
        
        if sources:
            with st.expander("📚 Sources", expanded=False):
                for src in sources:
                    st.write(f"- {src}")