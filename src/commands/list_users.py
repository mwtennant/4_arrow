"""Enhanced list users command implementation for the 4th Arrow Tournament Control application."""

import csv
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

import click
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import Query
from sqlalchemy.exc import SQLAlchemyError

from core.models import User, ProfileRole
from storage.database import db_manager
from utils.csv_writer import export_users_to_csv, validate_csv_path


def parse_date_filter(date_str: str) -> datetime:
    """Parse YYYY-MM-DD format with timezone awareness.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        datetime: Parsed datetime with UTC timezone
        
    Raises:
        click.BadParameter: If date format is invalid
    """
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        raise click.BadParameter(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


def build_enhanced_user_query(
    session,
    filters: Dict[str, str],
    role: Optional[ProfileRole] = None,
    created_since: Optional[datetime] = None,
    order: str = "id"
) -> Query:
    """Build SQLAlchemy query with enhanced filters and ordering.
    
    Args:
        session: SQLAlchemy session object
        filters: Dictionary of legacy filter key-value pairs
        role: Profile role filter
        created_since: Filter for users created after this date
        order: Ordering field (id, last_name, created_at)
        
    Returns:
        SQLAlchemy Query object with applied filters and ordering
    """
    query = session.query(User)
    
    # Filter out soft-deleted users
    query = query.filter(User.deleted_at.is_(None))
    
    # Apply legacy partial match filters for string fields
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
    
    # Apply legacy exact match filters for ID fields
    if filters.get('usbc_id'):
        query = query.filter(User.usbc_id == filters['usbc_id'])
    if filters.get('tnba_id'):
        query = query.filter(User.tnba_id == filters['tnba_id'])
    
    # Apply role filter - we'll filter in Python since role is computed
    # Note: For production, this would be better with a database column or computed column
    
    # Apply date filter
    if created_since:
        query = query.filter(User.created_at >= created_since)
    
    # Apply ordering
    if order == "last_name":
        query = query.order_by(User.last_name, User.first_name)
    elif order == "created_at":
        query = query.order_by(User.created_at.desc())
    else:  # default to id
        query = query.order_by(User.id)
    
    return query


def list_users_enhanced(
    first: Optional[str] = None,
    last: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None,
    role: Optional[ProfileRole] = None,
    created_since: Optional[datetime] = None,
    order: str = "id",
    page_size: int = 50,
    csv_path: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """List users with enhanced filtering, ordering, and export options.
    
    Args:
        first: First name filter (partial match)
        last: Last name filter (partial match)
        email: Email filter (partial match)
        phone: Phone filter (partial match)
        address: Address filter (partial match)
        usbc_id: USBC ID filter (exact match)
        tnba_id: TNBA ID filter (exact match)
        role: Profile role filter
        created_since: Filter for users created after this date
        order: Ordering field (id, last_name, created_at)
        page_size: Number of results per page (0 = no limit)
        csv_path: If provided, export to CSV instead of displaying
        
    Returns:
        List of dictionaries containing user data
        
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
        query = build_enhanced_user_query(session, filters, role, created_since, order)
        all_users = query.all()
        
        # Filter by role in Python (since role is computed)
        if role:
            filtered_users = [user for user in all_users if user.get_role() == role]
        else:
            filtered_users = all_users
        
        # Convert to dictionary format for consistent return type
        users_data = []
        for user in filtered_users:
            users_data.append({
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'role': user.get_role().value,
                'email': user.email or '',
                'created_at': user.created_at.isoformat() if user.created_at else ''
            })
        
        # Handle CSV export
        if csv_path:
            export_users_to_csv(users_data, csv_path)
            return users_data
        
        # Handle pagination for table display
        if page_size > 0 and len(users_data) > page_size:
            return paginate_and_display(users_data, page_size)
        else:
            display_users_table(users_data)
            return users_data
        
    except SQLAlchemyError:
        raise
    finally:
        session.close()


# Backward compatibility function
def list_users(
    first: Optional[str] = None,
    last: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None
) -> List[User]:
    """List users with optional filters (legacy function for backward compatibility).
    
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
        query = build_enhanced_user_query(session, filters)
        users = query.all()
        
        return users
        
    except SQLAlchemyError:
        raise
    finally:
        session.close()


def display_users_table(users_data: List[Dict[str, Any]]) -> None:
    """Display users in a formatted Rich table with zebra striping.
    
    Args:
        users_data: List of dictionaries containing user data
    """
    console = Console()
    
    if not users_data:
        console.print("No users found matching criteria.")
        return
    
    # Create table with zebra striping
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        row_styles=["", "dim"]  # Zebra striping
    )
    table.add_column("User ID", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Role", style="yellow")
    table.add_column("Email", style="blue")
    table.add_column("Created", style="magenta")
    
    # Add rows
    for user in users_data:
        # Format created_at for display
        created_display = ""
        if user['created_at']:
            try:
                dt = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
                created_display = dt.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                created_display = str(user['created_at'])[:10]  # Fallback
        
        table.add_row(
            str(user['id']),
            user['name'],
            user['role'].replace('_', ' ').title(),
            user['email'],
            created_display
        )
    
    console.print(table)


def paginate_and_display(users_data: List[Dict[str, Any]], page_size: int) -> List[Dict[str, Any]]:
    """Display users with pagination support.
    
    Args:
        users_data: List of dictionaries containing user data
        page_size: Number of users per page
        
    Returns:
        List of all user data (same as input)
    """
    console = Console()
    total_users = len(users_data)
    pages = (total_users + page_size - 1) // page_size  # Ceiling division
    
    for page in range(pages):
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, total_users)
        page_data = users_data[start_idx:end_idx]
        
        # Display current page
        display_users_table(page_data)
        
        # Show pagination info if not last page
        if page < pages - 1:
            remaining = total_users - end_idx
            
            # Check if we're in an interactive environment
            if not sys.stdin.isatty():
                # Non-interactive environment - just show all results
                console.print(f"\n[dim]Showing remaining {remaining} results...[/dim]")
                continue
            
            console.print(f"\nNext {remaining} results... (press Enter to continue, 'q' to quit)")
            
            try:
                user_input = input().strip().lower()
                if user_input == 'q':
                    break
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Pagination interrupted by user[/yellow]")
                break
    
    return users_data


# Legacy display function for backward compatibility
def display_users(users: List[User]) -> None:
    """Display users in a formatted Rich table (legacy function).
    
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