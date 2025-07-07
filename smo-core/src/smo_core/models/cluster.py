"""Cluster table model."""

from sqlalchemy import Boolean, Column, Float, Integer, String

from smo_core.database import Base


class Cluster(Base):
    __tablename__ = "cluster"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    location = Column(String(100))
    available_cpu = Column(Float, nullable=False)
    available_ram = Column(String, nullable=False)
    availability = Column(Boolean, nullable=False)
    acceleration = Column(Boolean, nullable=False)
    grafana = Column(String)

    def to_dict(self):
        """Returns a dictionary representation of the class."""
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "available_cpu": self.available_cpu,
            "available_ram": self.available_ram,
            "availability": self.availability,
            "acceleration": self.acceleration,
            "grafana": self.grafana,
        }
