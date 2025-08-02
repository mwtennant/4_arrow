"""Create organization role command implementation."""

import sys
from typing import Optional, List

import click
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Organization, Role, Permission, RolePermission
from storage.database import db_manager


def validate_role_name(name: str) -> str:
    """Validate and normalize role name.
    
    Args:
        name: Role name to validate
        
    Returns:
        str: Normalized role name
        
    Raises:
        click.ClickException: If name is invalid
    """
    if not name or not name.strip():
        raise click.ClickException("Role name cannot be empty")
    
    normalized_name = name.strip()
    if len(normalized_name) > 64:
        raise click.ClickException("Role name cannot exceed 64 characters")
    
    return normalized_name


def parse_permissions_list(permissions_str: Optional[str]) -> List[str]:
    """Parse comma-separated permissions list.
    
    Args:
        permissions_str: Comma-separated permissions string
        
    Returns:
        List[str]: List of normalized permission names
    """
    if not permissions_str or not permissions_str.strip():
        return []
    
    # Split, strip whitespace, and filter empty entries
    permissions = [p.strip() for p in permissions_str.split(',')]
    permissions = [p for p in permissions if p]  # Remove empty strings
    
    return permissions


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


def check_role_exists_in_org(session: Session, name: str, organization_id: int) -> bool:
    """Check if role with given name already exists in organization (case-insensitive).
    
    Args:
        session: Database session
        name: Role name to check
        organization_id: Organization ID to check within
        
    Returns:
        bool: True if role exists in the organization
    """
    existing = session.query(Role).filter(
        Role.name.ilike(name),
        Role.organization_id == organization_id
    ).first()
    return existing is not None


def validate_permissions_exist_in_org(
    session: Session, 
    permission_names: List[str], 
    organization_id: int
) -> List[Permission]:
    """Validate that all permission names exist in organization and return Permission objects.
    
    Args:
        session: Database session
        permission_names: List of permission names to validate
        organization_id: Organization ID to check within
        
    Returns:
        List[Permission]: List of Permission objects
        
    Raises:
        click.ClickException: If any permission doesn't exist
    """
    if not permission_names:
        return []
    
    permissions = []
    for perm_name in permission_names:
        permission = session.query(Permission).filter(
            Permission.name.ilike(perm_name),
            Permission.organization_id == organization_id
        ).first()
        
        if not permission:
            raise click.ClickException(f"Permission '{perm_name}' not found in organization")
        
        permissions.append(permission)
    
    return permissions


def create_org_role(
    organization_id: int,
    name: str,
    permissions: Optional[str] = None
) -> Role:
    """Create a new organization role with optional permissions.
    
    Args:
        organization_id: Organization ID (required)
        name: Role name (required)
        permissions: Comma-separated list of permission names (optional)
        
    Returns:
        Role: The created role
        
    Raises:
        click.ClickException: If validation fails or role exists
    """
    # Validate and normalize inputs
    normalized_name = validate_role_name(name)
    permission_names = parse_permissions_list(permissions)
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        # Check if organization exists
        if not check_organization_exists(session, organization_id):
            raise click.ClickException("Organization not found")
        
        # Check if role already exists in organization (case-insensitive)
        if check_role_exists_in_org(session, normalized_name, organization_id):
            raise click.ClickException("Role with this name already exists in the organization")
        
        # Validate all permissions exist in the organization
        permission_objects = validate_permissions_exist_in_org(
            session, permission_names, organization_id
        )
        
        # Create new role
        role = Role(
            name=normalized_name,
            organization_id=organization_id
        )
        
        # Add to session and commit to get the role ID
        session.add(role)
        session.commit()
        
        # Refresh to ensure ID is loaded
        session.refresh(role)
        
        # Create role-permission associations if permissions were provided
        if permission_objects:
            for permission in permission_objects:
                role_permission = RolePermission(
                    role_id=role.id,
                    permission_id=permission.id
                )
                session.add(role_permission)
            
            session.commit()
        
        return role
        
    except IntegrityError as e:
        session.rollback()
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            raise click.ClickException("Role with this name already exists in the organization")
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
    help='Role name (required, max 64 characters, case-insensitive uniqueness within org)'
)
@click.option(
    '--permissions',
    help='Comma-separated list of permission names to assign to this role (optional)'
)
def create_org_role_command(
    organization_id: int,
    name: str,
    permissions: Optional[str]
) -> None:
    """Create a new organization role with optional permissions.
    
    Creates a new role that can be assigned to users within the specified organization.
    Role names must be unique within each organization (case-insensitive).
    Optionally, you can assign existing permissions to the role during creation.
    
    Examples:
        ./run create-org-role --organization-id 1 --name "Tournament Director"
        ./run create-org-role --organization-id 1 --name "Score Keeper" --permissions "Edit Scores,View Reports"
    """
    try:
        role = create_org_role(
            organization_id=organization_id,
            name=name,
            permissions=permissions
        )
        
        # Success output
        click.echo("Role created successfully!")
        click.echo(f"Role ID: {role.id}")
        click.echo(f"Name: {role.name}")
        click.echo(f"Organization ID: {role.organization_id}")
        
        # Show assigned permissions if any
        if permissions:
            permission_names = parse_permissions_list(permissions)
            if permission_names:
                click.echo(f"Assigned permissions: {', '.join(permission_names)}")
            
    except click.ClickException as e:
        error_message = e.message
        click.echo(f"Error: {error_message}", err=True)
        
        # Map specific errors to exit codes as per PRP requirements
        if "Organization not found" in error_message:
            sys.exit(2)
        elif "Role with this name already exists" in error_message:
            sys.exit(3)
        elif "Permission" in error_message and "not found" in error_message:
            sys.exit(4)
        else:
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)