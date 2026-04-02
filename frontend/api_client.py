import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"


def register_user(email, password, role):
    """Register a new user."""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "email": email,
                "password": password,
                "role": role
            },
            timeout=10
        )
        
        if response.status_code == 201:
            return {
                "success": True,
                "message": "User registered successfully",
                "user": response.json().get("user")
            }
        elif response.status_code == 400:
            error_detail = response.json().get("detail", "User already exists")
            return {
                "success": False,
                "message": error_detail
            }
        else:
            return {
                "success": False,
                "message": f"Registration failed: {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to server. Is the backend running?"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def login_user(email, password):
    """Login user and get access token."""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "token": data.get("access_token"),
                "message": "Login successful"
            }
        elif response.status_code == 401:
            return {
                "success": False,
                "message": "Invalid email or password"
            }
        elif response.status_code == 403:
            return {
                "success": False,
                "message": "Account is inactive"
            }
        else:
            return {
                "success": False,
                "message": f"Login failed: {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to server. Is the backend running?"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def ask_question(question, token):
    """Ask a question to the RAG system."""
    try:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat",
            params={
                "question": question
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {
                "answer": "Session expired. Please login again.",
                "sources": []
            }
        elif response.status_code == 503:
            return {
                "answer": "RAG pipeline is not available. Please ensure all dependencies are installed.",
                "sources": []
            }
        else:
            return {
                "answer": f"Error from backend: {response.status_code}",
                "sources": []
            }
    except requests.exceptions.Timeout:
        return {
            "answer": "Request timed out. The query may be taking too long.",
            "sources": []
        }
    except requests.exceptions.ConnectionError:
        return {
            "answer": "Cannot connect to server. Is the backend running?",
            "sources": []
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)}",
            "sources": []
        }