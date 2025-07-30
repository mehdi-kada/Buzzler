# file_storage.py - Track all uploaded files
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, Boolean, Enum, Index, func
import enum

from backend.app.models.user import Base


class EntityType(enum.Enum):
    VIDEO = "video"
    CLIP = "clip"
    USER_AVATAR = "user_avatar"
    POST = "post"
    TRANSCRIPT = "transcript"


class FileType(enum.Enum):
    VIDEO = "video"
    THUMBNAIL = "thumbnail"
    AUDIO = "audio"
    TRANSCRIPT = "transcript"
    EXPORT = "export"

class FileStorage(Base):

    __tablename__ = 'file_storage'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[FileType] = mapped_column(Enum(FileType), nullable=False, index=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    file_size: Mapped[int] = mapped_column(Integer, nullable=False)            
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False)   
    storage_bucket: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    entity_type: Mapped[EntityType] = mapped_column(Enum(EntityType), nullable=False, index=True)  
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    is_temporary: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    expires_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())


    __table_args__ = (
        Index('idx_file_entity', 'entity_type', 'entity_id'),
        Index('idx_file_cleanup', 'is_temporary', 'expires_at'),
        Index('idx_file_storage_stats', 'storage_provider', 'file_type', 'created_at'),
    )