from pydantic_settings import BaseSettings
from shared_libs import SharedSettings
from typing import Optional
from pydantic import field_validator, ValidationInfo
import os

class Settings(SharedSettings):
    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    
    # Auth service settings
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    
    # JWT settings
    SECRET_KEY: str = "your-secret-key-here"  # This should be overridden in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Message queue settings
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # Validation for secret key
    @field_validator('SECRET_KEY')
    def secret_key_must_not_be_default(cls, v: str, info: ValidationInfo) -> str:
        if v == "your-secret-key-here":
            # In production, this should be set via environment variable
            if os.getenv('ENVIRONMENT') == 'production':
                raise ValueError('SECRET_KEY must be set in production environment')
        return v
    
    # Validation for algorithm
    @field_validator('ALGORITHM')
    def algorithm_must_be_valid(cls, v: str) -> str:
        valid_algorithms = ['HS256', 'HS384', 'HS512']
        if v not in valid_algorithms:
            raise ValueError(f'ALGORITHM must be one of {valid_algorithms}')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()