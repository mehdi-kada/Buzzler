from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Boolean, Enum, Text, Index, ForeignKey
from sqlalchemy.sql import func
import enum
from backend.app.db.database import Base, User
from backend.app.models.video import Video     

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

    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)

    # project details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, index=True)
    settings: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)


    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), )
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now())


    user : Mapped["User"] = relationship("User", back_populates="projects")
    videos : Mapped[list["Video"]] = relationship("Video", back_populates="project", cascade=("all, delete-orphan"))

 
    __table_args__ = (
        Index("idx_project_user_status", "user_id", "status"),
    )