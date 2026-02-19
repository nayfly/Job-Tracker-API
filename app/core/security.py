from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated=["bcrypt"],  # así bcrypt se considera “viejo”
)
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    pw = password.strip()

    # Política tuya (no la del algoritmo):
    # 256 caracteres es más que suficiente para contraseñas humanas + passphrases.
    if len(pw) > 256:
        raise ValueError("Password too long (max 256 characters)")

    return pwd_context.hash(pw)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password.strip(), hashed)


def needs_rehash(hashed: str) -> bool:
    return pwd_context.needs_update(hashed)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    exp_minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(UTC) + timedelta(minutes=exp_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise JWTError("Missing subject")
    return sub
