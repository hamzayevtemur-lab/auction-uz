from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from fastapi import HTTPException

from ..database import get_db
from ..dependencies import get_current_admin, get_current_user
from ..models.user import User
from ..models.auction import Auction
from ..models.bid import Bid
from ..models.payment import Payment
from ..config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── VERIFY ADMIN CODE ─────────────────────────────────────────────────────────
@router.post("/verify-code")
def verify_admin_code(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = payload.get("code", "").strip()
    if not code:
        raise HTTPException(400, "Kod kiritilmagan")
    if code != settings.ADMIN_SECRET_CODE:
        raise HTTPException(403, "Noto'g'ri admin kodi")
    user = db.query(User).filter(User.id == current_user.id).first()
    user.role = "admin"
    db.commit()
    db.refresh(user)
    return {"message": "Admin huquqi berildi!", "role": user.role, "full_name": user.full_name}


# ── STATS ─────────────────────────────────────────────────────────────────────
@router.get("/stats")
def platform_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    total_users      = db.query(func.count(User.id)).scalar()
    buyers           = db.query(func.count(User.id)).filter(User.role == "buyer").scalar()
    sellers          = db.query(func.count(User.id)).filter(User.role == "seller").scalar()
    active_users     = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    blocked_users    = db.query(func.count(User.id)).filter(User.is_active == False).scalar()
    total_auctions   = db.query(func.count(Auction.id)).scalar()
    active_auctions  = db.query(func.count(Auction.id)).filter(Auction.status == "active").scalar()
    pending_auctions = db.query(func.count(Auction.id)).filter(Auction.status == "pending").scalar()
    sold_auctions    = db.query(func.count(Auction.id)).filter(Auction.status == "sold").scalar()
    ended_auctions   = db.query(func.count(Auction.id)).filter(Auction.status == "ended").scalar()
    total_bids       = db.query(func.count(Bid.id)).scalar()
    total_revenue    = db.query(func.sum(Payment.amount)).filter(Payment.status == "completed").scalar()
    seller_fees      = db.query(func.sum(Payment.amount)).filter(Payment.type == "seller_fee", Payment.status == "completed").scalar()
    part_fees        = db.query(func.sum(Payment.amount)).filter(Payment.type == "participation_fee", Payment.status == "completed").scalar()

    return {
        "users": {
            "total": total_users,
            "buyers": buyers,
            "sellers": sellers,
            "active": active_users,
            "blocked": blocked_users,
        },
        "auctions": {
            "total": total_auctions,
            "active": active_auctions,
            "pending": pending_auctions,
            "sold": sold_auctions,
            "ended": ended_auctions,
        },
        "bids": {"total": total_bids},
        "revenue": {
            "total": float(total_revenue or 0),
            "seller_fees": float(seller_fees or 0),
            "part_fees": float(part_fees or 0),
        },
    }


# ── USERS ─────────────────────────────────────────────────────────────────────
@router.get("/users")
def all_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    blocked: Optional[bool] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if search:
        q = q.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%"))
        )
    if blocked is not None:
        q = q.filter(User.is_active == (not blocked))

    total = q.count()
    users = q.order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    items = []
    for u in users:
        items.append({
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "balance": float(u.balance or 0),
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "auction_count": db.query(func.count(Auction.id)).filter(Auction.seller_id == u.id).scalar(),
            "bid_count": db.query(func.count(Bid.id)).filter(Bid.bidder_id == u.id).scalar(),
        })

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "items": items,
    }


