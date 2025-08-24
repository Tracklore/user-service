from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import settings

engine = create_async_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()

# Create a sync engine for alembic migrations
sync_engine = engine.sync_engine

async def get_db():
    async with SessionLocal() as session:
        yield session