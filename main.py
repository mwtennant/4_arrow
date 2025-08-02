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
from src.commands.create_organization import create_organization_command
from src.commands.edit_organization import edit_organization_command
from src.commands.create_org_permission import create_org_permission_command
from src.commands.create_org_role import create_org_role_command
from src.commands.add_org_user import add_org_user_command
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
        session = db_manager.get_session()
        try:
            user = auth_manager.create_user(
                session=session,
                email=email,
                password=password,
                first_name=first,
                last_name=last,
                phone=phone,
                address=address,
                usbc_id=usbc_id,
                tnba_id=tnba_id
            )
        finally:
            session.close()
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
        session = db_manager.get_session()
        try:
            user = auth_manager.authenticate_user(session, email, password)
        finally:
            session.close()
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
        session = db_manager.get_session()
        try:
            user = get_profile(session=session, user_id=user_id, email=email, usbc_id=usbc_id, tnba_id=tnba_id)
        finally:
            session.close()
        
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
        session = db_manager.get_session()
        try:
            success = edit_profile(session=session, user_id=user_id, first=first, last=last, phone=phone, address=address)
            if success:
                session.commit()
        finally:
            session.close()
        
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
        session = db_manager.get_session()
        try:
            success = delete_profile(session=session, user_id=user_id)
            if success:
                session.commit()
        finally:
            session.close()
        
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
@click.option('-m', '--main-id', type=int, required=True, 
              help='ID of the main user to merge into')
@click.option('-i', '--merge-id', type=int, multiple=True, required=True,
              help='ID(s) of user(s) to merge (can be repeated)')
@click.option('--dry-run', is_flag=True, default=False,
              help='Show planned actions without executing')
@click.option('--prefer-main', 'resolution_mode', flag_value='prefer_main',
              help='Automatically prefer main user values in conflicts')
@click.option('--prefer-merge', 'resolution_mode', flag_value='prefer_merge', 
              help='Automatically prefer merge user values in conflicts')
@click.option('--prefer-longest', 'resolution_mode', flag_value='prefer_longest',
              help='Automatically prefer longer values in conflicts')
@click.option('--no-interactive', is_flag=True, default=False,
              help='Use automatic resolution without prompts')
def merge(main_id: int, merge_id: tuple, dry_run: bool, resolution_mode: str, no_interactive: bool):
    """Merge one or more user profiles into a main profile.
    
    This command consolidates duplicate user profiles by merging all data
    from the specified duplicate profiles into a single primary profile.
    All historical data is preserved under the primary user ID.
    
    Examples:
        # Basic merge with interactive conflict resolution
        python main.py merge --main-id 3 --merge-id 5
        
        # Merge multiple users with short flags
        python main.py merge -m 3 -i 5 -i 11
        
        # Preview merge actions without executing
        python main.py merge -m 3 -i 5 --dry-run
        
        # Auto-resolve conflicts preferring main user values
        python main.py merge -m 3 -i 5 --prefer-main --no-interactive
    """
    merge_ids = list(merge_id)
    
    exit_code = merge_profiles(
        main_id=main_id,
        merge_ids=merge_ids,
        dry_run=dry_run,
        resolution_mode=resolution_mode,
        no_interactive=no_interactive
    )
    
    if exit_code != 0:
        sys.exit(exit_code)


@cli.command(name='list-users')
@click.option('--first', help='First name filter (partial match)')
@click.option('--last', help='Last name filter (partial match)')
@click.option('--email', help='Email filter (partial match)')
@click.option('--phone', help='Phone filter (partial match)')
@click.option('--address', help='Address filter (partial match)')
@click.option('--usbc_id', help='USBC ID filter (exact match)')
@click.option('--tnba_id', help='TNBA ID filter (exact match)')
@click.option('--role', 
              type=click.Choice(['registered_user', 'unregistered_user', 'org_member']),
              help='Filter by user role classification')
