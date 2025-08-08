from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from smo_core.models.base import Base, JsonType


class Event(Base):
    """Model for tracking system events like deployments, alerts, etc."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Emoji icon representing the event type
    icon: Mapped[str] = mapped_column(String(10), nullable=False)
    # Description of the event
    message: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    # Source of the event, e.g., "deployment", "alert", etc.
    source: Mapped[Optional[str]] = mapped_column(String(50))
    # Additional metadata in JSON format
    meta: Mapped[dict[str, Any]] = mapped_column(JsonType, default={})

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary for easy serialization."""
        return {
            "id": self.id,
            "icon": self.icon,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.meta,
        }
