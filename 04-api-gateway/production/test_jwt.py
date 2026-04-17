import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "test"
ALGORITHM = "HS256"

payload = {
    "sub": "test",
    "iat": datetime.now(timezone.utc),
    "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
}

try:
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Token: {token}")
except Exception as e:
    print(f"Error: {e}")