@router.put("/users/{user_id}/block")
def toggle_block(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    if user.role == "admin":
        raise HTTPException(400, "Adminni bloklash mumkin emas")
    user.is_active = not user.is_active
    db.commit()
    action = "Bloklandi" if not user.is_active else "Blokdan chiqarildi"
    return {"blocked": not user.is_active, "message": action}


@router.put("/users/{user_id}/role")
def change_role(
    user_id: int,
    role: str = Query(..., pattern="^(buyer|seller|admin)$"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    user.role = role
    db.commit()
    return {"message": f"Rol '{role}' ga o'zgartirildi"}


# ── AUCTIONS ──────────────────────────────────────────────────────────────────
@router.get("/auctions")
def all_auctions(
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    q = db.query(Auction)
    if status:
        q = q.filter(Auction.status == status)
    if search:
        q = q.filter(Auction.title.ilike(f"%{search}%"))

    total = q.count()
    auctions = q.order_by(desc(Auction.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    items = []
    for a in auctions:
        seller_name = db.query(User.full_name).filter(User.id == a.seller_id).scalar()
        bid_count   = db.query(func.count(Bid.id)).filter(Bid.auction_id == a.id).scalar()
        items.append({
            "id": a.id,
            "title": a.title,
            "status": a.status,
            "category_id": a.category_id,
            "starting_price": float(a.starting_price),
            "current_bid": float(a.current_bid or a.starting_price),
            "seller_id": a.seller_id,
            "seller_name": seller_name,
            "bid_count": bid_count,
            "seller_fee_paid": a.seller_fee_paid,
            "starts_at": a.starts_at.isoformat() if a.starts_at else None,
            "ends_at": a.ends_at.isoformat() if a.ends_at else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        })

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
        "items": items,
    }


@router.put("/auctions/{auction_id}/cancel")
def cancel_auction(
    auction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    a = db.query(Auction).filter(Auction.id == auction_id).first()
    if not a:
        raise HTTPException(404, "Auktsion topilmadi")
    a.status = "cancelled"
    db.commit()
    return {"message": "Auktsion bekor qilindi"}


@router.put("/auctions/{auction_id}/activate")
def activate_auction(
    auction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    a = db.query(Auction).filter(Auction.id == auction_id).first()
    if not a:
        raise HTTPException(404, "Auktsion topilmadi")
    a.status = "active"
    db.commit()
    return {"message": "Auktsion faollashtirildi"}


# ── PAYMENTS ──────────────────────────────────────────────────────────────────
@router.get("/payments")
def all_payments(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    total    = db.query(func.count(Payment.id)).scalar()
    payments = db.query(Payment).order_by(desc(Payment.created_at)).offset((page - 1) * per_page).limit(per_page).all()

    items = []
    for p in payments:
        user_name = db.query(User.full_name).filter(User.id == p.user_id).scalar()
        items.append({
            "id": p.id,
            "type": p.type,
            "amount": float(p.amount),
            "status": p.status,
            "method": p.method,
            "user_id": p.user_id,
            "user_name": user_name,
            "auction_id": p.auction_id,
            "description": p.description,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })

    return {
        "total": total,
        "page": page,
        "pages": (total + per_page - 1) // per_page,
        "items": items,
    }


# ── BIDS ──────────────────────────────────────────────────────────────────────
@router.get("/bids/recent")
def recent_bids(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    bids = db.query(Bid).order_by(desc(Bid.created_at)).limit(limit).all()

    result = []
    for b in bids:
        bidder_name   = db.query(User.full_name).filter(User.id == b.bidder_id).scalar()
        auction_title = db.query(Auction.title).filter(Auction.id == b.auction_id).scalar()
        result.append({
            "id": b.id,
            "auction_id": b.auction_id,
            "amount": float(b.amount),
            "bidder_id": b.bidder_id,
            "bidder_name": bidder_name,
            "auction_title": auction_title,
            "created_at": b.created_at.isoformat() if b.created_at else None,
        })

    return result


# ── ADMIN CODE LOGIN (no account needed) ──────────────────────────────────────
@router.post("/login-with-code")
def admin_login_with_code(
    payload: dict,
    db: Session = Depends(get_db),
):
    """
    Faqat admin kodi orqali kirish.
    Kod to'g'ri bo'lsa, admin hisobiga JWT token qaytaradi.
    """
    from ..utils.security import create_access_token

    code = payload.get("code", "").strip()
    if not code:
        raise HTTPException(400, "Kod kiritilmagan")
    if code != settings.ADMIN_SECRET_CODE:
        raise HTTPException(403, "Noto'g'ri admin kodi")

    # Find or create a system admin account
    admin_user = db.query(User).filter(User.role == "admin").first()
    if not admin_user:
        # Fallback: create a default admin if none exists
        admin_user = db.query(User).filter(User.email == "admin@savdo.uz").first()
        if admin_user:
            admin_user.role = "admin"
            db.commit()
        else:
            raise HTTPException(404, "Admin hisobi topilmadi. Avval seed.sql ni yuklang.")

    token = create_access_token({"sub": str(admin_user.id), "role": "admin"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": admin_user.id,
            "full_name": admin_user.full_name,
            "email": admin_user.email,
            "role": admin_user.role,
        }
    }


# ── DELETE USER ───────────────────────────────────────────────────────────────
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    if user.id == current_admin.id:
        raise HTTPException(400, "O'zingizni o'chira olmaysiz")

    # Clean up related records first (avoid FK errors)
    db.query(Bid).filter(Bid.bidder_id == user_id).delete()
    db.query(Payment).filter(Payment.user_id == user_id).delete()

    from ..models.auction import Auction, AuctionParticipant
    db.query(AuctionParticipant).filter(AuctionParticipant.user_id == user_id).delete()

    # Delete user's auctions and their dependent rows
    auction_ids = [a.id for a in db.query(Auction.id).filter(Auction.seller_id == user_id).all()]
    if auction_ids:
        db.query(Bid).filter(Bid.auction_id.in_(auction_ids)).delete(synchronize_session=False)
        db.query(Payment).filter(Payment.auction_id.in_(auction_ids)).delete(synchronize_session=False)
        db.query(AuctionParticipant).filter(AuctionParticipant.auction_id.in_(auction_ids)).delete(synchronize_session=False)
        db.query(Auction).filter(Auction.seller_id == user_id).delete(synchronize_session=False)

    from ..models.payment import Notification
    db.query(Notification).filter(Notification.user_id == user_id).delete()

    db.delete(user)
    db.commit()
    return {"message": f"'{user.full_name}' o'chirildi"}