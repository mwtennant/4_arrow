"""List users command implementation for the 4th Arrow Tournament Control application."""

from typing import Dict, List, Optional

from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError

from core.models import User
from storage.database import db_manager


def build_user_query(session, filters: Dict[str, str]) -> Query:
    """Build SQLAlchemy query with dynamic filters.
    
    Args:
        session: SQLAlchemy session object
        filters: Dictionary of filter key-value pairs
        
    Returns:
        SQLAlchemy Query object with applied filters
    """
    query = session.query(User)
    
    # Apply partial match filters for string fields
    if filters.get('first'):
        query = query.filter(User.first_name.ilike(f"%{filters['first']}%"))
    if filters.get('last'):
        query = query.filter(User.last_name.ilike(f"%{filters['last']}%"))
    if filters.get('email'):
        query = query.filter(User.email.ilike(f"%{filters['email']}%"))
    if filters.get('phone'):
        query = query.filter(User.phone.ilike(f"%{filters['phone']}%"))
    if filters.get('address'):
        query = query.filter(User.address.ilike(f"%{filters['address']}%"))
    
    # Apply exact match filters for ID fields
    if filters.get('usbc_id'):
        query = query.filter(User.usbc_id == filters['usbc_id'])
    if filters.get('tnba_id'):
        query = query.filter(User.tnba_id == filters['tnba_id'])
    
    return query


def list_users(
    first: Optional[str] = None,
    last: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None
) -> List[User]:
    """List users with optional filters.
    
    Args:
        first: First name filter (partial match)
        last: Last name filter (partial match)
        email: Email filter (partial match)
        phone: Phone filter (partial match)
        address: Address filter (partial match)
        usbc_id: USBC ID filter (exact match)
        tnba_id: TNBA ID filter (exact match)
        
    Returns:
        List of User objects matching the filters
        
    Raises:
        SQLAlchemyError: If database operation fails
    """
    session = db_manager.get_session()
    try:
        # Build filters dictionary, excluding None/empty values
        filters = {}
        if first and first.strip():
            filters['first'] = first.strip()
        if last and last.strip():
            filters['last'] = last.strip()
        if email and email.strip():
            filters['email'] = email.strip()
        if phone and phone.strip():
            filters['phone'] = phone.strip()
        if address and address.strip():
            filters['address'] = address.strip()
        if usbc_id and usbc_id.strip():
            filters['usbc_id'] = usbc_id.strip()
        if tnba_id and tnba_id.strip():
            filters['tnba_id'] = tnba_id.strip()
        
        # Build and execute query
        query = build_user_query(session, filters)
        users = query.all()
        
        return users
        
    except SQLAlchemyError:
        raise
    finally:
        session.close()


def display_users(users: List[User]) -> None:
    """Display users in a formatted Rich table.
    
    Args:
        users: List of User objects to display
    """
    console = Console()
    
    if not users:
        console.print("No users found matching criteria.")
        return
    
    # Create table with minimal border
    table = Table(show_header=True, header_style="bold", border_style="dim")
    table.add_column("User ID", style="cyan")
    table.add_column("First", style="green")
    table.add_column("Last", style="green")
    table.add_column("Email", style="blue")
    table.add_column("Phone", style="magenta")
    table.add_column("Address", style="yellow")
    table.add_column("USBC ID", style="red")
    table.add_column("TNBA ID", style="red")
    
    # Add rows
    for user in users:
        table.add_row(
            str(user.id),
            user.first_name or "",
            user.last_name or "",
            user.email or "",
            user.phone or "",
            user.address or "",
            user.usbc_id or "",
            user.tnba_id or ""
        )
    
    console.print(table)