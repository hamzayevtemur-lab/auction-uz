from pydantic import BaseModel, field_validator
from datetime import datetime
from decimal import Decimal

class BidCreate(BaseModel):
    auction_id: int
    amount: Decimal

    @field_validator("amount")
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Taklif miqdori musbat bo'lishi kerak")
        return v

class BidOut(BaseModel):
    id:         int
    auction_id: int
    bidder_id:  int
    amount:     Decimal
    is_winner:  bool
    created_at: datetime

    class Config:
        from_attributes = True
