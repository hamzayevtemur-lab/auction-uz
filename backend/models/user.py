from sqlalchemy import Column, Integer, String, Boolean, Numeric, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, index=True)
    full_name   = Column(String(100), nullable=False)
    email       = Column(String(150), unique=True, nullable=False, index=True)
    phone       = Column(String(20),  unique=True, nullable=False)
    password    = Column(String(255), nullable=False)
    role        = Column(Enum("buyer", "seller", "admin"), default="buyer")
    balance     = Column(Numeric(15, 2), default=0.00)   # escrow hisobi
    is_verified = Column(Boolean, default=False)
    is_active   = Column(Boolean, default=True)
    avatar_url  = Column(String(255), nullable=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, onupdate=func.now())

    # Relationships
    auctions     = relationship("Auction", back_populates="seller", foreign_keys="Auction.seller_id")
    bids         = relationship("Bid",     back_populates="bidder")
    payments     = relationship("Payment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
