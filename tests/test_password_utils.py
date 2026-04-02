from backend.auth.password_utils import hash_password, verify_password

password = "securepassword123"

hashed = hash_password(password)

print("Hashed Password:", hashed)

is_valid = verify_password(password, hashed)

print("Password Verified:", is_valid)