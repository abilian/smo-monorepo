"""Application graph service node model."""

from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from sqlalchemy.types import JSON

from smo_core.database import Base

JsonType = JSON().with_variant(JSONB, "postgresql")


class Service(Base):
    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    status: Mapped[Optional[str]] = mapped_column(String(255))
    grafana: Mapped[Optional[str]] = mapped_column(String(255))
    cluster_affinity: Mapped[Optional[str]] = mapped_column(String(255))
    artifact_ref: Mapped[Optional[str]] = mapped_column(String(255))
    artifact_type: Mapped[Optional[str]] = mapped_column(String(255))
    artifact_implementer: Mapped[Optional[str]] = mapped_column(String(255))
    cpu: Mapped[Optional[str]] = mapped_column(String(255))
    memory: Mapped[Optional[str]] = mapped_column(String(255))
    storage: Mapped[Optional[str]] = mapped_column(String(255))
    gpu: Mapped[Optional[str]] = mapped_column(String(255))

    # For JSON columns, you can type hint with Dict, List, or Any
    values_overwrite: Mapped[Optional[JsonType]] = mapped_column(JsonType)
    alert: Mapped[Optional[JsonType]] = mapped_column(JsonType)

    # Foreign Key and Relationship
    graph_id: Mapped[int] = mapped_column(ForeignKey("graph.id"))
    graph: Mapped["Graph"] = relationship(back_populates="services")

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
