from sqlalchemy import Column, Integer, String, Numeric, Enum, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Payment(Base):
    __tablename__ = "payments"

    id             = Column(Integer, primary_key=True, index=True)
    user_id        = Column(Integer, ForeignKey("users.id"),    nullable=False, index=True)
    auction_id     = Column(Integer, ForeignKey("auctions.id"), nullable=True)
    type           = Column(
        Enum("seller_fee", "participation_fee", "escrow", "payout", "refund"),
        nullable=False
    )
    amount         = Column(Numeric(15, 2), nullable=False)
    status         = Column(
        Enum("pending", "completed", "failed", "refunded"),
        default="pending"
    )
    method         = Column(
        Enum("payme", "click", "uzcard", "balance"),
        default="payme"
    )
    transaction_id = Column(String(255), nullable=True)  # Payme/Click ID
    description    = Column(String(255), nullable=True)
    created_at     = Column(DateTime, server_default=func.now())

    user    = relationship("User",    back_populates="payments")
    auction = relationship("Auction", back_populates="payments")

class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type       = Column(Enum("outbid", "winner", "payment", "auction_start", "auction_end"), nullable=False)
    title      = Column(String(200), nullable=False)
    message    = Column(String(500), nullable=True)
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications")
