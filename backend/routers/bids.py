from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.bid import BidCreate, BidOut
from ..services.bid_service import place_bid, get_auction_bids, get_my_bids
from ..utils.websocket_manager import ws_manager
from typing import List

router = APIRouter(prefix="/bids", tags=["Bids"])

@router.post("", response_model=BidOut, status_code=201)
async def create_bid(
    data: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Yangi taklif berish"""
    bid = place_bid(db, data.auction_id, float(data.amount), current_user)

    # WebSocket orqali barcha kuzatuvchilarga broadcast
    await ws_manager.broadcast(data.auction_id, {
        "event":     "new_bid",
        "bid_id":    bid.id,
        "amount":    float(bid.amount),
        "bidder":    current_user.full_name,
        "auction_id":bid.auction_id,
    })
    return bid

@router.get("/auction/{auction_id}", response_model=List[BidOut])
def auction_bids(auction_id: int, db: Session = Depends(get_db)):
    """Auktsion taklif tarixi"""
    return get_auction_bids(db, auction_id)

@router.get("/my", response_model=List[BidOut])
def my_bids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mening barcha takliflarim"""
    return get_my_bids(db, current_user.id)
