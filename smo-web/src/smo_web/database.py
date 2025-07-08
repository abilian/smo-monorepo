""" """

from dataclasses import dataclass

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from smo_core.models.base import Base


@dataclass
class DbManager:
    config: dict

    def get_engine(self):
        """
        Returns the SQLAlchemy engine for the CLI's SQLite database.
        This is used to create sessions and interact with the database.
        """
        db_uri = self.config["SQLALCHEMY_URI"]
        return create_engine(db_uri)

        # For SQLite only
        # return create_engine(db_uri, connect_args={"check_same_thread": False})

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
