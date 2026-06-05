from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "auction_uz"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 soat

    # Platform
    PLATFORM_COMMISSION_SELLER: float = 1.0   # 1% garov
    PLATFORM_COMMISSION_FINAL: float  = 3.0   # 3% yakuniy komissiya
    PARTICIPATION_FEE: int = 50000            # 50,000 so'm

    # Payme
    PAYME_MERCHANT_ID: str = ""
    PAYME_SECRET_KEY: str  = ""

    # Click
    CLICK_MERCHANT_ID: str = ""
    CLICK_SECRET_KEY: str  = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
