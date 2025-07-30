# analytics.py - Performance tracking and insights
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Enum, Text, ForeignKey, Index, Float, Date, UniqueConstraint, func
import enum


from app.db.database import Base

class AnalyticsType(enum.Enum):
    POST_PERFORMANCE = "post_performance"
    ACCOUNT_GROWTH = "account_growth"
    ENGAGEMENT_TRENDS = "engagement_trends"
    AUDIENCE_INSIGHTS = "audience_insights"


class AnalyticsData(Base):
    """
    time-series analytics data for insights and reporting
    """
    __tablename__ = 'analytics_data'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # data source
    account_id: Mapped[int] = mapped_column(ForeignKey('social_account.id'), nullable=False, index=True)
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey('post.id'), nullable=True, index=True)

    # analytics metadata
    type: Mapped[AnalyticsType] = mapped_column(Enum(AnalyticsType), nullable=False, index=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)           # date for aggregation (enabling time series analytics)


    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)                    # JSON with all metrics

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    account : Mapped["SocialAccount"] = relationship("SocialAccount")
    post : Mapped["Post"] = relationship("Post")

    __table_args__ = (
        Index('idx_analytics_account_date', 'account_id', 'date'),
        Index('idx_analytics_type_date', 'type', 'date'),
        # unique constraint to prevent duplicate daily data
        UniqueConstraint('account_id', 'type', 'date', name='unique_daily_analytics'),
    )