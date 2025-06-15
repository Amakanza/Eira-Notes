import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    API_URL: str = Field("http://localhost:8000", env="API_URL")
    
    # App Configuration
    APP_NAME: str = "Eira Desktop"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(False, env="DEBUG")
    
    # Database Configuration
    DB_PATH: str = Field(
        os.path.join(os.path.expanduser("~"), ".eira", "eira.db"),
        env="DB_PATH"
    )
    
    # Sync Configuration
    AUTO_SYNC_INTERVAL: int = Field(60, env="AUTO_SYNC_INTERVAL")  # seconds
    SYNC_ON_STARTUP: bool = Field(True, env="SYNC_ON_STARTUP")
    SYNC_ON_SHUTDOWN: bool = Field(True, env="SYNC_ON_SHUTDOWN")
    
    # UI Configuration
    THEME: str = Field("system", env="THEME")  # system, light, dark
    ACCENT_COLOR: str = Field("#1a73e8", env="ACCENT_COLOR")
    FONT_SIZE: int = Field(12, env="FONT_SIZE")
    
    # Logging Configuration
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_DIR: str = Field(
        os.path.join(os.path.expanduser("~"), ".eira", "logs"),
        env="LOG_DIR"
    )
    
    # Cache Configuration
    CACHE_DIR: str = Field(
        os.path.join(os.path.expanduser("~"), ".eira", "cache"),
        env="CACHE_DIR"
    )
    CACHE_EXPIRY: int = Field(86400, env="CACHE_EXPIRY")  # 24 hours in seconds
    
    # Network Configuration
    CONNECTION_TIMEOUT: int = Field(10, env="CONNECTION_TIMEOUT")  # seconds
    RETRY_ATTEMPTS: int = Field(3, env="RETRY_ATTEMPTS")
    RETRY_BACKOFF: float = Field(1.5, env="RETRY_BACKOFF")
    
    # Security Configuration
    TOKEN_STORAGE: str = Field("keyring", env="TOKEN_STORAGE")  # keyring, file, memory
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
Path(os.path.dirname(settings.DB_PATH)).mkdir(parents=True, exist_ok=True)
Path(settings.LOG_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.CACHE_DIR).mkdir(parents=True, exist_ok=True)