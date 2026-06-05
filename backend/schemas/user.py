from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    role: str = "buyer"

    @field_validator("role")
    def role_must_be_valid(cls, v):
        if v not in ("buyer", "seller"):
            raise ValueError("Role must be buyer or seller")
        return v

    @field_validator("password")
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgi bo'lishi kerak")
        return v

    @field_validator("phone")
    def phone_format(cls, v):
        digits = "".join(c for c in v if c.isdigit())
        if len(digits) < 9:
            raise ValueError("Telefon raqami noto'g'ri")
        return v

class UserLogin(BaseModel):
    identifier: str   # email yoki telefon
    password: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    role: str
    balance: Decimal
    is_verified: bool
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str]     = None
    avatar_url: Optional[str]= None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
