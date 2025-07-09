"""Main CLI entry point for the 4th Arrow Tournament Control application."""

import sys
from typing import Optional

import click

from core.auth import auth_manager, AuthenticationError
from storage.database import db_manager


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


if __name__ == '__main__':
    cli()