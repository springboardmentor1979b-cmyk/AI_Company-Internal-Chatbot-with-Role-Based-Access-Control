from backend.auth.jwt_handler import create_access_token, verify_token

user_data = {
    "user_id": 1,
    "email": "finance_user@company.com",
    "role": "finance"
}

token = create_access_token(user_data)

print("Generated JWT:\n", token)

decoded = verify_token(token)

print("\nDecoded Payload:")
print(decoded)