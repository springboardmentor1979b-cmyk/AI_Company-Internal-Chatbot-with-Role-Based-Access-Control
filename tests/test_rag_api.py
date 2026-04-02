import requests

BASE_URL = "http://127.0.0.1:8000"

EMAIL = "finance@company.com"
PASSWORD = "securepassword123"


def test_full_rag_pipeline():

    print("Testing login...")

    login = requests.post(
        f"{BASE_URL}/auth/login",
        params={
            "email": EMAIL,
            "password": PASSWORD
        }
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    print("Testing chat endpoint...")

    response = requests.post(
        f"{BASE_URL}/chat",
        params={
            "question": "What was the revenue growth in Q3?"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    print("Answer:", data["answer"])
    print("Sources:", data["sources"])

    assert "answer" in data
    assert "sources" in data

    print("End-to-End Test Passed")


if __name__ == "__main__":
    test_full_rag_pipeline()