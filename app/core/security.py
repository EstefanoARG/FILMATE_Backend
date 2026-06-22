import os
import hashlib
import base64
import hmac
import json
import time
import secrets


SECRET_KEY = base64.b64encode(os.urandom(32)).decode("utf-8")
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return base64.b64encode(salt + dk).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    data = base64.b64decode(hashed.encode("utf-8"))
    salt, dk = data[:16], data[16:]
    new_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hmac.compare_digest(new_dk, dk)


def create_access_token(user_id: int, role_ids: list[int]) -> str:
    payload = {
        "user_id": user_id,
        "roles": role_ids,
        "exp": time.time() + TOKEN_EXPIRE_HOURS * 3600,
        "iat": time.time(),
        "jti": secrets.token_hex(16),
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("utf-8")
    sig = hmac.new(
        SECRET_KEY.encode("utf-8"), b64.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return f"{b64}.{sig}"


def verify_access_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        b64, sig = parts
        expected = hmac.new(
            SECRET_KEY.encode("utf-8"), b64.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        padded = b64 + "=" * (4 - len(b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None
