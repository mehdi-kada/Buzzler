from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Boolean, Enum, Text, ForeignKey, Index, func
import enum

from app.db.database import Base




class TemplateType(enum.Enum):
    POST_TEMPLATE = "post_template"
    HASHTAG_SET = "hashtag_set"
    CONTENT_SERIES = "content_series"
    CAMPAIGN = "campaign"

class SocialPlatform(enum.Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TIKTOK = "tiktok"
    YOUTUBE_SHORTS = "youtube_shorts"

class ContentTemplate(Base):
    """
    reusable content templates for consistent branding
    supports variables and platform specific customization
    """
    __tablename__ = 'content_templates'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False, index=True)

    # Template details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[TemplateType] = mapped_column(Enum(TemplateType), nullable=False, index=True)

    # template content (supports variables like {{video_title}})
    content: Mapped[str] = mapped_column(Text, nullable=False)
    hashtags: Mapped[Optional[list[str]]] = mapped_column(JSON, nullable=True)                   

    # platform-specific versions
    platform_variations: Mapped[Optional[list[SocialPlatform]]] = mapped_column(JSON, nullable=True)   

    # usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now())


    user : Mapped["User"] = relationship("User", back_populates="templates" )



    __table_args__ = (
        Index('idx_template_user_type', 'user_id', 'type'),
    )

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User