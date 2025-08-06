from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from smo_core.models.base import Base


class Event(Base):
    """Model for tracking system events like deployments, alerts, etc."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    icon: Mapped[str] = mapped_column(String(10), nullable=False)  # Emoji icon
    message: Mapped[str] = mapped_column(Text, nullable=False)  # Event description
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), nullable=False
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # What generated the event
    meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})  # Additional context

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for easy serialization."""
        return {
            "id": self.id,
            "icon": self.icon,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "metadata": self.meta,
        }
