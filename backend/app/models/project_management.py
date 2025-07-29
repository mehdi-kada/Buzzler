from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Boolean, Enum, Text, Index, ForeignKey
from sqlalchemy.sql import func
import enum
from backend.app.models.user import Base     

class ProjectStatus(enum.Enum):
    DRAFT = "draft"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """
        table to group related videos and posts , optimized for user filtering
    """
    __tablename__ = "project"

    #PK
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    #FK to user 
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)

    # project details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, index=True)
    settings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), )
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now())

    # relationships
    user = relationship("User", back_populates="projects")
    videos = relationship("Video", back_populates="projects", cascade=("all, delete-orphan"))

    # index for efficient querying (user and status of the proejct)
    __table_args__ = (
        Index("idx_project_user_status", "user_id", "status"),
    )