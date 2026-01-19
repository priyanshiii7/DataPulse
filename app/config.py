from pydantic_settings import BaseSettings
from functools import lru_cache

from pydantic_settings import BaseSettings
from datetime import datetime
import pytz

class Settings(BaseSettings):
    APP_NAME: str = "DataPulse"
    DEBUG: bool = False
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    HEALTH_CHECK_INTERVAL: int = 60
    HEALTH_CHECK_TIMEOUT: int = 10
    MAX_CONCURRENT_CHECKS: int = 50
    CACHE_TTL_SECONDS: int = 300
    SLACK_WEBHOOK_URL: str = ""
    ALERT_EMAIL: str = ""
    
    # NEW: Add timezone setting
    TIMEZONE: str = "Asia/Kolkata"  # Indian Standard Time
    
    class Config:
        env_file = ".env"

settings = Settings()

# Helper function to get current time in IST
def get_current_time():
    """Get current time in configured timezone"""
    tz = pytz.timezone(settings.TIMEZONE)
    return datetime.now(tz)

def utc_to_local(utc_dt):
    """Convert UTC datetime to local timezone"""
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    tz = pytz.timezone(settings.TIMEZONE)
    return utc_dt.astimezone(tz)

@lru_cache()
def get_settings() -> Settings:
    return Settings()
