from datetime import datetime
import math

def calc_seller_fee(starting_price: float, percent: float = 1.0) -> int:
    """Sotuvchi garov to'lovini hisoblash (1%)"""
    return math.ceil(starting_price * percent / 100)

def calc_platform_commission(final_price: float, percent: float = 3.0) -> int:
    """Platforma komissiyasini hisoblash (3%)"""
    return math.ceil(final_price * percent / 100)

def format_uzs(amount: int) -> str:
    """UZS formatida narxni qaytarish"""
    return f"{amount:,} so'm".replace(",", " ")

def is_auction_active(ends_at: datetime) -> bool:
    return datetime.utcnow() < ends_at

def paginate(query, page: int, per_page: int):
    """SQLAlchemy query-ni sahifalash"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page),
    }
