"""Application graph service node model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped

from smo_core.models.base import Base, JsonType

if TYPE_CHECKING:
    # Avoid circular import
    from .graph import Graph

__all__ = ["Service"]


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[str | None] = mapped_column(String(255))
    grafana: Mapped[str | None] = mapped_column(String(255))
    cluster_affinity: Mapped[str | None] = mapped_column(String(255))
    artifact_ref: Mapped[str | None] = mapped_column(String(255))
    artifact_type: Mapped[str | None] = mapped_column(String(255))
    artifact_implementer: Mapped[str | None] = mapped_column(String(255))
    cpu: Mapped[str | None] = mapped_column(String(255))
    memory: Mapped[str | None] = mapped_column(String(255))
    storage: Mapped[str | None] = mapped_column(String(255))
    gpu: Mapped[str | None] = mapped_column(String(255))

    # For JSON columns, you can type hint with Dict, List, or Any
    values_overwrite: Mapped[JSON | None] = mapped_column(JsonType)
    alert: Mapped[JSON | None] = mapped_column(JsonType)

    # Foreign Key and Relationship
    graph_id: Mapped[int] = mapped_column(ForeignKey("graph.id"))
    graph: Mapped[Graph] = relationship(back_populates="services")

    def to_dict(self):
        """Returns a dictionary representation of the class."""
        return {
            "name": self.name,
            "status": self.status,
            "grafana": self.grafana,
            "cluster_affinity": self.cluster_affinity,
            "cpu": self.cpu,
            "memory": self.memory,
            "storage": self.storage,
            "gpu": self.gpu,
            "values_overwrite": self.values_overwrite,
            "alert": self.alert,
            "artifact_ref": self.artifact_ref,
            "artifact_type": self.artifact_type,
            "artifact_implementer": self.artifact_implementer,
        }
