from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_admin
from ..models.user import User
from ..models.auction import Auction
from ..models.payment import Payment

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats")
def platform_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    """Platforma umumiy statistikasi"""
    from sqlalchemy import func
    total_users    = db.query(func.count(User.id)).scalar()
    total_auctions = db.query(func.count(Auction.id)).scalar()
    active_auctions= db.query(func.count(Auction.id)).filter(Auction.status=="active").scalar()
    total_payments = db.query(func.sum(Payment.amount)).filter(Payment.status=="completed").scalar()
    return {
        "total_users":     total_users,
        "total_auctions":  total_auctions,
        "active_auctions": active_auctions,
        "total_revenue_uzs": float(total_payments or 0),
    }

@router.get("/users")
def all_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return db.query(User).order_by(User.created_at.desc()).limit(100).all()

@router.put("/users/{user_id}/block")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")
    user.is_active = not user.is_active
    db.commit()
    return {"message": f"Foydalanuvchi {'bloklandi' if not user.is_active else 'blokdan chiqarildi'}"}

@router.get("/auctions")
def all_auctions(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    return db.query(Auction).order_by(Auction.created_at.desc()).limit(100).all()
