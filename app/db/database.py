from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.settings import settings

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine, 
    class_=AsyncSession,
    expire_on_commit=False  # Prevents lazy loading issues after commit
)

Base = declarative_base()

# Create a sync engine for alembic migrations
sync_engine = engine.sync_engine

async def get_db():
    """
    Dependency to get a database session.
    
    This function provides a database session that is properly managed
    with async context management. The session is automatically closed
    when the request is completed.
    """
    async with SessionLocal() as session:
        yield session