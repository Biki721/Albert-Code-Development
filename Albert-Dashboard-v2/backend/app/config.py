"""
Configuration settings for Albert Dashboard Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Albert Automation Dashboard"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_EMAIL_DOMAIN: str = "hpe.com"
    SHARED_LOGIN_PASSWORD: str = "Admin@123"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    CONFIG_DIR: Path = BASE_DIR / "config"
    MODULES_DIR: Path = BASE_DIR.parent / "UAT"  # Original automation modules
    REPORTS_DIR: Path = MODULES_DIR / "Reports"
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./albert_dashboard.db"
    
    # Users file
    USERS_FILE: Path = CONFIG_DIR / "users.json"
    ACCOUNTS_FILE: Path = CONFIG_DIR / "accounts.json"
    
    # Session lock settings
    SESSION_LOCK_TIMEOUT: int = 1800  # 30 minutes in seconds
    SESSION_CHECK_INTERVAL: int = 60   # Check every minute
    
    # Scheduler
    SCHEDULER_TIMEZONE: str = "Asia/Kolkata"
    
    # Rate limiting
    RATE_LIMIT_LOGIN: int = 5  # Max login attempts per minute
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
