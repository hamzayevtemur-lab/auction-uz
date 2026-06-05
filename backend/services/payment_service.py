from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models.payment import Payment, Notification
from ..models.auction import Auction, AuctionParticipant
from ..models.user import User
from ..utils.helpers import calc_seller_fee
from ..config import settings

# ── SOTUVCHI 1% GAROV TO'LOVI ────────────────────────────────────────────
def pay_seller_fee(db: Session, auction_id: int, seller: User, method: str) -> Payment:
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")
    if auction.seller_id != seller.id:
        raise HTTPException(status_code=403, detail="Bu sizning auktsioningiz emas")
    if auction.seller_fee_paid:
        raise HTTPException(status_code=400, detail="Garov to'lovi allaqachon amalga oshirilgan")

    fee = calc_seller_fee(float(auction.starting_price), settings.PLATFORM_COMMISSION_SELLER)

    # To'lov yozuvi
    payment = Payment(
        user_id=seller.id,
        auction_id=auction_id,
        type="seller_fee",
        amount=fee,
        method=method,
        status="completed",            # Real integratsiyada "pending" bo'ladi
        description=f"Garov to'lovi: {auction.title}",
    )
    db.add(payment)

    # Auktsionni faollashtirish
    auction.seller_fee_paid   = True
    auction.seller_fee_amount = fee
    auction.status            = "active"

    db.commit()
    db.refresh(payment)
    return payment

# ── XARIDOR ISHTIROK TO'LOVI ─────────────────────────────────────────────
def pay_participation_fee(db: Session, auction_id: int, buyer: User, method: str) -> Payment:
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")
    if auction.status != "active":
        raise HTTPException(status_code=400, detail="Auktsion faol emas")
    if auction.seller_id == buyer.id:
        raise HTTPException(status_code=400, detail="O'z auktsioniga qatnasha olmaysiz")

    # Allaqachon to'laganmi?
    existing = db.query(AuctionParticipant).filter(
        AuctionParticipant.auction_id == auction_id,
        AuctionParticipant.user_id    == buyer.id,
        AuctionParticipant.fee_paid   == True,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Siz allaqachon auktsiyonga qo'shilgansiz")

    fee = settings.PARTICIPATION_FEE

    # To'lov yozuvi
    payment = Payment(
        user_id=buyer.id,
        auction_id=auction_id,
        type="participation_fee",
        amount=fee,
        method=method,
        status="completed",
        description=f"Ishtirok to'lovi: {auction.title}",
    )
    db.add(payment)
    db.flush()  # payment.id ni olish uchun

    # Qatnashuvchi sifatida qo'shish
    participant = AuctionParticipant(
        auction_id=auction_id,
        user_id=buyer.id,
        fee_paid=True,
        payment_id=payment.id,
    )
    db.add(participant)
    db.commit()
    db.refresh(payment)
    return payment

# ── G'OLIBGA ESCROW TO'LOV ───────────────────────────────────────────────
def pay_escrow(db: Session, auction_id: int, winner: User, method: str) -> Payment:
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auktsion topilmadi")
    if auction.winner_id != winner.id:
        raise HTTPException(status_code=403, detail="Siz bu auktsionning g'olibi emassiz")
    if auction.status != "ended":
        raise HTTPException(status_code=400, detail="Auktsion hali tugamagan")

    amount = float(auction.current_bid or auction.starting_price)
    payment = Payment(
        user_id=winner.id,
        auction_id=auction_id,
        type="escrow",
        amount=amount,
        method=method,
        status="completed",
        description=f"G'oliblik to'lovi: {auction.title}",
    )
    db.add(payment)

    # Sotuvchiga xabar
    notif = Notification(
        user_id=auction.seller_id,
        type="payment",
        title="To'lov amalga oshirildi!",
        message=f"{auction.title} uchun g'olib to'lovni amalga oshirdi. Buyumni jo'nating.",
    )
    db.add(notif)
    auction.status = "sold"
    db.commit()
    db.refresh(payment)
    return payment

def get_my_payments(db: Session, user_id: int) -> list:
    return (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )
