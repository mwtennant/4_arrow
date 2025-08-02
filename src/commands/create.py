"""Create user command implementation for the 4th Arrow Tournament Control application."""

import sys
from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from core.models import User
from storage.database import db_manager


def create_user(
    first: str,
    last: str,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
) -> User:
    """Create a new user with the provided information.
    
    Args:
        first: First name (required, non-empty)
        last: Last name (required, non-empty)
        address: User address (optional)
        usbc_id: USBC ID (optional)
        tnba_id: TNBA ID (optional)
        phone: Phone number (optional)
        email: Email address (optional)
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If first or last name is empty
        IntegrityError: If email already exists in database
        SQLAlchemyError: If database operation fails
    """
    # Validate required fields
    if not first or not first.strip():
        raise ValueError("First name cannot be empty")
    if not last or not last.strip():
        raise ValueError("Last name cannot be empty")
    
    # Clean string inputs
    first = first.strip()
    last = last.strip()
    
    # Create user object
    user = User(
        first_name=first,
        last_name=last,
        address=address.strip() if address else None,
        usbc_id=usbc_id.strip() if usbc_id else None,
        tnba_id=tnba_id.strip() if tnba_id else None,
        phone=phone.strip() if phone else None,
        email=email.strip() if email else None
    )
    
    # Save to database
    session = db_manager.get_session()
    try:
        # Check for duplicate email if provided
        if email:
            existing_user = session.query(User).filter_by(email=email.strip()).first()
            if existing_user:
                raise IntegrityError("Email already exists", None, None)
        
        # Check for duplicate USBC ID if provided
        if usbc_id:
            existing_user = session.query(User).filter_by(usbc_id=usbc_id.strip()).first()
            if existing_user:
                raise IntegrityError("USBC ID already exists", None, None)
        
        # Check for duplicate TNBA ID if provided
        if tnba_id:
            existing_user = session.query(User).filter_by(tnba_id=tnba_id.strip()).first()
            if existing_user:
                raise IntegrityError("TNBA ID already exists", None, None)
        
        session.add(user)
        session.commit()
        session.refresh(user)
        
        return user
        
    except IntegrityError:
        session.rollback()
        raise
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def validate_create_args(first: str, last: str) -> None:
    """Validate create command arguments.
    
    Args:
        first: First name
        last: Last name
        
    Raises:
        SystemExit: With exit code 3 if validation fails
    """
    if not first or not first.strip():
        print("ERROR: First name cannot be empty", file=sys.stderr)
        sys.exit(3)
    if not last or not last.strip():
        print("ERROR: Last name cannot be empty", file=sys.stderr)
        sys.exit(3)