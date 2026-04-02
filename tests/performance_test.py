import requests
import time

BASE_URL = "http://127.0.0.1:8000"

login = requests.post(
    f"{BASE_URL}/auth/login",
    params={
        "email": "finance@company.com",
        "password": "securepassword123"
    }
)

token = login.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}"
}

start = time.time()

response = requests.post(
    f"{BASE_URL}/chat",
    params={"question": "What was the revenue growth in Q3?"},
    headers=headers
)

end = time.time()

print("Response time:", end - start, "seconds")
print(response.json())