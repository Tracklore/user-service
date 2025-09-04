from pydantic_settings import BaseSettings
from shared_libs import SharedSettings
from typing import Optional
from pydantic import field_validator, ValidationInfo
import os

class Settings(SharedSettings):
    # Database settings
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600  # 1 hour
    
    # Auth service settings
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    
    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Message queue settings
    RABBITMQ_URL: str
    
    # Validation for secret key
    @field_validator('SECRET_KEY')
    def secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('SECRET_KEY must not be empty')
        return v
    
    # Validation for database URL
    @field_validator('DATABASE_URL')
    def database_url_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('DATABASE_URL must not be empty')
        return v
    
    # Validation for database pool size
    @field_validator('DATABASE_POOL_SIZE')
    def database_pool_size_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('DATABASE_POOL_SIZE must be positive')
        return v
    
    # Validation for database max overflow
    @field_validator('DATABASE_MAX_OVERFLOW')
    def database_max_overflow_must_be_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError('DATABASE_MAX_OVERFLOW must be non-negative')
        return v
    
    # Validation for RabbitMQ URL
    @field_validator('RABBITMQ_URL')
    def rabbitmq_url_must_not_be_empty(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError('RABBITMQ_URL must not be empty')
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