"""Enhanced merge profiles command implementation for the 4th Arrow Tournament Control application."""

import json
import sys
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

import click
from rich.console import Console
from rich.table import Table
from rich import box
from sqlalchemy.exc import SQLAlchemyError

from core.models import User
from core.logging import log_merge_event
from storage.database import db_manager

console = Console()

# Resolution modes
RESOLUTION_MODES = ["prefer_main", "prefer_merge", "prefer_longest"]


def merge_profiles(
    main_id: int, 
    merge_ids: List[int],
    dry_run: bool = False,
    resolution_mode: Optional[str] = None,
    no_interactive: bool = False
) -> int:
    """Enhanced merge one or more user profiles into a main profile.
    
    Args:
        main_id: ID of the main user to merge into
        merge_ids: List of user IDs to merge into main_id
        dry_run: If True, show planned actions without executing
        resolution_mode: Auto-resolution mode for conflicts
        no_interactive: If True, use automatic resolution without prompts
        
    Returns:
        Exit code (0 for success, other codes for errors)
        
    Raises:
        ValueError: If any user ID is invalid or if attempting to merge user into themselves
        SQLAlchemyError: If database operation fails
    """
    try:
        # Validate arguments
        validate_merge_args(main_id, merge_ids)
        
        session = db_manager.get_session()
        try:
            # Lock and retrieve all users
            with session.begin():
                # Get main user with row lock
                main_user = session.query(User).filter_by(id=main_id).with_for_update().first()
                if not main_user:
                    click.echo(f"ERROR: Main user with ID {main_id} not found", err=True)
                    return 4
                
                if main_user.is_deleted():
                    click.echo(f"ERROR: Main user with ID {main_id} is deleted", err=True)
                    return 4
                
                # Get all merge users with row locks
                merge_users = []
                for merge_id in merge_ids:
                    merge_user = session.query(User).filter_by(id=merge_id).with_for_update().first()
                    if not merge_user:
                        click.echo(f"ERROR: Merge user with ID {merge_id} not found", err=True)
                        return 4
                    
                    if merge_user.is_deleted():
                        click.echo(f"ERROR: Merge user with ID {merge_id} is deleted", err=True)
                        return 4
                    
                    merge_users.append(merge_user)
                
                # Detect all conflicts across all users
                all_conflicts = {}
                all_resolutions = {}
                
                for merge_user in merge_users:
                    conflicts = _detect_conflicts(main_user, merge_user)
                    
                    if conflicts:
                        if dry_run:
                            all_conflicts[merge_user.id] = conflicts
                        else:
                            # Resolve conflicts
                            if no_interactive and not resolution_mode:
                                # Check for email conflicts in non-interactive mode
                                if 'email' in conflicts:
                                    click.echo("ERROR: Email conflict detected in non-interactive mode", err=True)
                                    return 2
                            
                            resolved_values = _resolve_conflicts(
                                main_user, merge_user, conflicts,
                                resolution_mode, no_interactive
                            )
                            
                            # Apply resolved values to main user
                            for field, (value, resolution) in resolved_values.items():
                                setattr(main_user, field, value)
                                all_resolutions[field] = resolution
                    
                    # Merge non-conflicting fields
                    if not dry_run:
                        filled_fields = _merge_non_conflicting_fields(main_user, merge_user)
                        for field in filled_fields:
                            all_resolutions[field] = "kept_duplicate"
                
                if dry_run:
                    _show_dry_run_preview(main_user, merge_users, all_conflicts)
                    return 0
                
                # Show summary and get confirmation unless non-interactive
                if not no_interactive and not _confirm_merge(main_user, merge_users):
                    click.echo("Merge operation cancelled.")
                    return 5
                
                # Perform soft delete on merged users
                for merge_user in merge_users:
                    merge_user.soft_delete()
                
                # Commit transaction
                session.commit()
                
                # Log the successful merge
                log_merge_event(main_id, merge_ids, all_resolutions)
                
                click.echo("Profile merge completed successfully.")
                return 0
                
        except KeyboardInterrupt:
            session.rollback()
            click.echo("\nMerge operation aborted by user.", err=True)
            return 5
        except SQLAlchemyError as e:
            session.rollback()
            click.echo(f"ERROR: Database error occurred: {e}", err=True)
            return 1
        except Exception as e:
            session.rollback()
            click.echo(f"ERROR: An unexpected error occurred: {e}", err=True)
            return 1
        finally:
            session.close()
            
    except Exception as e:
        return handle_merge_errors(e)


