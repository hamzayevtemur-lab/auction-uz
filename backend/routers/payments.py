from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User
from ..schemas.payment import PaymentInitiate, PaymentOut
from ..services.payment_service import (
    pay_seller_fee, pay_participation_fee,
    pay_escrow, get_my_payments
)
from typing import List

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/seller-fee/{auction_id}", response_model=PaymentOut, status_code=201)
def seller_fee(
    auction_id: int,
    data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sotuvchi 1% garov to'lovini amalga oshiradi"""
    return pay_seller_fee(db, auction_id, current_user, data.method)

@router.post("/participation/{auction_id}", response_model=PaymentOut, status_code=201)
def participation_fee(
    auction_id: int,
    data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xaridor auktsiyonga qo'shilish uchun to'laydi"""
    return pay_participation_fee(db, auction_id, current_user, data.method)

@router.post("/escrow/{auction_id}", response_model=PaymentOut, status_code=201)
def escrow_payment(
    auction_id: int,
    data: PaymentInitiate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """G'olib escrow orqali to'lovni amalga oshiradi"""
    return pay_escrow(db, auction_id, current_user, data.method)

@router.get("/my", response_model=List[PaymentOut])
def my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mening barcha to'lovlarim"""
    return get_my_payments(db, current_user.id)
