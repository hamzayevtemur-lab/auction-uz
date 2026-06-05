from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from ..models.bid import Bid
from ..models.auction import Auction, AuctionParticipant
from ..models.payment import Notification
from ..models.user import User

def place_bid(db: Session, auction_id: int, amount: float, bidder: User) -> Bid:
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")

    # Auktsion faolmi?
    if auction.status != "active":
        raise HTTPException(status_code=400, detail="Auktsion faol emas")

    # Vaqt tugaganmi?
    if datetime.utcnow() > auction.ends_at:
        raise HTTPException(status_code=400, detail="Auktsion muddati tugagan")

    # Qatnashuvchimi?
    is_participant = db.query(AuctionParticipant).filter(
        AuctionParticipant.auction_id == auction_id,
        AuctionParticipant.user_id    == bidder.id,
        AuctionParticipant.fee_paid   == True,
    ).first()
    if not is_participant:
        raise HTTPException(
            status_code=400,
            detail="Taklif berish uchun avval ishtirok to'lovini to'lang"
        )

    # O'z auktsioniga taklif bera olmaydi
    if auction.seller_id == bidder.id:
        raise HTTPException(status_code=400, detail="O'z auktsioniga taklif bera olmaysiz")

    # Minimal taklif miqdori
    current  = float(auction.current_bid or auction.starting_price)
    min_next = current + float(auction.min_step)
    if amount < min_next:
        raise HTTPException(
            status_code=400,
            detail=f"Minimal taklif: {min_next:,.0f} so'm"
        )

    # Avvalgi eng yuqori bidder-ga xabar
    prev_top = db.query(Bid).filter(
        Bid.auction_id == auction_id
    ).order_by(Bid.amount.desc()).first()

    if prev_top and prev_top.bidder_id != bidder.id:
        notif = Notification(
            user_id=prev_top.bidder_id,
            type="outbid",
            title="Taklifingizdan o'tildi!",
            message=f"{auction.title} auktsionida yangi taklif: {amount:,.0f} so'm",
        )
        db.add(notif)

    # Yangi bid saqlash
    bid = Bid(auction_id=auction_id, bidder_id=bidder.id, amount=amount)
    db.add(bid)

    # Auktsion joriy narxini yangilash
    auction.current_bid = amount
    db.commit()
    db.refresh(bid)
    return bid

def get_auction_bids(db: Session, auction_id: int) -> list:
    return (
        db.query(Bid)
        .filter(Bid.auction_id == auction_id)
        .order_by(Bid.amount.desc())
        .all()
    )

def get_my_bids(db: Session, user_id: int) -> list:
    return (
        db.query(Bid)
        .filter(Bid.bidder_id == user_id)
        .order_by(Bid.created_at.desc())
        .all()
    )
