from app.models.enums import VideoStatus
from app.db.database import Base
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Enum, Text, Boolean, Index, Float, func


class Video(Base):
    """
    table to store video metadata (not the file itself)
    """
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
    azure_file_path: Mapped[Optional[str]] = mapped_column(String(512))  # Path in Azure blob storage
    azure_url: Mapped[Optional[str]] = mapped_column(Text)  # Full Azure blob URL
    azure_upload_completed: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # Temporary storage
    temp_video_path: Mapped[Optional[str]] = mapped_column(String(512))  # Local temp video path
    temp_audio_path: Mapped[Optional[str]] = mapped_column(String(512))  # Local temp audio path
    temp_created_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, default=func.now())
    temp_cleanup_scheduled: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    
    # Processing status
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus), default=VideoStatus.UPLOADING, index=True)
    upload_progress_percent: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    
    # Video metadata (filled during processing)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float)
    resolution_width: Mapped[Optional[int]] = mapped_column(Integer)
    resolution_height: Mapped[Optional[int]] = mapped_column(Integer)
    fps: Mapped[Optional[float]] = mapped_column(Float)
    video_codec: Mapped[Optional[str]] = mapped_column(String(50))
    audio_codec: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), index=True)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    azure_uploaded_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    temp_cleaned_at: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    
    # Relationship
    clips: Mapped[list["Clip"]] = relationship("Clip", back_populates="video", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_videos_status_created', 'status', 'created_at'),
        Index('idx_videos_temp_cleanup', 'temp_created_at', 'temp_cleanup_scheduled'),
        Index('idx_videos_user_created', 'user_id', 'created_at'),
    )


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.clip import Clip


    def __repr__(self):
        return f"<Video(id={self.id}, filename='{self.original_filename}', status='{self.status}')>"