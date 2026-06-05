from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User
from ..schemas.user import UserRegister, UserLogin
from ..utils.security import hash_password, verify_password, create_access_token

def register_user(db: Session, data: UserRegister) -> User:
    # Email yoki telefon allaqachon mavjudmi?
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email allaqachon ro'yxatdan o'tgan"
        )
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu telefon raqami allaqachon ro'yxatdan o'tgan"
        )
    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def login_user(db: Session, data: UserLogin) -> dict:
    # Email yoki telefon bilan qidiruv
    user = (
        db.query(User)
        .filter(
            (User.email == data.identifier) |
            (User.phone == data.identifier)
        )
        .first()
    )
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/telefon yoki parol noto'g'ri"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hisobingiz bloklangan. Yordam uchun murojaat qiling."
        )
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "user": user}
