from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import create_access_token, hash_password, needs_rehash, verify_password
from app.models.user import User
from app.schemas.auth import RegisterIn, TokenOut

router = APIRouter()

# in-memory crude rate limiting for login attempts. keyed by username and
# kept only for a short window; this shop‑floor solution is sufficient for a
# demo and can be replaced with redis/fastapi-limiter in production.
_login_attempts: dict[str, list] = {}
_MAX_ATTEMPTS = 5
_WINDOW_MINUTES = 1



@router.post("/register", status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)) -> dict:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=payload.email, hashed_password=hash_password(payload.password), is_active=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenOut:
    # basic username-based throttle; window in minutes
    from datetime import datetime, timedelta, UTC

    now = datetime.now(UTC)
    attempts = _login_attempts.get(form.username, [])
    window = timedelta(minutes=_WINDOW_MINUTES)
    attempts = [t for t in attempts if now - t < window]
    if len(attempts) >= _MAX_ATTEMPTS:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many login attempts, try again later")
    attempts.append(now)
    _login_attempts[form.username] = attempts
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials")

    # Si el hash es bcrypt (o params antiguos), lo actualizas a argon2 sin drama
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(form.password)
        db.add(user)
        db.commit()

    token = create_access_token(user.email)
    return TokenOut(access_token=token)