"""CSV export utilities for the 4th Arrow Tournament Control application."""

import csv
from pathlib import Path
from typing import List, Dict, Any


def export_users_to_csv(users_data: List[Dict[str, Any]], output_path: Path) -> None:
    """Export user data to RFC 4180 compliant CSV file.
    
    Args:
        users_data: List of dictionaries containing user data
        output_path: Path where CSV file should be written
        
    Raises:
        OSError: If file cannot be written to specified path
        PermissionError: If insufficient permissions to write file
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = ['id', 'name', 'role', 'email', 'created_at']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(users_data)


def validate_csv_path(path_str: str) -> Path:
    """Validate and convert CSV path string to Path object.
    
    Args:
        path_str: String path to CSV file
        
    Returns:
        Path: Validated Path object
        
    Raises:
        ValueError: If path is invalid or parent directory doesn't exist and can't be created
    """
    try:
        path = Path(path_str)
        
        # Check if parent directory exists or can be created
        if not path.parent.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create directory for CSV file: {e}")
        
        # Check if we can write to the directory
        if not path.parent.is_dir():
            raise ValueError(f"Parent path is not a directory: {path.parent}")
            
        return path
        
    except OSError as e:
        raise ValueError(f"Invalid CSV path: {e}")