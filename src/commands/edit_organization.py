"""Edit organization command implementation for the 4th Arrow Tournament Control application."""

import sys
from typing import Optional

import click
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from core.models import Organization
from storage.database import db_manager


def validate_empty_field(field_name: str, value: Optional[str]) -> None:
    """Validate that a field value is not empty.
    
    Args:
        field_name: Name of the field being validated
        value: Field value to validate
        
    Raises:
        ValueError: If value is an empty string
    """
    if value is not None and value.strip() == "":
        raise ValueError("Empty value not allowed")


def check_name_conflict(session: Session, new_name: str, organization_id: int) -> bool:
    """Check if a new organization name conflicts with existing organizations.
    
    Args:
        session: Database session
        new_name: New organization name to check
        organization_id: ID of organization being edited (to exclude from check)
        
    Returns:
        True if name conflicts with existing organization, False otherwise
    """
    existing_org = (
        session.query(Organization)
        .filter(Organization.name.ilike(new_name))
        .filter(Organization.id != organization_id)
        .filter(Organization.deleted_at.is_(None))
        .first()
    )
    return existing_org is not None


def update_organization_fields(
    organization: Organization,
    name: Optional[str] = None,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None
) -> bool:
    """Update organization fields with provided values.
    
    Args:
        organization: Organization object to update
        name: New name (optional)
        address: New address (optional)
        phone: New phone (optional)
        email: New email (optional)  
        website: New website (optional)
        
    Returns:
        True if any field was updated, False if no changes made
    """
    updated = False
    
    if name is not None:
        organization.name = name
        updated = True
        
    if address is not None:
        organization.address = address
        updated = True
        
    if phone is not None:
        organization.phone = phone
        updated = True
        
    if email is not None:
        organization.email = email
        updated = True
        
    if website is not None:
        organization.website = website
        updated = True
        
    return updated


@click.command()
@click.option('--organization-id', required=True, type=int, help='Organization ID to edit')
@click.option('--name', type=str, help='Organization name')
@click.option('--address', type=str, help='Organization address')
@click.option('--phone', type=str, help='Organization phone')
@click.option('--email', type=str, help='Organization email')
@click.option('--website', type=str, help='Organization website')
def edit_organization_command(
    organization_id: int,
    name: Optional[str] = None,
    address: Optional[str] = None,
    phone: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None
) -> None:
    """Update an existing organization's details.
    
    Updates only the fields provided. Fields not specified will remain unchanged.
    The operation is successful even if no fields are provided (no-op).
    
    Args:
        organization_id: ID of organization to edit
        name: New organization name (must be unique)
        address: New organization address
        phone: New organization phone number
        email: New organization email address
        website: New organization website URL
    """
    try:
        # Validate empty fields
        for field_name, value in [
            ('name', name),
            ('address', address), 
            ('phone', phone),
            ('email', email),
            ('website', website)
        ]:
            validate_empty_field(field_name, value)
            
        session = db_manager.get_session()
        try:
            # Find organization by ID
            organization = (
                session.query(Organization)
                .filter(Organization.id == organization_id)
                .filter(Organization.deleted_at.is_(None))
                .first()
            )
            
            if not organization:
                click.echo("Organization not found.", err=True)
                sys.exit(2)
            
            # Check name conflict if name is being updated
            if name is not None and check_name_conflict(session, name, organization_id):
                click.echo("Organization name already exists.", err=True)
                sys.exit(3)
            
            # Update fields
            updated = update_organization_fields(
                organization=organization,
                name=name,
                address=address,
                phone=phone,
                email=email,
                website=website
            )
            
            # Commit changes if any were made
            if updated:
                session.commit()
                
        finally:
            session.close()
            
    except ValueError as e:
        if "Empty value not allowed" in str(e):
            click.echo("Empty value not allowed", err=True)
            sys.exit(1)
        else:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    except SQLAlchemyError as e:
        click.echo(f"Database error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        sys.exit(1)


# Export the command for use in main.py
edit_organization = edit_organization_command