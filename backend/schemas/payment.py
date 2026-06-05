from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    auction_id: Optional[int] = None
    type:       str
    amount:     Decimal
    method:     str = "payme"

class PaymentOut(BaseModel):
    id:             int
    user_id:        int
    auction_id:     Optional[int]
    type:           str
    amount:         Decimal
    status:         str
    method:         str
    transaction_id: Optional[str]
    description:    Optional[str]
    created_at:     datetime

    class Config:
        from_attributes = True

class PaymentInitiate(BaseModel):
    auction_id: int
    method:     str = "payme"   # payme | click | uzcard