def _detect_conflicts(main_user: User, merge_user: User) -> Dict[str, Tuple[Any, Any]]:
    """Detect conflicting field values between two users.
    
    Args:
        main_user: Main user object
        merge_user: User to merge
        
    Returns:
        Dictionary mapping field names to (main_value, merge_value) tuples
    """
    conflicts = {}
    
    # Fields that can have conflicts
    conflict_fields = ['email', 'phone', 'address', 'usbc_id', 'tnba_id']
    
    for field in conflict_fields:
        main_value = getattr(main_user, field)
        merge_value = getattr(merge_user, field)
        
        # Skip if both values are null/empty
        if not main_value and not merge_value:
            continue
            
        # Only consider it a conflict if both values are non-empty and different
        if (main_value and merge_value and 
            str(main_value).strip() != str(merge_value).strip()):
            conflicts[field] = (main_value, merge_value)
    
    return conflicts


def _resolve_conflicts(
    main_user: User, 
    merge_user: User, 
    conflicts: Dict[str, Tuple[Any, Any]],
    resolution_mode: Optional[str] = None,
    no_interactive: bool = False
) -> Dict[str, Tuple[Any, str]]:
    """Resolve conflicts through interactive prompts or automatic resolution.
    
    Args:
        main_user: Main user object
        merge_user: User to merge
        conflicts: Dictionary of conflicting fields
        resolution_mode: Auto-resolution mode
        no_interactive: If True, use automatic resolution
        
    Returns:
        Dictionary mapping field names to (resolved_value, resolution_type) tuples
    """
    resolved_values = {}
    
    for field, (main_value, merge_value) in conflicts.items():
        if resolution_mode or no_interactive:
            # Automatic resolution
            if resolution_mode == "prefer_main":
                resolved_values[field] = (main_value, "kept_primary")
            elif resolution_mode == "prefer_merge":
                resolved_values[field] = (merge_value, "kept_duplicate")
            elif resolution_mode == "prefer_longest":
                if len(str(merge_value)) > len(str(main_value)):
                    resolved_values[field] = (merge_value, "kept_longest")
                else:
                    resolved_values[field] = (main_value, "kept_longest")
            else:
                # Default to main value in non-interactive mode
                resolved_values[field] = (main_value, "kept_primary")
        else:
            # Interactive resolution
            field_display = field.replace('_', ' ').title()
            
            console.print(f"\n[bold yellow]Conflicting {field_display.lower()}s found:[/bold yellow]")
            console.print(f"[cyan]Main user (ID {main_user.id}):[/cyan] {main_value}")
            console.print(f"[magenta]Merge user (ID {merge_user.id}):[/magenta] {merge_value}")
            
            while True:
                choice = click.prompt(
                    "Choose which value to keep [1=main, 2=merge, s=skip]",
                    type=str
                ).lower()
                
                if choice == '1':
                    resolved_values[field] = (main_value, "kept_primary")
                    break
                elif choice == '2':
                    resolved_values[field] = (merge_value, "kept_duplicate")
                    break
                elif choice == 's':
                    # Skip - keep main user's value
                    resolved_values[field] = (main_value, "kept_primary")
                    break
                else:
                    console.print("[red]Invalid choice. Please enter 1, 2, or s.[/red]")
    
    return resolved_values


def _merge_non_conflicting_fields(main_user: User, merge_user: User) -> List[str]:
    """Merge non-conflicting fields from merge_user into main_user.
    
    Args:
        main_user: Main user object to update
        merge_user: User to merge from
        
    Returns:
        List of field names that were filled from merge_user
    """
    # Fields that can be merged
    mergeable_fields = ['email', 'phone', 'address', 'usbc_id', 'tnba_id']
    filled_fields = []
    
    for field in mergeable_fields:
        main_value = getattr(main_user, field)
        merge_value = getattr(merge_user, field)
        
        # If main user doesn't have a value but merge user does, use merge value
        if not main_value and merge_value:
            setattr(main_user, field, merge_value)
            filled_fields.append(field)
    
    return filled_fields


