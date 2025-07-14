"""Main CLI entry point for the 4th Arrow Tournament Control application."""

import sys
from typing import Optional

import click

from core.auth import auth_manager, AuthenticationError
from core.profile import get_profile, display_profile, edit_profile, delete_profile
from storage.database import db_manager
from src.commands.create import create_user, validate_create_args
from src.commands.merge import merge_profiles, validate_merge_args, handle_merge_errors
from src.commands.list_users import list_users, display_users
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


@click.group()
def cli():
    """4th Arrow Tournament Control CLI."""
    # Initialize database tables
    db_manager.create_tables()


@cli.command()
@click.option('--email', required=True, help='User email address')
@click.option('--password', required=True, help='User password')
@click.option('--first', required=True, help='User first name')
@click.option('--last', required=True, help='User last name')
@click.option('--phone', required=True, help='User phone number')
@click.option('--address', help='User address (optional)')
@click.option('--usbc_id', help='User USBC ID (optional)')
@click.option('--tnba_id', help='User TNBA ID (optional)')
def signup(
    email: str,
    password: str,
    first: str,
    last: str,
    phone: str,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None
):
    """Sign up a new user account."""
    try:
        user = auth_manager.create_user(
            email=email,
            password=password,
            first_name=first,
            last_name=last,
            phone=phone,
            address=address,
            usbc_id=usbc_id,
            tnba_id=tnba_id
        )
        click.echo(f"User account created successfully for {user.email}")
        
    except AuthenticationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--email', required=True, help='User email address')
@click.option('--password', required=True, help='User password')
def login(email: str, password: str):
    """Log in with email and password."""
    try:
        user = auth_manager.authenticate_user(email, password)
        click.echo(f"Login successful. Welcome, {user.first_name} {user.last_name}!")
        
    except AuthenticationError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        sys.exit(1)


@cli.command(name='get-profile')
@click.option('--user-id', type=int, help='User ID to retrieve')
@click.option('--email', help='Email address to retrieve')
@click.option('--usbc_id', help='USBC ID to retrieve')
@click.option('--tnba_id', help='TNBA ID to retrieve')
def get_profile_cmd(user_id: Optional[int], email: Optional[str], usbc_id: Optional[str], tnba_id: Optional[str]):
    """Get user profile by ID."""
    # Check that exactly one ID flag is provided
    provided_flags = sum(1 for flag in [user_id, email, usbc_id, tnba_id] if flag is not None)
    
    if provided_flags != 1:
        click.echo("ERROR: Exactly one ID flag must be provided", err=True)
        sys.exit(1)
    
    try:
        user = get_profile(user_id=user_id, email=email, usbc_id=usbc_id, tnba_id=tnba_id)
        
        if user is None:
            click.echo("ERROR: No user found.", err=True)
            sys.exit(1)
            
        display_profile(user)
        
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command(name='edit-profile')
@click.option('--user-id', type=int, required=True, help='User ID to edit')
@click.option('--first', help='New first name')
@click.option('--last', help='New last name')
@click.option('--phone', help='New phone number')
@click.option('--address', help='New address')
def edit_profile_cmd(user_id: int, first: Optional[str], last: Optional[str], phone: Optional[str], address: Optional[str]):
    """Edit user profile."""
    # Check that at least one field is provided
    if all(field is None for field in [first, last, phone, address]):
        click.echo("ERROR: At least one field must be provided", err=True)
        sys.exit(1)
    
    try:
        success = edit_profile(user_id=user_id, first=first, last=last, phone=phone, address=address)
        
        if not success:
            click.echo("ERROR: User not found", err=True)
            sys.exit(1)
            
        click.echo("Profile updated.")
        
    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command(name='delete-profile')
@click.option('--user-id', type=int, required=True, help='User ID to delete')
@click.option('--confirm', help='Confirmation flag (must be "yes")')
def delete_profile_cmd(user_id: int, confirm: Optional[str]):
    """Delete user profile."""
    if confirm != "yes":
        click.echo("ERROR: Deletion aborted.", err=True)
        sys.exit(1)
    
    try:
        success = delete_profile(user_id)
        
        if not success:
            click.echo("ERROR: User not found", err=True)
            sys.exit(1)
            
        click.echo("Profile deleted.")
        
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--first', required=True, help='First name (required)')
@click.option('--last', required=True, help='Last name (required)')
@click.option('--address', help='User address (optional)')
@click.option('--usbc_id', help='USBC ID (optional)')
@click.option('--tnba_id', help='TNBA ID (optional)')
@click.option('--phone', help='Phone number (optional)')
@click.option('--email', help='Email address (optional)')
def create(
    first: str,
    last: str,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None
):
    """Create a new user."""
    # Validate required arguments
    validate_create_args(first, last)
    
    try:
        user = create_user(
            first=first,
            last=last,
            address=address,
            usbc_id=usbc_id,
            tnba_id=tnba_id,
            phone=phone,
            email=email
        )
        
        # Success message
        if email:
            click.echo(f"User created successfully: {user.first_name} {user.last_name} ({user.email})")
        else:
            click.echo(f"User created successfully: {user.first_name} {user.last_name}")
        
    except ValueError as e:
        if "First name cannot be empty" in str(e):
            click.echo("ERROR: First name cannot be empty", err=True)
            sys.exit(3)
        elif "Last name cannot be empty" in str(e):
            click.echo("ERROR: Last name cannot be empty", err=True)
            sys.exit(3)
        else:
            click.echo(f"ERROR: {e}", err=True)
            sys.exit(1)
    except IntegrityError as e:
        if "Email already exists" in str(e):
            click.echo("ERROR: Email already exists. Try using get-profile to find the existing user.", err=True)
            sys.exit(2)
        elif "USBC ID already exists" in str(e):
            click.echo("ERROR: USBC ID already exists in the database.", err=True)
            sys.exit(2)
        elif "TNBA ID already exists" in str(e):
            click.echo("ERROR: TNBA ID already exists in the database.", err=True)
            sys.exit(2)
        else:
            click.echo(f"ERROR: {e}", err=True)
            sys.exit(1)
    except SQLAlchemyError as e:
        click.echo(f"ERROR: Database error occurred: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: An unexpected error occurred: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--main-id', type=int, required=True, help='ID of the main user to merge into')
@click.option('--merge-id', type=int, multiple=True, required=True, help='ID(s) of user(s) to merge (can be repeated)')
def merge(main_id: int, merge_id: tuple):
    """Merge one or more user profiles into a main profile."""
    merge_ids = list(merge_id)
    
    # Validate arguments
    validate_merge_args(main_id, merge_ids)
    
    try:
        merge_profiles(main_id, merge_ids)
        
    except Exception as e:
        handle_merge_errors(e)


@cli.command(name='list-users')
@click.option('--first', help='First name filter (partial match)')
@click.option('--last', help='Last name filter (partial match)')
@click.option('--email', help='Email filter (partial match)')
@click.option('--phone', help='Phone filter (partial match)')
@click.option('--address', help='Address filter (partial match)')
@click.option('--usbc_id', help='USBC ID filter (exact match)')
@click.option('--tnba_id', help='TNBA ID filter (exact match)')
def list_users_cmd(
    first: Optional[str] = None,
    last: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None
):
    """List users with optional filters."""
    try:
        users = list_users(
            first=first,
            last=last,
            email=email,
            phone=phone,
            address=address,
            usbc_id=usbc_id,
            tnba_id=tnba_id
        )
        
        display_users(users)
        
    except SQLAlchemyError as e:
        click.echo(f"ERROR: Database error occurred: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"ERROR: An unexpected error occurred: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()