from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine  
from logging.config import fileConfig
import os
from dotenv import load_dotenv

load_dotenv()

from app.models.user import User
from app.models.project import Project
from app.models.video import Video
from app.models.clip import Clip
from app.models.social_account import SocialAccount
from app.models.post import Post
from app.models.ai_analytics import AIInsight
from app.models.analytics_data import AnalyticsData
from app.models.content_template import ContentTemplate
from app.models.file_storage import FileStorage
from app.models.audit_logs import AuditLog
from app.db.database import Base

config = context.config
fileConfig(config.config_file_name)

# Set the sqlalchemy.url from environment variable
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        pool_pre_ping=True
    )
    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata
            )
        )
        async with context.begin_transaction():
            await connection.run_sync(lambda sync_conn : context.run_migrations() )

    await connectable.dispose()

if context.is_offline_mode():
  run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
    
      