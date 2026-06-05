from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from .database import engine, Base
from .routers import auth, users, auctions, bids, payments, admin

# ── Barcha jadvallarni yaratish ───────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: jadvallarni yaratish (agar mavjud bo'lmasa)
    Base.metadata.create_all(bind=engine)
    print("✅ Ma'lumotlar bazasi jadvallari tayyor")
    yield
    # Shutdown
    print("🛑 Server to'xtatildi")

app = FastAPI(
    title="Savdo.uz API",
    description="O'zbekiston auktsion platformasi backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ── CORS — Frontend bilan aloqa ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",   # Live Server
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://localhost:8080",
        "*",                       # Development uchun; productiondan olib tashlang
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routerlarni ulash ────────────────────────────────────────────────────
API = "/api"
app.include_router(auth.router,     prefix=API)
app.include_router(users.router,    prefix=API)
app.include_router(auctions.router, prefix=API)
app.include_router(bids.router,     prefix=API)
app.include_router(payments.router, prefix=API)
app.include_router(admin.router,    prefix=API)

# ── Health check ─────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Savdo.uz API ishlayapti 🚀"}

# ── Ishga tushirish uchun (to'g'ridan python main.py bilan) ──────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
