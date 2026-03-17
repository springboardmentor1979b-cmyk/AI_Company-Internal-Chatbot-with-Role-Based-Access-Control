import pytest
import requests

BASE = "http://localhost:8000"


# ── Helper functions ──────────────────────────────────────────────────────────

def login(username, password):
    r = requests.post(f"{BASE}/login", data={"username": username, "password": password})
    assert r.status_code == 200, f"Login failed for {username}: {r.text}"
    return r.json()["access_token"]

def chat(token, query):
    return requests.post(
        f"{BASE}/chat",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"}
    )


# ── Auth Tests ────────────────────────────────────────────────────────────────

def test_login_admin_success():
    token = login("admin", "admin123")
    assert token is not None
    assert len(token) > 20

def test_login_invalid_password():
    r = requests.post(f"{BASE}/login", data={"username": "admin", "password": "wrong"})
    assert r.status_code == 401

def test_login_invalid_user():
    r = requests.post(f"{BASE}/login", data={"username": "ghost", "password": "x"})
    assert r.status_code == 401

def test_chat_without_token():
    r = requests.post(f"{BASE}/chat", json={"query": "hello"})
    assert r.status_code == 401


# ── RBAC Tests ────────────────────────────────────────────────────────────────

def test_clevel_can_access_finance():
    token = login("admin", "admin123")
    r = chat(token, "What is the company revenue?")
    assert r.status_code == 200
    assert r.json()["documents_used"] > 0

def test_clevel_can_access_hr():
    token = login("admin", "admin123")
    r = chat(token, "What is the remote work policy?")
    assert r.status_code == 200
    assert r.json()["documents_used"] > 0

def test_finance_can_access_finance():
    token = login("finance_user", "finance123")
    r = chat(token, "What is the company revenue?")
    assert r.status_code == 200
    assert r.json()["documents_used"] > 0

def test_finance_blocked_from_hr():
    token = login("finance_user", "finance123")
    r = chat(token, "What is the HR leave policy?")
    assert r.status_code == 200
    assert r.json()["documents_used"] == 0
    assert "access" in r.json()["answer"].lower()

def test_hr_can_access_hr():
    token = login("hr_user", "hr123")
    r = chat(token, "What is the remote work policy?")
    assert r.status_code == 200
    assert r.json()["documents_used"] > 0

def test_hr_blocked_from_marketing():
    token = login("hr_user", "hr123")
    r = chat(token, "What is our marketing budget?")
    assert r.status_code == 200
    assert r.json()["documents_used"] == 0

def test_marketing_blocked_from_salary():
    token = login("marketing_user", "marketing123")
    r = chat(token, "What is the employee salary structure?")
    assert r.status_code == 200
    assert r.json()["documents_used"] == 0
    assert "access" in r.json()["answer"].lower()

def test_marketing_can_access_marketing():
    token = login("marketing_user", "marketing123")
    r = chat(token, "Show the social media campaign results")
    assert r.status_code == 200
    assert r.json()["documents_used"] > 0

def test_engineering_can_access_engineering():
    token = login("engineering_user", "engineering123")
    r = chat(token, "How many engineers are on the team?")
    assert r.status_code == 200
    assert r.json()["documents_used"] > 0

def test_engineering_blocked_from_finance():
    token = login("engineering_user", "engineering123")
    r = chat(token, "What is the company revenue?")
    assert r.status_code == 200
    assert r.json()["documents_used"] == 0


# ── Guard Tests ───────────────────────────────────────────────────────────────

def test_off_topic_weather_blocked():
    token = login("admin", "admin123")
    r = chat(token, "What is the weather today?")
    assert r.status_code == 200
    ans = r.json()["answer"].lower()
    assert "company" in ans or "only" in ans or "access" in ans

def test_off_topic_joke_blocked():
    token = login("admin", "admin123")
    r = chat(token, "Tell me a joke")
    assert r.status_code == 200
    ans = r.json()["answer"].lower()
    assert "company" in ans or "only" in ans

def test_off_topic_poem_blocked():
    token = login("admin", "admin123")
    r = chat(token, "Write me a poem")
    assert r.status_code == 200
    ans = r.json()["answer"].lower()
    assert "company" in ans or "only" in ans

def test_small_talk_hi():
    token = login("admin", "admin123")
    r = chat(token, "hi")
    assert r.status_code == 200
    assert r.json()["documents_used"] == 0

def test_role_identity_finance():
    token = login("finance_user", "finance123")
    r = chat(token, "What is my role?")
    assert r.status_code == 200
    assert "finance" in r.json()["answer"].lower()

def test_role_identity_clevel():
    token = login("admin", "admin123")
    r = chat(token, "What is my role?")
    assert r.status_code == 200
    assert "c-level" in r.json()["answer"].lower()


# ── Dashboard Tests ───────────────────────────────────────────────────────────

def test_dashboard_clevel_access():
    token = login("admin", "admin123")
    r = requests.get(f"{BASE}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert "total_users" in data
    assert "total_queries" in data
    assert "recent_logs" in data

def test_dashboard_blocked_finance():
    token = login("finance_user", "finance123")
    r = requests.get(f"{BASE}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

def test_dashboard_blocked_hr():
    token = login("hr_user", "hr123")
    r = requests.get(f"{BASE}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403

def test_history_returns_data():
    token = login("admin", "admin123")
    r = requests.get(f"{BASE}/history", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "history" in r.json()


# ── Upload Tests ──────────────────────────────────────────────────────────────

def test_uploads_list():
    token = login("admin", "admin123")
    r = requests.get(f"{BASE}/uploads", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert "files" in r.json()

def test_uploads_requires_auth():
    r = requests.get(f"{BASE}/uploads")
    assert r.status_code == 401
