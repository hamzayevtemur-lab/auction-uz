from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    f"?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # ulanish uzilganda avtomatik qayta ulanish
    pool_recycle=3600,        # 1 soatda bir ulanishni yangilash
    echo=False,               # SQL so'rovlarini loglash (debug uchun True)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI dependency — har so'rov uchun DB sessiya"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
