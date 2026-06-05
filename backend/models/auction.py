from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Auction(Base):
    __tablename__ = "auctions"

    id              = Column(Integer, primary_key=True, index=True)
    seller_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id     = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title           = Column(String(200), nullable=False)
    description     = Column(Text, nullable=True)
    item_condition  = Column(String(100), nullable=True)   # renamed from 'condition'
    location        = Column(String(100), nullable=True)
    delivery        = Column(String(100), nullable=True)
    images          = Column(JSON, default=list)
    starting_price  = Column(Numeric(15, 2), nullable=False)
    reserve_price   = Column(Numeric(15, 2), nullable=True)
    min_step        = Column(Numeric(15, 2), default=10000)
    current_bid     = Column(Numeric(15, 2), nullable=True)
    winner_id       = Column(Integer, ForeignKey("users.id"), nullable=True)
    status          = Column(
        Enum("draft", "pending", "active", "ended", "cancelled", "sold"),
        default="draft", index=True
    )
    starts_at         = Column(DateTime, nullable=False)
    ends_at           = Column(DateTime, nullable=False, index=True)
    seller_fee_paid   = Column(Boolean, default=False)
    seller_fee_amount = Column(Numeric(15, 2), nullable=True)
    created_at        = Column(DateTime, server_default=func.now())

    # Relationships
    seller       = relationship("User", back_populates="auctions", foreign_keys=[seller_id])
    winner       = relationship("User", foreign_keys=[winner_id])
    category     = relationship("Category")
    bids         = relationship("Bid", back_populates="auction", order_by="Bid.amount.desc()")
    payments     = relationship("Payment", back_populates="auction")
    participants = relationship("AuctionParticipant", back_populates="auction")

class AuctionParticipant(Base):
    __tablename__ = "auction_participants"

    id         = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"), nullable=False)
    user_id    = Column(Integer, ForeignKey("users.id"),    nullable=False)
    fee_paid   = Column(Boolean, default=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    joined_at  = Column(DateTime, server_default=func.now())

    auction = relationship("Auction", back_populates="participants")
    user    = relationship("User")
