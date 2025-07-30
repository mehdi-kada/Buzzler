from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum, Text, ForeignKey, Index, func
import enum

from backend.app.models.post import Post
from backend.app.models.user import Base
from backend.app.models.video import Video



class ClipFormat(enum.Enum):
    VERTICAL_9_16 = "9:16"      # TikTok, Instagram Reels
    SQUARE_1_1 = "1:1"          # Instagram Square
    HORIZONTAL_16_9 = "16:9"    # YouTube, LinkedIn

class ClipStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Clip(Base):
    """
        clips generated from videos , optimized for batch processing 
    """
    __tablename__ = 'clips'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    video_id: Mapped[int] = mapped_column(ForeignKey('video.id'), nullable=False, index=True)

    # clip timing and format
    start_time: Mapped[int] = mapped_column(Integer, nullable=False)       
    end_time: Mapped[int] = mapped_column(Integer, nullable=False)          
    format: Mapped[ClipFormat] = mapped_column(Enum(ClipFormat), nullable=False)

    # file storage
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # AI generated metadata
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript: Mapped[Optional[list[dict]]] = mapped_column(Text, nullable=True)
    ai_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)           
    ai_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)         


    status: Mapped[ClipStatus] = mapped_column(Enum(ClipStatus), default=ClipStatus.PENDING, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    video : Mapped["Video"] = relationship("Video", back_populates="clips")
    posts : Mapped[list["Post"]] = relationship("Post", back_populates="clip")
    

    __table_args__ = (
        Index('idx_clip_video_status', 'video_id', 'status'),
        Index('idx_clip_score_format', 'ai_score', 'format'),
    )