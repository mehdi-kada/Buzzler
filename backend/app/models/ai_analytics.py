# analytics.py - Performance tracking and insights
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Integer, DateTime, Enum, Text, ForeignKey, Index, Float, Date, UniqueConstraint, func
import enum

from backend.app.models.post import Post
from backend.app.models.social_account import SocialAccount
from backend.app.db.database import Base

class InsightType(enum.Enum):
    BEST_POSTING_TIME = "best_posting_time"
    TRENDING_TOPICS = "trending_topics"
    VIRAL_PREDICTION = "viral_prediction"
    AUDIENCE_PREFERENCE = "audience_preference"
    CONTENT_OPTIMIZATION = "content_optimization"


class AIInsight(Base):
    """
    AI-generated insights and recommendations
    stores llms analysis for users
    """
    __tablename__ = 'ai_insights'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False, index=True)

    # insight details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)                   
    insight_type: Mapped[InsightType] = mapped_column(Enum(InsightType), nullable=False, index=True)  
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)    # this is for feedback     
    best_action: Mapped[str] = mapped_column(Text,nullable=True)

    # metadata
    data_period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    data_period_end: Mapped[Date] = mapped_column(Date, nullable=False)

    # user interaction (for user behavior analysis)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_feedback: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)       

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(),  onupdate=func.now())

    __table_args__ = (
        Index('idx_insights_user_type', 'user_id', 'insight_type'),
    )