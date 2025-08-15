from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost/"

    class Config:
        env_file = ".env"

settings = Settings()