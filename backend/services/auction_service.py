from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import datetime
from typing import Optional
from ..models.auction import Auction, AuctionParticipant
from ..models.user import User
from ..schemas.auction import AuctionCreate
from ..utils.helpers import calc_seller_fee, paginate

def create_auction(db: Session, data: AuctionCreate, seller: User) -> Auction:
    fee = calc_seller_fee(float(data.starting_price))
    auction = Auction(
        seller_id=seller.id,
        category_id=data.category_id,
        title=data.title,
        description=data.description,
        item_condition=data.item_condition,
        location=data.location,
        delivery=data.delivery,
        starting_price=data.starting_price,
        reserve_price=data.reserve_price,
        min_step=data.min_step,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        status="pending",
        seller_fee_amount=fee,
        seller_fee_paid=False,
    )
    db.add(auction)
    db.commit()
    db.refresh(auction)
    return auction

def get_auction(db: Session, auction_id: int) -> Auction:
    auction = (
        db.query(Auction)
        .options(joinedload(Auction.seller), joinedload(Auction.bids))
        .filter(Auction.id == auction_id)
        .first()
    )
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")
    return auction

def list_auctions(
    db: Session,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    per_page: int = 12,
):
    q = db.query(Auction)
    if category_id:
        q = q.filter(Auction.category_id == category_id)
    if status:
        q = q.filter(Auction.status == status)
    if search:
        q = q.filter(Auction.title.ilike(f"%{search}%"))
    q = q.order_by(Auction.ends_at.asc())
    return paginate(q, page, per_page)

def activate_auction(db: Session, auction_id: int) -> Auction:
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")
    auction.status = "active"
    auction.seller_fee_paid = True
    db.commit()
    db.refresh(auction)
    return auction

def end_auction(db: Session, auction_id: int) -> Auction:
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")
    if auction.bids:
        top_bid = max(auction.bids, key=lambda b: b.amount)
        if auction.reserve_price and top_bid.amount < auction.reserve_price:
            auction.status = "ended"
        else:
            auction.winner_id = top_bid.bidder_id
            top_bid.is_winner = True
            auction.status = "ended"
    else:
        auction.status = "ended"
    db.commit()
    db.refresh(auction)
    return auction

def check_participant(db: Session, auction_id: int, user_id: int) -> bool:
    return db.query(AuctionParticipant).filter(
        AuctionParticipant.auction_id == auction_id,
        AuctionParticipant.user_id    == user_id,
        AuctionParticipant.fee_paid   == True,
    ).first() is not None
