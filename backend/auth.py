import hashlib, secrets, time, base64, json

SECRET = 'smarterp-secret-key'

def hash_password(password: str) -> str:
    return hashlib.sha256((password + SECRET).encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_token(user_id: int) -> str:
    payload = {"user_id": user_id, "exp": int(time.time()) + 86400}
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode()

def read_token(token: str):
    try:
        data = json.loads(base64.urlsafe_b64decode(token.encode()).decode())
        if data.get('exp', 0) < time.time():
            return None
        return data
    except Exception:
        return None
