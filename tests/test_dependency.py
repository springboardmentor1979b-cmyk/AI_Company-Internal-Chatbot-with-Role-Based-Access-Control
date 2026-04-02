from backend.auth.jwt_handler import create_access_token
from backend.auth.dependencies import verify_token

user = {
    "user_id": 1,
    "email": "finance@company.com",
    "role": "finance"
}

token = create_access_token(user)

print("Generated Token:\n", token)

decoded = verify_token(token)

print("\nDecoded User:")
print(decoded)