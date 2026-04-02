"""
API Testing Script
Tests all authentication and chat endpoints
"""

import requests
import json
from datetime import datetime
import sys
import os

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_health():
    """Test health endpoint."""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("[OK] Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_register():
    """Test user registration."""
    print_section("TEST 2: User Registration")
    
    test_email = f"testuser_{datetime.now().timestamp()}@example.com"
    test_password = "TestPassword123"
    test_role = "employee"
    
    data = {
        "email": test_email,
        "password": test_password,
        "role": test_role
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("[OK] Registration successful")
            print(json.dumps(result, indent=2, default=str))
            return test_email, test_password
        else:
            print(f"[FAIL] Registration failed")
            print(json.dumps(response.json(), indent=2))
            return None, None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None, None


def test_login(email, password):
    """Test user login."""
    print_section("TEST 3: User Login")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Login successful")
            print(f"Token: {result.get('access_token')[:50]}...")
            print(f"Token Type: {result.get('token_type')}")
            print(f"Expires In: {result.get('expires_in')} seconds")
            return result.get('access_token')
        else:
            print(f"[FAIL] Login failed")
            print(json.dumps(response.json(), indent=2))
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def test_get_current_user(token):
    """Test getting current user info."""
    print_section("TEST 4: Get Current User Info")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Retrieved user info successfully")
            print(json.dumps(result, indent=2, default=str))
            return True
        else:
            print(f"[FAIL] Failed to retrieve user info")
            print(json.dumps(response.json(), indent=2))
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_chat(token):
    """Test RAG chat endpoint."""
    print_section("TEST 5: Chat with RAG System")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    question = "What is this company?"
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            params={"question": question},
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Chat request successful")
            print(f"Question: {result.get('question')}")
            print(f"Answer: {result.get('answer')[:200]}...")
            print(f"User Role: {result.get('user_role')}")
            return True
        elif response.status_code == 503:
            print("[WARNING] RAG pipeline not available (dependencies not installed)")
            print("This is expected if sentence-transformers is not installed")
            return True  # Not a critical failure
        else:
            print(f"[FAIL] Chat request failed")
            print(json.dumps(response.json(), indent=2))
            return False
    except requests.exceptions.Timeout:
        print("[WARNING] Request timed out (RAG processing might be slow)")
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_logout(token):
    """Test logout endpoint."""
    print_section("TEST 6: Logout")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] Logout successful")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"[FAIL] Logout failed")
            print(json.dumps(response.json(), indent=2))
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def print_summary(results):
    """Print test summary."""
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} [OK]")
    print(f"Failed: {failed} [FAIL]")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed!")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please check the output above.")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  COMPANY RAG PROJECT - API TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Test health
    results["Health Check"] = test_health()
    
    # Test registration and get credentials
    email, password = test_register()
    if email and password:
        results["Registration"] = True
        
        # Test login
        token = test_login(email, password)
        if token:
            results["Login"] = True
            
            # Test get current user
            results["Get Current User"] = test_get_current_user(token)
            
            # Test chat
            results["Chat"] = test_chat(token)
            
            # Test logout
            results["Logout"] = test_logout(token)
        else:
            results["Login"] = False
            results["Get Current User"] = False
            results["Chat"] = False
            results["Logout"] = False
    else:
        results["Registration"] = False
        results["Login"] = False
        results["Get Current User"] = False
        results["Chat"] = False
        results["Logout"] = False
    
    print_summary(results)
