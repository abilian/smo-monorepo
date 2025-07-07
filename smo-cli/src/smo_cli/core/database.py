"""
This module handles the CLI-specific database setup for SQLite.
"""

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smo_cli.core.config import Config
from smo_core import models
from smo_core.database import Base

# Ensure model stay imported to register them with the Base metadata.
assert models

_engine = None


@dataclass
class DbManager:
    cli_config: Config

    def get_engine(self):
        """
        Returns the SQLAlchemy engine for the CLI's SQLite database.
        This is used to create sessions and interact with the database.
        """
        db_file = self.cli_config.get_db_file()
        db_uri = f"sqlite:///{db_file}"
        return create_engine(db_uri, connect_args={"check_same_thread": False})

    def get_session_factory(self):
        engine = self.get_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def init_db(self):
        """
        Creates all tables in the database.
        This function imports all necessary models from smo_core before calling create_all
        to ensure they are registered on the Base's metadata.
        """
        engine = self.get_engine()
        Base.metadata.create_all(bind=engine)
