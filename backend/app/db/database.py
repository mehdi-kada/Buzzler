from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('database.log'),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)

logger = logging.getLogger(__name__)

logger.info(f"connecting to database : {DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "local DB"}")

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_timeout =30,
    pool_recycle=3600,      
    echo=False   
    pool_reset_on_return='commit'
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
