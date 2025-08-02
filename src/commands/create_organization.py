"""Create organization command implementation."""

import sys
from typing import Optional

import click
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.models import Organization
from storage.database import db_manager


def validate_organization_name(name: str) -> str:
    """Validate and normalize organization name.
    
    Args:
        name: Organization name to validate
        
    Returns:
        str: Normalized organization name
        
    Raises:
        click.ClickException: If name is invalid
    """
    if not name or not name.strip():
        raise click.ClickException("Organization name cannot be empty")
    
    normalized_name = name.strip()
    if len(normalized_name) > 255:
        raise click.ClickException("Organization name cannot exceed 255 characters")
    
    return normalized_name


def check_organization_exists(session: Session, name: str) -> bool:
    """Check if organization with given name already exists (case-insensitive).
    
    Args:
        session: Database session
        name: Organization name to check
        
    Returns:
        bool: True if organization exists
    """
    existing = session.query(Organization).filter(
        Organization.name.ilike(name)
    ).first()
    return existing is not None


def create_organization(
    name: str,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None
) -> Organization:
    """Create a new organization.
    
    Args:
        name: Organization name (required)
        address: Organization address
        phone: Phone number
        email: Email address
        website: Website URL
        
    Returns:
        Organization: The created organization
        
    Raises:
        click.ClickException: If validation fails or organization exists
    """
    # Validate and normalize name
    normalized_name = validate_organization_name(name)
    
    # Get database session
    session = db_manager.get_session()
    
    try:
        # Note: Database unique constraint will catch duplicates
        
        # Create new organization
        organization = Organization(
            name=normalized_name,
            address=address.strip() if address and address.strip() else None,
            phone=phone.strip() if phone and phone.strip() else None,
            email=email.strip() if email and email.strip() else None,
            website=website.strip() if website and website.strip() else None
        )
        
        # Add to session and commit
        session.add(organization)
        session.commit()
        
        # Refresh to ensure ID is loaded
        session.refresh(organization)
        
        return organization
        
    except IntegrityError as e:
        session.rollback()
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            raise click.ClickException("Organization with this name already exists")
        else:
            raise click.ClickException(f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise click.ClickException(f"Database error: {str(e)}")
    finally:
        try:
            session.close()
        except Exception:
            # Suppress session close errors to not interfere with main operation
            pass


@click.command()
@click.option(
    '--name',
    required=True,
    help='Organization name (required, must be unique)'
)
@click.option(
    '--address',
    help='Organization address'
)
@click.option(
    '--phone',
    help='Phone number'
)
@click.option(
    '--email',
    help='Email address'
)
@click.option(
    '--website',
    help='Website URL'
)
def create_organization_command(
    name: str,
    address: Optional[str],
    phone: Optional[str],
    email: Optional[str],
    website: Optional[str]
) -> None:
    """Create a new organization.
    
    Creates a new organization with the specified name and optional contact information.
    Organization names must be unique (case-insensitive).
    
    Examples:
        ./run create-organization --name "4th Arrow Bowling Center"
        ./run create-organization --name "Pine Valley Lanes" --address "123 Main St" --phone "555-1234"
    """
    try:
        organization = create_organization(
            name=name,
            address=address,
            phone=phone,
            email=email,
            website=website
        )
        
        # Success output
        click.echo("Organization created successfully!")
        click.echo(f"Organization ID: {organization.id}")
        click.echo(f"Name: {organization.name}")
        if organization.address:
            click.echo(f"Address: {organization.address}")
        if organization.phone:
            click.echo(f"Phone: {organization.phone}")
        if organization.email:
            click.echo(f"Email: {organization.email}")
        if organization.website:
            click.echo(f"Website: {organization.website}")
            
    except click.ClickException as e:
        click.echo(f"Error: {e.message}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)