from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout =30,
    pool_recycle=3600,      
    echo=False   
)

AsyncSessionLocal = async_sessionmaker(
    bind= engine,
    class_= AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
