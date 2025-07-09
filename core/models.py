"""User model for the 4th Arrow Tournament Control application."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """User model for storing user account information."""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=True)
    usbc_id = Column(String(50), nullable=True)
    tnba_id = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self) -> str:
        """String representation of User model."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"