"""
Configuration settings for the cybersecurity risk framework.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cybersec_risk.db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    VIRUSTOTAL_API_KEY: str = os.getenv("VIRUSTOTAL_API_KEY", "")
    SHODAN_API_KEY: str = os.getenv("SHODAN_API_KEY", "")
    OTX_API_KEY: str = os.getenv("OTX_API_KEY", "")
    IBM_XFORCE_API_KEY: str = os.getenv("IBM_XFORCE_API_KEY", "")
    IBM_XFORCE_API_PASSWORD: str = os.getenv("IBM_XFORCE_API_PASSWORD", "")
    
    # Model settings
    MODEL_PATH: str = "models/risk_model.pkl"
    THRESHOLD: float = 0.7
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Elasticsearch
    ELASTICSEARCH_URL: str = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "app.log")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This will ignore extra fields in the .env file

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 