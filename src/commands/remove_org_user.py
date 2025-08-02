"""Remove user from organization command implementation."""

import sys
from typing import List, Optional, Set

import click
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Organization, User, OrganizationMembership
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


def check_user_membership(session: Session, user_id: int, organization_id: int) -> Optional[OrganizationMembership]:
    """Check if user is a member of the organization and return membership.
    
    Args:
        session: Database session
        user_id: User ID to check
        organization_id: Organization ID to check
        
    Returns:
        OrganizationMembership: The membership object, or None if not a member
    """
    membership = session.query(OrganizationMembership).filter(
        OrganizationMembership.user_id == user_id,
        OrganizationMembership.organization_id == organization_id
    ).first()
    
    return membership


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


def remove_users_from_organization(
    organization_id: int,
    user_ids: List[int]
) -> None:
    """Remove multiple users from an organization.
    
    Args:
        organization_id: Organization ID to remove users from
        user_ids: List of user IDs to remove
        
    Raises:
        click.ClickException: For various validation and processing errors
    """
    # Deduplicate user IDs
    user_ids = deduplicate_user_ids(user_ids)
    
    if not user_ids:
        click.echo("Error: No user IDs provided", err=True)
        sys.exit(5)
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        # Validate organization exists
        organization = validate_organization_exists(session, organization_id)
        
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
            
            # Check if user is a member of the organization
            membership = check_user_membership(session, user_id, organization_id)
            if not membership:
                skipped_users.append(f"User {user_id}: Not a member of organization {organization_id}")
                continue
            
            # Remove membership
            try:
                session.delete(membership)
                successful_users.append(f"User {user_id}")
                
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
        if not successful_users and not skipped_users and error_users:
            # All users failed - this should not happen in normal conditions
            # as skipped_users should contain non-members
            click.echo("Error: No users could be processed", err=True)
            for error_msg in error_users:
                click.echo(f"- {error_msg}", err=True)
            sys.exit(1)
        
        # Display success results
        if successful_users:
            if len(successful_users) == 1:
                # Single user removal success
                user_info = successful_users[0]
                click.echo(f"{user_info} successfully removed from organization {organization_id}")
            else:
                # Multiple users success
                click.echo(f"Successfully removed the following users from organization {organization_id}:")
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
        
        # Exit successfully - partial success scenarios are considered successful
        # as per PRP requirements
        
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
    help='User ID(s) to remove (can be repeated, must be valid user IDs)'
)
@click.option(
    '--force',
    is_flag=True,
    help='Force flag for destructive batch actions (future-compatible, currently no-op)'
)
def remove_org_user_command(
    organization_id: int,
    user_id: tuple,
    force: bool
) -> None:
    """Remove users from an organization.
    
    This command removes existing users from organizations with proper validation 
    and graceful error handling. Multiple users can be processed in a single command.
    Non-member users are gracefully skipped with warnings.
    
    Examples:
        ./run remove-org-user --organization-id 1 --user-id 123
        ./run remove-org-user --organization-id 1 --user-id 123 --user-id 456 --user-id 789
        ./run remove-org-user --organization-id 2 --user-id 100 --force
    """
    try:
        # Convert tuple to list for processing
        user_ids = list(user_id)
        
        # Validate that at least one user ID is provided
        if not user_ids:
            click.echo("Error: No user IDs provided", err=True)
            sys.exit(5)
        
        remove_users_from_organization(
            organization_id=organization_id,
            user_ids=user_ids
        )
        
    except click.ClickException as e:
        click.echo(f"Error: {e.message}", err=True)
        # Exit codes are handled within the remove_users_from_organization function
        if "not found" in e.message and "Organization" in e.message:
            sys.exit(2)
        else:
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: An unexpected error occurred: {str(e)}", err=True)
        sys.exit(1)