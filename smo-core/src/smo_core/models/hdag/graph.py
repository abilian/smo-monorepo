"""Application graph model."""

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from sqlalchemy.types import JSON

from ..base import Base

# Use standard JSON for SQLite compatibility, with a variant for PostgreSQL's JSONB.
JsonType = JSON().with_variant(JSONB, "postgresql")


class Graph(Base):
    __tablename__ = "graph"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str] = mapped_column(String(255))
    project: Mapped[str] = mapped_column(String(255))
    grafana: Mapped[str] = mapped_column(String(255), nullable=True)

    graph_descriptor: Mapped[dict] = mapped_column(JsonType)
    placement: Mapped[dict] = mapped_column(JsonType, nullable=True)

    services = relationship("Service", back_populates="graph", cascade="all,delete")

    def to_dict(self):
        """Returns a dictionary representation of the class."""
        instance_dict = {
            "name": self.name,
            "status": self.status,
            "project": self.project,
            "grafana": self.grafana,
            "hdaGraph": self.graph_descriptor,
            "placement": self.placement,
        }
        if self.services:
            instance_dict["services"] = [service.to_dict() for service in self.services]
        else:
            instance_dict["services"] = []

        return instance_dict
