import streamlit as st
import requests

API_URL = "http://localhost:8000"

def show_admin_dashboard(token):

    headers = {"Authorization": f"Bearer {token}"}

    st.title("📊 Admin Dashboard")

    stats = requests.get(f"{API_URL}/dashboard/stats", headers=headers)

    if stats.status_code == 200:
        data = stats.json()

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Users", data["total_users"])
        col2.metric("Total Queries", data["total_queries"])
        col3.metric("Unauthorized Attempts", data["unauthorized_attempts"])

    else:
        st.error("Access Denied")