"""Authentication logic for the 4th Arrow Tournament Control application."""

import re
from typing import Optional

import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.models import User
from storage.database import db_manager


class AuthenticationError(Exception):
    """Exception raised for authentication-related errors."""
    pass


class AuthManager:
    """Manages user authentication and registration."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address to validate.
            
        Returns:
            True if email format is valid, False otherwise.
        """
        if not email or not email.strip():
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email.strip()))
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """Validate password strength.
        
        Args:
            password: Password to validate.
            
        Returns:
            True if password is valid, False otherwise.
        """
        return bool(password and len(password.strip()) >= 6)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password to hash.
            
        Returns:
            Hashed password string.
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            password: Plain text password to verify.
            password_hash: Hashed password to compare against.
            
        Returns:
            True if password matches hash, False otherwise.
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    @staticmethod
    def create_user(
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: str,
        address: Optional[str] = None,
        usbc_id: Optional[str] = None,
        tnba_id: Optional[str] = None
    ) -> User:
        """Create a new user account.
        
        Args:
            email: User's email address.
            password: User's password.
            first_name: User's first name.
            last_name: User's last name.
            phone: User's phone number.
            address: User's address (optional).
            usbc_id: User's USBC ID (optional).
            tnba_id: User's TNBA ID (optional).
            
        Returns:
            Created User object.
            
        Raises:
            AuthenticationError: If validation fails or user already exists.
        """
        # Validate required fields
        if not email or not email.strip():
            raise AuthenticationError("Email is required")
        
        if not AuthManager.validate_email(email):
            raise AuthenticationError("Invalid email format")
        
        if not password or not password.strip():
            raise AuthenticationError("Password is required")
        
        if not AuthManager.validate_password(password):
            raise AuthenticationError("Password must be at least 6 characters long")
        
        if not first_name or not first_name.strip():
            raise AuthenticationError("First name is required")
        
        if not last_name or not last_name.strip():
            raise AuthenticationError("Last name is required")
        
        if not phone or not phone.strip():
            raise AuthenticationError("Phone number is required")
        
        # Create database session
        session = db_manager.get_session()
        
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(User.email == email.strip().lower()).first()
            if existing_user:
                raise AuthenticationError("Email already exists")
            
            # Hash password
            password_hash = AuthManager.hash_password(password)
            
            # Create new user
            user = User(
                email=email.strip().lower(),
                password_hash=password_hash,
                first_name=first_name.strip(),
                last_name=last_name.strip(),
                phone=phone.strip(),
                address=address.strip() if address else None,
                usbc_id=usbc_id.strip() if usbc_id else None,
                tnba_id=tnba_id.strip() if tnba_id else None
            )
            
            session.add(user)
            session.commit()
            session.refresh(user)
            
            return user
            
        except SQLAlchemyError as e:
            session.rollback()
            raise AuthenticationError(f"Database error: {e}")
        finally:
            session.close()
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> User:
        """Authenticate a user with email and password.
        
        Args:
            email: User's email address.
            password: User's password.
            
        Returns:
            User object if authentication succeeds.
            
        Raises:
            AuthenticationError: If authentication fails.
        """
        if not email or not email.strip():
            raise AuthenticationError("Email is required")
        
        if not password or not password.strip():
            raise AuthenticationError("Password is required")
        
        session = db_manager.get_session()
        
        try:
            user = session.query(User).filter(User.email == email.strip().lower()).first()
            
            if not user:
                raise AuthenticationError("Invalid email or password")
            
            if not AuthManager.verify_password(password, user.password_hash):
                raise AuthenticationError("Invalid email or password")
            
            return user
            
        except SQLAlchemyError as e:
            raise AuthenticationError(f"Database error: {e}")
        finally:
            session.close()


# Global auth manager instance
auth_manager = AuthManager()