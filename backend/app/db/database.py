
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database.log'),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL env var is not set. Set it before starting the app.")
    raise RuntimeError("DATABASE_URL env var is required")

logger.info(f"connecting to database : {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else 'local DB'}")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout =30,
    pool_recycle=3600,      
    echo=False,
    pool_reset_on_return='commit'
)

AsyncSessionLocal = async_sessionmaker(
    bind= engine,
    class_= AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

sync_engine = create_engine(
    DATABASE_URL.replace("asyncpg", "psycopg"),
    pool_size=20,
    max_overflow=30,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
