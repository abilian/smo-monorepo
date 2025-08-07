"""
Defines the SQLAlchemy declarative base.

Consumer applications (like smo-web or smo-cli) are responsible for creating
the database engine and session factory, and then calling:
`Base.metadata.create_all(engine)`
"""

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

__all__ = ["Base", "JsonType"]

# The single source of truth for all model definitions.
Base = declarative_base()

# Use standard JSON for SQLite compatibility, with a variant for PostgreSQL's JSONB.
JsonType = JSON().with_variant(JSONB, "postgresql")
