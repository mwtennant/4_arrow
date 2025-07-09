"""Database connection and initialization for the 4th Arrow Tournament Control application."""

import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from core.models import Base


class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, database_url: Optional[str] = None) -> None:
        """Initialize database manager.
        
        Args:
            database_url: Database connection URL. Defaults to local SQLite file.
        """
        if database_url is None:
            database_url = "sqlite:///tournament_control.db"
        
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
        except SQLAlchemyError as e:
            raise RuntimeError(f"Failed to create database tables: {e}")
    
    def get_session(self) -> Session:
        """Get a database session.
        
        Returns:
            SQLAlchemy session object.
        """
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close the database connection."""
        self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()