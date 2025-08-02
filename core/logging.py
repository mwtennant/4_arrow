"""Structured logging utilities for the 4th Arrow Tournament Control application."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

# JSON Schema for merge profile events
MERGE_PROFILE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "MergeProfileEvent",
    "type": "object",
    "required": [
        "event",
        "timestamp", 
        "primary_id",
        "merged_ids",
        "field_resolutions"
    ],
    "properties": {
        "event": {"const": "MERGE_PROFILE"},
        "timestamp": {"type": "string", "format": "date-time"},
        "primary_id": {"type": "integer"},
        "merged_ids": {"type": "array", "items": {"type": "integer"}},
        "field_resolutions": {
            "type": "object",
            "additionalProperties": {
                "enum": ["kept_primary", "kept_duplicate", "kept_longest"]
            }
        }
    }
}


def ensure_logs_directory() -> Path:
    """Ensure the logs directory exists and return its path.
    
    Returns:
        Path to the logs directory.
    """
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def log_merge_event(
    primary_id: int,
    merged_ids: List[int], 
    field_resolutions: Dict[str, str]
) -> None:
    """Log a merge profile event to the structured log file.
    
    Args:
        primary_id: ID of the primary user that was kept
        merged_ids: List of user IDs that were merged into primary
        field_resolutions: Dictionary mapping field names to resolution decisions
    """
    logs_dir = ensure_logs_directory()
    log_file = logs_dir / "merge_profile.log"
    
    # Create log entry
    log_entry = {
        "event": "MERGE_PROFILE",
        "timestamp": datetime.now().isoformat() + "Z",
        "primary_id": primary_id,
        "merged_ids": merged_ids,
        "field_resolutions": field_resolutions
    }
    
    # Validate against schema if jsonschema is available
    if JSONSCHEMA_AVAILABLE:
        try:
            jsonschema.validate(log_entry, MERGE_PROFILE_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Log entry validation failed: {e}")
    
    # Append to log file as JSON Lines format
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")


def validate_log_entry(log_entry: Dict[str, Any]) -> bool:
    """Validate a log entry against the merge profile schema.
    
    Args:
        log_entry: Dictionary representing the log entry
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If jsonschema is not available
    """
    if not JSONSCHEMA_AVAILABLE:
        raise ValueError("jsonschema library is required for log validation")
    
    try:
        jsonschema.validate(log_entry, MERGE_PROFILE_SCHEMA)
        return True
    except jsonschema.ValidationError:
        return False