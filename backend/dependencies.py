from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .utils.security import decode_token
from .models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati o'tgan",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exc

    raw_sub = payload.get("sub")
    if raw_sub is None:
        raise credentials_exc

    # JWT "sub" is always a string by spec, regardless of how it was encoded.
    # Casting here is mandatory — comparing User.id (int column) against a
    # string "sub" can silently match zero rows on some DB drivers, which
    # was causing every authenticated request to 401 right after login.
    try:
        user_id = int(raw_sub)
    except (TypeError, ValueError):
        raise credentials_exc

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exc
    return user


def get_current_seller(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("seller", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amal faqat sotuvchilar uchun mavjud"
        )
    return current_user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amal faqat adminlar uchun mavjud"
        )
    return current_user