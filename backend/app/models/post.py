from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Enum as SAEnum, Text, ForeignKey, Index, Float, Date, UniqueConstraint, func

from app.db.database import Base
from app.models.enums import PostStatus

class Post(Base):
    """
    social media posts with scheduling and analytics
    """
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    clip_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('clips.id'), nullable=True, index=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey('social_accounts.id'), nullable=False, index=True)

    # content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)
    media_urls: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)

    # publishing
    status: Mapped[PostStatus] = mapped_column(SAEnum(PostStatus), default=PostStatus.DRAFT, index=True)
    scheduled_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    published_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    platform_post_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)    # Platform's post ID
    platform_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)       # Direct link to post

    # error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # performance tracking (updated by analytics jobs)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    shares: Mapped[int] = mapped_column(Integer, default=0)
    comments: Mapped[int] = mapped_column(Integer, default=0)
    engagement_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)           # Calculated engagement %

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_analytics_update: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)

    clip: Mapped["Clip"] = relationship("Clip", back_populates="posts")
    account: Mapped["SocialAccount"] = relationship("SocialAccount", back_populates="posts")

    __table_args__ = (
        Index('idx_post_scheduled', 'status', 'scheduled_at'),
        Index('idx_post_account_status', 'account_id', 'status'),
        Index('idx_post_performance', 'published_at', 'engagement_rate'),
    )

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.clip import Clip
    from app.models.social_account import SocialAccount
