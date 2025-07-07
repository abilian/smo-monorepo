"""Cluster table model."""

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from smo_core.database import Base


class Cluster(Base):
    __tablename__ = "cluster"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    location: Mapped[str] = mapped_column(nullable=True)
    available_cpu: Mapped[float] = mapped_column()
    available_ram: Mapped[str] = mapped_column()
    availability: Mapped[bool] = mapped_column()
    acceleration: Mapped[bool] = mapped_column()
    grafana: Mapped[str] = mapped_column(nullable=True)

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
