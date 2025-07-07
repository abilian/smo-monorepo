"""
This module handles the CLI-specific database setup for SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smo_core import models
from smo_core.database import Base

from .config import get_db_file

# Ensure model stay imported to register them with the Base metadata.
assert models

_engine = None


def get_engine():
    """
    Returns the SQLAlchemy engine for the CLI's SQLite database.
    This is used to create sessions and interact with the database.
    """
    global _engine

    if _engine is not None:
        return _engine

    db_file = get_db_file()
    db_uri = f"sqlite:///{db_file}"
    _engine = create_engine(db_uri, connect_args={"check_same_thread": False})
    return _engine


def get_session_factory():
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    Creates all tables in the database.
    This function imports all necessary models from smo_core before calling create_all
    to ensure they are registered on the Base's metadata.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
