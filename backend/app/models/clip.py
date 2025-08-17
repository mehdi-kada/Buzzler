from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Enum as SAEnum, Text, ForeignKey, Index, Float, Date, func

from app.models.enums import ClipFormat, ClipStatus
from app.db.database import Base

class Clip(Base):
    """
        clips generated from videos , optimized for batch processing
    """
    __tablename__ = 'clip'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    video_id: Mapped[int] = mapped_column(Integer, ForeignKey('video.id'), nullable=False, index=True)

    # clip timing and format
    start_time: Mapped[int] = mapped_column(Integer, nullable=False)
    end_time: Mapped[int] = mapped_column(Integer, nullable=False)
    format: Mapped[ClipFormat] = mapped_column(SAEnum(ClipFormat), nullable=False)

    # file storage
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # AI generated metadata
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript: Mapped[Optional[list[dict]]] = mapped_column(JSON, nullable=True)
    ai_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    status: Mapped[ClipStatus] = mapped_column(SAEnum(ClipStatus), default=ClipStatus.PENDING, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    video: Mapped["Video"] = relationship("Video", back_populates="clips")
    posts: Mapped[list["Post"]] = relationship("Post", back_populates="clip")

    __table_args__ = (
        Index('idx_clip_video_status', 'video_id', 'status'),
        Index('idx_clip_score_format', 'ai_score', 'format'),
    )

if TYPE_CHECKING:
    from app.models.video import Video
    from app.models.post import Post
