"""Add user to organization command implementation."""

import sys
from typing import List, Optional, Set

import click
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Organization, User, OrganizationMembership, Role
from storage.database import db_manager


def validate_organization_exists(session: Session, organization_id: int) -> Organization:
    """Validate that organization exists and return it.
    
    Args:
        session: Database session
        organization_id: Organization ID to validate
        
    Returns:
        Organization: The organization object
        
    Raises:
        click.ClickException: If organization doesn't exist
    """
    organization = session.query(Organization).filter(
        Organization.id == organization_id,
        Organization.deleted_at.is_(None)
    ).first()
    
    if not organization:
        raise click.ClickException(f"Organization with ID {organization_id} not found")
    
    return organization


def validate_user_exists(session: Session, user_id: int) -> Optional[User]:
    """Validate that user exists and return it.
    
    Args:
        session: Database session
        user_id: User ID to validate
        
    Returns:
        User: The user object, or None if not found
    """
    user = session.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    
    return user


def validate_role_exists(session: Session, role_name: str, organization_id: int) -> Optional[Role]:
    """Validate that role exists within the organization (case-insensitive).
    
    Args:
        session: Database session
        role_name: Role name to validate
        organization_id: Organization ID where role should exist
        
    Returns:
        Role: The role object, or None if not found
    """
    role = session.query(Role).filter(
        Role.name.ilike(role_name.strip()),
        Role.organization_id == organization_id
    ).first()
    
    return role


def check_user_membership(session: Session, user_id: int, organization_id: int) -> bool:
    """Check if user is already a member of the organization.
    
    Args:
        session: Database session
        user_id: User ID to check
        organization_id: Organization ID to check
        
    Returns:
        bool: True if user is already a member
    """
    membership = session.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.organization_id == organization_id
    ).first()
    
    return membership is not None


def deduplicate_user_ids(user_ids: List[int]) -> List[int]:
    """Remove duplicate user IDs while preserving order.
    
    Args:
        user_ids: List of user IDs (may contain duplicates)
        
    Returns:
        List[int]: Deduplicated list of user IDs
    """
    seen: Set[int] = set()
    result = []
    
    for user_id in user_ids:
        if user_id not in seen:
            seen.add(user_id)
            result.append(user_id)
    
    return result


