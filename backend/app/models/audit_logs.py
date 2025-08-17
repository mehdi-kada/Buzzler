from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from app.models.enums import ActionType
from app.db.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON, String, Integer, DateTime, Enum as SAEnum, Text, ForeignKey, Index, func

class AuditLog(Base):

    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('user.id'), nullable=True, index=True)  # Null for system actions

    action: Mapped[ActionType] = mapped_column(SAEnum(ActionType), nullable=False, index=True)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)    # video, clip, post, etc.
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    log_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)                          # JSON with additional context

    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True, index=True)      # IPv4/IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped[Optional['User']] = relationship("User")

    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action', 'created_at'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_time_action', 'created_at', 'action'),
    )

if TYPE_CHECKING:
    from app.models.user import User