def _show_dry_run_preview(
    main_user: User, 
    merge_users: List[User], 
    all_conflicts: Dict[int, Dict[str, Tuple[Any, Any]]]
) -> None:
    """Show a preview of planned merge actions in dry-run mode.
    
    Args:
        main_user: Main user object
        merge_users: List of users to merge
        all_conflicts: Dictionary mapping user IDs to their conflicts
    """
    console.print("\n[bold green]PLANNED MERGE ACTIONS (DRY RUN)[/bold green]")
    console.print(f"[cyan]Primary user:[/cyan] {main_user.first_name} {main_user.last_name} (ID {main_user.id})")
    
    # Create table for merge summary
    table = Table(title="Merge Summary", box=box.ROUNDED)
    table.add_column("User ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Action", style="yellow")
    table.add_column("Conflicts", style="red")
    
    for merge_user in merge_users:
        conflicts = all_conflicts.get(merge_user.id, {})
        conflict_str = ", ".join(conflicts.keys()) if conflicts else "None"
        
        table.add_row(
            str(merge_user.id),
            f"{merge_user.first_name} {merge_user.last_name}",
            "Soft delete",
            conflict_str
        )
    
    console.print(table)
    
    # Show detailed conflicts if any
    if all_conflicts:
        console.print("\n[bold yellow]CONFLICT DETAILS:[/bold yellow]")
        for user_id, conflicts in all_conflicts.items():
            user = next(u for u in merge_users if u.id == user_id)
            console.print(f"\n[cyan]User {user_id} ({user.first_name} {user.last_name}):[/cyan]")
            
            for field, (main_val, merge_val) in conflicts.items():
                console.print(f"  • {field}: [green]{main_val}[/green] vs [red]{merge_val}[/red]")


def _confirm_merge(main_user: User, merge_users: List[User]) -> bool:
    """Show summary and confirm merge operation.
    
    Args:
        main_user: Main user object
        merge_users: List of users to merge
        
    Returns:
        True if user confirms, False otherwise
    """
    console.print(f"\n[bold green]Merge Summary:[/bold green]")
    console.print(f"[cyan]Main user:[/cyan] {main_user.first_name} {main_user.last_name} (ID {main_user.id})")
    console.print(f"[magenta]Users to merge:[/magenta] {', '.join([f'{u.first_name} {u.last_name} (ID {u.id})' for u in merge_users])}")
    
    return click.confirm("Proceed with merge?", default=False)


def validate_merge_args(main_id: Optional[int], merge_ids: List[int]) -> None:
    """Validate merge command arguments.
    
    Args:
        main_id: Main user ID
        merge_ids: List of merge user IDs
        
    Raises:
        SystemExit: With exit code 4 if validation fails
    """
    if main_id is None:
        click.echo("ERROR: --main-id is required", err=True)
        sys.exit(4)
    
    if not merge_ids:
        click.echo("ERROR: At least one --merge-id is required", err=True)
        sys.exit(4)
    
    if main_id in merge_ids:
        click.echo(f"ERROR: Cannot merge user {main_id} into themselves", err=True)
        sys.exit(4)


def handle_merge_errors(e: Exception) -> int:
    """Handle merge command errors with appropriate exit codes.
    
    Args:
        e: Exception to handle
        
    Returns:
        Exit code
    """
    if isinstance(e, ValueError):
        error_msg = str(e)
        if "not found" in error_msg:
            click.echo(f"ERROR: {error_msg}", err=True)
            return 4
        else:
            click.echo(f"ERROR: {error_msg}", err=True)
            return 4
    elif isinstance(e, SQLAlchemyError):
        click.echo(f"ERROR: Database error occurred: {e}", err=True)
        return 1
    else:
        click.echo(f"ERROR: An unexpected error occurred: {e}", err=True)
        return 1