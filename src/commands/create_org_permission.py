"""Create organization permission command implementation."""

import sys
from typing import Optional

import click
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Organization, Permission
from storage.database import db_manager


def validate_permission_name(name: str) -> str:
    """Validate and normalize permission name.
    
    Args:
        name: Permission name to validate
        
    Returns:
        str: Normalized permission name
        
    Raises:
        click.ClickException: If name is invalid
    """
    if not name or not name.strip():
        raise click.ClickException("Permission name cannot be empty")
    
    normalized_name = name.strip()
    if len(normalized_name) > 64:
        raise click.ClickException("Permission name cannot exceed 64 characters")
    
    return normalized_name


def validate_permission_description(description: Optional[str]) -> Optional[str]:
    """Validate and normalize permission description.
    
    Args:
        description: Permission description to validate
        
    Returns:
        Optional[str]: Normalized description or None
        
    Raises:
        click.ClickException: If description is invalid
    """
    if description is None:
        return None
    
    # Empty string is allowed
    if description == "":
        return ""
    
    normalized_description = description.strip()
    if len(normalized_description) > 255:
        raise click.ClickException("Permission description cannot exceed 255 characters")
    
    return normalized_description


def check_organization_exists(session: Session, organization_id: int) -> bool:
    """Check if organization with given ID exists.
    
    Args:
        session: Database session
        organization_id: Organization ID to check
        
    Returns:
        bool: True if organization exists
    """
    existing = session.query(Organization).filter(
        Organization.id == organization_id
    ).first()
    return existing is not None


def check_permission_exists_in_org(session: Session, name: str, organization_id: int) -> bool:
    """Check if permission with given name already exists in organization (case-insensitive).
    
    Args:
        session: Database session
        name: Permission name to check
        organization_id: Organization ID to check within
        
    Returns:
        bool: True if permission exists in the organization
    """
    existing = session.query(Permission).filter(
        Permission.name.ilike(name),
        Permission.organization_id == organization_id
    ).first()
    return existing is not None


def create_org_permission(
    organization_id: int,
    name: str,
    description: Optional[str] = None
) -> Permission:
    """Create a new organization permission.
    
    Args:
        organization_id: Organization ID (required)
        name: Permission name (required)
        description: Permission description (optional)
        
    Returns:
        Permission: The created permission
        
    Raises:
        click.ClickException: If validation fails or permission exists
    """
    # Validate and normalize inputs
    normalized_name = validate_permission_name(name)
    normalized_description = validate_permission_description(description)
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        # Check if organization exists
        if not check_organization_exists(session, organization_id):
            raise click.ClickException("Organization not found")
        
        # Check if permission already exists in organization (case-insensitive)
        if check_permission_exists_in_org(session, normalized_name, organization_id):
            raise click.ClickException("Permission with this name already exists in the organization")
        
        # Create new permission
        permission = Permission(
            name=normalized_name,
            description=normalized_description,
            organization_id=organization_id
        )
        
        # Add to session and commit
        session.add(permission)
        session.commit()
        
        # Refresh to ensure ID is loaded
        session.refresh(permission)
        
        return permission
        
    except IntegrityError as e:
        session.rollback()
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            raise click.ClickException("Permission with this name already exists in the organization")
        else:
            raise click.ClickException(f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise
    finally:
        try:
            session.close()
        except Exception:
            # Suppress session close errors to not interfere with main operation
            pass


@click.command()
@click.option(
    '--organization-id',
    type=int,
    required=True,
    help='Organization ID (required)'
)
@click.option(
    '--name',
    required=True,
    help='Permission name (required, max 64 characters, case-insensitive uniqueness within org)'
)
@click.option(
    '--description',
    help='Permission description (optional, max 255 characters)'
)
def create_org_permission_command(
    organization_id: int,
    name: str,
    description: Optional[str]
) -> None:
    """Create a new organization permission.
    
    Creates a new permission that can later be assigned to roles within the specified organization.
    Permission names must be unique within each organization (case-insensitive).
    
    Examples:
        ./run create-org-permission --organization-id 1 --name "Create Tournament"
        ./run create-org-permission --organization-id 1 --name "Edit Scores" --description "Allow editing of tournament scores"
    """
    try:
        permission = create_org_permission(
            organization_id=organization_id,
            name=name,
            description=description
        )
        
        # Success output
        click.echo("Permission created successfully!")
        click.echo(f"Permission ID: {permission.id}")
        click.echo(f"Name: {permission.name}")
        click.echo(f"Organization ID: {permission.organization_id}")
        if permission.description:
            click.echo(f"Description: {permission.description}")
            
    except click.ClickException as e:
        error_message = e.message
        click.echo(f"Error: {error_message}", err=True)
        
        # Map specific errors to exit codes as per PRP requirements
        if "Organization not found" in error_message:
            sys.exit(2)
        elif "Permission with this name already exists" in error_message:
            sys.exit(3)
        else:
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)