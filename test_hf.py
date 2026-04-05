import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HF_API_TOKEN")

print(f"Token present: {bool(token)}")

for model in ["google/flan-t5-base", "mistralai/Mistral-7B-Instruct-v0.2", "TinyLlama/TinyLlama-1.1B-Chat-v1.0"]:
    print(f"\n--- Testing {model} ---")
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    payload = {"inputs": "What is 2+2?", "parameters": {"max_new_tokens": 100}}
    try:
        resp = requests.post(url, headers=headers, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:200]}")
    except Exception as e:
        print(f"Exception: {e}")
