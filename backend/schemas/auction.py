from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class AuctionCreate(BaseModel):
    category_id:    int
    title:          str
    images: Optional[List[str]] = []
    description:    Optional[str] = None
    item_condition: Optional[str] = None
    location:       Optional[str] = None
    delivery:       Optional[str] = None
    starting_price: Decimal
    reserve_price:  Optional[Decimal] = None
    min_step:       Decimal = Decimal("10000")
    starts_at:      datetime
    ends_at:        datetime

    @field_validator("title")
    def title_length(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Sarlavha kamida 10 ta belgi bo'lishi kerak")
        return v.strip()

    @field_validator("starting_price")
    def price_positive(cls, v):
        if v < 1000:
            raise ValueError("Boshlang'ich narx kamida 1 000 so'm bo'lishi kerak")
        return v

    @field_validator("ends_at")
    def ends_in_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError("Tugash vaqti kelajakda bo'lishi kerak")
        return v

class AuctionOut(BaseModel):
    id:             int
    seller_id:      int
    category_id:    int
    title:          str
    description:    Optional[str]
    item_condition: Optional[str]
    location:       Optional[str]
    delivery:       Optional[str]
    images:         Optional[List[str]]
    starting_price: Decimal
    reserve_price:  Optional[Decimal]
    min_step:       Decimal
    current_bid:    Optional[Decimal]
    winner_id:      Optional[int]
    status:         str
    starts_at:      datetime
    ends_at:        datetime
    seller_fee_paid: bool
    created_at:     datetime

    class Config:
        from_attributes = True
