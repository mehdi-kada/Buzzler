from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, Integer, DateTime, Enum as SAEnum, Text, ForeignKey, Index, Float, Date, func
from app.models.enums import InsightType
from app.db.database import Base


class AIInsight(Base):
    """
    AI-generated insights and recommendations
    stores llms analysis for users
    """
    __tablename__ = 'ai_insights'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False, index=True)

    # insight details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    insight_type: Mapped[InsightType] = mapped_column(SAEnum(InsightType), nullable=False, index=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)    # this is for feedback
    best_action: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # metadata
    data_period_start: Mapped[Date] = mapped_column(Date, nullable=False)
    data_period_end: Mapped[Date] = mapped_column(Date, nullable=False)

    # user interaction (for user behavior analysis)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_feedback: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_insights_user_type', 'user_id', 'insight_type'),
    )

if TYPE_CHECKING:
    from app.models.user import User