def add_users_to_organization(
    organization_id: int,
    user_ids: List[int],
    role_name: Optional[str] = None
) -> None:
    """Add multiple users to an organization with optional role assignment.
    
    Args:
        organization_id: Organization ID to add users to
        user_ids: List of user IDs to add
        role_name: Optional role name to assign to users
        
    Raises:
        click.ClickException: For various validation and processing errors
    """
    # Deduplicate user IDs
    user_ids = deduplicate_user_ids(user_ids)
    
    if not user_ids:
        click.echo("Error: No users provided", err=True)
        sys.exit(5)
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        # Validate organization exists
        organization = validate_organization_exists(session, organization_id)
        
        # Validate role exists if provided
        role = None
        if role_name and role_name.strip():
            role = validate_role_exists(session, role_name, organization_id)
            if not role:
                click.echo(f"Error: Role '{role_name}' not found in organization {organization_id}", err=True)
                sys.exit(4)
        
        # Process each user
        successful_users = []
        skipped_users = []
        error_users = []
        
        for user_id in user_ids:
            # Check if user exists
            user = validate_user_exists(session, user_id)
            if not user:
                error_users.append(f"User {user_id}: User not found")
                continue
            
            # Check if user is already a member
            if check_user_membership(session, user_id, organization_id):
                skipped_users.append(f"User {user_id}: Already a member of organization {organization_id}")
                continue
            
            # Create membership
            try:
                membership = OrganizationMembership(
                    user_id=user_id,
                    organization_id=organization_id,
                    role_id=role.id if role else None
                )
                session.add(membership)
                
                # Add to successful list for output
                role_text = f" (role: {role.name})" if role else ""
                successful_users.append(f"User {user_id}{role_text}")
                
            except Exception as e:
                error_users.append(f"User {user_id}: {str(e)}")
                continue
        
        # Commit all successful operations
        if successful_users:
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                click.echo(f"Error: Database constraint violation: {str(e)}", err=True)
                sys.exit(1)
        
        # Handle output based on results
        if not successful_users and not skipped_users:
            # All users failed
            click.echo("Error: No users could be added", err=True)
            for error_msg in error_users:
                click.echo(f"- {error_msg}", err=True)
            sys.exit(1)
        
        # Display success results
        if successful_users:
            if len(successful_users) == 1:
                # Single user success
                user_info = successful_users[0]
                if role:
                    # Parse user info to extract user ID and role
                    if " (role: " in user_info:
                        user_part = user_info.split(" (role: ")[0]
                        role_part = user_info.split(" (role: ")[1].rstrip(")")
                        click.echo(f"{user_part} successfully added to organization {organization_id} with role '{role_part}'")
                    else:
                        click.echo(f"{user_info} successfully added to organization {organization_id}")
                else:
                    click.echo(f"{user_info} successfully added to organization {organization_id}")
            else:
                # Multiple users success
                click.echo(f"Successfully added the following users to organization {organization_id}:")
                for user_info in successful_users:
                    click.echo(f"- {user_info}")
        
        # Display skipped results
        if skipped_users or error_users:
            if successful_users:
                click.echo()  # Add blank line after success messages
            click.echo("Skipped the following users:")
            for skip_msg in skipped_users:
                click.echo(f"- {skip_msg}")
            for error_msg in error_users:
                click.echo(f"- {error_msg}")
        
        # Exit with appropriate code for partial success scenarios
        if successful_users and (skipped_users or error_users):
            # Partial success - some users added, some skipped
            pass  # Exit code 0 for partial success
        elif not successful_users and skipped_users and not error_users:
            # All users already members
            sys.exit(3)
        
    except click.ClickException:
        # Re-raise ClickExceptions to maintain error codes
        raise
    except Exception as e:
        session.rollback()
        click.echo(f"Error: Database error occurred: {str(e)}", err=True)
        sys.exit(1)
    finally:
        try:
            session.close()
        except Exception:
            # Suppress session close errors
            pass


@click.command()
@click.option(
    '--organization-id',
    type=int,
    required=True,
    help='Organization ID (must exist in database)'
)
@click.option(
    '--user-id',
    type=int,
    multiple=True,
    required=True,
    help='User ID(s) to add (can be repeated, must exist in database)'
)
@click.option(
    '--role',
    help='Role name (optional, must exist within the specified organization, case-insensitive)'
)
def add_org_user_command(
    organization_id: int,
    user_id: tuple,
    role: Optional[str]
) -> None:
    """Add users to an organization with optional role assignment.
    
    This command adds existing users (both registered and unregistered) to organizations
    with optional role assignment. Multiple users can be processed in a single command.
    
    Examples:
        ./run add-org-user --organization-id 1 --user-id 123 --role Manager
        ./run add-org-user --organization-id 1 --user-id 123 --user-id 456 --user-id 789
        ./run add-org-user --organization-id 2 --user-id 100 --role "Tournament Director"
    """
    try:
        # Convert tuple to list for processing
        user_ids = list(user_id)
        
        # Validate that at least one user ID is provided
        if not user_ids:
            click.echo("Error: No users provided", err=True)
            sys.exit(5)
        
        add_users_to_organization(
            organization_id=organization_id,
            user_ids=user_ids,
            role_name=role
        )
        
    except click.ClickException as e:
        click.echo(f"Error: {e.message}", err=True)
        # Exit codes are handled within the add_users_to_organization function
        if "not found" in e.message and "Organization" in e.message:
            sys.exit(2)
        elif "not found" in e.message and "Role" in e.message:
            sys.exit(4)
        else:
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: An unexpected error occurred: {str(e)}", err=True)
        sys.exit(1)