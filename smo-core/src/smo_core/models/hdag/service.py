"""Application graph service node model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from ...database import Base

JsonType = JSON().with_variant(JSONB, "postgresql")


class Service(Base):
    __tablename__ = "service"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    status = Column(String(255))
    grafana = Column(String(255))
    cluster_affinity = Column(String(255))
    artifact_ref = Column(String(255))
    artifact_type = Column(String(255))
    artifact_implementer = Column(String(255))
    cpu = Column(String(255))
    memory = Column(String(255))
    storage = Column(String(255))
    gpu = Column(String(255))
    values_overwrite = Column(JsonType)
    alert = Column(JsonType)

    graph_id = Column(Integer, ForeignKey("graph.id"), nullable=False)
    graph = relationship("Graph", back_populates="services")

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
