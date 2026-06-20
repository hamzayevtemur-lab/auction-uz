"""
Background task that automatically closes auctions whose ends_at has
passed. Runs on a simple asyncio loop (no extra dependency like Celery
needed for this scale) every CHECK_INTERVAL_SECONDS.

For each auction still marked "active" with ends_at in the past:
  - If there is at least one bid -> status = "sold", winner_id = highest bidder
  - If there are no bids at all   -> status = "ended", winner_id stays None

A Notification row is created for the winner ("winner" type) so the
dashboard can show a "you won, pay now" banner — this was the agreed
mechanism instead of a popup/email, since the user only wanted it
surfaced inside the dashboard.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models.auction import Auction
from .models.bid import Bid
from .models.payment import Notification

logger = logging.getLogger("auction_closer")

CHECK_INTERVAL_SECONDS = 60  # run once a minute


def _close_expired_auctions(db: Session) -> int:
    """Runs one pass. Returns how many auctions were closed (for logging)."""
    now = datetime.now(timezone.utc)

    expired = (
        db.query(Auction)
        .filter(Auction.status == "active", Auction.ends_at <= now)
        .all()
    )

    closed_count = 0
    for auction in expired:
        top_bid = (
            db.query(Bid)
            .filter(Bid.auction_id == auction.id)
            .order_by(Bid.amount.desc())
            .first()
        )

        if top_bid:
            auction.status = "sold"
            auction.winner_id = top_bid.bidder_id

            notif = Notification(
                user_id=top_bid.bidder_id,
                type="winner",
                title="🏆 Tabriklaymiz, siz g'olib bo'ldingiz!",
                message=(
                    f"\"{auction.title}\" auktsionida g'olib bo'ldingiz. "
                    f"Buyumni olish uchun escrow to'lovini amalga oshiring."
                ),
                is_read=False,
            )
            db.add(notif)

            # Let the seller know too, separately, so they're not left
            # wondering why nothing happened.
            seller_notif = Notification(
                user_id=auction.seller_id,
                type="auction_end",
                title="✅ Auktsioningiz sotildi",
                message=f"\"{auction.title}\" auktsioni yakunlandi va g'olib aniqlandi.",
                is_read=False,
            )
            db.add(seller_notif)
        else:
            auction.status = "ended"
            auction.winner_id = None

            seller_notif = Notification(
                user_id=auction.seller_id,
                type="auction_end",
                title="⏱️ Auktsioningiz tugadi",
                message=f"\"{auction.title}\" auktsioniga hech kim taklif bermadi.",
                is_read=False,
            )
            db.add(seller_notif)

        closed_count += 1

    if closed_count:
        db.commit()

    return closed_count


async def run_auction_closer_loop():
    """
    Fire-and-forget background loop. Started once at app startup via
    main.py's lifespan handler with asyncio.create_task(...).
    """
    logger.info("Auction auto-closer started (interval=%ss)", CHECK_INTERVAL_SECONDS)
    while True:
        try:
            db = SessionLocal()
            try:
                closed = _close_expired_auctions(db)
                if closed:
                    logger.info("Auto-closed %d expired auction(s)", closed)
            finally:
                db.close()
        except Exception:
            # Never let one bad pass kill the whole background loop.
            logger.exception("Error while closing expired auctions")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)