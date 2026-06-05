from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..dependencies import get_current_user, get_current_seller
from ..models.user import User
from ..schemas.auction import AuctionCreate, AuctionOut
from ..services.auction_service import (
    create_auction, get_auction, list_auctions, check_participant
)
from ..utils.websocket_manager import ws_manager

router = APIRouter(prefix="/auctions", tags=["Auctions"])

@router.get("", summary="Barcha auktsionlar ro'yxati")
def get_auctions(
    category_id: Optional[int] = None,
    status:      Optional[str] = Query(None, pattern="^(active|pending|ended|sold)$"),
    search:      Optional[str] = None,
    page:        int = Query(1, ge=1),
    per_page:    int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return list_auctions(db, category_id, status, search, page, per_page)

@router.get("/my", summary="Mening auktsionlarim")
def get_my_auctions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from ..models.auction import Auction
    return (
        db.query(Auction)
        .filter(Auction.seller_id == current_user.id)
        .order_by(Auction.created_at.desc())
        .all()
    )

@router.get("/{auction_id}", response_model=AuctionOut)
def get_one(auction_id: int, db: Session = Depends(get_db)):
    return get_auction(db, auction_id)

@router.post("", response_model=AuctionOut, status_code=201)
def create(
    data: AuctionCreate,
    db: Session = Depends(get_db),
    seller: User = Depends(get_current_seller),
):
    return create_auction(db, data, seller)

@router.get("/{auction_id}/participants/me")
def check_my_participation(
    auction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    is_p = check_participant(db, auction_id, current_user.id)
    return {"participating": is_p}

@router.websocket("/{auction_id}/ws")
async def auction_ws(auction_id: int, websocket: WebSocket):
    await ws_manager.connect(auction_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(auction_id, websocket)


@router.get("/stats/top-sellers")
def top_sellers(db: Session = Depends(get_db)):
    """Ko'p auktsion joylashtirilgan sotuvchilar"""
    from sqlalchemy import func
    from ..models.auction import Auction
    from ..models.user import User

    results = (
        db.query(
            User.id,
            User.full_name,
            func.count(Auction.id).label("auction_count"),
            func.sum(Auction.current_bid).label("total_volume"),
        )
        .join(Auction, Auction.seller_id == User.id)
        .filter(Auction.status.in_(["active", "sold", "ended"]))
        .group_by(User.id, User.full_name)
        .order_by(func.count(Auction.id).desc())
        .limit(5)
        .all()
    )

    return [
        {
            "id":            r.id,
            "full_name":     r.full_name,
            "initials":      "".join(w[0] for w in r.full_name.split()).upper()[:2],
            "auction_count": r.auction_count,
            "total_volume":  float(r.total_volume or 0),
        }
        for r in results
    ]


@router.get("/stats/recent-sold")
def recent_sold(db: Session = Depends(get_db)):
    """So'ngi sotilgan auktsionlar"""
    from ..models.auction import Auction
    auctions = (
        db.query(Auction)
        .filter(Auction.status.in_(["sold", "ended"]))
        .order_by(Auction.ends_at.desc())
        .limit(5)
        .all()
    )
    return [
        {
            "id":            a.id,
            "title":         a.title,
            "category_id":   a.category_id,
            "final_price":   float(a.current_bid or a.starting_price),
            "ends_at":       a.ends_at.isoformat() if a.ends_at else None,
            "status":        a.status,
        }
        for a in auctions
    ]
