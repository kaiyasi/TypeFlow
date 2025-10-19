from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg://typeflow:password@localhost:5432/typeflow"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    OAUTH_REDIRECT_URI: str = "https://typeflow.serelix.xyz/auth/callback"
    
    # Rate Limiting
    RATE_LIMIT_PER_MIN: int = 120
    
    # Admin
    ADMIN_EMAIL: str = "admin@typeflow.local"
    ADMIN_PASSWORD: str = "admin123"
    
    # Application
    DEBUG: bool = False
    LOG_LEVEL: str = "info"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://typeflow.serelix.xyz",
        "http://localhost:5173",
        "http://localhost:3000"
    ]
    
    # Guest settings
    GUEST_RANKING_TTL: int = 1800  # 30 minutes in seconds
    
    # Progress rate calculation
    PROGRESS_SAMPLE_SIZE: int = 10
    MIN_PROGRESS_SAMPLES: int = 3
    
    # Practice modes
    PRACTICE_DURATIONS: List[int] = [60, 180, 300, 600]  # 1, 3, 5, 10 minutes
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()