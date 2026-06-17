from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from ..config import settings


def hash_password(password: str) -> str:
    """Parolni bcrypt bilan xeshlash"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Parolni tekshirish"""
    try:
        return bcrypt.checkpw(
            plain.encode('utf-8'),
            hashed.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT token yaratish.
    "sub" claim JWT standartiga ko'ra har doim string bo'lishi kerak —
    shuning uchun bu yerda majburan str() ga o'tkazamiz. Aks holda
    dependencies.py dagi int(payload.get("sub")) bilan mos kelmay,
    foydalanuvchi har safar 401 olishi mumkin edi.
    """
    to_encode = data.copy()
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])

    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """JWT tokenni tekshirish"""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
    except JWTError:
        return None