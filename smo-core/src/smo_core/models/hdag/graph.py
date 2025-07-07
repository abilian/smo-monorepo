"""Application graph model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

from smo_core.database import Base

# Use standard JSON for SQLite compatibility, with a variant for PostgreSQL's JSONB.
JsonType = JSON().with_variant(JSONB, "postgresql")


class Graph(Base):
    __tablename__ = "graph"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    status = Column(String(255))
    project = Column(String(255))
    grafana = Column(String(255))
    graph_descriptor = Column(JsonType)
    placement = Column(JsonType)

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
