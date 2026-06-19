import hashlib
from datetime import datetime, timedelta, timezone

from cryptography.fernet import Fernet
from jose import jwt
from passlib.context import CryptContext

from app.config import get_settings


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


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
