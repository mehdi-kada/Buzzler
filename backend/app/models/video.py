from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Float, Text, Index, func, Enum as SAEnum
from app.models.enums import VideoStatus





class Video(Base):
    __tablename__ = "videos"

    # Primary fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_extension: Mapped[Optional[str]] = mapped_column(String(10))

    # Azure storage
    azure_file_path: Mapped[Optional[str]] = mapped_column(String(512), unique=True)  # Relative path in Azure container
    azure_video_url: Mapped[Optional[str]] = mapped_column(Text)                       # Final public/private URL of the video
    azure_audio_url: Mapped[Optional[str]] = mapped_column(Text)                       # URL for the extracted audio

    # Upload process
    upload_url: Mapped[Optional[str]] = mapped_column(Text)                      # The pre-signed URL given to the client
    upload_expires_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Processing status
    status: Mapped[VideoStatus] = mapped_column(SAEnum(VideoStatus), default=VideoStatus.PENDING_UPLOAD, index=True)

    # Video metadata (filled during processing)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    resolution_width: Mapped[Optional[int]] = mapped_column(Integer)
    resolution_height: Mapped[Optional[int]] = mapped_column(Integer)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    upload_completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    processing_completed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)

    # Relationships
    clips: Mapped[list["Clip"]] = relationship("Clip", back_populates="video", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_videos_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"


if TYPE_CHECKING:
    from app.models.clip import Clip
