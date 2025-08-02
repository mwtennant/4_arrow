"""Profile management functionality for the 4th Arrow Tournament Control application."""

from typing import Optional

from sqlalchemy.orm import Session
from rich.console import Console
from rich.table import Table

from core.models import User


console = Console()


def get_profile(
    session: Session,
    user_id: Optional[int] = None,
    email: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None
) -> Optional[User]:
    """Get a user profile by one of the supported ID types.
    
    Args:
        user_id: User ID to search by
        email: Email address to search by
        usbc_id: USBC ID to search by
        tnba_id: TNBA ID to search by
        
    Returns:
        User object if found, None otherwise
    """
    try:
        if user_id is not None:
            user = session.query(User).filter(User.id == user_id).first()
        elif email is not None:
            user = session.query(User).filter(User.email == email).first()
        elif usbc_id is not None:
            user = session.query(User).filter(User.usbc_id == usbc_id).first()
        elif tnba_id is not None:
            user = session.query(User).filter(User.tnba_id == tnba_id).first()
        else:
            return None
            
        return user
        
    except Exception:
        raise


def display_profile(user: User) -> None:
    """Display user profile in Rich table format.
    
    Args:
        user: User object to display
    """
    from rich.table import Table
    from rich import box
    
    table = Table(show_header=True, header_style="bold", show_lines=False, box=box.MINIMAL)
    table.add_column("user_id")
    table.add_column("first") 
    table.add_column("last")
    table.add_column("email")
    table.add_column("phone")
    table.add_column("address")
    table.add_column("usbc_id")
    table.add_column("tnba_id")
    
    table.add_row(
        str(user.id),
        user.first_name,
        user.last_name,
        user.email,
        user.phone,
        user.address or "",
        user.usbc_id or "",
        user.tnba_id or ""
    )
    
    console.print(table)


def edit_profile(
    session: Session,
    user_id: int,
    first: Optional[str] = None,
    last: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None
) -> bool:
    """Edit user profile fields.
    
    Args:
        user_id: User ID to edit
        first: New first name
        last: New last name
        phone: New phone number
        address: New address
        
    Returns:
        True if successful, False otherwise
    """
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False
            
        # Update fields if provided
        if first is not None:
            if first.strip() == "":
                raise ValueError("First name cannot be empty")
            user.first_name = first
            
        if last is not None:
            if last.strip() == "":
                raise ValueError("Last name cannot be empty")
            user.last_name = last
            
        if phone is not None:
            if phone.strip() == "":
                raise ValueError("Phone cannot be empty")
            user.phone = phone
            
        if address is not None:
            if address.strip() == "":
                raise ValueError("Address cannot be empty")
            user.address = address
            
        session.commit()
        return True
        
    finally:
        session.close()


def delete_profile(user_id: int) -> bool:
    """Delete a user profile.
    
    Args:
        user_id: User ID to delete
        
    Returns:
        True if successful, False if user not found
    """
    session: Session = db_manager.get_session()
    
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False
            
        session.delete(user)
        session.commit()
        return True
        
    finally:
        session.close()