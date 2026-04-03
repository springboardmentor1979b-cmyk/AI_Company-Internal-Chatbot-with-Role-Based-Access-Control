"""
test_rbac.py
────────────
Run with:  pytest tests/test_rbac.py -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from src.auth.auth_handler import create_user, authenticate, create_token, decode_token, seed_demo_users
from src.data_processing.preprocessor import clean_text, chunk_text, get_roles_for_file


# ── Preprocessor tests ────────────────────────────────────────

def test_clean_text():
    raw = "Hello   \n\t World!!"
    assert clean_text(raw) == "Hello World!!"


def test_chunk_text_basic():
    text = " ".join(["word"] * 700)
    chunks = chunk_text(text, chunk_size=300)
    assert len(chunks) > 1
    for chunk in chunks:
        words = chunk.split()
        assert len(words) <= 300


def test_roles_for_hr_file():
    roles = get_roles_for_file("hr_data.csv")
    assert "hr" in roles
    assert "c_level" in roles


def test_roles_for_unknown_file():
    roles = get_roles_for_file("random_unknown.csv")
    # Should fall back to c_level only
    assert "c_level" in roles


# ── Auth tests ────────────────────────────────────────────────

def test_create_and_authenticate():
    seed_demo_users()   # idempotent
    user = authenticate("alice", "alice123")
    assert user is not None
    assert user["role"] == "finance"


def test_wrong_password():
    user = authenticate("alice", "wrongpassword")
    assert user is None


def test_jwt_roundtrip():
    seed_demo_users()
    user = authenticate("frank", "frank123")
    token = create_token(user)
    decoded = decode_token(token)
    assert decoded["username"] == "frank"
    assert decoded["role"] == "c_level"


def test_invalid_role():
    with pytest.raises(ValueError):
        create_user("hacker", "pass123", "superadmin")


# ── RBAC access logic tests ───────────────────────────────────

def test_finance_cannot_access_hr():
    hr_roles = get_roles_for_file("hr_data.csv").split(",")
    assert "finance" not in hr_roles


def test_c_level_sees_all_roles():
    # c_level is added to every file via get_roles_for_file
    roles = get_roles_for_file("hr_data.csv").split(",")
    assert "c_level" in roles


def test_marketing_file_roles():
    roles = get_roles_for_file("marketing_report.md").split(",")
    assert "marketing" in roles
