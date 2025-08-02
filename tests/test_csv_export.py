"""Tests for CSV export utilities."""

import pytest
import csv
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from utils.csv_writer import export_users_to_csv, validate_csv_path


class TestExportUsersToCSV:
    """Test CSV export functionality."""
    
    def test_export_empty_users_list(self):
        """Test exporting empty users list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "empty_test.csv"
            
            export_users_to_csv([], csv_path)
            
            assert csv_path.exists()
            
            # Check content
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) == 1  # Only header
                assert rows[0] == ['id', 'name', 'role', 'email', 'created_at']
    
    def test_export_single_user(self):
        """Test exporting single user."""
        users_data = [
            {
                'id': 1,
                'name': 'John Doe',
                'role': 'registered_user',
                'email': 'john@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "single_user.csv"
            
            export_users_to_csv(users_data, csv_path)
            
            assert csv_path.exists()
            
            # Check content
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) == 2  # Header + 1 user
                assert rows[0] == ['id', 'name', 'role', 'email', 'created_at']
                assert rows[1] == ['1', 'John Doe', 'registered_user', 'john@example.com', '2024-01-15T10:30:00Z']
    
    def test_export_multiple_users(self):
        """Test exporting multiple users."""
        users_data = [
            {
                'id': 1,
                'name': 'John Doe',
                'role': 'registered_user',
                'email': 'john@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'role': 'org_member',
                'email': 'jane@tournamentorg.com',
                'created_at': '2024-02-01T14:22:30Z'
            },
            {
                'id': 3,
                'name': 'Bob Wilson',
                'role': 'unregistered_user',
                'email': '',
                'created_at': '2024-03-01T09:15:45Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "multiple_users.csv"
            
            export_users_to_csv(users_data, csv_path)
            
            assert csv_path.exists()
            
            # Check content
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) == 4  # Header + 3 users
                assert rows[0] == ['id', 'name', 'role', 'email', 'created_at']
                assert rows[1][1] == 'John Doe'
                assert rows[2][1] == 'Jane Smith'
                assert rows[3][1] == 'Bob Wilson'
    
    def test_export_unicode_characters(self):
        """Test exporting users with Unicode characters."""
        users_data = [
            {
                'id': 1,
                'name': 'José García',
                'role': 'registered_user',
                'email': 'jose@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'name': 'Zoë Smith',
                'role': 'registered_user',
                'email': 'zoe@example.com',
                'created_at': '2024-02-01T14:22:30Z'
            },
            {
                'id': 3,
                'name': '田中太郎',  # Japanese characters
                'role': 'registered_user',
                'email': 'tanaka@example.com',
                'created_at': '2024-03-01T09:15:45Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "unicode_test.csv"
            
            export_users_to_csv(users_data, csv_path)
            
            assert csv_path.exists()
            
            # Check content preserves Unicode
            with open(csv_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'José García' in content
                assert 'Zoë Smith' in content
                assert '田中太郎' in content
    
    def test_export_special_csv_characters(self):
        """Test exporting users with special CSV characters (commas, quotes, newlines)."""
        users_data = [
            {
                'id': 1,
                'name': 'O\'Malley, Patrick',  # Comma and apostrophe
                'role': 'registered_user',
                'email': 'patrick@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'name': 'Smith "The Great"',  # Quotes
                'role': 'registered_user',
                'email': 'smith@example.com',
                'created_at': '2024-02-01T14:22:30Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "special_chars.csv"
            
            export_users_to_csv(users_data, csv_path)
            
            assert csv_path.exists()
            
            # Check that CSV parsing works correctly
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                assert len(rows) == 3  # Header + 2 users
                assert rows[1][1] == 'O\'Malley, Patrick'
                assert rows[2][1] == 'Smith "The Great"'
    
    def test_export_creates_parent_directory(self):
        """Test that export creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "nested" / "dirs" / "test.csv"
            
            users_data = [
                {
                    'id': 1,
                    'name': 'Test User',
                    'role': 'registered_user',
                    'email': 'test@example.com',
                    'created_at': '2024-01-15T10:30:00Z'
                }
            ]
            
            export_users_to_csv(users_data, csv_path)
            
            assert csv_path.exists()
            assert csv_path.parent.exists()
    
    def test_export_permission_error(self):
        """Test handling of permission errors."""
        users_data = [
            {
                'id': 1,
                'name': 'Test User',
                'role': 'registered_user',
                'email': 'test@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            }
        ]
        
        # Mock a permission error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                export_users_to_csv(users_data, Path("/tmp/test.csv"))
    
    def test_export_rfc4180_compliance(self):
        """Test RFC 4180 compliance of exported CSV."""
        users_data = [
            {
                'id': 1,
                'name': 'Test User',
                'role': 'registered_user',
                'email': 'test@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "rfc4180_test.csv"
            
            export_users_to_csv(users_data, csv_path)
            
            # Verify RFC 4180 compliance by parsing with standard csv module
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                rows = list(csv_reader)
                
                # Should parse without errors
                assert len(rows) == 2
                assert len(rows[0]) == 5  # 5 columns
                assert len(rows[1]) == 5  # 5 columns


class TestValidateCSVPath:
    """Test CSV path validation functionality."""
    
    def test_validate_valid_path(self):
        """Test validating a valid CSV path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path_str = str(Path(temp_dir) / "test.csv")
            
            result = validate_csv_path(csv_path_str)
            
            assert isinstance(result, Path)
            assert str(result) == csv_path_str
    
    def test_validate_path_creates_parent_directory(self):
        """Test that validation creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path_str = str(Path(temp_dir) / "nested" / "test.csv")
            
            result = validate_csv_path(csv_path_str)
            
            assert isinstance(result, Path)
            assert result.parent.exists()
            assert result.parent.is_dir()
    
    def test_validate_path_invalid_parent(self):
        """Test validation with invalid parent path."""
        # Try to create in a location that doesn't exist and can't be created
        with patch('pathlib.Path.mkdir', side_effect=OSError("Permission denied")):
            with pytest.raises(ValueError, match="Cannot create directory"):
                validate_csv_path("/invalid/path/test.csv")
    
    def test_validate_path_parent_is_file(self):
        """Test validation when parent path is a file, not directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file where we want a directory
            file_path = Path(temp_dir) / "file.txt"
            file_path.write_text("test")
            
            csv_path_str = str(file_path / "test.csv")
            
            with pytest.raises(ValueError, match="Parent path is not a directory"):
                validate_csv_path(csv_path_str)
    
    def test_validate_path_os_error(self):
        """Test validation with OS errors."""
        with patch('pathlib.Path.__init__', side_effect=OSError("Invalid path")):
            with pytest.raises(ValueError, match="Invalid CSV path"):
                validate_csv_path("invalid_path")
    
    def test_validate_path_relative_vs_absolute(self):
        """Test validation with both relative and absolute paths."""
        # Relative path
        result_rel = validate_csv_path("test.csv")
        assert isinstance(result_rel, Path)
        
        # Absolute path
        with tempfile.TemporaryDirectory() as temp_dir:
            abs_path = str(Path(temp_dir) / "test.csv")
            result_abs = validate_csv_path(abs_path)
            assert isinstance(result_abs, Path)
            assert result_abs.is_absolute()


class TestCSVRoundTrip:
    """Test CSV round-trip integrity."""
    
    def test_csv_round_trip_data_integrity(self):
        """Test that data survives CSV export and import."""
        original_data = [
            {
                'id': 1,
                'name': 'José García-O\'Malley',
                'role': 'registered_user',
                'email': 'jose@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2,
                'name': 'Smith, John "Jr."',
                'role': 'org_member',
                'email': 'john@example.com',
                'created_at': '2024-02-01T14:22:30Z'
            },
            {
                'id': 3,
                'name': 'Test\nUser',  # Newline in name
                'role': 'unregistered_user',
                'email': '',
                'created_at': '2024-03-01T09:15:45Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "round_trip_test.csv"
            
            # Export
            export_users_to_csv(original_data, csv_path)
            
            # Import
            imported_data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    imported_data.append(row)
            
            # Verify data integrity
            assert len(imported_data) == len(original_data)
            
            for original, imported in zip(original_data, imported_data):
                assert imported['id'] == str(original['id'])
                assert imported['name'] == original['name']
                assert imported['role'] == original['role']
                assert imported['email'] == original['email']
                assert imported['created_at'] == original['created_at']
    
    def test_csv_round_trip_unicode_preservation(self):
        """Test that Unicode characters are preserved in round-trip."""
        original_data = [
            {
                'id': 1,
                'name': '田中太郎',  # Japanese
                'role': 'registered_user',
                'email': 'tanaka@example.com',
                'created_at': '2024-01-15T10:30:00Z'
            },
            {
                'id': 2, 
                'name': 'Müller, Hans',  # German umlaut
                'role': 'registered_user',
                'email': 'hans@example.com',
                'created_at': '2024-02-01T14:22:30Z'
            },
            {
                'id': 3,
                'name': 'Øyvind Sørensen',  # Norwegian characters
                'role': 'registered_user',
                'email': 'oyvind@example.com',
                'created_at': '2024-03-01T09:15:45Z'
            }
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            csv_path = Path(temp_dir) / "unicode_round_trip.csv"
            
            # Export
            export_users_to_csv(original_data, csv_path)
            
            # Import
            imported_data = []
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    imported_data.append(row)
            
            # Verify Unicode preservation
            assert imported_data[0]['name'] == '田中太郎'
            assert imported_data[1]['name'] == 'Müller, Hans'
            assert imported_data[2]['name'] == 'Øyvind Sørensen'