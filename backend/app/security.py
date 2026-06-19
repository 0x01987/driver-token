import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from secrets import token_hex

from cryptography.fernet import Fernet
from jose import jwt

from app.config import get_settings


PBKDF2_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    salt = token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_hash = password_hash.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return hmac.compare_digest(actual_hash, expected_hash)


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=12)
    return jwt.encode(
        {"sub": user_id, "exp": expires_at},
        settings.jwt_secret,
        algorithm="HS256",
    )


def hash_external_id(platform: str, external_id: str) -> str:
    payload = f"{platform}:{external_id}".encode("utf-8")
    return "0x" + hashlib.sha256(payload).hexdigest()


def encrypt_token(token: str) -> str:
    return Fernet(get_settings().token_encryption_key).encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    return Fernet(get_settings().token_encryption_key).decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
