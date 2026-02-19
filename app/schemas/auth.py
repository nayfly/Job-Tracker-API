from pydantic import BaseModel, EmailStr, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_length(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        # bcrypt: 72 bytes límite, usamos bytes por si hay unicode
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password too long (max 72 bytes)")
        return v


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"