@click.option('--member', is_flag=True, 
              help='[DEPRECATED] Filter by registered users only. Use --role registered_user instead.')
@click.option('--created-since', 
              help='Show users created after YYYY-MM-DD (inclusive)')
@click.option('--order',
              type=click.Choice(['id', 'last_name', 'created_at']),
              default='id',
              help='Order results by field (default: id)')
@click.option('--page-size',
              type=int,
              default=50,
              help='Number of results per page (default: 50, 0 = no limit)')
@click.option('--csv',
              type=click.Path(),
              help='Export to CSV file instead of displaying table')
def list_users_cmd(
    first: Optional[str] = None,
    last: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    usbc_id: Optional[str] = None,
    tnba_id: Optional[str] = None,
    role: Optional[str] = None,
    member: bool = False,
    created_since: Optional[str] = None,
    order: str = 'id',
    page_size: int = 50,
    csv: Optional[str] = None
):
    """List users with enhanced filtering, ordering, pagination, and CSV export.
    
    Examples:
    
    \b
    # Basic usage
    python main.py list-users
    
    \b
    # Filter by role and order by name
    python main.py list-users --role registered_user --order last_name
    
    \b
    # Export to CSV with date filter
    python main.py list-users --created-since 2024-01-01 --csv users.csv
    
    \b
    # Complex filtering with pagination
    python main.py list-users --first John --role registered_user --page-size 10
    """
    try:
        from core.models import ProfileRole
        from src.commands.list_users import list_users_enhanced, parse_date_filter
        from utils.csv_writer import validate_csv_path
        import warnings
        
        # Handle deprecated --member flag
        if member and role:
            click.echo("ERROR: Cannot use both --member and --role flags", err=True)
            sys.exit(4)
        
        if member:
            warnings.warn(
                "--member flag is deprecated. Use --role registered_user instead.",
                DeprecationWarning,
                stacklevel=2
            )
            role = "registered_user"
        
        # Parse role filter
        role_filter = None
        if role:
            role_filter = ProfileRole(role)
        
        # Parse date filter  
        created_since_filter = None
        if created_since:
            try:
                created_since_filter = parse_date_filter(created_since)
            except click.BadParameter as e:
                click.echo(f"ERROR: {e}", err=True)
                sys.exit(4)
        
        # Parse CSV path
        csv_path = None
        if csv:
            try:
                csv_path = validate_csv_path(csv)
            except ValueError as e:
                click.echo(f"ERROR: {e}", err=True)
                sys.exit(1)
        
        # Validate page size
        if page_size < 0:
            click.echo("ERROR: page-size must be >= 0", err=True)
            sys.exit(4)
        
        # Call enhanced list users function
        users_data = list_users_enhanced(
            first=first,
            last=last,
            email=email,
            phone=phone,
            address=address,
            usbc_id=usbc_id,
            tnba_id=tnba_id,
            role=role_filter,
            created_since=created_since_filter,
            order=order,
            page_size=page_size,
            csv_path=csv_path
        )
        
        # Success message for CSV export
        if csv_path:
            click.echo(f"Exported {len(users_data)} users to {csv_path}")
        
    except SQLAlchemyError as e:
        click.echo(f"ERROR: Database error occurred: {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n[yellow]Operation interrupted by user[/yellow]")
        sys.exit(5)
    except Exception as e:
        click.echo(f"ERROR: An unexpected error occurred: {e}", err=True)
        sys.exit(1)


# Add the create-organization command to the CLI group
cli.add_command(create_organization_command, name='create-organization')

# Add the edit-organization command to the CLI group
cli.add_command(edit_organization_command, name='edit-organization')

# Add the create-org-permission command to the CLI group
cli.add_command(create_org_permission_command, name='create-org-permission')

# Add the create-org-role command to the CLI group
cli.add_command(create_org_role_command, name='create-org-role')

# Add the add-org-user command to the CLI group
cli.add_command(add_org_user_command, name='add-org-user')


if __name__ == '__main__':
    cli()