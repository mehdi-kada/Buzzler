from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Float, Text, Index, func, ForeignKey, Enum as SAEnum
from app.models.enums import VideoSource, VideoStatus

class Video(Base):
    __tablename__ = "video"

    # Primary fields
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, index=True)

    source : Mapped[VideoSource] = mapped_column(SAEnum(VideoSource, values_callable=lambda obj: [e.value for e in obj]), nullable=False)

    # File information
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100))
    file_extension: Mapped[Optional[str]] = mapped_column(String(10))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)

    # Azure storage
    azure_file_path: Mapped[Optional[str]] = mapped_column(String(512), unique=True)  # Relative path in Azure container
    azure_video_url: Mapped[Optional[str]] = mapped_column(Text)                       # Final public/private URL of the video
    azure_audio_url: Mapped[Optional[str]] = mapped_column(Text)                       # URL for the extracted audio

    # Upload process
    upload_url: Mapped[Optional[str]] = mapped_column(Text)                      # The pre-signed URL given to the client
    upload_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Processing status
    status: Mapped[VideoStatus] = mapped_column(SAEnum(VideoStatus, values_callable=lambda obj: [e.value for e in obj]), default=VideoStatus.PENDING_UPLOAD, index=True)

    # Video metadata (filled during processing)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    resolution_width: Mapped[Optional[int]] = mapped_column(Integer)
    resolution_height: Mapped[Optional[int]] = mapped_column(Integer)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    upload_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    clips: Mapped[list["Clip"]] = relationship("Clip", back_populates="video", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_videos_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Video(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"


if TYPE_CHECKING:
    from app.models.clip import Clip
