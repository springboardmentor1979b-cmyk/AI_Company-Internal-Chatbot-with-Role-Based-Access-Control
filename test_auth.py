from backend.database import get_db
from backend.models import User
from backend.auth import verify_password

db_gen = get_db()
db = next(db_gen)
try:
    user = db.query(User).filter(User.username == "finance_user").first()
    print(f"Match: {verify_password('pass123', user.password_hash)}")
finally:
    db.close()
