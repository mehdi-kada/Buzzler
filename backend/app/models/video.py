# videos.py - Core video storage and processing
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Enum, Text, ForeignKey, Index, Float, func
import enum

from backend.app.models.clips import Clip
from backend.app.models.project_management import Project
from backend.app.models.user import Base


# Enums for data consictency 
class VideoSource(enum.Enum):
    UPLOAD = "upload"
    URL_IMPORT  = "url_import"

class VideoStatus(enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    READY = "ready"
    FAILED = "failed"

class Video(Base):
    """
        table to store video metadata (not the file itself)
    """
    __tablename__ = "video"

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign Key to link to project (one to many)
    project_id : Mapped[int] = mapped_column(ForeignKey("project.id"), nullable=False, index=True)

    # video source 
    source: Mapped[VideoSource] = mapped_column(Enum(VideoSource), nullable=False)
    original_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)      
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)         
    storage_provider: Mapped[str] = mapped_column(String(50), default="supabase")  

    # video metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)   
    resolution: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)     
    fps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)                
    codec: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)          
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # status of the video, to save the progress 
    status: Mapped[VideoStatus] = mapped_column(Enum(VideoStatus), default=VideoStatus.UPLOADING, index=True)
    processing_progress: Mapped[int] = mapped_column(Integer, default=0)    # 0-100 percentage
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # AI generated metadata for the video (transcript to be split later for each clip/post,)
    transcript_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)       # ai transcription
    analysis_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)         # conetnt Analysis

    # timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    processed_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # RelationShips
    project : Mapped[list["Project"]] = relationship("Project", back_populates="videos")
    clips : Mapped[list["Clip"]] = relationship("Clip", back_populates="video", cascade="all, delete-orphan")

    # indexes for performance 
    __table_args__ = (
        Index("indx_vid_prj_status", "project_id", "status"),
        Index("idx_crt_at", "created_at")
    )