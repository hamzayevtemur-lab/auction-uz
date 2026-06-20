from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from .database import Base, engine
from .routers import auth, users, auctions, bids, payments, admin, upload

import asyncio
from contextlib import asynccontextmanager
from .auction_closer import run_auction_closer_loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    # Start the background loop that auto-closes expired auctions.
    # create_task schedules it without blocking startup; it runs
    # forever in the background until the app shuts down.
    closer_task = asyncio.create_task(run_auction_closer_loop())

    yield

    # Clean shutdown — cancel the loop so it doesn't error out when
    # the event loop closes.
    closer_task.cancel()
    try:
        await closer_task
    except asyncio.CancelledError:
        pass

app = FastAPI(title="Savdo.uz API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploaded images
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(auth.router,     prefix="/api")
app.include_router(users.router,    prefix="/api")
app.include_router(auctions.router, prefix="/api")
app.include_router(bids.router,     prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(admin.router,    prefix="/api")
app.include_router(upload.router,   prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}