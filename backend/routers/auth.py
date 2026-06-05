from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from ..services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Yangi foydalanuvchi ro'yxatdan o'tishi"""
    from ..utils.security import create_access_token
    user  = register_user(db, data)
    token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": token, "user": user}

@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Tizimga kirish"""
    result = login_user(db, data)
    return {"access_token": result["access_token"], "user": result["user"]}
