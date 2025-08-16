from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, Integer, DateTime, Enum as SAEnum, ForeignKey, Index, Date, UniqueConstraint, func

from app.models.enums import AnalyticsType
from app.db.database import Base


class AnalyticsData(Base):
    """
    time-series analytics data for insights and reporting
    """
    __tablename__ = "analytics_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # data source
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("social_accounts.id"), nullable=False, index=True)
    post_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("posts.id"), nullable=True, index=True)

    # analytics metadata
    type: Mapped[AnalyticsType] = mapped_column(SAEnum(AnalyticsType), nullable=False, index=True)
    date: Mapped[Date] = mapped_column(Date, nullable=False, index=True)  # date for aggregation (enabling time series analytics)

    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)  # JSON with all metrics

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    account: Mapped["SocialAccount"] = relationship("SocialAccount")
    post: Mapped["Post"] = relationship("Post")

    __table_args__ = (
        Index("idx_analytics_account_date", "account_id", "date"),
        Index("idx_analytics_type_date", "type", "date"),
        UniqueConstraint("account_id", "type", "date", name="unique_daily_analytics"),
    )


if TYPE_CHECKING:
    from app.models.social_account import SocialAccount
    from app.models.post import Post
