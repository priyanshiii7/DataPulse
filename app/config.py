from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App Config
    APP_NAME: str = "DataPulse"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:////data/datapulse.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Health Check Settings
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    HEALTH_CHECK_TIMEOUT: int = 10   # seconds
    MAX_CONCURRENT_CHECKS: int = 50
    
    # Alerts
    SLACK_WEBHOOK_URL: str = ""
    ALERT_EMAIL: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # Cache TTL
    CACHE_TTL_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
