"""
This module handles the CLI-specific database setup for SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smo_core.database import Base

from .config import DB_FILE

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE}"

# The engine is specific to the CLI's SQLite database.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# The session factory is configured for the CLI's engine.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Creates all tables in the database.
    This function imports all necessary models from smo_core before calling create_all
    to ensure they are registered on the Base's metadata.
    """
    from smo_core import models

    Base.metadata.create_all(bind=engine)
