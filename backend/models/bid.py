from sqlalchemy import Column, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Bid(Base):
    __tablename__ = "bids"

    id         = Column(Integer, primary_key=True, index=True)
    auction_id = Column(Integer, ForeignKey("auctions.id"), nullable=False, index=True)
    bidder_id  = Column(Integer, ForeignKey("users.id"),    nullable=False, index=True)
    amount     = Column(Numeric(15, 2), nullable=False)
    is_winner  = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    auction = relationship("Auction", back_populates="bids")
    bidder  = relationship("User",    back_populates="bids")
