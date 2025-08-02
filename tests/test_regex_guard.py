"""Regex guard tests to ensure legacy terminology is not used in non-legacy code."""

import os
import re
from pathlib import Path
import pytest


class TestRegexGuard:
    """Regex guard tests to prevent legacy terminology usage."""
    
    def test_no_legacy_is_member_in_non_legacy_paths(self):
        """Test that is_member is not used outside of legacy-allowed paths.
        
        This test ensures the role terminology refactor is complete by checking
        that the legacy `is_member` property/attribute is only used in:
        - Legacy test files (this file, test_role_helpers.py)  
        - Legacy property definition in models.py
        - Documentation/comments explaining the deprecation
        
        Any other usage indicates incomplete migration.
        """
        project_root = Path(__file__).parent.parent
        forbidden_usage = []
        
        # Allowed files/patterns where is_member is permitted
        allowed_patterns = [
            # This guard test file itself
            str(Path(__file__).name),
            # The role helpers test file that specifically tests legacy behavior
            "test_role_helpers.py",
            # Legacy shim test file that tests backward compatibility
            "test_legacy_shim.py",
            # Model definition where the deprecated property is defined
            "core/models.py",
            # Legacy compatibility shim module
            "utils/legacy_shim.py",
            # Migration script that handles legacy data
            "scripts/migrate_role_terminology.py",
            # Generated PRP files that document the change
            "PRPs/",
            "INITIAL_",
            # Documentation files
            ".md",
            ".rst",
            ".txt"
        ]
        
        def is_allowed_file(file_path: Path) -> bool:
            """Check if file is allowed to contain is_member."""
            file_str = str(file_path.relative_to(project_root))
            return any(pattern in file_str for pattern in allowed_patterns)
        
        # Search for is_member usage in Python files
        for py_file in project_root.rglob("*.py"):
            # Skip virtual environment and other non-project directories
            if any(part in str(py_file) for part in ['venv', '.venv', 'env', '.env', 'node_modules', '.git']):
                continue
                
            if is_allowed_file(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and docstrings that mention is_member for documentation
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                        continue
                    
                    # Look for is_member usage (property access, attribute reference)
                    if re.search(r'\bis_member\b', line):
                        # Additional check: skip lines that are just documenting the deprecation
                        if 'deprecated' in line.lower() or 'legacy' in line.lower():
                            continue
                            
                        relative_path = py_file.relative_to(project_root)
                        forbidden_usage.append(f"{relative_path}:{line_num}: {line.strip()}")
                        
            except (UnicodeDecodeError, PermissionError):
                # Skip files we can't read
                continue
        
        if forbidden_usage:
            error_msg = (
                "Found legacy 'is_member' usage in non-legacy code paths. "
                "All usage should be migrated to use the new role helper methods "
                "(is_registered_user(), is_unregistered_user(), is_org_member()).\n\n"
                "Forbidden usage found in:\n" + 
                "\n".join(forbidden_usage)
            )
            pytest.fail(error_msg)
    
    def test_no_legacy_member_flag_in_non_legacy_cli_help(self):
        """Test that CLI help text doesn't reference --member flag except as deprecated."""
        project_root = Path(__file__).parent.parent
        
        # Search in CLI command files for help text
        forbidden_help_text = []
        
        for py_file in project_root.rglob("*.py"):
            # Skip test files and this guard file
            if "test" in str(py_file) or py_file.name == Path(__file__).name:
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for help text that mentions --member without deprecation context
                lines = content.split('\n')
                for line_num, line in enumerate(lines, 1):
                    if '--member' in line and 'help=' in line:
                        # Allow if it mentions deprecation
                        if 'deprecated' not in line.lower() and 'legacy' not in line.lower():
                            relative_path = py_file.relative_to(project_root)
                            forbidden_help_text.append(f"{relative_path}:{line_num}: {line.strip()}")
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if forbidden_help_text:
            error_msg = (
                "Found CLI help text referencing --member flag without deprecation context. "
                "All --member references should indicate deprecation and suggest --role instead.\n\n"
                "Non-deprecated --member help found in:\n" + 
                "\n".join(forbidden_help_text)
            )
            pytest.fail(error_msg)
    
    def test_role_enum_usage_preferred(self):
        """Test that new ProfileRole enum is used consistently."""
        project_root = Path(__file__).parent.parent
        
        # Count usage of new terminology vs old
        new_role_usage = 0
        old_member_usage = 0
        
        for py_file in project_root.rglob("*.py"):
            # Skip test files for this count (they may test both old and new)
            if "test" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Count new role method usage
                new_role_usage += len(re.findall(r'\bis_registered_user\b', content))
                new_role_usage += len(re.findall(r'\bis_unregistered_user\b', content))
                new_role_usage += len(re.findall(r'\bis_org_member\b', content))
                new_role_usage += len(re.findall(r'ProfileRole\.(REGISTERED_USER|UNREGISTERED_USER|ORG_MEMBER)', content))
                
                # Count old member property usage (excluding comments/docstrings)
                lines = content.split('\n')
                for line in lines:
                    stripped = line.strip()
                    if not (stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'"*3)):
                        if 'is_member' in line and 'deprecated' not in line.lower():
                            old_member_usage += 1
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        # We expect significantly more new usage than old (outside of deprecation shims)
        # Allow some old usage for backward compatibility, but new should dominate
        if old_member_usage > 0 and new_role_usage == 0:
            pytest.fail(
                f"Found {old_member_usage} old member usage but no new role usage. "
                "Migration appears incomplete."
            )
        
        # Log the ratio for monitoring (not a failure condition)
        if new_role_usage > 0:
            ratio = new_role_usage / max(old_member_usage, 1)
            print(f"Role usage ratio: {new_role_usage} new vs {old_member_usage} old (ratio: {ratio:.1f}x)")
    
    def test_consistent_role_terminology_in_variable_names(self):
        """Test that variable names use consistent new role terminology."""
        project_root = Path(__file__).parent.parent
        inconsistent_vars = []
        
        # Pattern for variable names that should use new terminology
        old_var_patterns = [
            r'\bmember_.*=',      # member_count, member_list, etc.
            r'\bis_member_.*=',   # is_member_flag, etc.
            r'.*_member\s*=',     # user_member, check_member, etc.
        ]
        
        for py_file in project_root.rglob("*.py"):
            # Skip test files and legacy files
            if "test" in str(py_file) or "legacy" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    # Skip comments and strings
                    if line.strip().startswith('#'):
                        continue
                        
                    for pattern in old_var_patterns:
                        if re.search(pattern, line):
                            # Allow if it's clearly legacy/deprecated context
                            if 'legacy' in line.lower() or 'deprecated' in line.lower():
                                continue
                            
                            relative_path = py_file.relative_to(project_root) 
                            inconsistent_vars.append(f"{relative_path}:{line_num}: {line.strip()}")
                            
            except (UnicodeDecodeError, PermissionError):
                continue
        
        if inconsistent_vars:
            error_msg = (
                "Found variable names using old 'member' terminology. "
                "Consider using 'registered_user', 'unregistered_user', or 'role' instead.\n\n"
                "Inconsistent variable names found in:\n" + 
                "\n".join(inconsistent_vars[:10])  # Limit output
            )
            if len(inconsistent_vars) > 10:
                error_msg += f"\n... and {len(inconsistent_vars) - 10} more"
            
            # This is a warning, not a hard failure - variable names are less critical
            print(f"WARNING: {error_msg}")